# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import re
from entity import *
from mysqlTemplate import *
import uuid
import utils
import sys
import copy
import chardet
import time

reload(sys)
sys.setdefaultencoding('utf-8')


class HuNanSpider:
    def __init__(self):
        self.data = ktgg()
        self.href = 'http://hunanfy.chinacourt.org/article/detail/'
        self.data.no = '199'
        self.data.sheng = '湖南省'
        self.page = 1
        self.sqltemp = mysqlTemplate()
        self.proxies = {}

    def getHerf(self):
        href = "http://hunanfy.chinacourt.org/article/index/id/M0jONTAwNzAwNCACAAA%3D/page/" + str(self.page) + ".shtml"
        print(href)
        time.sleep(1)
        r = requests.get(href, proxies=self.proxies)
        soup = BeautifulSoup(r.content)
        div = soup.find("div", attrs={"id": "list", "class": "font14"})
        detail_pattern = re.compile('<a href="/article/detail/(.*?)".*?>', re.S)
        detail_result = re.findall(detail_pattern, str(div))
        for result in detail_result:
            self.getDetailInfo(self.href + result)

    def getDetailInfo(self, href):
        while True:
            try:
                r = requests.get(href, proxies=self.proxies)
            except:
                ips = utils.getProxy()
                print("换代理")
                print(self.proxies)
                self.proxies["http"] = ips[0]
                self.proxies["https"] = ips[1]
            else:
                break
        soup = BeautifulSoup(r.content)
        yuanwen = soup.find("div", attrs={"class": "detail"})
        data = copy.deepcopy(self.data)
        data.gonggao = str(yuanwen).replace("'", "\"")
        data.created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.sqltemp.insertKtgg(data)


obj = HuNanSpider()
for i in range(1, 32):
    obj.page = i
    obj.getHerf()
