# -*- coding: utf-8 -*-
"""
Created on 2018/1/11

@author: leng

"""

from lxml import html
import requests


def getHtmlTree(url, headers=None):
    return html.fromstring(requests.get(url=url, headers=headers).text)


def postHtmlTree(url, headers=None, postParam=None):
    return html.fromstring(requests.post(url=url, data=postParam, headers=headers).text)


def getContent(url, headers=None):
    return requests.get(url=url, headers=headers).text


def postContent(url, headers=None, postParam=None):
    return requests.post(url=url, data=postParam, headers=headers).text
