# -*- coding:utf-8 -*-
"""
@Time: 2022/11/13下午5:50
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: __init__.py.py
@Detail: 阴阳师斗技相关
"""
import re
from nonebot import on_command
from nonebot import get_driver, logger
from nonebot.matcher import Matcher
from nonebot.adapters import Message, Event
from nonebot.adapters.onebot.v11 import MessageSegment, GroupMessageEvent, Bot
# from nonebot_plugin_txt2img import Txt2Img
from nonebot.params import Arg, CommandArg, ArgPlainText

from utils.yys_time import get_few_days
from .search_about_hat import *
from .async_request_search import *
from .search_about_palyer import *
from .html_generate_picture import run_image
from .build_player_card_image import build_card_image

config = get_driver().config.dict()

yyspvp_accept_group = config.get('yyspvp_accept_group', [])


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


# 全局数据
all_server_list, all_infos = get_all_server()
# logger.info(f"全服数据: {all_infos}")
# 命令
blue_level = on_command("blue_hat", rule=group_checker, aliases={'蓝帽子', '蓝'}, priority=3)
red_level = on_command("red_hat", rule=group_checker, aliases={'红帽子', '红'}, priority=2)
player_level = on_command("player_search", rule=group_checker, aliases={'玩家'}, priority=1)
server_table = on_command("server_search", rule=group_checker, aliases={'code', '编码表'}, priority=5)


def get_image_message(file_name):
    with open(file_name, "rb") as f:
        images = f.read()
    return MessageSegment.image(images)


@player_level.handle()
async def player_handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        matcher.set_arg("player_name", args)


@blue_level.handle()
async def blue_handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        matcher.set_arg("b_hat", args)


@red_level.handle()
async def red_handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    matcher.set_arg("r_hat", args)


@server_table.handle()
async def server_code_search(bot: Bot, event: GroupMessageEvent):
    _prompt = "          阴阳师区服表      \n"
    for info in all_infos:
        _prompt += " " + info[0] + " " + info[1]
    await bot.send(event, message=_prompt, at_sender=True)


@player_level.got('player_name', prompt="请输入你想查询的玩家ID:")
async def handle_player_request(event: Event, matcher: Matcher, player_name: str = ArgPlainText("player_name")):
    user_id = event.get_user_id()
    flag = False
    try:
        flag = int(player_name)
    except ValueError as e:
        logger.error(e)

    date_time_list = get_month_date_time_list()
    _prompt = "查询失败~请稍后再试~"
    if str(player_name) in ["a", "b", "c", "d"] or (flag in range(1, 11)):
        if not flag:
            week_date = date_time_list[["a", "b", "c", "d"].index(str(player_name))]
            player_name_key = f'player_name_{user_id}'
            user_search_name = globals().get(player_name_key)
            globals().pop(player_name_key)
            infos = es_search_player_infos(role_name=user_search_name, week_date=week_date)
            # 暂时只取匹配前10项
            infos = format_es_data(infos)[:10]
            if len(infos) > 0:
                i = 1
                # 动态变量
                exec(f'player_search_{user_id} = {infos}', globals())
                _prompt = "请输入以下数字，代表选中玩家ID：\n"
                for info in infos:
                    server_name = get_server_name(info["yys_server"], all_infos)
                    _prompt += (str(i) + "、 " + server_name + "————" + info["role_name"]) + "\n"
                    i += 1
                _prompt += "(如若不存在，请输入完整ID)"
                await player_level.reject(prompt=_prompt, at_sender=True)
            else:
                _prompt = "查无此人"
        else:
            # 获取变量key
            user_key = f'player_search_{user_id}'
            infos = globals().get(user_key)
            # 删除变量
            globals().pop(user_key)
            infos = infos[flag - 1]
            uid = infos["user_id"]
            role_name = infos['role_name']
            logger.info(f"玩家id: {uid}--{role_name}\n,")
            # 常用阵容
            datas = list(cal_common_lineup(uid))
            dts = master_shift_right(datas)
            image_list = [get_shishen_image(dt[0]) for dt in dts]
            sunday = str(infos['week_date'])
            # 时间截止范围
            date_range = f"{get_few_days(-6, str(sunday))}~{sunday}"
            win_rate = str(round(infos["count_win"] / infos["count_all"], 3) * 100)[:4]
            card_data = {
                'date_range': date_range,
                'role_name': role_name,
                'server_name': get_server_name(infos["yys_server"], all_infos),
                'rank': infos["yys_rank"],
                'score': score_to_star(infos["score"]),
                'all_counts': infos["count_all"],
                'win_rate': win_rate,
                "image_src_list": image_list
            }
            # 卡片图
            file_name = build_card_image(card_data)
            message = get_image_message(file_name)
            await player_level.finish(message, at_sender=True)
    else:
        player_name = matcher.get_arg("player_name")
        logger.debug(player_name)
        exec(f'player_name_{user_id} = "{player_name}"', globals())
        _prompt = f'请输入a-d之间字母，代表截止日期，如：\na、（{date_time_list[0]}）\nb、（{date_time_list[1]}）' \
                  f'\nc、（{date_time_list[2]}）\nd、（{date_time_list[3]}）'
        await player_level.reject(prompt=_prompt, at_sender=True)

    await player_level.finish(_prompt, at_sender=True)


