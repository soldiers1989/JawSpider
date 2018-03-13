# -*- coding: UTF-8 -*-
from lxml import etree
import requests
from entity import ktgg
from mysqlTemplate import mysqlTemplate
import time
import copy
import re
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType


class zhongguotingshenggongkaiwan:
    def __init__(self):
        self.href = "http://tingshen.court.gov.cn/"
        self.page = 1
        self.data = ktgg()
        self.data.no = '2'
        self.data.dangshirenjx_flag = '1'
        self.sqltemp = mysqlTemplate()
        self.areaCourtList = []
        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Referer': 'http://tingshen.court.gov.cn/court/1541',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'acw_tc=AQAAAFyOJGPmjgEA5fzdq/EY1/bdHEdP; _uab_collina=151987044428282196778462; _pk_ses.1.a5e3=*; _pk_id.1.a5e3=778c76380d98675f.1519870445.1.1519874896.1519870445.; SERVERID=2666959f4331fe3ad439f4610ea751e3|1519874896|1519870444',
            'Host': 'tingshen.court.gov.cn',
            'Upgrade-Insecure-Requests': '1'}

    def getDetailInfo(self, gonggaoId, text):
        tree = etree.HTML(text)
        data = copy.deepcopy(self.data)
        try:
            data.gonggao = tree.xpath('//div[@class="part case-summary"]/p/@title')[0].strip()
        except:
            print(u"没有公告")
        data.anhao = tree.xpath('//*[@id="wrapper"]/div[5]/div[1]/div[3]/ul[1]/li[1]/@title')[0].strip()
        data.anyou = tree.xpath('//*[@id="wrapper"]/div[5]/div[1]/div[3]/ul[1]/li[3]/@title')[0].strip()
        data.fating = tree.xpath('//*[@id="wrapper"]/div[5]/div[1]/div[3]/ul[1]/li[4]/text()')[0].strip()
        data.kaitingriqi = \
            tree.xpath('//*[@id="wrapper"]/div[5]/div[1]/div[3]/ul[1]/li[2]/text()')[1].strip().split(" ")[0].replace(
                u'年', '-').replace(u'月', '-').replace(u'日', '')
        try:
            data.zhushen = tree.xpath('//*[@id="judgeul"]/li/i/text()')[0].strip().split(":")[1].replace(';', '')
        except:
            try:
                data.zhushen = tree.xpath('//*[@id="judgeul"]/li/i/text()')[0].strip()
            except:
                print u"没有主审"
        dangshiren_pattren = re.compile('var party = "(.*?)";', re.S)
        dangshiren_result = re.findall(dangshiren_pattren, r.text)
        data.dangshiren = dangshiren_result[0].replace(u'\\', ',').replace(u"：", ":").replace(u"；", ";").replace(u'、', ',').replace(u"　","").replace(" ","");



        beigao = re.compile(u'((被告)|(被申请(执行)?(再审)?)|(被上诉))(\d)?(人)?:(.*?)(;|$)', re.S)
        yuangao = re.compile(u'((?<=;)|(^))((原告)|(申请(执行)?(再审)?)|(上诉)|((公诉)(机关)?))(人)?:(.*?)(;|$)', re.S)
        beigaoResult = re.findall(beigao, data.dangshiren)
        yuangaoResult = re.findall(yuangao, data.dangshiren)
        qita_patten = re.compile(u'(第三)(人|方):(.*?)(;|$)', re.S)
        qita_result = re.findall(qita_patten, data.dangshiren)
        beigaoList=[]
        yuangaoList=[]
        qitaList=[]
        try:
            for reslut in beigaoResult:
                beigaoList.append(reslut[8])
        except:
            print "没有被告"
        try:
            for reslut in yuangaoResult:
                yuangaoList.append(reslut[12])
        except:

            print("没有原告")
        try:
            for reslut in qita_result:
                qitaList.append(reslut[2])
        except:
            print("没有第三人")
        data.yuangao=",".join(yuangaoList)
        data.beigao=",".join(beigaoList)
        data.qita=",".join(qitaList)
        data.gonggao_id = str(gonggaoId)
        print data.dangshiren
        print data.yuangao
        print data.beigao


        data.fayuan = tree.xpath('//*[@id="wrapper"]/div[4]/div[1]/p/a/text()')[0]
        fayuanId = tree.xpath('//*[@id="wrapper"]/div[4]/div[1]/p/a/@href')[0].split("/")[2]
        data.sheng = self.getShengByFayuanId(fayuanId)
        data.created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if len(data.yuangao) > 0:
            data.dangshirenjx = data.yuangao + "," + data.beigao
        else:
            data.dangshirenjx = data.beigao
        if len(data.qita) > 0:
            data.dangshirenjx = data.dangshirenjx + "," + data.qita
        self.sqltemp.insertKtgg(data)

    def getShengByFayuanId(self, fayuanId):
        """
        通过法院ＩＤ　获得省
        :param fayuanId:
        :return:
        """
        for list in self.areaCourtList:
            if fayuanId in list['courtList']:
                return list['areaName']
        return ""

    def getShengInfo(self):
        """
        获取每个省的法院ＩＤ
        """
        r = requests.get(self.href + "/court", headers=self.headers)
        r.encoding = "utf-8"
        tree = etree.HTML(r.text)
        areacodeList = tree.xpath('//*[@id="wrapper"]/div[4]/div/div[1]/div/span/@areacode')
        areaList = tree.xpath('//*[@id="wrapper"]/div[4]/div/div[1]/div/span/text()')
        i = 0
        courtCode_pattern = re.compile('<a href="/court/(\d+)" target="_blank">')

        for areacode in areacodeList:
            time.sleep(3)
            href = self.href + "/court?areaCode=" + areacode
            r = requests.get(href, headers=self.headers)
            print href
            r.encoding = "utf-8"
            data = {}
            data["areaName"] = areaList[i]
            data["courtList"] = []
            countCode_reslut = re.findall(courtCode_pattern, r.text)
            for result in countCode_reslut:
                data["courtList"].append(result)
            self.areaCourtList.append(data)
            i += 1
        print(u"省信息获取完毕")

    def getTodayGonggaoId(self):
        """
        获取今天的公告ＩＤ
        :return:
        """
        gonggaoidList = []
        page = 1
        while True:
            href = self.href + "preview/findCases?pageNumber=" + str(page) + "&timeStr=" + time.strftime("%Y-%m-%d",
                                                                                                         time.localtime())
            print(href)
            page += 1
            time.sleep(3)
            r = requests.get(href, headers=self.headers)
            caselist = r.json()['list']
            if len(caselist) <= 0:
                break
            for item in caselist:
                gonggaoidList.append(item['caseId'])
        print u"今日公告id获取完毕"
        return gonggaoidList

    def get_cai_pan_wen_shu(self, id):
        """
        获得裁判文书
        :return: 裁判文书
        """
        driver = webdriver.PhantomJS()
        driver.set_page_load_timeout(5)
        driver.set_script_timeout(5)
        driver.get(self.href + "live/" + str(id))
        elem = driver.find_element_by_xpath('//*[@id="adDocuments"]/a')
        time.sleep(4)
        driver.execute_script("arguments[0].scrollIntoView(false);", elem)
        time.sleep(3)
        elem.click()
        handkes = driver.window_handles
        driver.switch_to_window(handkes[-1])
        time.sleep(4)
        print driver.page_source


