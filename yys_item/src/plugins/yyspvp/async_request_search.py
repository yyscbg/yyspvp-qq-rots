# -*- coding:utf-8 -*-
"""
@Time: 2022/11/20下午1:58
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: asynv_request_search.py
@Detail:
"""
from .search_about_hat import search_month_blue_hat, search_all_server_blue_hat, search_month_red_hat


async def get_month_blue_hat(server_code: str):
    """获取一个月内特定区蓝帽子分数线"""
    return search_month_blue_hat("yys_server", server_code)


async def get_all_server_blue_hat(date_time: str):
    """获取所有区特定周蓝帽子分数线"""
    return search_all_server_blue_hat(date_time)


async def get_month_red_hat(date_time: str = None):
    """获取某周红帽子分数线"""
    return search_month_red_hat(date_time)


async def get_player_infos_card():
    """获取玩家信息卡片"""
    pass
