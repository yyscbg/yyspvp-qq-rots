# -*- coding:utf-8 -*-
"""
@Time: 2022/12/2下午2:31
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: __init__.py.py
@Detail: 
"""

import re
from nonebot import on_command
from nonebot import get_driver, logger
from nonebot.matcher import Matcher
from nonebot.adapters import Message, Event
from nonebot.adapters.onebot.v11 import MessageSegment, GroupMessageEvent, Bot

from utils.yys_proxy import ProxyTool
from utils.common_functions import select_sql
from .yys_spider import get_equip_detail
from .yys_parse import get_speed_info

config = get_driver().config.dict()

# yyspvp_accept_group = config.get('yyspvp_accept_group', [])
yyspvp_accept_group = ["569426079"]


async def group_checker(event: Event) -> bool:
    """自定义群组规则"""
    # 匹配群组id
    group_id = ""
    flag = False
    # user_id = event.get_user_id()
    _group = re.findall("group_(\\d+)_", event.get_session_id())
    if _group:
        group_id = _group[0]
    if group_id in yyspvp_accept_group:
        flag = True
    return flag


yycbg_level = on_command("yyscbg_search", rule=group_checker, aliases={'藏宝阁', 'cbg', 'Cbg', "CBG"}, priority=0)


@yycbg_level.handle()
async def server_code_search(bot: Bot, event: GroupMessageEvent):
    try:
        game_ordersn = re.findall("\\d{15}-\\d{1,2}-[0-9A-Z]+", str(event.message))[0]
        print(game_ordersn)
    except Exception as e:
        print(e)
        _prompt = "代理出错，请重试"
    else:
        _prompt = parse_yyscbg_url(game_ordersn)
        await bot.send(event, message=_prompt, at_sender=True)


def get_infos(game_ordersn):
    proxy_handle = ProxyTool()
    while True:
        proxies = proxy_handle.get_proxy()
        try:
            infos = get_equip_detail(game_ordersn, proxies=proxies, timeout=10)
            if infos:
                """{'msg': '为了您的账号安全，请登录之后继续访问！', 'status': 2, 'status_code': 'SESSION_TIMEOUT'}"""
                if infos.get('status_code') == "SESSION_TIMEOUT" or infos.get('status') == 2:
                    continue

                return infos
            else:
                return False
        except Exception as e:
            proxy_handle = ProxyTool()
            proxies = proxy_handle.get_proxy()
            print(f"{e}: 刷新代理: {proxies}")


def parse_yyscbg_url(game_ordersn=None):
    _prompt = "链接格式错误~"
    if game_ordersn:
        _num = 1
        while True:
            datas = get_infos(game_ordersn)
            if datas:
                history_price = "暂无"
                history_url = "暂无"
                datas = get_speed_info(datas)
                equip_name = datas["equip_name"]
                server_name = datas["server_name"]
                status_des = datas["status_des"]
                highlights = datas["highlights"]
                price = datas["price"]
                yuhun_buff = int(datas["yuhun_buff"])/3600/24
                yuhun_buff = str(round(yuhun_buff, 2)) + "天" if yuhun_buff > 24 else str(round(yuhun_buff, 2)) + "时"
                goyu = datas["goyu"]
                hunyu = datas["hunyu"]
                strength = datas["strength"]
                speed_infos = datas["speed_infos"]
                head_info = speed_infos["head_info"]
                mz_info = speed_infos["mz_info"]
                dk_info = speed_infos["dk_info"]
                suit_speed = datas["suit_speed"]
                sql = f"select * from yys_cbg.all_cbg_url where equip_name='{equip_name}' and server_name='{server_name}'" \
                      f"and status_des=3 and game_ordersn!='{game_ordersn}' order by create_time desc"
                print(sql)
                _history = select_sql(sql)
                if _history:
                    history_price = _history[0]["price"]
                    game_ordersn = _history[0]["game_ordersn"]
                    server_id = game_ordersn.split('-')[1]
                    history_url = "https://yys.cbg.163.com/cgi/mweb/equip/" + server_id + "/" + game_ordersn
                _prompt = f"ID: {equip_name}\n区服: {server_name}\n状态: {status_des}\n高亮文字: {highlights}\n" \
                          f"价格: {int(price)}\n历史价格: {history_price}\n历史链接：{history_url}\n" \
                          f"御魂加成: {yuhun_buff}\n勾玉: {goyu}\n魂玉: {hunyu}\n体力: {strength}\n" \
                          f"头: {get_str(head_info['value_list'])}\n尾: {get_str(mz_info['value_list'])}\n" \
                          f"{get_suit_str(suit_speed)}"
                print(_prompt)
                break
            else:
                if _num >= 3:
                    break
                _num += 1
                _prompt = "代理出错，请重试"
    return _prompt


def get_str(_array):
    return ", ".join(list(map(lambda info: f"{info['yh_type']}: {round(info['speed'], 3)}", _array)))


def get_suit_str(_array):
    return "\n".join(list(map(lambda info: f"{info['suit_name']}: {round(info['speed_sum'], 3)}", _array)))
