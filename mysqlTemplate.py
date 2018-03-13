# -*- coding: UTF-8 -*-
import MySQLdb
import sys


class mysqlTemplate:

    def __init__(self):
        # 打开数据库连接
        self.db = MySQLdb.connect("rm-bp11towre3n815e78o.mysql.rds.aliyuncs.com",
                                  "crawler_2",
                                  "Crawler_ICK_2017",
                                  "ktgg_test",
                                  charset="utf8"
                                  )

        # 使用cursor()方法获取操作游标
        self.cursor = self.db.cursor()
        self.insertSql = ""

    # 使用execute方法执行SQL语句
    def insertktggList(self, obj):
        self.insertSql = "INSERT INTO ktgg (no, created_at, gonggao_id, gonggao, fayuan, fating, kaitingriqi, anhao, anyou, chengban, zhushen, yuangao, beigao, dangshiren,qita,sheng,dangshirenjx,danshirenjx_flag) VALUES "

        isfirst = True
        for item in obj:
            if isfirst:
                self.insertSql += "('" + item.no + "','" + item.created_at + "','" + item.gonggao_id + "','" + \
                                  item.gonggao + "','" + item.fayuan + "','" + item.fating + "','" + item.kaitingriqi + \
                                  "','" + item.anhao + "','" + item.anyou + "','" + item.chengban + "','" + item.zhushen \
                                  + "','" + item.yuangao + "','" + item.beigao + "','" + item.dangshiren + "','" + item.qita + "','" + item.sheng+ "','" + item.dangshirenjx + "','" + item.dangshirenjx_flag + "')"
                isfirst = False
            else:
                self.insertSql += ",('" + item.no + "','" + item.created_at + "','" + item.gonggao_id + "','" + \
                                  item.gonggao + "','" + item.fayuan + "','" + item.fating + "','" + item.kaitingriqi + \
                                  "','" + item.anhao + "','" + item.anyou + "','" + item.chengban + "','" + item.zhushen \
                                  + "','" + item.yuangao + "','" + item.beigao + "','" + item.dangshiren + "','" + item.qita + "','"+ item.sheng +"','" + item.dangshirenjx + "','" + item.dangshirenjx_flag + "')"
        print(self.insertSql)
        # self.cursor.execute(self.insertSql)
        # self.db.close()

    def insertLog(self, obj):
        self.insertSql = "INSERT  into log (node_id, no, pid, level, cate, msg)VALUES "
        self.insertSql += "('" + obj.node_id + "','" + obj.no + "','" + obj.pid + "','" + obj.level + "','" + obj.cate + "','" + obj.msg + "')"
        print(self.insertSql)
        self.cursor.execute(self.insertSql)
        self.db.close()

    def insertKtgg(self, item):
        self.insertSql = "INSERT INTO ktgg (no, created_at, gonggao_id, gonggao, fayuan, fating, kaitingriqi, anhao, anyou, chengban, zhushen, yuangao, beigao, dangshiren,qita,sheng,dangshirenjx,dangshirenjx_flag) VALUES "

        self.insertSql += "('" + item.no + "','" + item.created_at + "','" + item.gonggao_id + "','" + \
                                  item.gonggao + "','" + item.fayuan + "','" + item.fating + "','" + item.kaitingriqi + \
                                  "','" + item.anhao + "','" + item.anyou + "','" + item.chengban + "','" + item.zhushen \
                                  + "','" + item.yuangao + "','" + item.beigao + "','" + item.dangshiren + "','" + item.qita + "','" + item.sheng + "','" + item.dangshirenjx + "','" + item.dangshirenjx_flag + "')"
        # self.insertSql = self.insertSql.decode(encoding="utf-8", errors="ignore")
        print self.insertSql
        self.cursor.execute(self.insertSql)
        self.db.commit()

    def queryCountBy_gonggaoid_and_no(self, gonggaoid, no):
        self.insertSql = "SELECT count(1) FROM ktgg WHERE no=" + str(no) + " AND gonggao_id='" + str(gonggaoid) + "'"
        try:
            # 执行SQL语句
            self.cursor.execute(self.insertSql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
            return results[0][0]

        except:
            print "Error: unable to fecth data"
    def release(self):
        self.db.close()
# 使用 fetchone() 方法获取一条数据
# data = cursor.fetchone()


# 关闭数据库连接
