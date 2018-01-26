# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import re
from entity import *
from mysqlTemplate import *
import uuid
import sys
import chardet
import time

reload(sys)
sys.setdefaultencoding('utf-8')


class hainaiSpider:
    def __init__(self):
        self.href = "http://www.hicourt.gov.cn/ggws/fyggnew.asp?bulletin_type=1"
        self.paras = {}
        self.data = ktgg()
        self.data.no = '251'
        self.sqltemp = mysqlTemplate()

    def getData(self):
        r = requests.get(self.href)
        time.sleep(1)
        while '内部服务器错误' in r.content.decode('gbk'):
            time.sleep(5)
            r = requests.get(self.href)
        aLabel_pattern = re.compile('<td width="38%" height="22">(.*?)</td>', re.S)
        aLabel_reslut = re.findall(aLabel_pattern, r.content.decode('gbk'))
        date_pattern = re.compile('<td width="12%"><font color="#999900">\((.*?)\)</font></td>')
        date_reslut = re.findall(date_pattern, r.content.decode('gbk'))
        i = 0
        for reslut in date_reslut:
            print(i)
            # if i < 928:
            #     i += 1
            #     continue
            href_pattern = re.compile('<a href="(.*?)" target="_blank">(.*?)</a>', re.S)
            href_reslut = re.findall(href_pattern, aLabel_reslut[i].strip())
            herf = href_reslut[0][0]
            anhao = href_reslut[0][1]
            self.getDetail(herf, anhao, reslut.strip())
            i += 1

    def getDetail(self, href, anhao, riqi):
        link = "http://www.hicourt.gov.cn/ggws/" + href
        print(link)
        r = requests.get(link)
        time.sleep(1)
        while '内部服务器错误' in r.content.decode('gbk'):
            time.sleep(10)
            r = requests.get(link)
        fayuan_pattern = re.compile('<FONT color=#ff0033.*?><STRONG>(.*?)</STRONG></FONT>', re.S)
        fayuan_reslut = re.search(fayuan_pattern, r.content.decode('gbk'))
        soup = BeautifulSoup(r.content.decode('gbk'))
        divs = soup.find_all("div", attrs={"class": "p15"})
        for div in divs:
            self.data.gonggao = str(div.parent)
            break
        self.data.anhao = str(anhao)
        riqi = riqi.split("/")
        self.data.kaitingriqi = riqi[0] + "-"
        if (len(riqi[1]) == 1):
            self.data.kaitingriqi += "0" + riqi[1] + "-"
        else:
            self.data.kaitingriqi += riqi[1] + "-"
        if (len(riqi[2]) == 1):
            self.data.kaitingriqi += "0" + riqi[2]
        else:
            self.data.kaitingriqi += riqi[2]

        self.data.created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        strs = self.data.kaitingriqi + "_" + self.data.anhao
        self.data.gonggao_id = str(uuid.uuid3(uuid.NAMESPACE_OID, strs.encode("utf-8")))
        try:
            self.data.fayuan = fayuan_reslut.group(1)
        except AttributeError:
            self.getDetail(href, anhao, riqi)
        self.sqltemp.insertKtgg(self.data)


obj = hainaiSpider()
obj.getData()
obj.sqltemp.release()



