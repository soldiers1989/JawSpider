# coding:utf-8
import MySQLdb
import time
import sys
import datetime
import xlwt
import os
from pyhive import hive
import requests
import json

reload(sys)
sys.setdefaultencoding('utf8')

# local_host = MySQLdb.connect(
#                 host='192.168.1.106',
#                 user='root',
#                 passwd='icekredit-MYSQL2',
#                 db ='icekredit_platform',
#                 charset = 'utf8'
#             )
test_db = MySQLdb.connect(
    host='rm-bp16bqq3yg948i461.mysql.rds.aliyuncs.com',
    user='zhouciyi',
    passwd='Zhouciyi_2017',
    db='zhouciyi',
    charset='utf8'
)
# all_data_hive =hive.connect(
#     host='cd.icekredit.com',
#     username='zgq',
#     password='zgq_fjz189dufjdzklsur89qrojf88',
#     auth='LDAP'
# )
all_data_hive = hive.connect(
    host='10.23.0.103',
    username='test',
    password='test',
    auth='LDAP'
)
online_db = MySQLdb.connect(
    host='rr-bp10h27e605za2kf2o.mysql.rds.aliyuncs.com',
    user='ick_admin',
    passwd='yueyue1228',
    db='gouchao',
    charset='utf8'
)

hive_cur = all_data_hive.cursor()
cur = test_db.cursor()
online_cur = online_db.cursor()

start_date = '2018-07-01'
end_date = '2018-08-01'


# cur = local_host.cursor()

# hive_cur.execute('set io.sort.mb=10')
# hive_cur.execute('set hive.map.aggr=true')
# hive_cur.execute('set hive.groupby.skewindata=true')


def get_user_service_info(cur):
    get_service_sql = 'select *,(SELECT rule_desc from use_count_rule where rule_id = use_count_config.rule) from use_count_config ORDER by maneger,user_name'

    cur.execute(get_service_sql)

    user_info_list = []
    for i in cur:
        # print i
        user_info = {}
        # print i
        user_info['name'] = i[2]
        user_info['manager'] = i[6]
        user_info['service_name'] = i[5]
        user_info['rule'] = i[7]
        user_info['rule_desc'] = i[12]
        user_info['database'] = i[8]
        user_info['table_name'] = i[9]
        user_info['uid'] = i[1]
        user_info['id'] = i[4]
        user_info['id_type'] = i[3]
        user_info['hit'] = i[10]
        user_info['time_name'] = i[11]
        user_info['all_count'] = 0
        user_info['hit_count'] = ''
        user_info_list.append(user_info)
    return user_info_list


def get_person_pipeline_count(cur, start_date, end_date):
    get_person_pipeline_count_sql = '''select
    uid,sid,count(1),
    count(CASE WHEN get_json_object(result,"$.ConvertDeviceScore.bj_score")BETWEEN 300 and 850 or get_json_object(result,"$.DeviceScoreDetail.bj_score")BETWEEN 300 and 850 THEN 1 ELSE NULL END ),
    count(CASE WHEN get_json_object(result,"$.RepaymentAbility.bj_score")BETWEEN 300 and 850 or get_json_object(result,"$.LargeAmountHuiYan.result.bj_score")BETWEEN 300 and 850 or get_json_object(result,"$.GeneralRepaymentScore.GeneralRepaymentScore.bj_score")BETWEEN 300 and 850 THEN 1 ELSE NULL END ),
    count(CASE WHEN get_json_object(result,"$.BlackListIntegration.hit_status")='01' or get_json_object(result,"$.BlackList.hit_status")='01' THEN 1 ELSE NULL END )
    from person_pipeline
    where create_date_partition >= '%s' and create_date_partition <'%s'
    group by uid,sid
        ''' % (start_date, end_date)
    show_table_sql = 'show tables'
    cur.execute(get_person_pipeline_count_sql)
    person_pipeline_count_list = []
    for i in cur:
        person_pipeline_count = {}
        person_pipeline_count['uid'] = i[0]
        person_pipeline_count['sid'] = i[1]
        person_pipeline_count['count'] = i[2]
        person_pipeline_count['huomou'] = i[3]
        person_pipeline_count['huiyan'] = i[4]
        person_pipeline_count['Blacklist'] = i[5]
        person_pipeline_count_list.append(person_pipeline_count)
        # if person_pipeline_count['uid'] == 304 and person_pipeline_count['sid'] == 1642:
        #     print person_pipeline_count
    return person_pipeline_count_list


