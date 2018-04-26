# -*- coding: UTF-8 -*-
from lxml import etree
import requests
from entity import ktgg
from mysqlTemplate import mysqlTemplate
import time
from datetime import timedelta, datetime
import copy
import re
from Base import Base
from pyutils.cate import Cate
import utils


class zhongguotingshenggongkaiwan(Base):
    class Logger:
        def __init__(self, func):
            self.func = func

        def info(self, cate, msg, *args):
            self.func(msg % args, "info", cate)

        def error(self, cate, msg, *args):
            self.func(msg % args, "error", cate)

    def __init__(self):
        Base.__init__(self)
        self.logger = self.Logger(self.log.log)
        self.href = "http://tingshen.court.gov.cn/"
        self.page = 1
        self.proxies = {}
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
        data.gonggao = self.getDetailInfoByXpath(tree, '//div[@class="part case-summary"]/p/@title', 0)
        data.anhao = self.getDetailInfoByXpath(tree, '//*[@id="wrapper"]/div[5]/div[1]/div[3]/ul[1]/li[1]/@title', 0)
        data.anyou = self.getDetailInfoByXpath(tree, '//*[@id="wrapper"]/div[5]/div[1]/div[3]/ul[1]/li[3]/@title', 0)
        data.fating = self.getDetailInfoByXpath(tree, '//*[@id="wrapper"]/div[5]/div[1]/div[3]/ul[1]/li[4]/text()', 0)
        data.kaitingriqi = \
            self.getDetailInfoByXpath(tree, '//*[@id="wrapper"]/div[5]/div[1]/div[3]/ul[1]/li[2]/text()', 1).split(" ")[
                0].replace(
                u'年', '-').replace(u'月', '-').replace(u'日', '')
        try:
            zhushen = self.getDetailInfoByXpath(tree, '//*[@id="judgeul"]/li/i/text()', 0).split(":")[1].replace(';',
                                                                                                                 '')
        except:
            zhushen = self.getDetailInfoByXpath(tree, '//*[@id="judgeul"]/li/i/text()', 0)
        data.zhushen = zhushen
        dangshiren_pattren = re.compile('var party = "(.*?)";', re.S)
        dangshiren_result = re.findall(dangshiren_pattren, r.text)
        data.dangshiren = dangshiren_result[0].replace(u'\\', ',').replace(u"：", ":").replace(u"；", ";").replace(u'、',
                                                                                                                 ',').replace(
            u"　", "").replace(" ", "").replace('\'', '')

        beigao = re.compile(u'((被告)|(被申请(执行)?(再审)?)|(被上诉))(\d)?(人)?:(.*?)(;|$)', re.S)
        yuangao = re.compile(u'((?<=;)|(^))((原告)|(申请(执行)?(再审)?)|(上诉)|((公诉)(机关)?))(人)?:(.*?)(;|$)', re.S)
        beigaoResult = re.findall(beigao, data.dangshiren)
        yuangaoResult = re.findall(yuangao, data.dangshiren)
        qita_patten = re.compile(u'(第三)(人|方):(.*?)(;|$)', re.S)
        qita_result = re.findall(qita_patten, data.dangshiren)
        beigaoList = []
        yuangaoList = []
        qitaList = []
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
        data.yuangao = ",".join(yuangaoList)
        data.beigao = ",".join(beigaoList)
        data.qita = ",".join(qitaList)
        data.gonggao_id = str(gonggaoId)
        print data.dangshiren
        print data.yuangao
        print data.beigao

        data.fayuan = tree.xpath('//*[@id="wrapper"]/div[4]/div[1]/p/a/text()')[0].replace('\'', '')
        fayuanId = tree.xpath('//*[@id="wrapper"]/div[4]/div[1]/p/a/@href')[0].split("/")[2]
        data.sheng = self.getShengByFayuanId(fayuanId)
        data.created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        data.dangshirenjx = ",".join(yuangaoList + beigaoList + qitaList)
        if data.kaitingriqi == "" and data.dangshirenjx == "":
            raise Exception
        self.sqltemp.insertKtgg_with_unicode(data)

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

    def getDetailInfoByXpath(self, tree, xpath, index):
        try:
            return tree.xpath(xpath)[index].strip().replace(
                '\'',
                '')
        except:
            print(u"没有信息" + xpath)
            return ""

    def getShengInfo(self):
        """
        获取每个省的法院ＩＤ
        """
        areacodeList = []
        while len(areacodeList) <= 0:
            r = requests.get(self.href + "/court", headers=self.headers, proxies=self.proxies)
            r.encoding = "utf-8"
            tree = etree.HTML(r.text)
            areacodeList = tree.xpath('//*[@id="wrapper"]/div[4]/div/div[1]/div/span/@areacode')
            areaList = tree.xpath('//*[@id="wrapper"]/div[4]/div/div[1]/div/span/text()')
            courtCode_pattern = re.compile('<a href="/court/(\d+)" target="_blank">')
            ips = utils.getProxy()
            print("换代理")
            print(obj.proxies)
            self.proxies["http"] = ips[0]
            self.proxies["https"] = ips[1]
            time.sleep(1)
        i = 0
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


