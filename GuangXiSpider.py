# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
from entity import *
from mysqlTemplate import *
import sys
import copy
import utils
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType

import time

reload(sys)
sys.setdefaultencoding('utf-8')


class GuangXiSpider:
    def __init__(self):
        self.href = "http://171.106.48.55:8899/legalsystem/ReportServer?_=1516007627616&__boxModel__=true&op=page_content&sessionID=2170&pn="
        self.page = 1
        self.data = ktgg()
        self.data.no = '236'
        self.data.sheng = '广西省'
        self.data.dangshirenjx_flag = '1'
        self.sqltemp = mysqlTemplate()

    def getTable(self):
        i = 3
        ips = []
        while True:
            try:
                i += 1
                if i > 3:
                    ips = utils.getProxy()
                    print "换代理"
                    i = 0
                proxy = Proxy(
                    {
                        'proxyType': ProxyType.MANUAL,
                        'httpProxy': ips[i]  # 代理ip和端口
                    }
                )

                desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
                # 把代理ip加入到技能中
                proxy.add_to_capabilities(desired_capabilities)
                driver = webdriver.PhantomJS(
                    desired_capabilities=desired_capabilities
                )
                driver.set_page_load_timeout(5)
                driver.set_script_timeout(5)
                driver.get("http://171.106.48.55:8899/legalsystem/ReportServer?reportlet=ktgg/ktgglist.cpt&fbdm=450000")
                time.sleep(20)
            except Exception as e:

                print e
            else:
                break
        self.getDetail(BeautifulSoup(driver.page_source))
        for i in range(0, 400):
            try:
                elem = driver.find_elements_by_xpath('//*[@id="fr-btn-"]/tbody/tr[2]/td[2]/em/button')
                time.sleep(10)
                elem[2].click()
                time.sleep(20)
                self.getDetail(BeautifulSoup(driver.page_source))
            except:
                time.sleep(10)

        driver.quit()

    def getDetail(self, soup):
        tds = soup.find_all("td", attrs={"class": "fh tac bw pl2 brw1 brss bbw1 bbss blw1 blss btw1 btss"})
        i = 1
        data = copy.deepcopy(self.data)
        span_num = 0
        rowspan = 0
        isCos = False

        for td in tds:
            try:
                rowspan = int(td["rowspan"])
                isCos = True
                if i % 7 == 1:
                    if td.string and data.kaitingriqi != td.string:
                        data.kaitingriqi = td.string
                if i % 7 == 2:
                    if td.string and td.string != data.fayuan:
                        data.fayuan = td.string
                if i % 7 == 3:
                    if td.string and td.string != data.fating:
                        data.fating = td.string
                if i % 7 == 4:
                    if td.string and td.string != data.anhao:
                        data.anhao = td.string
                if i % 7 == 5:
                    if td.string and td.string != data.anyou:
                        data.anyou = td.string
                if i % 7 == 6:
                    if td.string and td.string != data.yuangao:
                        data.yuangao = td.string
                if i % 7 == 0:
                    if td.string and td.string != data.beigao:
                        data.beigao = td.string
                i += 1
                span_num += 1

            except KeyError:

                while isCos and i % 7 <= span_num and i % 7 != 0:
                    i += 1
                if i % 7 == 1:
                    if td.string and data.kaitingriqi != td.string:
                        data.kaitingriqi += td.string
                if i % 7 == 2:
                    if td.string and td.string != data.fayuan:
                        data.fayuan += td.string
                if i % 7 == 3:
                    if td.string and td.string != data.fating:
                        data.fating += td.string
                if i % 7 == 4:
                    if td.string and td.string != data.anhao:
                        data.anhao += td.string
                if i % 7 == 5:
                    if td.string and td.string != data.anyou:
                        data.anyou += td.string
                if i % 7 == 6:
                    if td.string and td.string != data.yuangao:
                        data.yuangao += td.string
                if i % 7 == 0:
                    if td.string and td.string != data.beigao:
                        data.beigao += td.string
                    rowspan -= 1
                    if rowspan == 0:
                        isCos = False

                    if isCos == False:
                        data.created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        strs = data.kaitingriqi + "_" + data.anhao
                        data.gonggao_id = strs
                        data.dangshiren = "原告/上诉人：" + data.yuangao + ";被告/被上诉人：" + data.beigao + ";"
                        if len(data.yuangao) > 0:
                            data.dangshirenjx = data.yuangao + "," + data.beigao
                        else:
                            data.dangshirenjx = data.beigao
                        if len(data.qita) > 0:
                            data.dangshirenjx = data.dangshirenjx + "," + data.qita
                        if self.sqltemp.queryCountBy_gonggaoid_and_no(data.gonggao_id, 236) > 0:
                            print "重复数据:" + data.gonggao_id
                            continue
                        self.sqltemp.insertKtgg(data)
                        data = copy.deepcopy(self.data)
                i += 1

    def start(self):
        self.getTable()

if __name__ == "__main__":
    obj = GuangXiSpider()
    obj.start()
