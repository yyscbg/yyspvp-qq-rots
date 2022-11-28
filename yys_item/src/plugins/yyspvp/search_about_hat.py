# -*- coding:utf-8 -*-
"""
@Time: 2022/11/14上午9:49
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: search_records.py
@Detail: 查询帽子相关分数线
"""
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.yys_redis import YysRedis
from utils.yys_time import get_weekly_date
from utils.common_functions import list_dict_order_by_key, score_to_star, select_sql
from configs.all_config import redis_config

client = YysRedis(
    host=redis_config["host"],
    port=redis_config["port"],
    password=redis_config["password"],
    db=2
)


def get_all_server():
    """获取所有区编码"""
    sql = "SELECT yys_server, server_name FROM yys_pvp.yys_server_infos where run_flag!=-1"
    infos = select_sql(sql, False)
    server_list = [i[0] for i in infos]
    server_list.append("all")
    return server_list, infos


def get_server_name(server_code, infos):
    """获取服务器名称"""
    for info in infos:
        if info[0] == server_code:
            return info[1]


def get_month_date_time_list(_start=1, _end=5):
    """获取N个周天日期数组
    :param _start
    :param _end
    :return list
    """
    current_day = datetime.date.today()
    if current_day.weekday() == 6:
        _start = 2
        _end = 6
    return [str(get_weekly_date(i)) for i in range(_start, _end)]


def pick_rank_records(date_time):
    """从redis读取数据"""
    try:
        datas = client.read(date_time)
        if len(datas) != 0:
            return datas[0]
        return []
    except Exception as e:
        print(e)


def filter_columns(datas, column_name, column_value):
    """过滤数据
    :param datas: list数组
    :param column_name: 字段名
    :param column_value: 字段值
    :return list
    """

    def choose_column(dt):
        return dt[column_name] == column_value

    return list(filter(choose_column, datas))


def search_red_hat(date_time):
    """全区红帽子
    :param date_time: 时间
    :return int
    """
    try:
        dts = pick_rank_records(date_time)
        rts = list_dict_order_by_key(dts, "score")
        # 转换成✨
        return score_to_star(rts[:500][-1:][0]["score"])
    except Exception as e:
        print(e)
        return False


def search_month_red_hat(date_time=None):
    """查询一个月红帽子"""
    datas = []
    if date_time is None:
        date_time_list = get_month_date_time_list()
        print(date_time_list)
        with ThreadPoolExecutor(max_workers=4) as executor:
            all_tasks = [executor.submit(search_red_hat, date_time) for date_time in date_time_list]
            for future in as_completed(all_tasks):
                datas.append(future.result())
    else:
        datas(search_red_hat(date_time))
    return datas


def search_blue_hat(date_time, column_name, column_value, datas=None):
    """某区蓝帽子
    :param date_time: 时间
    :param column_name: 字段名
    :param column_value: 字段值
    :param datas: 数据,默认None
    :return int
    """
    try:
        if datas is None:
            datas = pick_rank_records(date_time)
        dts = filter_columns(datas, column_name, column_value)
        rts = list_dict_order_by_key(dts, "score")
        # 转换成✨
        return score_to_star(rts[-1:][0]["score"]), column_value
    except Exception as e:
        print(e)
        return False


def search_month_blue_hat(column_name, column_value):
    """某区蓝帽子"""
    datas = []
    date_time_list = get_month_date_time_list()
    print(date_time_list)
    with ThreadPoolExecutor(max_workers=4) as executor:
        all_tasks = [executor.submit(search_blue_hat, dtime, column_name, column_value) for dtime in date_time_list]
        for future in as_completed(all_tasks):
            datas.append(future.result()[0])
    return datas


def search_all_server_blue_hat(date_time):
    """各服蓝帽子线"""
    sql = "SELECT yys_server, server_name FROM yys_pvp.yys_server_infos where run_flag!=-1"
    infos = select_sql(sql)
    records = pick_rank_records(date_time)
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        all_tasks = [executor.submit(search_blue_hat, date_time, "yys_server", info["yys_server"], records) for info in
                     infos]
        for future in as_completed(all_tasks):
            result = future.result()
            results.append({"server": result[1], "score": result[0]})

    datas = []
    for rt in results:
        for info in infos:
            if info["yys_server"] == rt["server"]:
                datas.append({"server_name": info["server_name"], "score": rt["score"]})
                break
    return datas


def test():
    # 某区蓝帽子
    column_name = "yys_server"
    column_value = "10009"
    dts = search_month_blue_hat(column_name, column_value)
    print(dts)
    # 全服红帽子
    dts = search_month_red_hat()
    print(dts)
    # 某周全服蓝帽子
    date_time = "2022-11-13"
    dts = search_all_server_blue_hat(date_time)
    dts = list_dict_order_by_key(dts, "score")
    print(dts)


if __name__ == '__main__':
    # test()
    a, infos = get_all_server()
    for info in infos:
        print(info)
