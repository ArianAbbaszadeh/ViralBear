import time
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

def upload_videos(cookies_path = "cookies_youtube/cookies1.json"):
    # Set up your paths
    USER_DATA_DIR = "/Users/abbaszadeh/Library/Application Support/Google/Chrome/Ablour"
    VIDEOS_DIRECTORY = './ready'

    #set up driver service 
    service = ChromeService()
    driver = None
    try:
        # Set up Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        #options.add_argument(f"user-data-dir={USER_DATA_DIR}")

        # Initialize the Chrome driver
        driver = webdriver.Chrome(service=service, options=options)

        # Load cookies from the cookies file and add them to the browser
        with open(cookies_path, 'r', encoding='utf-8') as cookies_file:
            cookies_content = cookies_file.read()
            cookies = json.loads(cookies_content)
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    print(f"{cookie}: is there a sign that says dead nigger storage on my garage?")
       
        driver.get('https://www.youtube.com')
        print("\033[1;31;40m IMPORTANT: Ensure the video names are in the right format.")

        video_files = [f for f in os.listdir(VIDEOS_DIRECTORY) if f.endswith('.mp4')]
        print("   ", len(video_files), " Videos found in the videos folder, ready to upload...")

        for video in video_files:
            # Go to the YouTube Studio website
            driver.get("https://studio.youtube.com")
            wait = WebDriverWait(driver, 10)

            # Wait until the upload button is clickable and click it
            upload_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="upload-icon"]')))
            upload_button.click()
            time.sleep(1)

            # Select the file input element
            file_input = driver.find_element(By.XPATH, '//*[@id="content"]/input')

            simp_path = os.path.join(VIDEOS_DIRECTORY, video)
            abs_path = os.path.abspath(simp_path)

            # Upload the video file
            file_input.send_keys(abs_path)
            time.sleep(7)

            # Click the next button
            next_button = driver.find_element(By.XPATH, '//*[@id="next-button"]')
            for _ in range(3):
                next_button.click()
                time.sleep(1)

            # Click the done button
            done_button = driver.find_element(By.XPATH, '//*[@id="done-button"]')
            done_button.click()
            time.sleep(5)
    except Exception as e:
        # Print an error message if something goes wrong
        traceback.print_exc()
    finally:
        if driver is not None:
            driver.quit()

upload_videos()









