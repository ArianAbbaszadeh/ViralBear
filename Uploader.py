from tiktok_uploader.auth import AuthBackend
from tiktok_uploader.upload import upload_video, upload_videos
from selenium import webdriver
from selenium.webdriver import *
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os.path import abspath

def upload_video_youtube(filepath, description, cookies_path):

    auth = AuthBackend(cookies = cookies_path)
    
    print('Create a chrome browser instance')
    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options) 

    driver = auth.authenticate_agent(driver=driver, is_tiktok = False)

    try:
        path = abspath(filepath)

        print(f'Posting {filepath}\n with description: {description}')
        complete_upload_form(driver, path, description)

    except Exception as e:
        return False
    finally:
        driver.quit()

    #return upload_video(f"ViralBear/ready/{filepath}", description= description, cookies = cookies_path)

def complete_upload_form(driver, path: str, description: str) -> None:
    """
    Actually uploades each video

    Parameters
    ----------
    driver : selenium.webdriver
        The selenium webdriver to use for uploading
    path : str
        The path to the video to upload
    """
    go_to_upload(driver)
   # set_video(driver, path=path, **kwargs)
   # set_interactivity(driver, **kwargs)
   # set_description(driver, description)
    #post_video(driver)

def go_to_upload(driver):
    #youtube studio: https://studio.youtube.com/
    print("Navigating to upload page")

    driver.get("https://studio.youtube.com")
    
    wait = WebDriverWait(driver, 10)

    # Wait until the upload button is clickable and click it
    upload_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="upload-icon"]')))
    upload_button.click()
    #time.sleep(1)

if __name__ == '__main__':
    auth = AuthBackend(cookies="cookies/cookies1.txt")

    videos = [{"path": "downloaded/7260232408643964203.mp4", "description": "Test1", "schedule": "2024-04-01 07:30"},
              {"path": "downloaded/7259474993799646507.mp4", "description": "Test2", "schedule": "2024-04-01 16:20"}]
    upload_videos(videos, auth)
    #upload_video("ready/testoutput.mp4", description="Test", cookies="cookies/cookies2.txt", schedule = "2024-03-31 15:30")