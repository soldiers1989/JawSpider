#!/usr/bin/env python
# -*- coding:utf8 -*-

"""移除 HTML 转义符"""

import re
from htmlentitydefs import name2codepoint

__author__ = "chiachi"


entitydefs = {key: unichr(name2codepoint[key]) for key in name2codepoint}
entitydefs["apos"] = u"'"
irregular_entities = r"&({})".format("|".join([key for key in name2codepoint]))


def _replace_entities(s):
    s = s.groups()[0]
    try:
        if s[0] == "#":
            s = s[1:]
            if s[0] in ["x", "X"]:
                c = int(s[1:], 16)
            else:
                c = int(s)
            return unichr(c)
    except ValueError:
        return "&#" + s + ";"
    else:
        try:
            return entitydefs[s]
        except KeyError:
            return "&" + s + ";"


def _replace_irregular_entities(s):
    s = s.groups()[0]
    return entitydefs.get(s, "&" + s)


def _remove_single_escape(s, strict_replace=True):
    """
    替换 `&xx;` 形式的转义符
    :param s:               待清洗文本
    :param strict_replace:  是否严格替换，严格替换时不处理丢失 `;` 的情况
    :return:
    """
    if "&" not in s:
        return s
    s = re.sub(r"&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));", _replace_entities, s)
    return s if strict_replace else re.sub(irregular_entities, _replace_irregular_entities, s)


def remove_escape(s, strict_replace=True):
    """
    移除递归的转义符
    """
    while True:
        s_checker = _remove_single_escape(s, strict_replace=strict_replace)
        if s_checker == s:
            return s
        s = s_checker


if __name__ == "__main__":
    print remove_escape("&amp;")
    print remove_escape("&amp")
    print remove_escape("&amp", False)
    print remove_escape("&amp;amp;amp;amp;amp;amp;amp;")
