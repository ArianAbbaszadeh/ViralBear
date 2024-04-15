import os
import ssl
import certifi
import requests
from urllib.request import urlopen
from Editor import *
from tiktok_uploader.upload import upload_video
from tiktok_uploader.browsers import get_browser
from tiktok_uploader import config, logger
from tiktok_uploader.utils import green
from tiktok_uploader.auth import AuthBackend
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from schedule import *
from Channel import *
import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import logging
import random

def remove_emojis(data):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)

def get_id(link):
    #return the id portion of the link 
    return link.split("/")[-1]

def get_data_channel(link):
    #download data

    auth = AuthBackend('', '', None, cookies="cookies/cookies1.txt")
    driver = get_browser()
    driver = auth.authenticate_agent(driver)

    logger.debug(green('Navigating to link'))
    driver.get(link)
    confirmation = EC.presence_of_element_located(
        (By.XPATH, config["selectors"]["upload"]["confirmation"])
    )
    WebDriverWait(driver, config['explicit_wait']).until(confirmation)
    #make soup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup = soup.find_all('div', class_='css-1qb12g8-DivThreeColumnContainer eegew6e2')
    #write to file
    with open("tiktok_current.html", "w", encoding='utf-8') as file:
        file.write(str(soup))
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_video_links_from_html(html_path):
    """Extract video links from an HTML file."""
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True) if "tiktok.com" in a['href']]

def download(link, downloaded_set, download_log_path):
    """Download a video if it's not already downloaded, log the download, and return the size of the downloaded file."""
    cookies = {
        '_gid': 'GA1.2.247148643.1690580091',
        '__cflb': '0H28v8EEysMCvTTqtu4Ydr4bADFLp2DZYjhRqD8oBC9',
        '_gat_UA-3524196-6': '1',
        '_ga': 'GA1.2.550956787.1690580091',
        '_ga_ZSF3D6YSLC': 'GS1.1.1690580091.1.1.1690580248.0.0.0',
    }

    headers = {
        'authority': 'ssstik.io',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'hx-current-url': 'https://ssstik.io/en',
        'hx-request': 'true',
        'hx-target': 'target',
        'hx-trigger': '_gcaptcha_pt',
        'origin': 'https://ssstik.io',
        'referer': 'https://ssstik.io/en',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    params = {'url': 'dl'}
    data = {'id': link, 'locale': 'en', 'tt': 'ckc5cjNh'}

    try:
        response = requests.post('https://ssstik.io/abc', params=params, cookies=cookies, headers=headers, data=data)
        logging.info(f"Response Status: {response.status_code} for URL: {response.url}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            download_link = soup.a.get("href") if soup.a else None
            if download_link and download_link not in downloaded_set:
                downloaded_set.add(download_link)
                context = ssl.create_default_context(cafile=certifi.where())
                mp4_temp = urlopen(download_link, context=context)
                file_path = f"downloaded/{link.split('/')[-1]}.mp4"
                with open(file_path, "wb") as output:
                    total_bytes = 0
                    while True:
                        buffer = mp4_temp.read(4096)
                        if not buffer:
                            break
                        output.write(buffer)
                        total_bytes += len(buffer)
                with open(download_log_path, "a") as log_file:
                    log_file.write(f"{download_link}\n")
                logging.info(f"Successfully downloaded: {file_path}")
                return float(total_bytes)
            else:
                logging.warning("No new download link found or duplicate found.")
                return 0.0
        else:
            logging.error(f"Failed to download {link}: HTTP status code {response.status_code}")
            return 0.0
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for {link}: {e}")
        return 0.0

def manage_downloads(html_path, quantity, download_log_path):
    """Extract links from HTML, shuffle them, and manage the download process for a random set of videos."""
    links = get_video_links_from_html(html_path)
    random.shuffle(links)  # Shuffle links to randomize the selection
    downloaded_set = set()
    if os.path.exists(download_log_path):
        with open(download_log_path, "r") as file:
            downloaded_set.update(file.read().splitlines())
    
    count = 0
    for link in links:
        if count >= quantity:
            break
        result = download(link, downloaded_set, download_log_path)
        if result > 0.0:
            count += 1
            logging.info(f"Successfully downloaded: {link}")
        else:
            logging.info(f"Failed to download or skipped: {link}")
    return count


if __name__ == "__main__":
    get_data_channel("https://www.tiktok.com/@bobbyleeclips")
    download()
    html_path = "tiktok_current.html"
    quantity = 2
    download_log_path = "downloaded_videos_log.txt"
    manage_downloads(html_path, quantity, download_log_path)