def get_mobilerealname_count(cur, start_date, end_date, uid, sid, hit):
    CMCC_list = [
        134, 135, 136, 137, 138, 139, 150, 151, 152, 157, 158, 159, 182, 183, 184, 188, 187, 147, 178
    ]
    CT_list = [130, 131, 132, 155, 156, 186, 185, 176, 175]
    CU_list = [133, 153, 180, 181, 189, 177, 173]

    if hit == "0":
        get_mobilerealname_count_sql = '''
        select
        phone
        from person_pipeline
        where create_date_partition >= '%s' and create_date_partition <'%s' and uid = %s and sid = %s
        ''' % (start_date, end_date, uid, sid)
    else:
        get_mobilerealname_count_sql = '''
        select
        a.phone
        from (
            SELECT DISTINCT phone,name,id
            from person_pipeline
            where create_date_partition >= '%s' and create_date_partition <'%s' and uid = %s and sid = %s and get_json_object(trans_json,"$.mobileAuth.response_code")="00"
        ) a
        ''' % (start_date, end_date, uid, sid)

    cur.execute(get_mobilerealname_count_sql)
    phone_list = []
    for i in cur:
        phone_list.append(i[0])
    phone_list = json.loads(request_hive_aes(phone_list))['data']
    CMCC_count = 0
    CT_count = 0
    CU_count = 0
    for i in phone_list:
        try:
            # print i[0:3]
            if int(i[0:3]) in CMCC_list:
                CMCC_count += 1
            elif int(i[0:3]) in CT_list:
                CT_count += 1
            elif int(i[0:3]) in CU_list:
                CU_count += 1
            else:
                print i
                CMCC_count += 1
        except:
            print i
            CMCC_count += 1
    # print CMCC_count,CU_count,CT_count
    return "移动%s,联通%s,电信%s" % (
        CMCC_count, CU_count, CT_count
    )


def get_blacklist_hit_count(cur, start_date, end_date, uid, sid):
    get_blacklist_hit_count_sql = '''
    select
    count(CASE WHEN get_json_object(result,"$.BlackListIntegration.response_resource")='00' THEN 1 ELSE NULL END ),
    count(CASE WHEN get_json_object(result,"$.BlackListIntegration.response_resource")='01' THEN 1 ELSE NULL END ),
    count(CASE WHEN get_json_object(result,"$.BlackListIntegration.response_resource")='02' THEN 1 ELSE NULL END ),
    count(CASE WHEN get_json_object(result,"$.BlackListIntegration.response_resource")='03' THEN 1 ELSE NULL END ),
    count(CASE WHEN get_json_object(result,"$.BlackListIntegration.response_resource")='04' THEN 1 ELSE NULL END )
    from person_pipeline
    where create_date_partition >= '%s' and create_date_partition <'%s' and uid = %s and sid = %s
        ''' % (start_date, end_date, uid, sid)
    cur.execute(get_blacklist_hit_count_sql)
    blacklist_count = cur.fetchone()
    return "本地%s,闪银%s,前海%s,甄视%s,万达%s" % (
        blacklist_count[0],
        blacklist_count[1],
        blacklist_count[2],
        blacklist_count[3],
        blacklist_count[4]
    )


def rule_9(cur, start_date, end_date, uid, sid):
    # 维氏盾驾驶证、行驶证附加核查
    sql = "select spider_uuid from dc_cost_data where uid = %s and pid = %s and `time` BETWEEN '%s' and '%s' " % (
    uid, sid, start_date + ' 00:00:00', end_date + ' 00:00:00')
    cur.execute(sql)
    uuid_list = []
    for i in cur:
        uuid = i[0]
        uuid_list.append(uuid)
    # print len(uuid_list)
    uuid_tuple = json.dumps(tuple(uuid_list)).replace('[', '(').replace(']', ')')
    sql3 = "select count(1) from crawler_common where uuid in " + uuid_tuple + " and result_json  like '%\"response_code\":\"00\"%'"

    cur.execute(
        sql3
    )
    count_info = {
        'all': len(uuid_list),
        'hit': str(cur.fetchone()[0])
    }

    return count_info


