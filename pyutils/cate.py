#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
标识 cate 的枚举类
"""

# from enum import Enum

__author__ = "chiachi"


class Cate(object):

    # 初始化
    initial = "initial"

    # 获取列表
    list = "crawl-list"

    # 获取详情
    detail = "crawl-detail"

    # 结束
    ending = "ending"

    update_ok = "update_ok"

    update_err = "update_err"

if __name__ == "__main__":
    print Cate.ending
    print type(Cate.ending)
