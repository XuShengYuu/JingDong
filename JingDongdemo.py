import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from lxml import etree
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

browser = webdriver.Chrome()
wait = WebDriverWait(browser,50)

def search():
    browser.get('https://www.jd.com/')
    try:
        input = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"#key")))
        # 搜索框
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#search > div > div.form > button")))
        # 搜索确定按钮
        input[0].send_keys('牛奶')
        # 输入关键词
        submit.click()
        # 点击确定搜索关键词
        time.sleep(10)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        total = wait.until(EC.presence_of_all_elements_located
            ((By.CSS_SELECTOR,'#J_bottomPage > span.p-skip > em:nth-child(1) > b')))
        # 总页码数
        html = browser.page_source
        get_goods(html)
        # 执行get_goods函数，获取第一页商品信息
        return total[0].text
        # 返回总页面数
    except TimeoutException:
        search()

def next_page(page_number):
    try:
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_bottomPage > span.p-num > a.pn-next > em')))
        # 翻页按钮
        button.click()
        # 点击翻页按钮
        time.sleep(10)
        # 暂停5秒，等待网页内容加载完毕
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # 下拉浏览器，加载后30个商品内容
        time.sleep(3)
        # 暂停3秒，等待网页加载完毕
        wait.until(EC.text_to_be_present_in_element
            ((By.CSS_SELECTOR,"#J_bottomPage > span.p-num > a.curr"),str(page_number)))
        # 判断是否翻页成功
        html = browser.page_source
        get_goods(html)
        # 执行get_goods函数，获取商品信息
    except TimeoutException:
        return next_page(page_number)

def get_goods(html):
    
    # 取得网页源码
    html = etree.HTML(html)
    # 解析网页
    # items = html.xpath('//*[@id="J_goodsList"]/ul/li')
    # # 获取所有商品列表
    # for i in range(len(items)):
    #     # 获取单个商品
    #     good = {
    #     # 商品信息
    #         'href':html.xpath('//*[@id="J_goodsList"]/ul/li/div/div[1]/a/@href'),
    #         # 商品链接
    #         'image':html.xpath('//*[@id="J_goodsList"]/ul/li/div/div[1]/a/img/@src'),
    #         # 商品图片
    #         'price':html.xpath('//*[@id="J_goodsList"]/ul/li/div/div[3]/strong/i/text()'),
    #         # 商品价格
    #         'title':html.xpath('//*[@id="J_goodsList"]/ul/li/div/div[4]/a/@title'),
    #         # 商品名称
    #         'shop':html.xpath('//*[@id="J_goodsList"]/ul/li/div/div[7]/span/a/text()')
    #     # 店铺名称
    #     }
    #     print(good)
    #     save_to_mongo(good)
    # 储存到MongoDB中
    items = ('//*[@id="J_goodsList"]/ul/li')
    
    i = 0
    for item in items:
        print("第",i,"个商品")
        href= item.xpath('./div/div[1]/a/@href')
        # print(href)
        image= item.xpath("./div/div[1]/a/img/@src")
        price= item.xpath("./div/div[3]/strong/i/text()")
        title= item.xpath("./div/div[4]/a/em/text()")
        # print(titles)
        shop= item.xpath("./div/div[7]/span/a/text()")
        i +=i
        print(item)
        # save_to_mongo(item)

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到MONGODB成功')
    except Exception:
        print('存储到MONGODB失败')

def main():
    print("第",1,"页")
    total = int(search())
    for i in range(2, total+1):
        time.sleep(3)
        print("第",i,"页")
        next_page(i)

if __name__ == '__main__':
    main()