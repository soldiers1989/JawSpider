#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""文本清洗方法"""

from text_lib import *
from escape import remove_escape

__author__ = "chiachi"


def clean_text(s, leave_space_in_non_words=False):
    """
    文本清洗方法，适合简单文本（如不包含 HTML 标签）
    :param s:                           待清洗字符串
    :param leave_space_in_non_words:    是否保留非英文中的空格，默认不保留（如 `今天 明天` -> `今天明天`）
    :return:

    1. 去除转义符
    2. 删除 `\t` 等空白字符
    3. 清除连续的空格以及换行符，但保留了换行符 `\n`
    """
    if isinstance(s, str):
        s = unicode(s)
    replacement = " " if leave_space_in_non_words else ""
    s = remove_escape(s).translate(SBC_DICT).translate(NL_DICT).translate(SPACE_DICT).strip()
    s = re.sub("\n+", "\n", RE_NL.sub("\n", RE_SPACE.sub(" ", s)))
    return RE_SPACE_BETWEEN_WORDS_TYPE_1.sub(" ", RE_SPACE_BETWEEN_WORDS_TYPE_2.sub(
        " ", RE_SPACE_BETWEEN_WORDS_TYPE_3.sub(" ", RE_SPACE_BETWEEN_NON_WORDS.sub(replacement, s))))


def clean_regex_list(s, regex_list, replacement=""):
    """使用正则表达式清洗文本"""
    for process in regex_list:
        s = process.sub(replacement, s)
    return s


def trans_brackets(s):
    """英文括号 -> 中文括号"""
    return clean_text(s.translate(BRACKETS_DICT))


if __name__ == "__main__":
    print clean_text(u"走私、贩卖、运输、制造毒品罪　,容留他人吸毒罪　")
    print clean_text(u"Mix                                   Apple                走私、贩卖、运输、制造毒品罪　，容留他人吸毒罪　")