if __name__ == "__main__":
    obj = zhongguotingshenggongkaiwan()
    obj.getShengInfo()
    id = 1192715
    while id < 2000000:
        if obj.sqltemp.queryCountBy_gonggaoid_and_no(id, 2) > 0:
            print u"重复数据:" + str(id)
            id += 1
            continue
        href = obj.href + "live/" + str(id)
        r = requests.get(href, headers=obj.headers)
        print href
        r.encoding = 'utf-8'
        time.sleep(3)
        if u"页面出错了" in r.text:
            print str(id) + u"不存在"
            id += 1
            continue
        obj.getDetailInfo(id, r.text)
        id += 1

    # strs=u"上诉人:许小川;上诉人:邵清华;上诉人:邵清华;上诉人:邵清华;上诉人:邵清华;上诉人:金鑫;上诉人:金鑫;上诉人:金鑫;"
    #
    # yuangao = re.compile(u'((?<=;)|(^))(上诉)(人)?:(.*?);', re.S)
    # yuangaoResult = re.findall(yuangao, strs)
    # for reslut in yuangaoResult:
    #     print(reslut[4])


    # id=1191738
    # href = obj.href + "live/" + str(id)
    # r = requests.get(href, headers=obj.headers)
    # print href
    # r.encoding = 'utf-8'
    # time.sleep(3)
    #
    # obj.getDetailInfo(id, r.text)
    # id += 1
