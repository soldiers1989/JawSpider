#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""解析常见日期格式"""

import re
import time
import datetime

__author__ = "chiachi"


YMD = (u"年", u"月", u"日")
CHAR_SEPS = [YMD, tuple(i.encode("utf-8") for i in YMD), tuple(i.encode("gb18030") for i in YMD)]

TIME_UNIT = {"unicode": {"days": u"天", "hours": u"小时", "minutes": u"分钟", "recent": u"最近"}}
TIME_UNIT["utf-8"] = {key: TIME_UNIT["unicode"][key].encode("utf-8") for key in TIME_UNIT["unicode"]}
TIME_UNIT["gb18030"] = {key: TIME_UNIT["unicode"][key].encode("gb18030") for key in TIME_UNIT["unicode"]}

TOWARD = {"unicode": {"before": u"前", "after": u"后"}}
TOWARD["utf-8"] = {key: TOWARD["unicode"][key].encode("utf-8") for key in TOWARD["unicode"]}
TOWARD["gb18030"] = {key: TOWARD["unicode"][key].encode("gb18030") for key in TOWARD["unicode"]}

DAYS = {"unicode": {"yesterday": u"昨天", "today": u"今天", "tomorrow": u"明天"}}
DAYS["utf-8"] = {key: DAYS["unicode"][key].encode("utf-8") for key in DAYS["unicode"]}
DAYS["gb18030"] = {key: DAYS["unicode"][key].encode("gb18030") for key in DAYS["unicode"]}


def _change_date_format(date_string, date_format, sep="-"):
    """
    已知日期格式的转换
    :param date_string: 日期字符串，如「1990年6月4日」
    :param date_format: 日期格式字符串，如「%Y年%m月%d日」
    :param sep:         连接符，默认为「-」
    :return:            返回统一格式的日期字符串，如「1990-06-04」
    """
    try:
        date_array = time.strptime(date_string, date_format)
        if "%Y" in date_format:
            return time.strftime(sep.join(["%Y", "%m", "%d"]), date_array)
        # 不带有年份信息则使用当前年份
        return time.strftime(sep.join([time.strftime("%Y"), "%m", "%d"]), date_array)
    except ValueError:
        return ""


def _trans_date_with_char(date_string):
    """
    对使用汉字进行连接的日期格式进行转换
    :param date_string: 使用「年月日」连接的日期格式，如「1990年6月4日」
    :return:            返回统一的日期格式，如「1990-06-04」

    两位年份判定: (70, ) 为 1970 年后，(, 50) 为 2050 年前
    """
    # 包含年份的情况
    for sep in CHAR_SEPS:
        result_list = re.findall("(?<!\d)(((19|20)?\d{2})\s*%s\s*\d{1,2}\s*%s\s*\d{1,2}\s*%s)" % sep, date_string)
        if result_list:
            date_string = ""
            date_result = result_list[0]
            if len(date_result[1]) == 2:
                if int(date_result[1]) <= 50:
                    date_string = "20" + date_result[0]
                if int(date_result[1]) >= 70:
                    date_string = "19" + date_result[0]
            else:
                date_string = date_result[0]
            return _change_date_format(re.sub("\s+", "", date_string), "%%Y%s%%m%s%%d%s" % sep)

    # 不包含年份的情况
    for sep in CHAR_SEPS:
        result_list = re.findall("(?<![%s\d])\d{1,2}\s*%s\s*\d{1,2}\s*%s" % sep, date_string)
        if result_list:
            return _change_date_format(re.sub("\s+", "", result_list[0]), "%%m%s%%d%s" % sep[1:])
    return ""


def _trans_date_with_sep(date_string):
    """
    对使用符号进行连接的日期格式进行转换
    :param date_string: 连接符为「-」或「/」的日期格式，如「1990-06-04」
    :return:            返回统一的日期格式，如「1990-06-04」
    """
    seps = ["-", "/"]

    # 包含年份的情况
    for sep in seps:
        result_list_with_year = re.findall("{}".join(["\s*", ] * 2).format(sep).join(
            ["(?<!\d)(((19|20)?\d{2})", "\d{1,2}", "\d{1,2})(?!\d)"]), date_string)
        if result_list_with_year:
            date_string = ""
            date_result = result_list_with_year[0]
            if len(date_result[1]) == 2:
                if int(date_result[1]) <= 50:
                    date_string = "20" + date_result[0]
                if int(date_result[1]) >= 70:
                    date_string = "19" + date_result[0]
            else:
                date_string = date_result[0]
            return _change_date_format(re.sub("\s+", "", date_string), "%%Y%s%%m%s%%d" % ((sep, ) * 2))

    # 不包含年份的情况
    for sep in seps:
        result_list_without_year = re.findall(sep.join(["\s*", ] * 2).join(
            ["(?<![%s\d])\d{1,2}" % sep, "\d{1,2}(?!\d)"]), date_string)
        if result_list_without_year:
            return _change_date_format(re.sub("\s+", "", result_list_without_year[0]), "%%m%s%%d" % sep)
    return ""


