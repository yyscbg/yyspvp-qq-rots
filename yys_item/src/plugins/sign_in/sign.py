# -*- coding:utf-8 -*-
"""
@Time: 2022/11/28下午2:21
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: login.py
@Detail: 签到模块
"""

from utils.yys_time import get_now_date, get_now
from utils.common_functions import select_sql, update_sql


def search_login_status(qq, score=10):
    """
    查询签到状态
    :param qq: qq号
    :return:
    """
    send = "签到失败，系统出错，请联系管理员！"
    sql = f"select * from qq_robots.user_infos where qq='{qq}'"
    result = select_sql(sql)
    if result:
        sign_date = result[0]["sign_date"]
        if str(get_now_date()) == sign_date:
            send = '你已经签到过了，明天再来吧'
    else:
        user_sign_in(qq, score)
        send = f'签到成功，获得{score}积分'
    return send


def user_sign_in(qq, score, sign_date=None):
    """
    用户签到
    :param qq: qq号
    :param score: 积分
    :param sign_date: 签到日期
    :return:
    """
    if sign_date is None:
        sign_date = str(get_now_date())
    update_time = str(get_now())
    sql = f"INSERT INTO qq_robots.user_infos (qq, sign_date, score, sign_num, update_time) " \
          f"VALUES('{qq}', '{sign_date}', {score}, 1, '{update_time}') ON DUPLICATE KEY UPDATE " \
          f"qq='{qq}', score=VALUES(score)+{score}, sign_num=VALUES(sign_num)+1, sign_date='{sign_date}', " \
          f"update_time='{update_time}';"
    update_sql(sql)
