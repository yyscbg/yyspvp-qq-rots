# -*- coding:utf-8 -*-
"""
@Time: 2022/11/14上午10:27
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: common_functions.py
@Detail: 通用函数
"""
import os
import json
import requests
import hashlib
import numpy as np

from utils.yys_mysql import YysMysql
from configs.all_config import mysql_config


def get_md5(_str):
    m = hashlib.md5()
    m.update(bytes(_str, encoding='utf-8'))
    return m.hexdigest()


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


def update_sql(sql, cursor_type=True):
    """mysql插入"""
    try:
        my_sql = YysMysql(cursor_type=cursor_type)
        mysql_handle = my_sql.sql_open(mysql_config)
        my_sql.update_mysql_record(mysql_handle, sql)
        mysql_handle.close()
        return True
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


def check_platform(_type):
    """判断平台"""
    if _type == 2:
        platform_type = "安卓"
    elif _type == 1:
        platform_type = "IOS"
    else:
        platform_type = "渠道"
    return platform_type


def check_sale_flag(status_desc):
    if status_desc == "卖家取回":
        flag = 1
    elif status_desc in ["被下单", "上架中"]:
        flag = 2
    elif status_desc == "买家取走":
        flag = 3
    elif status_desc == "未上架":
        flag = 4
    else:
        flag = 0
    return flag


def sort_2D_array_by_column(arr, column_index, _sort=True):
    """
    二维数组按某一列排序
    infos = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 2],
        [10, 9, 8, 7, 6, 5, 4, 3, 4, 1, 1],
        [2, 11, 1, 10, 6, 5, 4, 3, 1, 1, 3],
    ]
    :param arr: 二维数组
    :param column_index: 某列下标索引
    :param _sort: 默认降序
    :return:
    """
    xx = np.array(arr)
    if _sort:
        result = xx[np.argsort(xx[:, column_index])][::-1]
    else:
        result = xx[xx[:, column_index].argsort()]
    return result.tolist()


def read_Or_request_json_file(fn=None, f_type=None):
    """
    读或请求配置文件
    """
    if fn is not None:
        if os.path.exists(fn):
            with open(fn, "r") as f:
                data = json.load(f)
            return data
        return []
    else:
        url = "https://s.166.net/config/bbs_yys/"
        url = url + f_type + ".json"
        return requests.get(url).json()


def get_shishen_name(shishen_json, _id):
    master_id = [10, 11, 12, 13, 14]
    master_name = ["晴明", "神乐", "八百比丘尼", "源博雅"]
    if _id not in [900, 901, 902, 903]:
        try:
            if int(_id) in master_id:
                shishen_name = master_name[master_id.index(int(_id))]
            else:
                shishen_name = shishen_json[str(_id)]["name"]
        except Exception as e:
            print(f"式神未更新：{e}")
            shishen_name = ""
        finally:
            return shishen_name
    else:
        return None
