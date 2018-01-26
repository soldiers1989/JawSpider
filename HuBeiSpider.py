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

requests.adapters.DEFAULT_RETRIES = 5
reload(sys)
sys.setdefaultencoding('utf-8')


class HuBeiSpider:
    def __init__(self):
        self.href = "http://www.hbfy.org"
        self.data = ktgg()
        self.data.no = '185'
        self.data.sheng = '湖北省'
        self.sqltemp = mysqlTemplate()
        self.codeName = {}
        self.proxies = {}
        self.return_time = 5
        self.page = 1
        self.isNextFayuan = False

    # 各地区法院的链接
    def getUnitHerf(self):
        href = self.href + "/gfcms/web/unit/allUnit.do"
        r = requests.get(href, proxies=self.proxies)
        time.sleep(1)
        while "您的请求过于频繁" in r.content:
            ips = utils.getProxy()
            print("换代理")
            print(self.proxies)
            self.proxies["http"] = ips[0]
            self.proxies["https"] = ips[1]
            time.sleep(1)
            r = requests.get(href, proxies=self.proxies)
        soup = BeautifulSoup(r.content)
        areas = soup.find_all('area', attrs={"shape": "circle"})
        codeName_pattern = re.compile("""<a href="javascript:closeME\('(.*?)','(.*?)'\)\"""", re.S)
        codeName_result = re.findall(codeName_pattern, r.content)
        for reslut in codeName_result:
            self.codeName[reslut[0]] = reslut[1]
        for area in areas:
            r = requests.get(self.href + area["href"], proxies=self.proxies)
            while "您的请求过于频繁" in r.content:
                ips = utils.getProxy()
                print("换代理")
                print(self.proxies)
                self.proxies["http"] = ips[0]
                self.proxies["https"] = ips[1]
                time.sleep(3)
                r = requests.get(self.href + area["href"], proxies=self.proxies)
            codeName_result = re.findall(codeName_pattern, r.content)
            for reslut in codeName_result:
                self.codeName[reslut[0]] = reslut[1]
        j = 0
        for k in self.codeName.keys():
            self.isNextFayuan = False
            self.page = 1
            self.return_time = 5
            print("法院个数：" + str(j) + "/" + str(len(self.codeName)))
            # print(self.codeName[k])
            j += 1
            while not self.isNextFayuan:
                self.getInfo(k, self.page)
                self.page += 1

    def getInfo(self, code, page):
        href = 'http://www.hbfy.org/gfcms/templetPro.do?templetPath=overtbegin/overtbeginPage.html'
        para = {"page": page, "currChannelid": "5913d1c6-a73b-4cec-923c-c63376a05752", "currUnitId": code,
                "siteid": "ce0b9496-6b88-4f66-8da7-ede1a989fd6e", "pageNum": page}
        s = requests.session()
        s.keep_alive = False
        print("请求：　　" + self.codeName[code] + "   page" + str(page))
        while True:
            try:
                r = requests.post(href, data=para, proxies=self.proxies)
            except:
                s = requests.session()
                s.keep_alive = False
                ips = utils.getProxy()
                print("请求错误1：" + "换代理")
                print(self.proxies)
                time.sleep(2)
                self.proxies["http"] = ips[0]
                self.proxies["https"] = ips[1]
            else:
                break

        while "您的请求过于频繁" in r.content:
            ips = utils.getProxy()
            print("换代理")
            print(self.proxies)
            self.proxies["http"] = ips[0]
            self.proxies["https"] = ips[1]
            time.sleep(3)
            r = requests.post(href, data=para, proxies=self.proxies)

        soup = BeautifulSoup(r.content)
        table = soup.find("table", attrs={"class": "zebra"})
        if table:
            trs = table.find_all("tr")
        else:
            trs = []

        beigao_pattern = re.compile('((被告)|(被申请(执行)?(再审)?)|(被上诉))(人)?:(.*?)(;|$)', re.S)
        yuangao_patten = re.compile('((原告)|(申请(执行)?(再审)?)|(上诉))(人)?:(.*?)(;|$)', re.S)
        qita_patten = re.compile('(第三)(人|方):(.*?)(;|$)', re.S)
        if len(trs) > 1:
            for i in range(1, len(trs)):
                data = copy.deepcopy(self.data)
                data.created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                tds = trs[i].find_all("td")
                a_pattern = re.compile('<a href="(.*?)".*?>.*?</a>', re.S)
                a_reslut = re.search(a_pattern, str(tds[0]))
                yuanwen_result = self.getYuanwen(a_reslut.group(1))

                data.gonggao = str(yuanwen_result[0])
                data.chengban = str(yuanwen_result[1])
                data.kaitingriqi = tds[1].string.replace('年', '-').replace('月', '-').replace("日", "")
                data.dangshiren = str(tds[2].string.strip())
                data.anyou = str(tds[3].string)
                data.fayuan = self.codeName[code]
                yuangao_reslut = re.findall(yuangao_patten, str(data.dangshiren))
                beigao_reslut = re.findall(beigao_pattern, str(data.dangshiren))
                qita_result = re.findall(qita_patten, str(data.dangshiren))
                try:
                    data.yuangao = str(yuangao_reslut[0][7])
                except IndexError:
                    print "没有原告"
                try:
                    data.qita = str(qita_result[0][2])
                except IndexError:
                    print "没有第三方"
                try:
                    data.beigao = str(beigao_reslut[0][7])
                except IndexError:
                    print("没有被告")
                data.gonggao_id = str(uuid.uuid3(uuid.NAMESPACE_OID, str(data.dangshiren + "_" + data.kaitingriqi)))
                self.sqltemp.insertKtgg(data)
        else:
            self.return_time -= 1
            if self.return_time >= 0:
                print "10秒后再请求一次"
                time.sleep(10)
                self.getInfo(code, page)
            else:
                self.isNextFayuan = True
                self.page = 1

    def getYuanwen(self, href):
        s = requests.session()
        s.keep_alive = False
        while True:
            try:
                r = requests.get(self.href + href, proxies=self.proxies)
            except:
                s = requests.session()
                s.keep_alive = False
                ips = utils.getProxy()
                print("请求错误2:换代理")
                print(self.proxies)
                self.proxies["http"] = ips[0]
                self.proxies["https"] = ips[1]
                time.sleep(2)
            else:
                break
        time.sleep(2)
        while "您的请求过于频繁" in r.content:
            ips = utils.getProxy()
            print("换代理")
            print(self.proxies)
            self.proxies["http"] = ips[0]
            self.proxies["https"] = ips[1]
            r = requests.get(self.href + href, proxies=self.proxies)
        soup = BeautifulSoup(r.content)
        div = soup.find("div", attrs={"class": "fy_bm_rga"})
        chengban_pattern = re.compile("<p>.*?承办人：(　)?( )?(.*?)</p>")

        chengban_reslut = re.findall(chengban_pattern, str(div))
        chengban = ""
        try:
            chengban = chengban_reslut[0][2].replace(' ', '')
        except:
            pass
        return (str(div), str(chengban).strip())


obj = HuBeiSpider()
obj.getUnitHerf()
obj.sqltemp.release()
# str = '何波 '
# print str.replace(' ', '')
