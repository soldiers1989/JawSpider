# coding=utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import logging
import datetime
import re
import os
import json
import time
import requests
import urllib2
import random
import hashlib
from mysql import connector


def to_email(name, spider, errmsg):
    data = {
        'name': name,
        'codename': spider,
        'errmsg': errmsg
    }
    requests.post('http://app.icekredit.com:7070/send_mail', data=data)


def to_phone(name, spider, errmsg):
    data = {
        'name': name,
        'codename': spider,
        'errmsg': errmsg
    }
    requests.post('http://app.icekredit.com:7070/send_sms', data=data)


def getRedisConfig():
    return {
        'host': '101.37.145.10',
        'port': 6379,
        'db': 3,
        'password': 'd2b62c0d6db24f36:ICKredis2016',
        # https://github.com/andymccurdy/redis-py/issues/775
        'socket_timeout': 60
    }


def getMysqlConfig():
    # https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html
    return {
        'host': 'rm-bp11towre3n815e78o.mysql.rds.aliyuncs.com',
        'user': 'crawler_2',
        'password': 'Crawler_ICK_2017',
        'port': 3306,
        'database': 'ktgg_test',
        'charset': 'utf8',
        'autocommit': True
    }


def getProxy(type='proxy_icekredit'):
    proxies = {
        "proxy_icekredit": "http://proxy.icekredit.com/api/v2/proxy/adsl"
    }
    addr = proxies[type]
    req = urllib2.Request(addr)
    response = urllib2.urlopen(req, timeout=5).read()
    items = json.loads(response)
    ip_list = items["data"]["proxy_list"]
    return ip_list


# 如果key一样，每次都返回同一个UA，key为空则随机返回UA
def getUA(key=None):
    fn = os.path.realpath(os.path.dirname(__file__) + '/../resource/User-Agent-Chrome.txt')
    fp = open(fn)
    li = []
    while 1:
        line = fp.readline()
        if not line:
            break
        li.append(line)
    if key is None:
        return random.choice(li)
    else:
        md5 = hashlib.md5(key.encode('utf-8'))
        hexStr = md5.hexdigest()
        sum = int(hexStr, 16)
        li_sz = len(li)
        idx = sum % li_sz
        return li[idx]


class Log:

    def __del__(self):
        self.log("crawler exit", 'info', 'exit')

    def __init__(self, *args, **kwargs):
        self.startTime = int(time.time())
        self.no = 0
        self.logDir = None
        self.db = None
        self.excludedLogLevelOrCate = {
            "stdout": [],
            "file": [],
            "database": []
        }
        self.node_id = ''
        self.pid = os.getpid()
        for _ in sys.argv:
            res = re.search('node_id:(.*)', _)
            if res:
                self.node_id = res.group(1)
                break

        scriptName = os.path.basename(sys.argv[0])
        if scriptName == 'master.py':
            self.no = 0
        else:
            res = re.search('(\d+).py', scriptName)
            if not res:
                raise Exception("只有<master.py>或者<爬虫编号.py>的python文件能调用Log类")
            else:
                self.no = int(res.group(1))

        rootDir = os.path.realpath(os.path.dirname(__file__) + '/..')
        self.logDir = rootDir + '/var/log'
        if 'db' in kwargs.keys():
            self.db = connector.connect(**kwargs['db'])
        else:
            self.db = connector.connect(**getMysqlConfig())
        self.log("crawler start", 'info', 'start')

    def log(self, msg, level='debug', cate=''):
        dateStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cost_time = int(time.time()) - self.startTime

        logLine = "%s[%ss] <%s><%s>[%s][%s] %s\n" % (dateStr, cost_time, self.node_id, self.no, level, cate, msg)

        if level not in self.excludedLogLevelOrCate['stdout'] and cate not in self.excludedLogLevelOrCate['stdout']:
            sys.stdout.write(logLine)
        if level not in self.excludedLogLevelOrCate['file'] and cate not in self.excludedLogLevelOrCate['file']:
            # https://www.v2ex.com/t/425463
            try:
                fn = self.logDir + "/%d-%s-%s.log" % (self.no, level, cate)
                file_object = open(fn, 'a')
                file_object.write(logLine)
                file_object.close()
                fn = self.logDir + "/%d.log" % (self.no)
                file_object = open(fn, 'a')
                file_object.write(logLine)
                file_object.close()
            except Exception, e:
                sys.stdout.write(e.message)
        if level not in self.excludedLogLevelOrCate['database'] and cate not in self.excludedLogLevelOrCate['database']:
            # https://stackoverflow.com/questions/11597025/is-this-use-of-str-replace-sufficient-to-prevent-sql-injection-attacks
            msg_escaped = msg
            if msg_escaped:
                msg_escaped = msg_escaped.replace("'", "''")
                msg_escaped = msg_escaped.replace("\\", "\\\\")
            sql = "INSERT INTO `log` (node_id, no, pid, level, cate, msg, cost_time) VALUES('%s', '%d', '%d', '%s', '%s', '%s', '%d')" % (
                self.node_id, self.no, self.pid, level, cate, msg_escaped, cost_time)
            try:
                cursor = self.db.cursor()
                cursor.execute(sql)
                cursor.close()
            except Exception, e:
                # 连接可能会断，这里从连一下
                self.db = connector.connect(**getMysqlConfig())
                cursor = self.db.cursor()
                cursor.execute(sql)
                cursor.close()
