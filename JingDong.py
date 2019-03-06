from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyquery import PyQuery as py
import re
import pymongo
from config import *
import time

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

browser = webdriver.Chrome()
wait =  WebDriverWait(browser,10)

def search():
    try:
        browser.get('https://www.jd.com/')
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"#key")))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#search > div > div.form > button')))
        input.send_keys('牛奶')
        submit.click()
        time.sleep(5)
        length = 1200
        for i in range(0,4):
            js="var q=document.documentElement.scrollTop="+str(length)
            browser.execute_script(js)
            length += length
        # browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            # i += 1
            time.sleep(3)
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"##J_bottomPage > span.p-skip > em:nth-child(1) > b")))
        get_goods()
        return total.text
    except TimeoutException:
        return search()

def get_next_page(page_number):
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"#J_bottomPage > span.p-skip > input"))
        )
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_bottomPage > span.p-skip > a')))
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(EC.text_to_be_present_in_elemen((By.CSS_SELECTOR,'#J_bottomPage > span.p-num > a:nth-child(3)'),str(page_number)))
        get_goods()
    except TimeoutException:
        next_page(page_number)

def get_goods():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#m-list .J_goodsList .gl-item')))
    html = browser.page_soure
    doc = py(html)
    item = doc('#m-list .J_goodsList .gl-item').items()
    for item in items:
        good = {
            'image':item.find('.p-img img').attr('src'),
            'price':item.find('.p-price ').text(),
            'title':item.find('.p-name p-name-type-2').text(),
            'shop':item.find('.p-shop').text()
        }
        print(good)
        save_to_mongo(good)

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到MONGODB成功', result)
    except Exception:
        print('存储到MONGODB失败', result)

def main(): 
    # search()
    try:
        total = search()
        total = int(re.compile('\d+').search(total).group(1))
        print(total)
        for i in range(2,total+1):
            next_page(i)
    except Exception:
        print('出错啦') 
    finally:
        browser.close()

if __name__ == '__main__':
    main()