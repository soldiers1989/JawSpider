#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""HTML 源码清洗方法"""

import re
from lxml import etree

from escape import remove_escape
from text_lib import RE_TAG, RE_COMMON_TAGS
from text_cleaner import clean_text, clean_regex_list

__author__ = "chiachi"


def replace_html_tag(html, tag, replacement=""):
    """
    删除/替换 HTML 源码中的特定 tag
    :param html:            HTML 源码
    :param tag:             待删除/替换的 tag 名称
    :param replacement:     替换字符串
    :return:                清洗后的文本
    """
    return re.sub("<{}[\s\S]*?>".format(tag), replacement, html)


def remove_html_tag(html, **kwargs):
    """
    清洗含有大量标签的 HTML 源码
    :param html:    HTML 源码或 lxml.etree.ElementTree
    :param kwargs:  `new_line_tag` 对特定标签进行换行操作，接收标签类型
                    `strict_escape` remove_escape 的参数，默认为 True
                    `leave_space` 是否保留非英文中的空格，默认为 False
    :return:        清洗后的文本

    1. 移除转义字符
    2. （可选）对特定标签引入空行
    3. 移除常见的无用标签
    4. 移除所有 HTML 标签
    5. 清洗文本
    """
    if html is None:
        return
    if not isinstance(html, basestring):
        html = etree.tounicode(html)
    if kwargs.get("new_line_tag"):
        # 特定标签进行换行
        html = replace_html_tag(remove_escape(html, kwargs.get("strict_escape", True)),
                                kwargs["new_line_tag"], "\n")
    return clean_text(RE_TAG.sub("", clean_regex_list(remove_escape(
        html, kwargs.get("strict_escape", True)), RE_COMMON_TAGS)), kwargs.get("leave_space", False))


def clean_html_paras(html, sep="", leave_space=False):
    """
    对列表式的 HTML 文本进行拆分
    :param html:        HTML 源码或 lxml.etree.ElementTree
    :param sep:         用以划分段落的分隔符（正则形式如 `br` 或 `\t\n`）
    :param leave_space: 是否保留非英文中的空格，默认为 False
    :return: 
    """
    if not sep:
        raise TypeError("[clean_html_paras] got null `sep`, or use [remove_html_tag] instead")
    if not isinstance(html, basestring):
        html = etree.tounicode(html)
    return [remove_html_tag(html, leave_space=leave_space) for para in re.split(sep, html) if remove_html_tag(para)]


if __name__ == "__main__":
    print remove_html_tag(u"""<div class="text">
<h1>2018-01-23 10:49在东乡族自治县人民法院第三审判法庭开庭审理唐士坤走私、贩卖、运输、制造毒品罪一案</h1>
<h2>时间：2018-01-27 作者：东乡族自治县人民法院</h2>
<p style="text-indent: 0em; text-align:center; font-size:20px;">公告</p><br/>
<p style="text-indent: 2em;">我院定于2018年01月23日 10时49分在本院第三审判法庭依法公开审理唐士坤走私、贩卖、运输、制造毒品罪一案。</p>
<p style="text-indent: 0em;">特此公告</p>
<p style="float:right;">二〇一八年一月二十七日</p>
</div>""")
