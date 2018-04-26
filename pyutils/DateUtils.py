# -*- coding: utf-8 -*-
"""
Created on 2018/1/11

@author: leng

"""

import time
import datetime

DATE_PATTERN_DAY = "%Y-%m-%d"

DATE_PATTERN_DEFAULT = "%Y-%m-%d %H:%M:%S"


def dayTimeToTimestamp(timeString):
    return time.mktime(time.strptime(timeString, DATE_PATTERN_DAY))


def defaultTimeToTimestamp(timeString):
    return time.mktime(time.strptime(timeString, DATE_PATTERN_DEFAULT))


def timestampToDateTime(timestamp):
    return time.gmtime(timestamp)


def getTimeBeforeDays(timeString, day):
    print(datetime.datetime.strptime(timeString, DATE_PATTERN_DAY) - datetime.timedelta(days=day))


def getTimeAfterDays(timeString, day):
    print(datetime.datetime.strptime(timeString, DATE_PATTERN_DAY) + datetime.timedelta(days=day))
