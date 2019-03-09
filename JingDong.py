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
'''
PhantomJS浏览器配置，采集速度更快
# browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)
# browser.set_window_size(1400, 900)
'''

def search():
    browser.get('https://www.jd.com/')
    try:
        input = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"#key")))
        # 搜索框
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#search > div > div.form > button")))
        # 搜索确定按钮
        input[0].send_keys('KETWORD')
        # 输入关键词
        submit.click()
        # 点击确定搜索关键词
        time.sleep(10)
        # 暂停10s，等待信息加载完毕
        '''
        将浏览器逐渐下拉，加载出图片信息
        如果直接下拉到底，部分图片链接会加载不出
        如果不需要图片信息，可用下面另一种方法
        '''
        length = 1000
        for i in range(0,10):
            js="var q=document.documentElement.scrollTop="+str(length)
            length =length+1000
            browser.execute_script(js)
            i += 1
            time.sleep(1)
        '''
        此方法适用不需要加载图片信息
        time.sleep(3)
        # 暂停3秒，等待网页内容加载完毕
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # 下拉浏览器，加载后30个商品内容
        time.sleep(5)
        # 暂停3秒，等待网页加载完毕
        '''
        total = wait.until(EC.presence_of_all_elements_located
            ((By.CSS_SELECTOR,'#J_bottomPage > span.p-skip > em:nth-child(1) > b')))
        # 定位总页码数元素
        html = browser.page_source
        # 取得网页源码
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
        '''
        将浏览器逐渐下拉，加载出图片信息
        如果直接下拉到底，部分图片链接会加载不出
        如果不需要图片信息，可用下面另一种方法
        '''
        length = 1000
        for i in range(0,10):
            js="var q=document.documentElement.scrollTop="+str(length)
            length =length+1000
            browser.execute_script(js)
            i += 1
            time.sleep(1)
        '''
        此方法适用不需要加载图片信息
        time.sleep(3)
        # 暂停3秒，等待网页内容加载完毕
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # 下拉浏览器，加载后30个商品内容
        time.sleep(5)
        # 暂停3秒，等待网页加载完毕
        '''
        wait.until(EC.text_to_be_present_in_element
            ((By.CSS_SELECTOR,"#J_bottomPage > span.p-num > a.curr"),str(page_number)))
        # 判断是否翻页成功
        html = browser.page_source
        get_goods(html)
        # 执行get_goods函数，获取商品信息
    except TimeoutException:
        return next_page(page_number)

def get_goods(html):
    html = etree.HTML(html)
    # 解析网页
    items = html.xpath('//*[@id="J_goodsList"]/ul/li')
    # print(items)    
    i = 0
    # 初始化计数
    for item in items:
        # 取出单个商品信息
        print("第",i+1,"个商品")
        # 统计商品次序
        good = {
        # 单个商品信息
            'href': item.xpath("./div/div[1]/a/@href"),
            # 商品链接
            'image': item.xpath("./div/div[1]/a/img/@src"),
            # 商品图片
            'price': item.xpath("./div/div[3]/strong/i/text()"),
            # 商品价格
            'title': item.xpath("./div/div[4]/a/em/text()"),
            # 商品名称
            'shop': item.xpath("./div/div[7]/span/a/text()")
            # 商店名称
        }       
        i=i+1
        # 计数+1
        print(good)
        # 打印商品信息
        save_to_mongo(good)
        # 储存商品信息到MongoDB

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            #将商品信息储存到MongoDB表中
            print('存储到MONGODB成功')
    except Exception:
        print('存储到MONGODB失败')

def main():
    print("第",1,"页")
    # 打印页码
    total = int(search())
    # 总页码数
    for i in range(2, total+1):
        # 循环页码数
        time.sleep(3)
        print("第",i,"页")
        next_page(i)

if __name__ == '__main__':
    main()