from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager



driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://www.google.com')

search = driver.find_element_by_xpath("//input[@class='gLFyf gsfi']")

search.send_keys('曲面螢幕')
search.send_keys(Keys.RETURN)