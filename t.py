from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import discord
import time
import json
import pyautogui
import os
from tinytag import TinyTag
from io import BytesIO
from PIL import Image
import subprocess
from yt_dlp import YoutubeDL
import vt


client = vt.Client("24df8950f1703806d2fcee9b69bc869578c42eccba1c9ece21fb7c84ebf275e4")
#with open(r"C:\Users\USER\Downloads\trash_thumbnail_600px.jpg", "rb") as file:
    #analysis = client.scan_file(file, wait_for_completion=True)
analysis = client.scan_url('https://google.com',wait_for_completion=True)
print(analysis.get("stats"))
client.close()

"""
link = "I suggest you search it on https://www.google.com, there is a lot of stuff on it"
test_list = ['.com', '.ru', '.net', '.org', '.info', '.biz', '.io', '.co', "https://", "http://"]
link_matches = [ele for ele in test_list if(ele in link)]

if "https://" in link_matches or "http://" in link_matches and len(link_matches) > 1:
    link = link.split(link_matches[len(link_matches)-1])[1].split(link_matches[0])[0]
    link = f"{link_matches[len(link_matches)-1]}{link}{link_matches[0]}"
    print(link)
"""

"""
service = Service()
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option("detach", True)
#options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
driver.get(f"https://www.google.com")
box = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/textarea')
box.send_keys("test")
box.send_keys(Keys.ENTER)
#website = driver.find_elements(By.ID,'UWckNb')
website = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
for w in website:
    url = w.get_attribute("href")
    if url and "google" not in url:
        print(url)
"""

"""
service = Service()
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option("detach", True)
#options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
driver.get(f"https://www.youtube.com")
box = driver.find_element(By.XPATH,'/html/body/ytd-app/div[1]/div/ytd-masthead/div[4]/div[2]/ytd-searchbox/form/div[1]/div[1]/input')
box.send_keys("migraine")
box.send_keys(" "+Keys.BACKSPACE)
time.sleep(0.5)
option = driver.find_elements(By.CLASS_NAME,'sbqs_c')
print(option[0].text)

driver.get(f"https://www.youtube.com/results?search_query=the only thing i know for real")
time.sleep(2)
title = driver.find_elements(By.ID,'video-title')
for i in range(0,len(title)):
    if title[i].get_attribute("class") != "style-scope ytd-promoted-video-renderer":
        result = title[i].get_attribute("href")
        break
driver.get(result)
"""