from selenium import webdriver
import time
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
from Editor import *
from tiktok_uploader.upload import upload_video
from tiktok_uploader.browsers import get_browser
from tiktok_uploader import config, logger
from tiktok_uploader.utils import green
from Uploader import *
from schedule import *
from Channel import *
import re
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

    #Wait 2 seconds after direct.get() is completed to increase likelihood of success
    auth = AuthBackend('', '', None, cookies="cookies/cookies1.txt")
    driver = get_browser()
    driver = auth.authenticate_agent(driver)

    #time.sleep(10)
    logger.debug(green('Navigating to link'))
    driver.get(link)
    channel_name = link.split("@")[-1]
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

    driver.quit()

def get_channels(path = "channels.csv"):
    return [Channel(channel) for channel in pd.read_csv(path).to_dict('records')]

def download(link):
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
        # 'cookie': '_gid=GA1.2.247148643.1690580091; __cflb=0H28v8EEysMCvTTqtu4Ydr4bADFLp2DZYjhRqD8oBC9; _gat_UA-3524196-6=1; _ga=GA1.2.550956787.1690580091; _ga_ZSF3D6YSLC=GS1.1.1690580091.1.1.1690580248.0.0.0',
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

    params = {
        'url': 'dl',
    }

    data = {
        'id': link,
        'locale': 'en',
        'tt': 'ckc5cjNh',
    }

    #generate response and make soup from it
    response = requests.post('https://ssstik.io/abc', params=params, cookies=cookies, headers=headers, data=data)
    temp = BeautifulSoup(response.text, "html.parser")
    
    #get download link from href
    download_link = temp.a["href"]

    #Download in 4096 byte blocks until cannot read anymore data and break the loop
    mp4_temp = urlopen(download_link)
    with open(f"downloaded/{get_id(link)}.mp4", "wb") as output:
        bytes = 0
        while True:
            data = mp4_temp.read(4096)
            if data:
                #write 4096 bytes at a time
                output.write(data)
                bytes += 4096
            else:
                #return total when no more bytes can be written
                return float(bytes)

def parse(genre):    
    #get data from file
    soup = BeautifulSoup(open("tiktok_current.html", encoding="utf8"), "html.parser")
    
    #find all <a/> with class for tiktok links 
    videos = soup.find_all("a", {"class" : "tiktok-1wrhn5c-AMetaCaptionLine"})

    #create list of all seen videos
    cached = pd.read_csv('cached.csv')
    
    #finds all videos not in cache

    videos = [video for video in videos if f'{get_id(video["href"])}.mp4' not in os.listdir("downloads")]
        
    for num, video in enumerate(videos):
            #downlaods videos and writes to cache
            print(f'DOWNLOADING {get_id(video["href"])}.mp4({num+1}/{len(videos)})...')
            bytes = download(video["href"])

            #create new video for all channels
            for channel in [channel for channel in get_channels() if channel.genre == genre]:
                schedule = Schedule(channel)
                print(get_id(video["href"]) + "\n" + remove_emojis(video['title']))
                #schedule.new_video(get_id(video["href"]), remove_emojis(video['title']))

            print(f'DOWNLOADED {get_id(video["href"])}.mp4: {bytes}MB' if (bytes > 100000) else "FAILED TO DOWNLOAD: ")

    #return number of downloaded videos
    return len(videos)

def upload():
    tomorrow = datetime.today() + timedelta(days=1)
    for channel in get_channels():
        schedule = Schedule(channel)
        videos = schedule.get_videos_by_day(tomorrow)
        
        videos = [{"path": video["ID"], "description": video["TITLE"], "schedule": video["SCHEDULE"]} for video in videos]
        auth = AuthBackend(cookies= channel.cookies)
        print(videos)
        #upload_videos(videos, auth)

if __name__ == "__main__":
    get_data_channel("https://www.tiktok.com/@bobbyleeclips")