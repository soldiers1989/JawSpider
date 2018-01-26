# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import re
from entity import *
from mysqlTemplate import *
import uuid
import sys
import copy
import os
import time

reload(sys)
sys.setdefaultencoding('utf-8')


class HeiBieSpider:
    def __init__(self):
        self.href = "http://hbgy.hbsfgk.org/ktggPage.jspx"
        self.detailHrefList = []
        self.titleList = []
        self.paras = {}
        self.data = ktgg()
        self.data.no = '7'
        self.data.sheng = '河北'
        self.sqltemp = mysqlTemplate()

    def getLinkList(self):
        href = self.href + "?channelId=" + self.paras["channelId"] + "&listsize=" + self.paras[
            "listsize"] + "&pagego=" + \
               self.paras["pagego"]
        print(href)
        while True:
            r = requests.get(href)
            soup = BeautifulSoup(r.content)
            ul = soup.find_all("ul", class_="sswy_news")
            if not len(ul) < 0:
                break
            else:
                print "休息10秒   "
                time.sleep(10)

        for u in ul:
            lista = u.find_all("a")
            self.detailHrefList = []
            self.titleList = []
            for a in lista:
                self.detailHrefList.append(a["href"])
                self.titleList.append(a["title"])
            self.getDetail()

    def getDetail(self):
        i = 0
        for href in self.detailHrefList:
            r = requests.get(href)
            soup = BeautifulSoup(r.content)
            div = soup.find('div', attrs={"class": "ywzw_con_inner"})
            source = soup.find("h3", attrs={"class": "h3_title"})
            fating_pattern = re.compile("在本院(.*?)依法")
            fating_result = re.findall(fating_pattern, str(div))
            data = copy.deepcopy(self.data)
            data.fating = str(fating_result[0])
            data.fayuan = str(source.string)
            data.kaitingriqi = str(self.titleList[i][0:16])
            data.gonggao = str(div)
            strs = data.kaitingriqi + "_" + data.fating + "_" + data.fayuan
            data.gonggao_id = str(uuid.uuid3(uuid.NAMESPACE_OID, strs))
            data.created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.sqltemp.insertKtgg(data)
            i += 1

    def start(self):
        document = open("HeiBeiPage.txt", "r")
        page=document.readline()
        page=int(page)

        document.close()
        for i in range(page, 85077 + 1):
            obj.paras = {"channelId": "431", "listsize": "85077", "pagego": str(i)}
            document = open("HeiBeiPage.txt", "w+")
            print "文件名: ", document.name
            document.write(str(i))
            document.close()
            obj.getLinkList()
            time.sleep(2)


obj = HeiBieSpider()
obj.start()
obj.sqltemp.release()
