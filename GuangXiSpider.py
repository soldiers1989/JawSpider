# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import re
from entity import *
from mysqlTemplate import *
import uuid
import sys
import copy
import chardet
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
        self.sqltemp = mysqlTemplate()

    def getTable(self):
        href = self.href + str(self.page)
        print(href)
        r = requests.get(href)
        time.sleep(1)
        soup = BeautifulSoup(r.content.decode(encoding="gbk", errors="ignore"))
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
                        data.gonggao_id = str(uuid.uuid3(uuid.NAMESPACE_OID, strs.encode("utf-8")))
                        data.dangshiren = "原告/上诉人：" + data.yuangao + ";被告/被上诉人：" + data.beigao + ";"
                        self.sqltemp.insertKtgg(data)
                        data = copy.deepcopy(self.data)
                i += 1


    def start(self):
        for i in range(1, 404):
            self.page = i
            self.getTable()


obj = GuangXiSpider()
obj.start()