def rule_6(cur, start_date, end_date, uid, sid):
    # 数据中心黑名单命中
    sql = "select spider_uuid from dc_cost_data where uid = %s and pid = %s and `time` BETWEEN '%s' and '%s' " % (
    uid, sid, start_date + ' 00:00:00', end_date + ' 00:00:00')
    cur.execute(sql)
    uuid_list = []
    for i in cur:
        uuid = i[0]
        uuid_list.append(uuid)
    # print len(uuid_list)
    uuid_tuple = json.dumps(tuple(uuid_list)).replace('[', '(').replace(']', ')')
    sql3 = "select count(1) from crawler_common where uuid in " + uuid_tuple + " and result_json REGEXP '\"count\":\"[1-9]\"'"

    cur.execute(
        sql3
    )
    count_info = {
        'all': len(uuid_list),
        'hit': str(cur.fetchone()[0])
    }

    return count_info


def rule_8(cur, start_date, end_date, uid, sid):
    count_info = {
    }
    sql = "select count(1) from dc_cost_data where uid = %s and pid = %s and partition_day >= '%s' and partition_day <'%s' " % (
    uid, sid, start_date, end_date)
    cur.execute(sql)
    count_info['all'] = cur.fetchone()[0]
    sql = "select count(1) from dc_cost_data where uid = %s and pid = %s and partition_day >= '%s' and partition_day <'%s'and (response_code = '00' or response_code is null)" % (
    uid, sid, start_date, end_date)
    cur.execute(sql)
    count_info['hit'] = str(cur.fetchone()[0])
    return count_info


def rule_0_dc(cur, start_date, end_date, uid, sid):
    count_info = {
    }
    sql = "select count(1) from dc_cost_data where uid = %s and pid = %s and `time` BETWEEN '%s' and '%s' " % (
    uid, sid, start_date + ' 00:00:00', end_date + ' 00:00:00')
    cur.execute(sql)
    return str(cur.fetchone()[0])


def rule_11_dc(cur, start_date, end_date, uid, sid):
    count_info = {
    }
    sql = "select count(1) from dc_cost_data where uid = %s and pid = %s and `time` BETWEEN '%s' and '%s' " % (
    uid, sid, start_date + ' 00:00:00', end_date + ' 00:00:00')
    cur.execute(sql)
    count_info['all'] = cur.fetchone()[0]
    sql = "select count(DISTINCT query) from dc_cost_data where uid = %s and pid = %s and `time` BETWEEN '%s' and '%s' " % (
    uid, sid, start_date + ' 00:00:00', end_date + ' 00:00:00')
    cur.execute(sql)
    count_info['hit'] = cur.fetchone()[0]
    return count_info


def rule_mingjian(cur, start_date, end_date, uid, sid):
    get_mingjian_hit_count_sql = '''
    select
    count(CASE WHEN get_json_object(result,"$.bj_score") between 299 and 851 THEN 1 ELSE NULL END ),
    from person_pipeline
    where create_date_partition >= '%s' and create_date_partition <'%s' and uid = %s and sid = %s
        ''' % (start_date, end_date, uid, sid)
    cur.execute(get_mingjian_hit_count_sql)
    return str(cur.fetchone[0])


