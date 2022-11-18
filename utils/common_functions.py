# -*- coding:utf-8 -*-
"""
@Time: 2022/11/14上午10:27
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: common_functions.py
@Detail: 通用函数
"""

from utils.yys_mysql import YysMysql
from configs.all_config import mysql_config


def select_sql(sql, cursor_type=True):
    """mysql查询"""
    try:
        my_sql = YysMysql(cursor_type=cursor_type)
        mysql_handle = my_sql.sql_open(mysql_config)
        data = my_sql.select_mysql_record(mysql_handle, sql)
        mysql_handle.close()
        return data
    except Exception as e:
        print(e)
        return False


# from operator import itemgetter
# trends = sorted(trends,key = itemgetter('速度'),reverse = True)
def list_dict_order_by_key(list_data, key, revrese=True):
    """list中的dict按照某个key排序"""
    return sorted(list_data, key=lambda e: e[key], reverse=revrese)


def score_to_star(score):
    """斗技分数转换星星"""
    if score >= 6000:
        star = 100 + int((score - 6000) / 30)
    elif score >= 3000:
        star = int(100 - (6000 - score) / 30)
    else:
        star = score
    return star