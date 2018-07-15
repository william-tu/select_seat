# coding:utf-8
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from config import config
import datetime
import os
import json
import ConfigParser

basedir = os.path.abspath(os.path.dirname(__file__))

# 今天日期
today = datetime.date.today()
# 明天时间
tomorrow = today + datetime.timedelta(days=1)

user_agent = "Mozilla/5.0 (Linux; Android 7.0; STF-AL10 Build/HUAWEISTF-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043508 Safari/537.36 V1_AND_SQ_7.2.0_730_YYB_D QQ/7.2.0.3270 NetType/4G WebP/0.3.0 Pixel/1080"

start_time = str(config.get('start_time'))  # 输入座位预约的开始时间 注意格式(eg:18:00)
duration = int(config.get('duration')) * 3600
person_count = int(config.get("person_count"))

start_time = int(time.mktime(time.strptime(str(tomorrow) + " " + start_time, "%Y-%m-%d %H:%M")))
print start_time
print duration
print person_count
data_path = os.path.join(basedir + "/data.ini")
if not os.path.exists(data_path):
    os.system("touch " + data_path)

browser = webdriver.Chrome(config.get("chromedriver_path"))

cookies = {'api_access_token': None, 'auth': None, 'is_remember': None, 'org_id': None, 'uid': None,
           'web_language': None}
while not browser.get_cookie('api_access_token'):
    try:
        browser.get("https://jxnu.huitu.zhishulib.com/#!/User/Index/login?forward=/Space/Category/list?category_id=591")
        element = WebDriverWait(browser, 100).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='login_name']")))

        browser.find_element_by_xpath("//input[@name='login_name']").send_keys(config.get("stu_id"))
        browser.find_element_by_xpath("//input[@type='password']").send_keys(config.get("password"))
        browser.find_element_by_xpath(
            "//*[@id='react-root']/div/div/div[1]/div/div/div[1]/div[2]/div/div/div/div/div[1]/div[3]").click()
    except:
        print "retry..."

for name in cookies:
    cookies[name] = browser.get_cookie(name)['value']
# browser.get("https://jxnu.huitu.zhishulib.com/#!/Space/Category/list?category_id=591")

# browser.close()
# c = ConfigParser.ConfigParser()
# c.add_section('')
# c.write(open(data_path, 'w'))
# print c.sections()

exit(1)


def select_seat():
    res_list = []
    with requests.Session() as s:
        try:

            s.headers.update({"User-Agent": user_agent})
            uid = s.get('https://jxnu.huitu.zhishulib.com/Seat/Index/searchSeats',
                        params={'space_category[category_id]': 591,
                                'space_category[content_id]': 31,
                                'LAB_JSON': 1},
                        cookies=cookies).json().get("data").get("uid")
            print "uid:" + str(uid)
            res1 = s.post("https://jxnu.huitu.zhishulib.com/Seat/Index/searchSeats?LAB_JSON=1",
                          data={'beginTime': start_time, 'duration': duration, 'num': person_count,
                                'space_category[category_id]': 591,
                                'space_category[content_id]': 31})
            res_list.append(res1)
            if not res1.json().get("data"):
                return 2
            seat_id = res1.json().get("data").get("bestPairSeats").get("seats")[
                0].get("id")

            print 'seat_id:' + str(seat_id)
            res2 = s.post("https://jxnu.huitu.zhishulib.com/Seat/Index/bookSeats?LAB_JSON=1",
                          data={"beginTime": start_time, "duration": duration, "seats[0]": seat_id,
                                "seatBookers[0]": uid})
            res_list.append(res2)
            if res2.json().get("CODE") == "ok":
                print 'success'
                print res2.json().get("CODE")
                return 1
            else:
                print "select seat happened an error"
                print res2.json()
            print res2.status_code
        except Exception as e:
            print e.message
            for res in res_list:
                print res.request.method + ' ' + res.url
                if res.request.method == 'POST':
                    print res.request.body
                print res.content


su = False
while not su:
    now = datetime.datetime.now()
    print now.hour, '-', now.minute, '-', now.second

    if now.hour >= 22 and now.minute >= 0:
        su = select_seat()
        time.sleep(1)
    time.sleep(1)
    if su == 1:
        su = int(raw_input("抢座位成功，请检查预约的座位，核对后请选择是否结束本脚本？（1/0）1表示结束 0表示重启"))
        if not su:
            print type(duration)
            duration = int(
                raw_input(
                    "当前预约时间可能过于长（" + str(duration / 3600) + ") 是否设置新的预约时间？（0表示不设置,其他数表示修改后的预约时间）: ")) * 3600 or duration
    elif su == 2:
        duration = int(
            raw_input("当前预约时间可能过于长（" + str(duration) + ") 是否设置新的预约时间？（0表示不设置,其他数表示修改后的预约时间）: ")) or duration
        su = 0
