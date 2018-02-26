# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import copy
import time
from mysqlTemplate import mysqlTemplate
from entity import *
import uuid


class ShenzhengSpider:
    def __init__(self):
        self.href = "http://ssfw.szcourt.gov.cn/frontend/anjiangongkai/session"
        self.paras = {}
        self.data = ktgg()
        self.data.no = '216'
        self.data.sheng=''
        self.sqltempe = mysqlTemplate()
        self.page = 1
        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Referer': 'http://ssfw.szcourt.gov.cn/frontend/anjiangongkai/session?cc=1&page=0&pageLimit=10&caseNo=&appliers=&sessionDateBegin=&sessionDateEnd=',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'JSESSIONID=78D65A52AD0FE4FC5A8C6689FE053417',
            'Host': 'ssfw.szcourt.gov.cn',
            'Upgrade-Insecure-Requests': '1'}
        self.ccs = [0, 1, 2, 3, 4, 5, 6, 7]
        self.ccs_pages = {"0": 105, "1": 1, "2": 140, "3": 117, "4": 94, '5': 76, '6': 34, '7': 113}

        self.fatings = {"0": "中院", "1": "罗湖", "2": "福田", "3": "南山", "4": "宝安", "5": "宝安", "6": "盐田", "7": "前海"}

    def getInfo(self):
        href = self.href + "?cc=" + str(self.paras["cc"]) + "&page=" + str(
            self.page) + "&pageLimit=10&sessionDateBegin=2018-01-01&sessionDateEnd=2019-01-18"
        print(href)
        r = requests.get(href, headers=self.headers)
        soup = BeautifulSoup(r.content)
        jitr = soup.find_all("tr", attrs={"class": "ji"})
        eventr = soup.find_all("tr", attrs={"class": "even"})
        self.zuzhuangshuju(jitr)
        self.zuzhuangshuju(eventr)

    def zuzhuangshuju(self, datas):
        for ji in datas:
            data = copy.deepcopy(self.data)
            data.fayuan = self.fatings[str(self.paras["cc"])]
            data.created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            date_pattern = re.compile('<td .*?width="90">(.*?)</td>', re.S)
            time_pattern = re.compile('<td .*?width="50">(.*?)</td>', re.S)
            faguan_pattern = re.compile('<td .*?width="55">(.*?)</td>', re.S)
            anyou_pattern = re.compile('<td .*?width="100">(.*?)</td>', re.S)
            dangshiren_pattern = re.compile('<td .*?width="200">(.*?)</td>', re.S)
            time_result = re.findall(time_pattern, str(ji))
            faguan_result = re.findall(faguan_pattern, str(ji))
            anyou_result = re.findall(anyou_pattern, str(ji))
            date_result = re.findall(date_pattern, str(ji))
            beigao = re.compile('((被告)|(被申请(执行)?))(人)? ：(.*?)<br/>', re.S)
            yuangao = re.compile('((原告)|(申请(执行)?))(人)? ：(.*?)<br/>', re.S)
            beigaoResult = re.findall(beigao, str(ji))
            yuangaoResult = re.findall(yuangao, str(ji))
            qita_patten = re.compile('(第三)(人|方) ：(.*?)<br/>', re.S)
            qita_result = re.findall(qita_patten, str(ji))
            dangshiren_Result = re.findall(dangshiren_pattern, str(ji))
            beigaolist = []
            yuangaoList = []
            qitaList = []
            try:
                for reslut in beigaoResult:
                    beigaolist += reslut[5].strip().split(' ')

            except:
                print "没有被告"
            try:
                for reslut in yuangaoResult:
                    yuangaoList += reslut[5].strip().split(' ')
            except:

                print("没有原告")
            try:
                for reslut in qita_result:
                    qitaList += reslut[2].strip().split(' ')
            except:

                print("没有第三人")

            try:
                space_pattern = re.compile("\s{1,}", re.S)
                br_pattern = re.compile("<br/>", re.S)
                dangshiren = re.sub(pattern=space_pattern, repl=" ", string=dangshiren_Result[0].strip())
                dangshiren = re.sub(pattern=br_pattern, repl=";", string=dangshiren)
                data.dangshiren = dangshiren
                data.kaitingriqi += date_result[0].strip()
                data.kaitingriqi += " " + time_result[0].strip()
                data.fating = time_result[1].strip()
                data.anyou = anyou_result[1].strip()
                data.anhao = anyou_result[0].strip()
                data.zhushen = faguan_result[0].strip()
                data.gonggao_id = str(uuid.uuid3(uuid.NAMESPACE_OID, data.kaitingriqi + "_" + data.anhao))
            except:
                continue
            data.yuangao = ",".join(yuangaoList)
            data.beigao = ",".join(beigaolist)

            data.qita = ",".join(qitaList)
            if len(data.yuangao) > 0:
                data.dangshirenjx = data.yuangao + "," + data.beigao
            else:
                data.dangshirenjx = data.beigao
            if len(data.qita) > 0:
                data.dangshirenjx = data.dangshirenjx + "," + data.qita
            self.sqltempe.insertKtgg(data)

    def start(self):

        for cc in self.ccs:
            self.paras["cc"] = cc
            for i in range(1, self.ccs_pages[str(cc)]):
                self.page = i
                self.getInfo()
        self.sqltempe.release()


obj = ShenzhengSpider()
obj.start()