def _trans_recent_date(date_string, needs_time=False):
    """
    对描述性的时间单位进行转换
    :param date_string: (最近)\d+(天|小时|分钟)(前|后)，如「最近7天」「5天前」「3分钟后」等
    :param needs_time:  是否需要返回具体时间，具体时间根据当前时间计算
    :return:            返回统一的日期格式如「1990-06-04」或「1990-06-04 06:00:00」
    """
    for encoding in TIME_UNIT.keys():
        for unit in TIME_UNIT[encoding].keys():
            number = re.findall(TIME_UNIT[encoding]["recent"] + "\s*(\d+)\s*" + TIME_UNIT[encoding][unit], date_string)
            if number:
                date = datetime.datetime.now() + datetime.timedelta(**{unit: -1 * int(number[0])})
                return date.strftime("%Y-%m-%d %H:%M:%S") if needs_time else date.strftime("%Y-%m-%d")
            for ward in ["before", "after"]:
                number = re.findall("(\d+)\s*" + TIME_UNIT[encoding][unit] +
                                    "\s*" + TOWARD[encoding][ward], date_string)
                if number:
                    date = datetime.datetime.now() + datetime.timedelta(
                        **{unit: int(number[0]) * {"before": -1, "after": 1}[ward]})
                    time_string = _trans_time_with_comma(date_string)
                    return (date.strftime("%Y-%m-%d") + " " + time_string
                            if time_string else date.strftime("%Y-%m-%d %H:%M:%S")) \
                        if needs_time else date.strftime("%Y-%m-%d")
    return ""


def _trans_these_days(date_string):
    """
    对「昨天」、「今天」以及「明天」进行转换
    :param date_string: 「昨天」、「今天」、「明天」
    :return:            返回统一的日期格式如「2016-12-25」
    """
    for encoding in DAYS.keys():
        for day in DAYS[encoding].keys():
            if re.findall(DAYS[encoding][day], date_string):
                return (datetime.datetime.now() + datetime.timedelta(
                    **{"days": {"yesterday": -1, "today": 0, "tomorrow": 1}[day]})).strftime("%Y-%m-%d")
    return ""


def _trans_time_with_comma(time_string):
    """
    对具体时间进行清洗转换
    :param time_string: 包含使用冒号连接的时间字符串
    :return:            统一格式的时间字符串，如「12:23:34」
    """
    for i in (3, 2):  # 3 带秒，2 不带秒
        result_list = re.findall(":".join(["\s*", ] * 2).join(["\d{1,2}", ] * i), time_string)
        if result_list:
            try:
                return time.strftime("%H:%M:%S", time.strptime(re.sub("\s+", "", result_list[0]),
                                                               {3: "%H:%M:%S", 2: "%H:%M"}[i]))
            except ValueError:
                return ""
    return ""


def trans_time_stamp(time_string, needs_time=False):
    """
    对时间戳进行转换
    :param time_string: 包含时间戳的字符串
    :param needs_time:  是否需要返回具体时间
    :return:            转换时间戳为具体时间

    时间戳为 10 位或 13 位，并且要求第一位为「1」，适用时间范围为 (2001-09-09, 2033-05-18)
    """
    try:
        digit_string = re.search("(\d+)", time_string).group(1)
    except AttributeError:
        return ""
    if len(digit_string) in [10, 13] and digit_string.startswith("1"):
        time_stamp = int(digit_string) / (1000 if len(digit_string) == 13 else 1)
        return time.strftime({True: "%Y-%m-%d %H:%M:%S", False: "%Y-%m-%d"}[needs_time], time.localtime(time_stamp))
    return ""


def clean_date(date_string, needs_time=False):
    """
    「提取」日期和时间信息并进行清洗
    :param date_string: 包含日期信息的字符串
    :param needs_time: 是否需要具体时间，默认为「False」
    :return: 统一格式的时间字符串，如「1990-06-04」或「1990-06-04 06：00：00」

    可处理的类型：
    1. 「最近7天」、「5天前」、「3小时后」等
    2. 「昨天」、「今天」和「明天」
    3. 「1990年6月4日」
    4. 「1990-06-04」
    5. 「90/6/4」
    如输入字符串中出现具体时间，则会进行返回，否则返回零点时间（除情况 1 外）

    可处理的时间范围：
    4位年份: 1900 ~ 2099
    2位年份: 70 ~ 99 (20 世纪)
             00 ~ 50 (21 世纪)
    """
    if not isinstance(date_string, basestring):
        return
    for date in [_trans_recent_date(date_string, needs_time), trans_time_stamp(date_string, needs_time)]:
        if date:
            return date
    time_string = _trans_time_with_comma(date_string)
    for date in [_trans_these_days(date_string), _trans_date_with_char(date_string), _trans_date_with_sep(date_string)]:
        if date:
            return (date + " " + time_string if time_string else date + " 00:00:00") if needs_time else date
    if time_string:
        return datetime.datetime.now().strftime("%Y-%m-%d") + " " + time_string \
            if needs_time else datetime.datetime.now().strftime("%Y-%m-%d")
    return ""


if __name__ == "__main__":
    print(clean_date("2018年06月04日09:30"))
    print(clean_date("2018年06月04日09:30", True))
