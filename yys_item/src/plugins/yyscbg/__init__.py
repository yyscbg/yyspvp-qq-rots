# -*- coding:utf-8 -*-
"""
@Time: 2022/12/2下午2:31
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: __init__.py.py
@Detail: 
"""
import os
import re
from nonebot import on_command
from nonebot import get_driver, logger
from nonebot.matcher import Matcher
from nonebot.adapters import Message, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment
from configs.all_config import mysql_config
from utils.yys_time import get_now
from utils.common_functions import select_sql, check_sale_flag, search_history, get_yyscbg_url
from utils.yys_mysql import YysMysql
from .yys_spider import get_equip_detail, get_infos_by_kdl
from .yys_parse import get_speed_info, CbgDataParser, find_yuhun_uuid, choose_best_uuid
from .yys_cal_about import *
from .lotter_system import diffrent_data, get_infos_data

config = get_driver().config.dict()

yyscbg_accept_group = config.get('yyscbg_accept_group', [])
yyscbg_accept_vip_group = config.get('yyscbg_accept_vip_group', [])
# 当前目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))
vip_json_file = os.path.join(current_dir, "vip_infos.json")


async def group_checker(event: Event) -> bool:
    """自定义群组规则"""
    # 匹配群组id
    group_id = re.findall("group_(\\d+)_", event.get_session_id())
    if group_id and group_id[0] in yyscbg_accept_group:
        return True
    else:
        return False


async def group_checker_vip(event: Event) -> bool:
    """自定义群组规则"""
    # 匹配群组id
    group_id = re.findall("group_(\\d+)_", event.get_session_id())
    if group_id and (group_id[0] in yyscbg_accept_vip_group or group_id[0] in yyscbg_accept_vip_group):
        return True
    else:
        return False


yycbg_level = on_command("yyscbg_search", rule=group_checker, aliases={'藏宝阁', 'cbg', 'Cbg', "CBG"}, priority=0)
compare_data_level = on_command("yyscbg_compare", rule=group_checker_vip, aliases={'对比', 'compare'}, priority=0)


@yycbg_level.handle()
async def yyscbg_search(bot: Bot, event: GroupMessageEvent):
    try:
        # 检验是否权限过期
        user_id = event.get_user_id()
        if not check_vip_infos(user_id):
            _prompt = MessageSegment.text("无权限使用该功能，请找管理员开通或续费")
        else:
            game_ordersn = re.findall("\\d{15}-\\d{1,2}-[0-9A-Z]+", str(event.message))[0]
            try:
                print(game_ordersn)
                _prompt = parse_yyscbg_url(game_ordersn)
            except Exception as e:
                _prompt = MessageSegment.text("代理出错，请重试")
                print(e)
    except Exception as e:
        print(e)
        _prompt = MessageSegment.text("链接格式出错，请输入正确链接")
    await bot.send(event, message=_prompt, at_sender=True)


@compare_data_level.handle()
async def search_campare_data(bot: Bot, event: GroupMessageEvent):
    try:
        # 检验是否权限过期
        user_id = event.get_user_id()
        if not check_vip_infos(user_id):
            _prompt = MessageSegment.text("无权限使用该功能，请找管理员开通或续费")
        else:
            _prompt = "暂无历史记录"
            game_ordersn = re.findall("\\d{15}-\\d{1,2}-[0-9A-Z]+", str(event.message))[0]
            print(game_ordersn)
            try:
                infos1 = get_infos(game_ordersn)
                json1 = get_infos_data(infos1)
                create_time = json1["create_time"]
                del json1['highlights']
                del json1['desc_sumup_short']
                del json1['game_ordersn']
                history_data = search_history(game_ordersn, create_time)
                if history_data:
                    history_data = history_data[0]
                    infos2 = get_infos(history_data["game_ordersn"])
                    json2 = get_infos_data(infos2)
                    del json2['highlights']
                    del json2['desc_sumup_short']
                    del json2['game_ordersn']
                    diff_list = diffrent_data(json2, json1)
                    diff_list.insert(0, "\n")
                    current_url = get_yyscbg_url(game_ordersn)
                    diff_list.append(f"当前价格: {int(json1['price'])}")
                    diff_list.append(f"当前链接: {current_url}")
                    history_url = get_yyscbg_url(history_data["game_ordersn"])
                    diff_list.append(f"历史价格: {history_data['price']}")
                    diff_list.append(f"历史链接: {history_url}")
                    _prompt = "\n".join(diff_list)
            except Exception as e:
                _prompt = MessageSegment.text("代理出错，请重试")
                print(e)
    except Exception as e:
        print(e)
        _prompt = MessageSegment.text("链接格式出错，请输入正确链接")
    await bot.send(event, message=_prompt, at_sender=True)


