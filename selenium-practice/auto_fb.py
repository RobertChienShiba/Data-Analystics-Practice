# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 17:48:12 2021

@author: rober
"""

from selenium.webdriver.common.keys import Keys
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as Soup
from selenium.webdriver.common.action_chains import ActionChains
from pandas.core.frame import DataFrame

import time
import pandas as pd
import json


options = webdriver.ChromeOptions()
prefs = {
    'profile.default_content_setting_values':
        {
            'notifications': 2
        }
}
options.add_experimental_option('prefs', prefs)
options.add_argument("disable-infobars")
options.add_experimental_option('excludeSwitches', ['enable-automation'])

 



# ------ 設定要前往的網址 ------
url='https://www.facebook.com'    

# ------ 登入的帳號與密碼 ------
username = ''
password = ''


# ------ 透過Browser Driver 開啟 Chrome ------
driver = webdriver.Chrome('C:\\Users\\rober\\anaconda3\\Lib\\site-packages\\selenium\\webdriver\\chrome\\chromedriver.exe',options=options)        

# ------ 前往該網址 ------
driver.get(url)        

# # ------ 賬號密碼 ------


time.sleep(1)


# WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="email"]')))
# elem = driver.find_element_by_id("email")
# elem.send_keys(username)

## elem = driver.find_element_by_id("pass")
# elem.send_keys(password)        

# elem.send_keys(Keys.RETURN)
# time.sleep(5)

# cookies=driver.get_cookies()
# print(cookies)


##將帳密存成JSON檔作為Cookies 之後可自動登入
# with open ('facebook.json','w')as f:
#     f.write(json.dumps(cookies))
    
with open ('facebook.json','r')as f:
    data=json.loads(f.read())
    

for c in data:
    driver.add_cookie(c)
    
driver.refresh()



#檢查有沒有被擋下來
if len(driver.find_elements_by_xpath("//*[contains(text(), '你的帳號暫時被鎖住')]")) > 0:
    driver.find_elements_by_xpath("//*[contains(text(), '是')]")[1].click()

#切換頁面
spec_url = 'https://www.facebook.com/moea.gov.tw'
driver.get(spec_url)