# -*- coding: utf-8 -*-
import codecs
from os import path

## helper function:
expand = lambda b1, b2: (min(b1[0],b2[0]), max(b1[1], b2[1]))


class AnyouHelper(object):

    def __init__(self):

        f1 = path.realpath(path.dirname(__file__) + '/../../resource/anyou.txt')
        f2 = path.realpath(path.dirname(__file__) + '/../../resource/minshianyou.txt')
        with codecs.open(f1, encoding='utf8') as infile:
            self.anyou = set(line.split('|')[0] for line in infile.readlines())
        with codecs.open(f2, encoding='utf8') as infile:
            self.anyou.union(infile.readlines())
        self.anyou = sorted(list(self.anyou), key=len, reverse=True)

    def find(self, s, strict=False):
        """
        用案由库中的案由匹配字符串s中的案由部分，返回案由的边界索引
        :param s: 待匹配字符串
        :param strict: 如为False,在在成功匹配到一个案由后立即返回。如为True，会尝试匹配整个案由库，返回最大可能边界
        """
        border = None
        for anyou in self.anyou:
            start = s.find(anyou)
            if start != -1:
                new_border = (start, start + len(anyou))
                border = expand(border, new_border) if border else new_border
                if not strict:
                    return border
        if not border:
            raise Exception(u'未找到案由，请手动维护案由库: resource/anyou.txt')
        for anyou in self.anyou:
            start = s.rfind(anyou)
            if start != -1:
                new_border = (start, start + len(anyou))
                border = expand(border, new_border)
        return border

    def endswith(self, s, strict=False):
        size = None
        for anyou in self.anyou:
            if s.endswith(anyou):
                size = max(size, len(anyou)) if size else len(anyou)
                if not strict:
                    return len(s) - size, len(s)
        if size:
            return len(s) - size, len(s)
        raise Exception(u'未找到案由，请手动维护案由库: resource/anyou.txt')

    def get(self, s, strict=False, method='find'):
        # 返回字符串中的案由
        method = self.__getattribute__(method)
        border = method(s, strict)
        return s[border[0]:border[1]]

    def remove(self, s, strict=False, method='find'):
        # 返回移除字符串后的案由
        method = self.__getattribute__(method)
        border = method(s, strict)
        return s[:border[0]] + s[border[1]:]

    def lstrip(self, s, strict=False, method='find'):
        # 移除案由及案由前的部分，返回案由后的部分
        method = self.__getattribute__(method)
        border = method(s, strict)[1]
        return s[border:]

    def rstrip(self, s, strict=False, method='find'):
        # 移除案由及案由后的部分，返回案由前的部分
        method = self.__getattribute__(method)
        border = method(s, strict)[0]
        return s[:border]


# ====TEST====
def verbose_case(c, helper, strict=False, method='find'):
    print '===strict:', strict, 'method:', method, '==='
    print u'原字符串：', c
    print u'get():', helper.get(c, strict, method)
    print u'remove():', helper.remove(c, strict, method)
    print u'lstrip():', helper.lstrip(c, strict, method)
    print u'rstrip():', helper.rstrip(c, strict, method)


def test():
    helper = AnyouHelper()
    test_str = u'无锡市滨湖区人民检察院诉范育祥,樊天龙,张徐永,张阳传播淫秽物品牟利,传播淫秽物品'
    verbose_case(test_str, helper)
    verbose_case(test_str, helper, strict=True)
    verbose_case(test_str, helper, method='endswith')


if __name__ == '__main__':
    test()
