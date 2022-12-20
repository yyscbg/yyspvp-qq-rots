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

from configs.all_config import mysql_config
from utils.yys_proxy import ProxyTool
from utils.yys_time import get_now
from utils.common_functions import select_sql, check_sale_flag
from utils.yys_mysql import YysMysql
from .yys_spider import get_equip_detail
from .yys_parse import get_speed_info, CbgDataParser
from .yys_cal_about import *

config = get_driver().config.dict()

yyscbg_accept_group = config.get('yyscbg_accept_group', [])


async def group_checker(event: Event) -> bool:
    """自定义群组规则"""
    # 匹配群组id
    group_id = ""
    flag = False
    # user_id = event.get_user_id()
    _group = re.findall("group_(\\d+)_", event.get_session_id())
    if _group:
        group_id = _group[0]
    if group_id in yyscbg_accept_group:
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
            infos = get_infos(game_ordersn)
            dmg_str = get_dmg_str(infos)
            if infos and not isinstance(infos, str):
                history_price = "暂无"
                history_url = "暂无"
                server_id = game_ordersn.split('-')[1]
                current_url = "https://yys.cbg.163.com/cgi/mweb/equip/" + server_id + "/" + game_ordersn
                datas = get_speed_info(infos)
                if not datas:
                    if _num >= 3:
                        break
                    _num += 1
                    _prompt = "代理出错，请重试"
                    continue
                equip_name = datas["equip_name"]
                server_name = datas["server_name"]
                status_des = datas["status_des"]
                highlights = datas["highlights"]
                price = datas["price"]
                yuhun_buff = cal_time(datas["yuhun_buff"])
                goyu = datas["goyu"]
                hunyu = datas["hunyu"]
                strength = datas["strength"]
                speed_infos = datas["speed_infos"]
                head_info = speed_infos["head_info"]
                mz_info = speed_infos["mz_info"]
                dk_info = speed_infos["dk_info"]
                suit_speed = datas["suit_speed"]
                create_time = datas["create_time"]
                fengzidu = datas["fengzidu"]
                yard_num = len(datas['yard_list'])
                yard_prefix = f"（{yard_num}）" if yard_num else ''
                yard_str = "、 ".join(datas["yard_list"])
                dc_str = "、 ".join(datas["dc_list"])
                dc_num = len(datas["dc_list"])
                dc_prefix = f"（{dc_num}）" if dc_num else ''
                shouban_str = "、 ".join(datas["shouban_list"])
                shouban_num = len(datas["shouban_list"])
                shouban_prefix = f"（{shouban_num}）" if shouban_num else ''
                sql = f"""select * from yys_cbg.all_cbg_url where equip_name="{equip_name}" and server_name='{server_name}'""" \
                      f""" and status_des=3 and game_ordersn!='{game_ordersn}' and create_time<='{create_time}' """ \
                      f"""order by create_time desc"""
                print(sql)
                _history = select_sql(sql)
                if _history:
                    history_price = _history[0]["price"]
                    old_game_ordersn = _history[0]["game_ordersn"]
                    server_id = old_game_ordersn.split('-')[1]
                    history_url = "https://yys.cbg.163.com/cgi/mweb/equip/" + server_id + "/" + old_game_ordersn

                # 不存在入库
                search_res = select_sql(f"select * from yys_cbg.all_cbg_url where game_ordersn='{game_ordersn}'")
                if not search_res:
                    parse = CbgDataParser()
                    payload = parse.cbg_parse(infos, is_yuhun=False)
                    payload["status_des"] = check_sale_flag(payload["status_des"])
                    infos = {
                        "game_ordersn": game_ordersn,
                        "status_des": payload["status_des"],
                        "new_roleid": payload["new_roleid"],
                        "equip_name": payload["equip_name"],
                        "server_name": payload["server_name"],
                        "create_time": payload["create_time"],
                        "price": payload["price"],
                        "update_time": get_now(),
                    }
                    print(f"入库成功：{game_ordersn}")
                    hope_update_list = ["price", "status_des", "equip_name", "server_name", "create_time",
                                        "new_roleid"]
                    update_table_to_all_cbg_url([infos], hope_update_list)

                _prompt = f"\n当前链接：{current_url}\nID: {equip_name}\n区服: {server_name}\n状态: {status_des}\n" \
                          f"高亮文字: {highlights}\n" \
                          f"价格: {int(price)}\n历史价格: {history_price}\n历史链接：{history_url}\n" \
                          f"御魂加成: {yuhun_buff}\n勾玉: {goyu}\n魂玉: {hunyu}\n体力: {strength}\n" \
                          f"============================\n" \
                          f"满速个数: {datas['full_speed_num']}\n" \
                          f"头: {get_str(head_info['value_list'])}\n尾: {get_str(mz_info['value_list'])}\n" \
                          f"抵抗: {get_str(dk_info['value_list'])} \n{get_suit_str(suit_speed, True)}\n" \
                          f"============================\n" \
                          f"风姿度: {fengzidu}\n" \
                          f"庭院{yard_prefix}: {yard_str}\n典藏{dc_prefix}: {dc_str}\n" \
                          f"手办框{shouban_prefix}: {shouban_str}\n崽战框: {datas['zaizhan_str']}\n" \
                          f"氪金: {datas['kejin_str']}\n" \
                          f"============================\n" \
                          f"输出御魂：{dmg_str}"
                break
            else:
                if _num >= 3:
                    break
                _num += 1
                _prompt = "代理出错，请重试"
    return _prompt


