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
import concurrent.futures
from nonebot import get_driver, logger, get_bot, on_command, require
from nonebot.matcher import Matcher
from nonebot.adapters import Message, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment
from configs.all_config import mysql_config, proxy_url, http_prefix, redis_config, yys_history_mappings, es_config
from utils.yys_time import get_now, get_before_Or_after_few_times
from utils.yys_proxy import ProxyTool
from utils.common_functions import select_sql, check_sale_flag, format_number, get_yyscbg_url
from utils.yys_mysql import YysMysql
from utils.yys_redis import YysRedis
from utils.yys_elasticsearch import ElasticSearch
from .yys_spider import get_equip_detail, get_infos_by_kdl as get_infos
from .yys_parse import get_speed_info, CbgDataParser, find_yuhun_uuid, choose_best_uuid
from .yys_cal_about import *
from .lotter_system import diffrent_data, get_infos_data

scheduler = require("nonebot_plugin_apscheduler").scheduler

config = get_driver().config.dict()

yyscbg_accept_group = config.get('yyscbg_accept_group', [])
yyscbg_accept_vip_group = config.get('yyscbg_accept_vip_group', [])
# 当前目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))
vip_json_file = os.path.join(current_dir, "vip_infos.json")
groups = config.get('yyscbg_push_group', [])

# redis
redis_client = YysRedis(
    host=redis_config["host"],
    port=redis_config["port"],
    password=redis_config["password"],
    db=5
)

es_ip = es_config["es_ip"]
es_auth = es_config["auth"]
history_mappings = yys_history_mappings
history_index_name = "yys_history_sale"


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


async def send_notification(bot, group_id, message):
    message += f"\n时间校准:{get_now()}"
    await bot.send_group_msg(group_id=group_id, message=message)


async def get_datas():
    """获取半小时内的数据"""
    # 获取最多60个keynames
    keynames = redis_client.get_names()
    print(len(keynames))
    # 使用多线程并行处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(handle_data, data) for data in keynames]
        last_result = [f.result() for f in concurrent.futures.as_completed(futures) if f.result()]
    return last_result


def handle_data(data):
    try:
        # message = get_compara_infos(data['game_ordersn'], True, True)
        message = parse_yyscbg_url(data, True, False)
        if message == "暂无历史记录":
            return False
        return message
    except Exception as e:
        # 记录错误信息到日志文件
        logger.exception("Exception occurred while processing data %s", data)
        logger.exception(e)
        return ""


@scheduler.scheduled_job('interval', minutes=3, max_instances=3)
async def yyscbg_notice():
    # 5分钟通知一次
    bot = get_bot()
    infos = await get_datas()
    for group_id in groups:
        for msg in infos:
            await send_notification(bot, group_id, msg)


@yycbg_level.handle()
async def yyscbg_search(bot: Bot, event: GroupMessageEvent):
    try:
        # 检验是否权限过期
        user_id = event.get_user_id()
        if not check_vip_infos(user_id):
            _prompt = MessageSegment.text("无权限使用该功能，请找管理员开通或续费")
        else:
            try:
                _game_ordersn = re.findall(r"\d+-\d+-\w+", str(event.message))[0]
                _prompt = parse_yyscbg_url(_game_ordersn, False, is_proxy=True)
            except Exception as e:
                _prompt = MessageSegment.text("代理出错，请重试")
                print(e)
    except Exception as e:
        print(e)
        _prompt = MessageSegment.text("链接格式出错，请输入正确链接")
    await bot.send(event, message=_prompt, at_sender=True)


def get_compara_infos(game_ordersn, is_lotter=False, is_infos=False):
    """获取对比数据"""
    try:
        _prompt = "暂无历史记录"
        if is_infos:
            # infos1 = load_infos(game_ordersn)
            pass
        else:
            infos1 = get_infos(game_ordersn)
        json1 = get_infos_data(infos1)

        try:
            datas = get_speed_info(infos1)
            history_url, history_price, history_time = es_search(
                datas["uuid_json"],
                datas['game_ordersn'],
                datas['create_time']
            )
        except:
            history_url, history_price = ("暂无", "暂无")
        if is_lotter:
            if int(json1['price']) > int(history_price):
                return _prompt

        del json1['highlights']
        del json1['desc_sumup_short']
        del json1['game_ordersn']
        del json1['inventory']
        if isinstance(history_price, int):
            # history_game_ordersn = re.findall("\\d{15}-\\d{1,2}-[0-9A-Z]+", history_url)[0]
            history_game_ordersn = re.findall(r"\d+-\d+-\w+", history_url)[0]
            print(history_game_ordersn)
            infos2 = get_infos(history_game_ordersn)
            json2 = get_infos_data(infos2)
            del json2['highlights']
            del json2['desc_sumup_short']
            del json2['game_ordersn']
            del json2['inventory']
            diff_list = diffrent_data(json2, json1)
            diff_list.insert(0, "\n")
            current_url = get_yyscbg_url(game_ordersn)
            diff_list.append(f"当前价格: {int(json1['price'])}")
            diff_list.append(f"当前链接: {current_url}")
            diff_list.append(f"历史价格: {history_price}")
            diff_list.append(f"历史链接: {history_url}")
            _prompt = "\n".join(diff_list)
    except Exception as e:
        _prompt = MessageSegment.text("代理出错，请重试")
        print(e)
    return _prompt


