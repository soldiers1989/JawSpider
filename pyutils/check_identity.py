#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

__author__ = "chiachi"


ACCUSER = [
    u"附带民事诉讼原告人",
    u"附带民事原告人",
    u"公诉方",
    u"公诉机关",
    u"公诉人",
    u"起诉人",
    u"上诉人",
    u"申请方",
    u"申请人",
    u"申请再审人",
    u"申请执行人",
    u"申诉人",
    u"原告",
    u"原告人",
    u"原审上诉人",
    u"原审原告",
    u"再审申请人",
    u"债权人",
    u"支持抗诉机关",
    u"支持上诉机关",
    u"自诉人",
    u"自诉人暨附带民事诉讼原告人"
]

DEFENDANT = [
    u"辩护人",
    u"被告",
    u"被告人",
    u"被上诉人",
    u"被申请方",
    u"被申请人",
    u"被申请再审人",
    u"被申请执行人",
    u"被申诉人",
    u"被执行人",
    u"犯罪嫌疑人",
    u"附带民事诉讼被告人",
    u"赔偿义务机关",
    u"原审被告",
    u"原审被告人",
    u"原审被上诉人",
    u"原审(一审)被告人",
    u"再审被申请人",
    u"债务人",
    u"罪犯"
]

THIRD = [
    u"辩护人",
    u"当事人",
    u"第三人",
    u"原审第三人"
]


def check_accuser(title):
    """
    检查是否为原告身份
    """
    return True if re.search(u"^({})".format(u"|".join(ACCUSER)), title) else False


def check_defendant(title):
    """
    检查是否为被告身份
    """
    return True if re.search(u"^({})".format(u"|".join(DEFENDANT)), title) else False


def check_third(title):
    """
    检查是否为第三人身份
    """
    return True if re.search(u"^({})".format(u"|".join(THIRD)), title) else False


if __name__ == "__main__":
    print check_accuser(u"原告人")
