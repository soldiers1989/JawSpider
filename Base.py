# coding=utf-8
import utils
import datetime
from mysql import connector
from mysql.connector.errors import DataError, ProgrammingError

from pyutils.cate import Cate


class Base(object):

    class Logger:
        def __init__(self, func):
            self.func = func

        def info(self, cate, msg, *args):
            self.func(msg % args, "info", cate)

        def error(self, cate, msg, *args):
            self.func(msg % args, "error", cate)

    def __init__(self, mysqlConfig=None):
        """
        :param mysqlConfig: 用于自定义数据库连接的dict
        """
        if mysqlConfig is None:
            self.log = utils.Log()
            self.db = connector.connect(**utils.getMysqlConfig())
        else:
            self.log = utils.Log(db=mysqlConfig)
            self.db = connector.connect(**mysqlConfig)
        self.logger = self.Logger(self.log.log)
        self.cursor = self.db.cursor()

    def dbHashSet(self, key, value):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO `hash` (no, key32, value256) VALUES ('%d', '%s', '%s') ON DUPLICATE KEY UPDATE value256='%s', updated_at='%s'" % (
                self.log.no, key, value, value, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        cursor.close()

    def dbHashGet(self, key, defaultValue=None):
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT value256 FROM hash WHERE no='%s' AND key32='%s'" % (self.log.no, key))
        row = cursor.fetchone()
        if row:
            return row(0)
        else:
            return defaultValue

    def dbKtggGet(self, gonggao_id):
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM ktgg WHERE no='%d' AND gonggao_id='%s'" % (self.log.no, gonggao_id))
        row = cursor.fetchone()
        return row

    def dbKtggFilterNew(self, datas, key='gonggao_id'):
        """
        根据key过滤掉datas中已存在于数据库中的案件。
        注意：如果datas中对应key有重复的value，只会保留唯一一个拥有该value的案件。
        :param datas: 由案件构成的list，每一个案件是一个dict
        :param key:
        :return: new_datas: list of datas that not in database
        """
        # 去重
        deduped_datas = {data[key]: data for data in datas}

        sql = "SELECT {0} FROM ktgg WHERE no = {1} AND {0} in ({2})".format(
            key, self.log.no, ", ".join(("%s",) * len(deduped_datas.keys())))
        self.cursor.execute(sql, deduped_datas.keys())
        exist_values = set(v[0] for v in self.cursor.fetchall())
        return [deduped_datas.get(value) for value in deduped_datas.keys() if value not in exist_values]

    def dbKtggInsert(self, data, raise_programming_error=False, raise_data_error=False):
        """
        向ktgg插入数据的默认方法， 将data自动解析为SQL语句并执行
        :param data: 可以是代表一个案件的dict，也可以是由多个案件dict构成的list
        :param raise_programming_error: 如果希望自己处理ProgrammingError，传入True
        :param raise_data_error: 如果希望自己处理DataError，传入True
        :return: 插入成功的计数
        """
        if isinstance(data, list):
            return sum(self.dbKtggInsert(d, raise_programming_error, raise_data_error) for d in data)
        keys = data.keys()
        sql = "INSERT INTO ktgg ({}) VALUES ({})".format(", ".join(keys), ", ".join(("%s",) * len(keys)))
        try:
            self.cursor.execute(sql, [data[key] for key in keys])
            return 1
        except ProgrammingError as e:
            if raise_programming_error:
                raise e
            else:
                self.logger.error(Cate.detail, e.msg)
                return 0
        except DataError as e:
            if raise_data_error:
                raise e
            else:
                self.logger.error(Cate.detail, e.msg)
                return 0

    def dbKtggInsertNew(self, data, key='gonggao_id', raise_programming_error=False, raise_data_error=False):
        """
        给定一组或一个数据，根据key判断是否为新数据，向数据库中插入新数据
        :param data: 可以是代表一个案件的dict，也可以是由多个案件dict构成的list
        :param key: 用于判断是否为新数据的字段
        :param raise_programming_error: 如果希望自己处理ProgrammingError，传入True
        :param raise_data_error: 如果希望自己处理DataError，传入True
        :return: 插入成功的计数
        """
        if not data:  # data is a empty list or None
            return 0
        if isinstance(data, dict):
            data = [data]
        return self.dbKtggInsert(
            self.dbKtggFilterNew(data, key),
            raise_programming_error,
            raise_data_error)

    def run(self):
        count = 0
        COUNT_MAX = 10
        while True:
            count += 1
            if count > COUNT_MAX:
                #这里更新失败，打update_err的log
                self.log.log('crawler failed ' + str(count) + ', exit', 'error', 'update_err')
                break
            try:
                # 这里是翻页逻辑，由于爬虫必须保证任何时候都被暴力关闭，之后重新启动都可以继续爬，所以你应该记住爬到哪里了；如果是更新模式每次应该都是从头开始爬就不用了
                # 这个记录或别的一些琐碎信息最好dbHashSet或者dbHashGet存到数据库中的hash表中中去（存数据库更好一点），如果实在要存redis的话，保存格式为`ktgg:爬虫编号_hash`或者`ktgg:爬虫编号_string`这样

                # 假设这里已经把数据爬完了，需要打update_ok的log
                if False:
                    self.log.log('crawler update success', 'info', 'update_ok')
                    break
            except Exception, e:
                msg = e.message
                self.log.log(msg, 'warning')
