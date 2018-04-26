#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""解析 HTML 文本的基本方法"""

import logging
from lxml import etree

__author__ = "chiachi"


def build_tree(html, warnings=True):
    """
    建立 elementTree
    :param html:        HTML 源码
    :param warnings:    是否记录异常
    :return:            elementTree
    """
    if html is None:
        if warnings:
            logging.error(u"[build_tree] got `None` instead of HTML file")
        return
    try:
        return etree.HTML(html)
    except ValueError as e:
        if warnings:
            logging.error(u"[build_tree] got wrong type of input, e: %s", e)
        return
    except etree.XMLSyntaxError as e:
        if warnings:
            logging.error(u"[build_tree] parsing html failed, e: %s", e)
        return
    except Exception as e:
        if warnings:
            logging.error(u"[build_tree] got unknown error, e: %s", e)
        return


def _check_xpath(tree, xpath_expr, verify_str=u"", warnings=True):
    """
    校验 xpath 字段是否存在，以及特定标识字符是否存在于标签中
    :param tree:        element tree
    :param xpath_expr:  xpath 表达式
    :param verify_str:  校验字符
    :param warnings:    是否记录异常
    :return:            boolean
    """
    try:
        element_result = tree.xpath(xpath_expr)
    except (etree.XPathEvalError, etree.XPathSyntaxError) as e:
        if warnings:
            logging.error(u"[check_xpath] xpath extract failed, xpath_expr: %s, e: %s", xpath_expr, e)
        return False
    except Exception as e:
        if warnings:
            logging.error(u"[check_xpath] got unknown error, xpath_expr: %s, e: %s", xpath_expr, e)
        return False
    if not element_result:
        return False

    if verify_str:
        # 存在校验字符时，仅在该字符存在于目标字符串时返回 True
        return True if verify_str in etree.tounicode(element_result[0]) else False
    else:
        # 不存在校验字符时，仅在获取的结果 list 不为空时返回 True
        return True if element_result else False


def get_xpath(tree, target_xpath_expr, verify_xpath_expr="", verify_str=u"", multi=False, warnings=True):
    """
    提取 xpath 字段数据
    :param tree:                element tree
    :param target_xpath_expr:   xpath 表达式
    :param verify_xpath_expr:   校验 xpath 表达式
    :param verify_str:          校验字符
    :param multi:               是否取出多项数据
    :param warnings:            是否记录异常
    :return:                    string / list
    """
    if verify_xpath_expr:
        if _check_xpath(tree, verify_xpath_expr, verify_str):
            # 校验成功
            if _check_xpath(tree, target_xpath_expr):
                # 存在目标标签
                return tree.xpath(target_xpath_expr) if multi else tree.xpath(target_xpath_expr)[0]
            else:
                # 不存在目标标签
                if multi:
                    return []
                return u"" if target_xpath_expr == "text()" or target_xpath_expr.endswith("/text()") else None
        else:
            # 校验失败
            if warnings:
                logging.error(u"[get_xpath] couldn't find verify_str, verify_xpath_expr: %s, verify_str: %s",
                              verify_xpath_expr, verify_str)
            return
    else:
        if _check_xpath(tree, target_xpath_expr):
            # 存在目标标签
            return tree.xpath(target_xpath_expr) if multi else tree.xpath(target_xpath_expr)[0]
        else:
            # 不存在目标标签
            if multi:
                return []
            return u"" if target_xpath_expr == "text()" or target_xpath_expr.endswith("/text()") else None


def remove_tags(tree, tags_to_remove):
    """
    移除 element tree 中的特定标签
    :param tree:            element tree
    :param tags_to_remove:  待移除标签
    :return:                修改后的 element tree
    """
    tag_list = list()
    for tag in tags_to_remove:
        tag_list.extend(tree.xpath(tag))
    for tag in set(tag_list):
        try:
            tree.remove(tag)
        except ValueError:
            tag.getparent().remove(tag)
    return tree


def get_exact_xpath(tree, potential_xpath_tags, noise_xpath_tags=None):
    """
    获取特定 xpath 标签的数据
    :param tree:                    element tree
    :param potential_xpath_tags:    可能存在目标数据的 xpath 表达式列表
    :param noise_xpath_tags:        噪音 xpath 表达式列表
    :return:                        修改后的 tree
    """
    target_xpath_tag = None
    for tag in potential_xpath_tags:
        if _check_xpath(tree, tag):
            # 存在目标标签
            target_xpath_tag = tag
            break
    if target_xpath_tag is None:
        return
    else:
        if noise_xpath_tags is None:
            return get_xpath(tree, target_xpath_tag)
        else:
            return remove_tags(get_xpath(tree, target_xpath_tag), noise_xpath_tags)


if __name__ == "__main__":
    import requests
    r = requests.get("http://news.sina.com.cn/o/2015-09-15/162032310612.shtml")
    r.encoding = "gb18030"
    _tree = build_tree(r.text)
    print etree.tounicode(get_exact_xpath(_tree, ['//div[@id="artibody"]'], ['p[@align="right"]']))