@compare_data_level.handle()
async def search_campare_data(bot: Bot, event: GroupMessageEvent):
    try:
        # 检验是否权限过期
        user_id = event.get_user_id()
        if not check_vip_infos(user_id):
            _prompt = MessageSegment.text("无权限使用该功能，请找管理员开通或续费")
        else:
            # game_ordersn = re.findall("\\d{15}-\\d{1,2}-[0-9A-Z]+", str(event.message))[0]
            game_ordersn = re.findall(r"\d+-\d+-\w+", str(event.message))[0]
            print(game_ordersn)
            _prompt = get_compara_infos(game_ordersn)
    except Exception as e:
        print(e)
        _prompt = MessageSegment.text("链接格式出错，请输入正确链接")
    print(_prompt)
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


proxy_handle = ProxyTool(proxy_url, http_prefix)


def parse_es_data(infos):
    """解析es数据"""
    ret = []
    if infos.get("hits", False) and infos["hits"].get('total', False) and infos["hits"]["total"]["value"] >= 1:
        hits = infos["hits"]["hits"]
        for hit in hits:
            _source = hit["_source"]
            ret.append(_source)
    return ret


def es_search(uuid_json, game_ordersn, current_time, is_history=True):
    history_url = "暂无"
    history_price = "暂无"
    history_time = None
    if not uuid_json:
        return history_url, history_price, history_time
    es_object = ElasticSearch(es_ip, auth=es_auth)
    es_object.es_create(index_name=history_index_name, body=history_mappings)
    # 设置窗口必须
    es_object.es_set_max_windows(max_num=50000000)
    if is_history:
        es_body = {
            "track_total_hits": True,
            "_source": ["*"],
            "from": 0,
            "size": 1,
            "query": {
                "bool": {
                    "must": [
                        {
                            "terms": {
                                "uuid_json": uuid_json
                            }
                        },
                        {
                            "match": {
                                "status_des": 3
                            }
                        },
                        {
                            "range": {
                                "create_time": {
                                    "lt": current_time
                                }
                            }
                        }
                    ],
                    "must_not": {
                        "term": {
                            "game_ordersn": game_ordersn
                        }
                    }
                }
            },
            "sort": {
                "create_time": {
                    "order": "desc"
                }
            }
        }
    else:
        es_body = {
            "track_total_hits": True,
            "_source": ["*"],
            "from": 0,
            "size": 1,
            "query": {
                "bool": {
                    "must": [
                        {
                            "terms": {
                                "uuid_json": uuid_json
                            }
                        },
                        {
                            "range": {
                                "create_time": {
                                    "lt": current_time
                                }
                            }
                        }
                    ],
                    "must_not": {
                        "term": {
                            "game_ordersn": game_ordersn
                        }
                    }
                }
            },
            "sort": {
                "create_time": {
                    "order": "desc"
                }
            }
        }
    try:
        infos = es_object.es_search(index_name=history_index_name, body=es_body)
        res = parse_es_data(infos)
        if len(res) > 0:
            res = res[0]
            history_url = get_yyscbg_url(res["game_ordersn"])
            history_price = res["price"]
            history_time = res["create_time"]
    except Exception as e:
        logger.error(e)
    finally:
        return history_url, history_price, history_time