@red_level.got("r_hat")
async def handle_red_request(r_hat: Message = Arg(), week_num: str = ArgPlainText('r_hat')):
    _prompt = "查询失败~请稍后再试~"
    red_hat_infos = []
    hat_infos = await get_month_red_hat()
    date_time_list = get_month_date_time_list()
    for i in range(len(date_time_list)):
        sunday = date_time_list[i]
        monday = get_few_days(-6, str(sunday))
        red_hat_infos.append({
            "date_range": f"{str(monday)[5:]}~{str(sunday)[5:]}",
            "score": hat_infos[i - 1]
        })
    if len(red_hat_infos) == 0:
        _prompt = "超时请重新再试"
    # 发送图片
    title = "近一个月红帽子分数线"
    file_name = run_image(red_hat_infos, title, _type=None)
    if file_name:
        message = get_image_message(file_name)
        await blue_level.finish(message, at_sender=True)

    await blue_level.finish(_prompt, at_sender=True)


@blue_level.got("b_hat", prompt="你想查询哪个服务器，请输入编码：")
async def handle_blue_request(b_hat: Message = Arg(), server_code: str = ArgPlainText("b_hat")):
    # 获取所有区
    _type = None
    if server_code == "all":
        await blue_level.reject(prompt='请输入1-4之间数字，代表上几周，如：\n1（上周）\n2（上两周）\n3（上三周）\n4（上四周）', at_sender=True)
    elif server_code in ["1", "2", "3", "4"]:
        title = "全服蓝帽子分数线"
        _type = "all_blue"
        date_time = get_weekly_date(int(server_code))
        dts = await get_all_server_blue_hat(str(date_time))
        blue_hat_infos = list_dict_order_by_key(dts, "score")
    elif server_code in all_server_list:
        blue_hat_infos = []
        server_name = get_server_name(server_code, all_infos)
        title = f"近一个月蓝帽子分数线（{server_name}）"
        hat_infos = await get_month_blue_hat(server_code)
        date_time_list = get_month_date_time_list()
        for i in range(len(date_time_list)):
            sunday = date_time_list[i]
            monday = get_few_days(-6, str(sunday))
            blue_hat_infos.append({
                "date_range": f"{str(monday)[5:]}~{str(sunday)[5:]}",
                "score": hat_infos[i - 1]
            })
    else:
        await blue_level.reject(b_hat.template("你想查询服务器编码 \"{b_hat}\" 不存在,请重新输入！"), at_sender=True)

    # 发送图片
    file_name = run_image(blue_hat_infos, title, _type)
    if file_name:
        message = get_image_message(file_name)
        await blue_level.finish(message)
    else:
        await blue_level.finish("查询失败~请稍后再试~", at_sender=True)
