# -*- coding:utf-8 -*-
"""
@Time: 2022/11/18上午11:03
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: __init__.py.py
@Detail: 消息转发
"""
import re
import asyncio
from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.rule import startswith

from nonebot import get_driver, logger

config = get_driver().config.dict()

forwarder_source_group = config.get('forwarder_source_group', [])
forwarder_dest_group = config.get('forwarder_dest_group', [])
# 转发消息前缀
forwarder_prefix = config.get('forwarder_prefix', [""])
forwarder_explict = config.get('forwarder_explict', [""])

rule = startswith(forwarder_prefix)

msg_matcher = on_message(rule, priority=10, block=False)


async def send_meg(bot: Bot, group_id: str, msg: str):
    logger.debug(f"消息转发至: {group_id} 群")
    await bot.send_group_msg(group_id=int(group_id), message=msg, auto_escape=False)


@msg_matcher.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if str(event.group_id) in forwarder_source_group:
        flag = forwarder_explict[0] == "" or str(event.user_id) in forwarder_explict
        if flag and forwarder_dest_group[0] != "":
            msg = str(event.message)
            logger.debug(f"欲转发消息: {msg} | 来源: {event.group_id} 群")
            tasks = [send_meg(bot, gid, msg) for gid in forwarder_dest_group if gid != str(event.group_id)]
            await asyncio.wait(tasks)