if __name__ == "__main__":

    obj = zhongguotingshenggongkaiwan()
    yesterday = datetime.today() + timedelta(-3)
    # today_format = datetime.today().strftime('%Y-%m-%d')
    # yesterday_format = yesterday.strftime('%Y-%m-%d')
    today_format = '2018-04-13'
    yesterday_format = '2018-04-10'

    min = int(
        obj.sqltemp.queryMax_GonggaoId_by_no_and_kaitingriqi(2, yesterday_format))
    max = int(
        obj.sqltemp.queryMax_GonggaoId_by_no_and_kaitingriqi(2, today_format)) + 3000
    obj.logger.info(Cate.initial, u"遍历范围：(" + str(min) + "," + str(max) + ")")
    # obj.getShengInfo()
    for id in range(min, max):
        if obj.sqltemp.queryCountBy_gonggaoid_and_no(id, 2) > 0:
            obj.logger.info(Cate.detail, u"重复数据:" + str(id))
            continue
        href = obj.href + "live/" + str(id)
        print href
        r = requests.get(href, headers=obj.headers)
        time.sleep(1)
        r.encoding = 'utf-8'
        print(len(r.text))
        s = requests.session()
        s.keep_alive = False

        ergodic_times = 10
        while 'document.location.reload();' in r.text:
            ergodic_times -= 1
            if ergodic_times < 0:
                obj.log.log('crawler failed:id:' + str(id), 'error', 'update_err')
                break
            ips = utils.getProxy()
            print("换代理")
            obj.proxies["http"] = ips[0]
            obj.proxies["https"] = ips[1]
            print(obj.proxies)
            time.sleep(1)
            try:
                r.close()
                print u"使用代理"
                r = requests.get(href, headers=obj.headers, proxies=obj.proxies)
            except:
                ips = utils.getProxy()
                print("换代理")
                obj.proxies["http"] = ips[0]
                obj.proxies["https"] = ips[1]
                print(obj.proxies)
                time.sleep(1)
            else:
                if 'document.location.reload();' not in r.text:
                    break
        if u"页面出错了" in r.text or len(r.text) < 2000:
            r.close()
            obj.logger.info(Cate.detail, str(id) + u"不存在")
            continue
        # print r.text
        obj.logger.info(Cate.detail, str(id) + u"详情")
        try:
            obj.getDetailInfo(id, r.text)
        except:
            obj.log.log('crawler failed' + str(id), 'error', 'update_err')
            raise Exception
        r.close()
    obj.log.log('crawler update success', 'info', 'update_ok')
    obj.logger.info(Cate.ending, "任务完成")