def update_table_to_all_cbg_url(list_values, hope_update_list):
    """更新入库"""
    mysql_obj = YysMysql(cursor_type=True)
    mysql_handle = mysql_obj.sql_open(mysql_config)
    mysql_obj.insert_Or_update_mysql_record_many_new(
        handle=mysql_handle,
        db_table="yys_cbg.all_cbg_url",
        list_values=list_values,
        hope_update_list=hope_update_list
    )
    mysql_obj.sql_close(mysql_handle)


def cal_time(n_seconds: int):
    """
    计算加成时间
    :param n_seconds: 秒
    :return:
    """
    hour = round(n_seconds / 3600, 2)
    if hour >= 24:
        return str(round(hour / 24, 1)) + "天"
    else:
        return str(hour) + "时"


def get_str(_array):
    return ", ".join(list(map(lambda info: f"{info['yh_type']}: {round(info['speed'], 3)}", _array)))


def get_pos_str(items):
    """各个位置字符串"""
    return "\n" + ", ".join(
        list(map(lambda item: f"p{item['pos']}-{item['yh_type']}:{round(item['speed'], 2)}", items)))


def get_suit_str(_array, is_detail=False):
    """套装字符串"""
    if is_detail:
        return "\n".join(list(map(lambda info: f"{info['suit_name']}: {round(info['speed_sum'], 3)}"
                                               f"{get_pos_str(info['speed_list']) if info['suit_name'] == '除散件外独立招财' else ''}",
                                  _array)))
    return "\n".join(list(map(lambda info: f"{info['suit_name']}: {round(info['speed_sum'], 3)}", _array)))


def get_dmg_str(json_data):
    try:
        data_yuhun_std = extract_data_cbg(json_data)
        optimize_data_for_cal(data_yuhun_std)
        dmg_yuhun_list = pick_dmg_yuhun(
            data_yuhun_std,
            common_score=8,  # 普通8分
            special_score=10  # 逢魔皮10分
        )
        _str = ""
        for dmg_yuhun in dmg_yuhun_list:
            score_dmg = dmg_yuhun['score_dmg']  # 分数
            master_attr = dmg_yuhun['attrs']['main']['attr']  # 主属性
            _items = format_dmg_yuhun_str(dmg_yuhun['subs2'])
            sgl2_str = f"固有{list(dmg_yuhun['sgl2'].keys())[0]}" if dmg_yuhun['kind'] in ['荒骷髅', '鬼灵歌伎',
                                                                                           '土蜘蛛', '地震鲶',
                                                                                           '蜃气楼'] else ""
            # print(sgl2_str)
            _str += f"\n【{dmg_yuhun['pos']}号位 {master_attr} {dmg_yuhun['kind']} {score_dmg}分 {sgl2_str}】\n" \
                    + "\n".join(_items)
    except Exception as e:
        print(e)
    return _str