def check_vip_infos(user_id):
    """判断vip权限"""
    if not os.path.exists(vip_json_file):
        print("不存在文件!")
        return False

    with open(vip_json_file, "r") as fi:
        yyscbg_vip_infos = json.load(fi)

    qq_list = [vip_info["qq"] for vip_info in yyscbg_vip_infos]
    vip_expiry_times = {vip_info["qq"]: vip_info["vip_expiry_time"] for vip_info in yyscbg_vip_infos}

    if user_id in qq_list and str(get_now()) <= vip_expiry_times[user_id]:
        return True
    else:
        return False


def get_infos(game_ordersn):
    while True:
        proxies = None
        try:
            infos = get_equip_detail(game_ordersn, proxies=proxies, timeout=10)
            if infos and infos.get('status_code') not in ["SESSION_TIMEOUT"] and infos.get('status') != 2:
                return infos
        except Exception as e:
            print(e)
        return False


def find_history_infos(infos):
    equip_name = infos["equip_name"]
    server_name = infos["server_name"]
    create_time = infos["create_time"]
    game_ordersn = infos["game_ordersn"]

    # 方法一
    sql = f"""  
        select *  
        from yys_cbg.all_cbg_url  
        where equip_name="{equip_name}"  
            and server_name='{server_name}'  
            and status_des=3  
            and game_ordersn!='{game_ordersn}'  
            and create_time<='{create_time}'  
            order by create_time desc  
    """
    print(sql)
    _history = select_sql(sql)
    if _history:
        history_url = get_yyscbg_url(_history[0]["game_ordersn"])
        history_price = _history[0]["price"]
        return history_url, history_price
    # 方法二
    parse = CbgDataParser()
    yuhun_json = parse.init_yuhun(infos["inventory"])
    data_info = parse.sort_pos(yuhun_json)
    uuid_infos = find_yuhun_uuid(data_info)
    uuid_json = choose_best_uuid(uuid_infos)

    my_sql = YysMysql(cursor_type=True)
    mysql_handle = my_sql.sql_open(mysql_config)
    for _uuid in uuid_json[:10]:
        sql = f"""  
            SELECT *  
            FROM yys_cbg.all_cbg_url  
            WHERE JSON_CONTAINS(uuid_json, '"{_uuid}"')  
                and status_des=3  
                and game_ordersn!='{game_ordersn}'  
                and create_time<='{create_time}'  
                order by create_time desc
        """
        print(sql)
        _history = my_sql.select_mysql_record(mysql_handle, sql)
        if _history:
            history_url = get_yyscbg_url(_history[0]["game_ordersn"])
            history_price = _history[0]["price"]
            break
    else:
        # 如果未找到历史信息，则返回 None
        history_url = "暂无"
        history_price = "暂无"

    mysql_handle.close()
    return history_url, history_price


def parse_yyscbg_url(game_ordersn=None):
    _prompt = "链接格式错误~"
    if game_ordersn:
        _num = 1
        while True:
            infos = get_infos(game_ordersn)
            dmg_str = get_dmg_str(infos)
            if infos and not isinstance(infos, str):
                current_url = get_yyscbg_url(game_ordersn)
                datas = get_speed_info(infos)
                if not datas:
                    if _num >= 3:
                        break
                    _num += 1
                    _prompt = "代理出错，请重试"
                    continue
                datas['game_ordersn'] = game_ordersn
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
                # 查找历史
                history_url, history_price = find_history_infos(datas)
                print(history_url, history_price)
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
                          f"500天未收录: {datas['sp_coin']}\n" \
                          f"999天未收录: {datas['ssr_coin']}\n" \
                          f"水墨皮兑换券: {datas['special_skin_str1']}\n" \
                          f"限定皮兑换券: {datas['special_skin_str2']}\n" \
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
    time_str = f"{round(hour / 24, 1)}天" if hour >= 24 else f"{hour}时"
    return time_str


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
        _str = ""
        data_yuhun_std = extract_data_cbg(json_data)
        optimize_data_for_cal(data_yuhun_std)
        dmg_yuhun_list = pick_dmg_yuhun(
            data_yuhun_std,
            common_score=8,  # 普通8分
            special_score=10  # 逢魔皮10分
        )
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
