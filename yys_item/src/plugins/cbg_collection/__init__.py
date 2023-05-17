# -*- coding:utf-8 -*-
"""
@Time: 2023/4/20 11:23
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: __init__.py.py
@Detail: 
"""
import os
import re
import json
import concurrent.futures
from nonebot import get_driver, logger, get_bot, on_command, require
from nonebot.matcher import Matcher
from nonebot.adapters import Message, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment
from configs.all_config import mysql_config, proxy_url, http_prefix, redis_config
from utils.yys_time import get_now, get_before_Or_after_few_times
from utils.yys_proxy import ProxyTool
from utils.common_functions import select_sql, check_sale_flag, format_number, get_yyscbg_url
from utils.yys_mysql import YysMysql
from utils.yys_redis import YysRedis
from utils.common_functions import insert_table_to_all_cbg_url

scheduler = require("nonebot_plugin_apscheduler").scheduler

config = get_driver().config.dict()

# 当前目录路径
current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
vip_json_file = os.path.join(current_dir, "yyscbg/vip_infos.json")
yyscbg_accept_vip_group = config.get('yyscbg_accept_vip_group', [])

# redis链接
redis_client = YysRedis(
    host=redis_config["host"],
    port=redis_config["port"],
    password=redis_config["password"],
    db=0
)


async def group_checker(event: Event) -> bool:
    """自定义群组规则"""
    group_id = re.findall("group_(\\d+)_", event.get_session_id())
    if group_id and group_id[0] in yyscbg_accept_vip_group:
        return True
    else:
        return False


yycbg_collect_level = on_command("yyscbg_collect", rule=group_checker, aliases={'收藏', 'collect', '记录', "添加"},
                                 priority=2)
yycbg_bind_level = on_command("yyscbg_collect", rule=group_checker, aliases={'绑定', 'bind'}, priority=2)


@yycbg_bind_level.handle()
async def yyscbg_search(bot: Bot, event: GroupMessageEvent):
    try:
        # 检验是否权限过期
        user_id = event.get_user_id()
        print(user_id)
        if not check_vip_infos(user_id):
            _prompt = MessageSegment.text("无权限使用该功能，请找管理员开通或续费")
        else:
            try:
                _prompt = "uuid格式错误！"
                pattern = "^UID_[a-zA-Z0-9]+$"
                uuid = str(event.message).split("UID_")[1]
                uuid = "UID_" + uuid
                print(uuid)
                result = re.match(pattern, uuid)
                if result:
                    dts = {
                        'qq': user_id,
                        'uuid': uuid
                    }
                    hope_update_list = ['qq', 'uuid']
                    insert_table_to_all_cbg_url([dts], hope_update_list, table='qq_robots.user_infos')
                    _prompt = "绑定成功！"

            except Exception as e:
                _prompt = MessageSegment.text("uuid格式错误！请联系管理员！")
                print(e)
    except Exception as e:
        print(e)
        _prompt = MessageSegment.text("绑定异常，请联系管理员排查问题！")
    await bot.send(event, message=_prompt, at_sender=True)


@yycbg_collect_level.handle()
async def yyscbg_search(bot: Bot, event: GroupMessageEvent):
    try:
        # 检验是否权限过期
        user_id = event.get_user_id()
        print(user_id)
        if not check_vip_infos(user_id):
            _prompt = MessageSegment.text("无权限使用该功能，请找管理员开通或续费")
        else:
            try:
                game_ordersn = re.findall("\\d{15}-\\d{1,2}-[0-9A-Z]+", str(event.message))[0]
                print(game_ordersn)
                dts = {
                    'user_id': user_id,
                    'game_ordersn': game_ordersn
                }
                hope_update_list = ['user_id', 'game_ordersn']
                insert_table_to_all_cbg_url([dts], hope_update_list, table='qq_robots.bookmarks')
                _prompt = "收藏成功！"
            except Exception as e:
                _prompt = MessageSegment.text("链接格式出错，请输入正确链接")
                print(e)
    except Exception as e:
        print(e)
        _prompt = MessageSegment.text("收藏异常，请联系管理员排查问题！")
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
