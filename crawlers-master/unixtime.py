import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
# prefs = {
#     'profile.default_content_setting_values' :
#         {
#         'notifications' : 2
#           }
# }
# options.add_experimental_option('prefs',prefs)
#options.add_argument("headless") 

# declare prefs
# prefs = {"media.autoplay.enabled" : False, "dom.webnotifications.serviceworker.enabled": False,
#           "dom.webnotifications.enabled":False}

# add prefs 
# options.add_experimental_option("prefs", prefs)


# 不加載圖片，加快速度
# prefs = {"profile.managed_default_content_settings.images": 2}
# options.add_experimental_option("prefs", prefs)
# 此步骤很重要，設置為開發者模式，防止被各大網站識别出来使用了Selenium
options.add_experimental_option('excludeSwitches', ['enable-automation'])
# 添加本地代理


## 設置代理IP
import re
import random
res = requests.get('https://free-proxy-list.net/')
m = re.findall('\d+\.\d+\.\d+\.\d+:\d+', res.text)
validips = []
for ip in m[:30]:
    try:
        res = requests.get('https://api.ipify.org?format=json',proxies = {'http':ip, 'https':ip}, timeout = 5)
        validips.append({'ip':ip})
        print(res.json())
        break
    except:
        print('FAIL', ip )
proxy=random.choice(validips).get('ip')
options.add_argument('proxy-server=' + proxy)

# 設置中文
options.add_argument('lang=zh_CN.UTF-8')

# 添加UA
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
options.add_argument('user-agent=' + ua)

# 不使用自動化擴展
#options.add_experimental_option('useAutomationExtension', False)


input_=int(input('請輸入10位數秒數:'))
start=time.time()
driver=webdriver.Chrome(executable_path="C:\\Users\\rober\\anaconda3\\Lib\\site-packages\\selenium\\webdriver\\chrome\\chromedriver.exe",chrome_options=options)
url="https://www.unixtimestamp.com/"
driver.get(url)
elem=driver.find_element_by_xpath("//input[@id='timestamp']")
elem.send_keys(input_)
elem=driver.find_element_by_xpath("//div[@class='ui form']/button[@class='ui primary button']")
elem.click()
page=driver.page_source
#print(page)
soup = BeautifulSoup(page, 'lxml')
table=soup.find('table',class_="ui celled definition table timestamp-results")
UTC_time=soup.find('td',class_='gmt').text
local_time=soup.find('td',class_='local').text
end=time.time()
print('UTC時間:{},台灣時間:{}'.format(UTC_time,local_time))
print(f'總共花費{end-start}秒數:')