def get_yyscbg_prompt(datas, is_lotter=False):
    """获取当前链接数据"""
    _prompt = "暂无历史记录"
    ssr_flag = datas['ssr_flag']
    sp_flag = datas['sp_flag']
    equip_name = datas["equip_name"]
    server_name = datas["server_name"]
    status_des = datas["status_des"]
    highlights = datas["highlights"]
    price = datas["price"]
    yuhun_buff = cal_time(datas["yuhun_buff"])
    goyu = datas["goyu"]
    hunyu = datas["hunyu"]
    strength = datas["strength"]
    level_15 = datas['level_15']
    currency_900217 = datas['currency_900217']  # 蛇皮
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
    before_time_str = get_before_Or_after_few_times(minutes=-40)
    if is_lotter:
        if datas['create_time'] <= before_time_str:
            return False
    # 查找历史
    try:
        # history_url, history_price = find_history_infos(datas)
        history_url, history_price, history_time = es_search(
            datas["uuid_json"],
            datas['game_ordersn'],
            datas['create_time']
        )
    except:
        history_url, history_price = ("暂无", "暂无")
    print(history_url, history_price)
    currency_900217 = format_number(datas['currency_900217'])  # 蛇皮
    goyu = format_number(datas["goyu"])
    hunyu = format_number(datas["hunyu"])
    strength = format_number(datas["strength"])
    level_15 = format_number(datas['level_15'])
    if not is_lotter:
        _prompt = f"当前链接：{datas['current_url']}\nID: {equip_name}\n区服: {server_name}\n状态: {status_des}\n" \
                  f"高亮文字: {highlights}\n" \
                  f"价格: {int(price)}\n历史价格: {history_price}\n历史链接：{history_url}\n" \
                  f"御魂加成: {yuhun_buff}\n勾玉: {goyu}\n魂玉: {hunyu}\n体力: {strength}\n" \
                  f"强15+: {level_15}\n蛇皮: {currency_900217}\n" \
                  f"============================\n"
        _prompt += f"满速个数: {datas['full_speed_num']}\n"
        _prompt += f"头: {get_str(head_info['value_list'])}\n" if get_str(head_info['value_list']) else ""
        _prompt += f"尾: {get_str(mz_info['value_list'])}\n" if get_str(mz_info['value_list']) else ""
        _prompt += f"抵抗: {get_str(dk_info['value_list'])} \n" if get_str(dk_info['value_list']) else ""
        _prompt += f"============================\n"
        _prompt += f"崽战框: {datas['zaizhan_str']}\n" if datas['zaizhan_str'] else ""
        _prompt += f"氪金: {datas['kejin_str']}\n" if datas['kejin_str'] else ""
        _prompt += f"500天未收录: {datas['sp_coin']}\n" if datas['sp_coin'] else ""
        _prompt += f"999天未收录: {datas['ssr_coin']}\n" if datas['ssr_coin'] else ""
        _prompt += f"水墨皮兑换券: {datas['special_skin_str1']}\n" if datas['special_skin_str1'] else ""
        _prompt += f"限定皮兑换券: {datas['special_skin_str2']}\n" if datas['special_skin_str2'] else ""
        _prompt += f"============================\n"
        _prompt += f"{get_suit_str(suit_speed, True)}\n"
        _prompt += f"庭院{yard_prefix}: {yard_str}\n典藏{dc_prefix}: {dc_str}\n"
        _prompt += f"风姿度: {fengzidu}\n" if fengzidu else ""
        _prompt += f"手办框{shouban_prefix}: {shouban_str}\n"
        _prompt += f"输出御魂：{datas['dmg_str']}\n"
    else:
        _prompt = f"当前链接：{datas['current_url']}\nID: {equip_name}\n区服: {server_name}\n状态: {status_des}\n" \
                  f"高亮文字: {highlights}\n" \
                  f"价格: {int(price)}\n历史价格: {history_price}\n历史链接：{history_url}\n" \
                  f"勾玉: {goyu}\n强15+: {level_15}\n蛇皮: {currency_900217}\n" \
                  f"魂玉: {hunyu}\n" \
                  f"============================\n"
        _prompt += f"满速个数: {datas['full_speed_num']}\n"
        # _prompt += f"头: {get_str(head_info['value_list'])}\n" if get_str(head_info['value_list']) else ""
        # _prompt += f"尾: {get_str(mz_info['value_list'])}\n" if get_str(mz_info['value_list']) else ""
        # _prompt += f"抵抗: {get_str(dk_info['value_list'])} \n" if get_str(dk_info['value_list']) else ""
        _prompt += f"============================\n"
        _prompt += f"崽战框: {datas['zaizhan_str']}\n" if datas['zaizhan_str'] else ""
        _prompt += f"氪金: {datas['kejin_str']}\n" if datas['kejin_str'] else ""
        _prompt += f"500天未收录: {datas['sp_coin']}\n" if datas['sp_coin'] else ""
        _prompt += f"999天未收录: {datas['ssr_coin']}\n" if datas['ssr_coin'] else ""
        _prompt += f"水墨皮兑换券: {datas['special_skin_str1']}\n" if datas['special_skin_str1'] else ""
        _prompt += f"限定皮兑换券: {datas['special_skin_str2']}\n" if datas['special_skin_str2'] else ""
        _prompt += f"============================\n"
        _prompt += f"庭院: {yard_prefix}\n典藏: {dc_prefix}\n"
        _prompt += f"风姿度: {fengzidu}\n" if fengzidu else ""
        _prompt += f"手办框: {shouban_prefix}\n"

    return _prompt


def parse_yyscbg_url(game_ordersn, is_lotter=False, is_proxy=False):
    _prompt = ""
    if is_proxy is False:
        _prompt = redis_client.get(game_ordersn)
        redis_client.delete(game_ordersn)
    else:
        infos = get_infos(game_ordersn)
        if infos and not isinstance(infos, str):
            current_url = get_yyscbg_url(game_ordersn)
            datas = get_speed_info(infos)
            if datas:
                dmg_str = get_dmg_str(infos)
                datas['game_ordersn'] = game_ordersn
                datas['current_url'] = current_url
                datas['dmg_str'] = dmg_str
                _prompt = get_yyscbg_prompt(datas, is_lotter)
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
