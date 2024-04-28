import os
import ssl
import time as t

import certifi
import requests
from urllib.request import urlopen
from Editor import *
from tiktok_uploader.upload import upload_video, upload_videos
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
import pandas as pd

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
    driver.close()
    if soup is None:
        logger.debug(green(f"Error fetching data for {link}"))
        return
    soup = soup.find_all('div', class_='css-1qb12g8-DivThreeColumnContainer eegew6e2')
    #write to file
    with open(f"html_paths/{link.split('@')[-1]}.html", "w", encoding='utf-8') as file:
        file.write(str(soup))
    logger.debug(green(f"Successfully wrote data to {link.split('@')[-1]}.html"))

def get_video_links_from_html(html_path):
    """Extract video links from an HTML file."""
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True) if "tiktok.com" in a['href']]

def channel_to_dict(channel):
    tmp = dict()
    tmp["NAME"] = channel.name
    tmp["PATH"] = channel.path
    tmp["COOKIES_PATH"] = channel.cookies
    tmp["UPLOAD"] = channel.upload
    tmp["SCHEDULE_FILE"] = channel.schedule_file
    tmp["SCHEDULE"] = channel.schedule
    tmp["DOWNLOADED"] = channel.downloaded
    tmp["READY"] = channel.ready
    tmp["POSTED"] = channel.posted
    tmp["HTML_PATHS"] = channel.html_paths
    tmp["DESCRIPTIONS"] = channel.descriptions
    return tmp

def download(channel, available, quantity):
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

    to_be_downloaded = list()
    for count in range(quantity):
        temp = available[random.randint(0, len(available) - 1)]
        to_be_downloaded.append(temp)
        available.remove(temp)

    for download_link in to_be_downloaded:
        data = {'id': download_link, 'locale': 'en', 'tt': 'ckc5cjNh'}
        response = requests.post('https://ssstik.io/abc', params=params, cookies=cookies, headers=headers, data=data)
        logger.debug(f"Response Status: {response.status_code} for URL: {response.url}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            tmp_link = soup.a.get("href") if soup.a else None
            if not tmp_link:
                logger.debug("soup failed")
                continue
            context = ssl.create_default_context(cafile=certifi.where())
            mp4_temp = urlopen(tmp_link, context=context)
            file_path = f"downloaded/{download_link.split('/')[-1]}.mp4"
            with open(file_path, "wb") as output:
                total_bytes = 0
                while True:
                    buffer = mp4_temp.read(4096)
                    if not buffer:
                        break
                    output.write(buffer)
                    total_bytes += len(buffer)
                if(total_bytes > 4096):
                    channel.downloaded.append(file_path)
                    with open(channel.path, 'w') as f:
                        json.dump(channel_to_dict(channel), f)
                    to_be_downloaded.remove(download_link)
                    logger.debug(f"download succeeded for video {download_link} in channel {channel.name}")
                else:
                    os.remove(file_path)
                    logger.debug("download failed")
        else:
            logger.debug("response failed")
        t.sleep(5)

    return to_be_downloaded

def available_downloads(channel, min = 3):
    available = list()
    for html_path in channel.html_paths:
        count = 0
        for link in get_video_links_from_html(html_path):
            for posted in channel.posted:
                print(f"posted: {posted}\n link: {link}")
                if posted == link:
                    continue
            available.append(link)
        if len(available) < min:
            get_data_channel(html_path)
    return available if len(available) > min else None

def get_post_time(channel):
    current = channel.schedule
    if current == "" or datetime.now() > datetime.strptime(current, '%Y-%m-%d %H:%M'):
        current = datetime.now()
    else:
        current = datetime.strptime(current, '%Y-%m-%d %H:%M')

    times = list()
    with open(channel.schedule_file) as schedule:
        times = schedule.read().split("\n")
    times = [item.split("_") for item in times]

    if current.hour >= int(times[(current.weekday())][-1]):
        current = (current + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    for hour in times[current.weekday()]:
        if current.hour < int(hour):
            current = current.replace(hour=int(hour))
            break
    return current.strftime('%Y-%m-%d %H:%M')
def parse(quantity = 1):
    with open('channels.json') as f:
        channels_dict = json.load(f)

    for current_channel in channels_dict:
        #init channel
        with open(current_channel["FILEPATH"]) as f:
            channel = Channel(json.load(f))
        #confirm videos are available:
        available = available_downloads(channel, quantity)
        if available is None:
            logger.debug(f"not enough avalable downloads for channel {channel.name}")
        logger.debug(f"found available videos to download")
        #if videos are available download them
        failed = 0 if quantity - len(channel.downloaded) - len(channel.ready) <= 0 else download(channel, available, quantity - len(channel.downloaded) - len(channel.ready))
        if failed != 0:
            failed = len(failed)
        logger.debug(f"couldn't downloaded {failed}" if failed != 0 else "Downloaded everything!")

        #edit videos
        count = 0
        for path in channel.downloaded:
            if(count >= quantity - len(channel.ready)):
                break
            temp = f"ready/{path.split('/')[-1]}"
            try:
                make_video_format1(path, output=temp)
                channel.ready.append(temp)
                channel.downloaded.remove(path)
                with open(channel.path, 'w') as f:
                    json.dump(channel_to_dict(channel), f)
                logger.debug(f"successfully edited {path}")
                count += 1
            except Exception as e:
                logger.debug(f"failed to edit {path} retrying...")
        logger.debug(f"successfully edited {count}/{quantity - len(channel.ready)} videos")

        #upload videos
        count = 0
        for path in channel.ready:
            if count > quantity:
                break

            try:
                logger.debug(f"Adding video {path}")
                video = {"path": path,
                         "description": channel.descriptions[random.randint(0, len(channel.descriptions) - 1)],
                         "schedule": get_post_time(channel)}
                upload_video(path, description=video["description"], cookies=channel.cookies,
                             schedule=video["schedule"])
                channel.posted.append(video)
                channel.schedule = video["schedule"]
                channel.ready.remove(path)
                with open(channel.path, 'w') as f:
                    json.dump(channel_to_dict(channel), f)
                count += 1
            except:
                logger.debug(f"failed to upload {path}")



if __name__ == "__main__":
    parse(1)