def get_all():
    user_info_list = get_user_service_info(cur)
    person_pipeline_count_list = get_person_pipeline_count(hive_cur, start_date, end_date)
    print person_pipeline_count_list

    for user_info in user_info_list:
        print user_info['uid'], user_info['id_type'], user_info['id'], user_info['hit']
        if user_info['id_type'] == 'sid':
            for person_pipeline_count in person_pipeline_count_list:
                if user_info['uid'] == person_pipeline_count['uid'] and user_info['id'] == person_pipeline_count['sid']:
                    user_info['all_count'] = person_pipeline_count['count']
                    if str(person_pipeline_count['huomou']) != '0':
                        user_info['hit_count'] += '火眸命中%s,' % str(person_pipeline_count['huomou'])
                    if str(person_pipeline_count['huiyan']) != '0':
                        user_info['hit_count'] += '慧眼命中%s,' % str(person_pipeline_count['huiyan'])
                    if str(user_info['uid']) != '67':
                        if str(person_pipeline_count['Blacklist']) != '0':
                            user_info['hit_count'] += '黑名单命中%s,' % str(person_pipeline_count['Blacklist'])
                    else:
                        if str(user_info['id']) == '1505':
                            user_info['hit_count'] += get_blacklist_hit_count(hive_cur, start_date, end_date, 67, 1505)
                    if str(user_info['rule']) == '10':
                        user_info['hit_count'] += get_mobilerealname_count(hive_cur, start_date, end_date,
                                                                           user_info['uid'], user_info['id'],
                                                                           user_info['hit'])
                    if str(user_info['uid']) == 269 and str(user_info['id']) == 40002:
                        count_info = rule_0_dc(online_cur, start_date, end_date, user_info['uid'], 1343)
                        user_info['hit_count'] = count_info
                    if str(user_info['id']) in (110002, 110001):
                        count_info = rule_mingjian(online_cur, start_date, end_date, user_info['uid'], 1343)
                        user_info['hit_count'] = count_info
                    # if str(user_info['uid'])=='304' and str(user_info['id'])=='1642':
                    #     user_info['hit_count']+=get_mobilerealname_count(hive_cur,start_date,end_date,304,1642,1)
                    # if str(user_info['uid'])=='345' and str(user_info['id'])=='1797':
                    #     user_info['hit_count']+=get_mobilerealname_count(hive_cur,start_date,end_date,354,1797,0)
                    if str(user_info['uid']) == '269' and str(user_info['id']) == '40002':
                        user_info['hit_count'] += rule_8(hive_cur, start_date, end_date, 269, 1343)['hit']
        elif user_info['id_type'] == 'pid':
            if str(user_info['rule']) == '6':
                try:
                    count_info = rule_6(online_cur, start_date, end_date, user_info['uid'], user_info['id'])
                    user_info['all_count'] = count_info['all']
                    user_info['hit_count'] = count_info['hit']
                except:
                    pass
            elif str(user_info['rule']) == '8':
                try:
                    count_info = rule_8(online_cur, start_date, end_date, user_info['uid'], user_info['id'])
                    user_info['all_count'] = count_info['all']
                    user_info['hit_count'] = count_info['hit']
                except:
                    pass
            elif str(user_info['rule']) == '9':
                try:
                    count_info = rule_9(online_cur, start_date, end_date, user_info['uid'], user_info['id'])
                    user_info['all_count'] = count_info['all']
                    user_info['hit_count'] = count_info['hit']
                except:
                    pass
            elif str(user_info['rule']) == '11':
                try:
                    count_info = rule_11_dc(online_cur, start_date, end_date, user_info['uid'], user_info['id'])
                    user_info['all_count'] = count_info['all']
                    user_info['hit_count'] = count_info['hit']
                except:
                    pass
            else:
                count_info = rule_0_dc(online_cur, start_date, end_date, user_info['uid'], user_info['id'])
                user_info['all_count'] = count_info

    print json.dumps(user_info_list)

    file = open(u'201807online_hive使用情况.csv', 'w')
    file.write('用户名\t客户经理\t服务名\t收费规则\t查询数量\t命中数量\n'.encode('gbk'))
    for user_info in user_info_list:
        file.write(
            str(user_info['name']).encode('gbk') + '\t' +
            str(user_info['manager']).encode('gbk') + '\t' +
            str(user_info['service_name']).encode('gbk') + '\t' +
            str(user_info['rule_desc']).encode('gbk') + '\t' +
            str(user_info['all_count']).encode('gbk') + '\t' +
            str(user_info['hit_count']).encode('gbk') + '\n'
        )


## 对手机号解密
def request_hive_aes(phone_list):
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "mod": "aes_decrypt",
        "data": phone_list
    }
    response = requests.post("http://cd.icekredit.com:10001", headers=headers, data=json.dumps(data))
    return response.content


# get_person_pipeline_count(hive_cur,start_date,end_date)
print get_mobilerealname_count(hive_cur, start_date, end_date, 304, 1642, "0")

# print get_blacklist_hit_count(hive_cur,start_date,end_date,67,1505)
# print json.dumps(get_user_service_info(cur))
# print rule_9(online_cur,start_date,end_date,258,1347)
#

get_all()

# print  rule_8(hive_cur,start_date,end_date,269,1343)
# list = []
# for i in list:
#     print json.loads(i)


#    count(CASE WHEN get_json_object(trans_json,"$.mobileAuth.type")="CMCC" THEN 1 ELSE NULL END )
