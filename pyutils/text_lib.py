#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""正则表达式"""

import re

__author__ = "chiachi"


# 特殊空格 -> 空格
# 0x0009    HT              水平制表符     \t
# 0x000b    VT              垂直制表符
# 0x000c    FF              换页键
# 0x000d    CR              回车键         \r
# 0x00a0    NO-BREAK SPACE
# 0x2000    EN QUAD
# 0x2001    EM QUAD
# 0x2002    EN SPACE
# 0x2003    EM SPACE
# 0x2004    THREE-PER-EM SPACE
# 0x2005    FOUR-PER-EM SPACE
# 0x2006    SIX-PER-EM SPACE
# 0x2007    FIGURE SPACE
# 0x2008    PUNCTUATION SPACE
# 0x2009    THIN SPACE
# 0x200a    HAIR SPACE
# 0x200b    ZERO WIDTH SPACE
# 0x202f    NARROW NO-BREAK SPACE
# 0x205f    MEDIUM MATHEMATICAL SPACE
SPACE_DICT = dict((key, 32) for key in
                  [0x0009, 0x000b, 0x000c, 0x000d, 0x00a0] + range(0x2000, 0x200c) + [0x202f, 0x205f])

# 特殊换行 -> 换行
# 0x2028    LINE SEPARATOR
# 0x2029    PARAGRAPH SEPARATOR
NL_DICT = {0x2028: 10, 0x2029: 10}

# 全角空格、英文或数字 -> 半角
# 0xff10 - 0xff19   全角 0 ~ 9
# 0xff21 - 0xff3b   全角 A ~ Z
# 0xff41 - 0xff5b   全角 a ~ z
SBC_DICT = dict(zip([0x3000, ] + range(0xff10, 0xff1a) + range(0xff21, 0xff3b) + range(0xff41, 0xff5b),
                    [0x0020, ] + range(0x0030, 0x003a) + range(0x0041, 0x005b) + range(0x0061, 0x007b)))

# 英文括号 -> 中文括号
BRACKETS_DICT = {40: 0xff08, 41: 0xff09}

# 空白
RE_SPACE = re.compile("[\f\r\t\v]")
RE_NL = re.compile("[ ]*\n[ ]*")
RE_SPACE_BETWEEN_WORDS_TYPE_1 = re.compile("(?<=\w)[ ]+(?=\w)")     # 英文字符中的空白
RE_SPACE_BETWEEN_WORDS_TYPE_2 = re.compile("(?<=\w)[ ]+(?=\W)")     # 英文字符、中文字符之间的空白
RE_SPACE_BETWEEN_WORDS_TYPE_3 = re.compile("(?<=\W)[ ]+(?=\w)")     # 中文字符、英文字符之间的空白
RE_SPACE_BETWEEN_NON_WORDS = re.compile("(?<=\W)[ ]+(?=\W)")        # 非英文字符间的空白

# HTML 标签
RE_TAG = re.compile("<[\s\S]*?>", re.I)
RE_IMG = re.compile(u"<img[\s\S]*?>", re.I)
RE_COMM = re.compile("<!--[\s\S]*?-->", re.I)
RE_SCRIPT, RE_STYLE, RE_LINK = [
    re.compile(u"<{0}.*?>([\s\S]*?)</{0}[ ]*>".format(i), re.I) for i in ("script", "style", "link")]
RE_COMMON_TAGS = [RE_COMM, RE_SCRIPT, RE_STYLE, RE_LINK, RE_IMG]
