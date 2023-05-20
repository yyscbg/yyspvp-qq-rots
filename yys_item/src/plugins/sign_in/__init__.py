# -*- coding:utf-8 -*-
"""
@Time: 2022/11/28下午2:21
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: __init__.py.py
@Detail: 签到插件
"""

from nonebot import on_regex, get_driver
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from .sign import search_login_status

config = get_driver().config.dict()

yyspvp_accept_group = config.get('yyspvp_accept_group', [])

qd = on_regex(pattern=r'^签到$', priority=3)


@qd.handle()
async def group_sign_in(event: GroupMessageEvent):
    if str(event.group_id) in yyspvp_accept_group:
        _qq = event.user_id
        lovelive_send = search_login_status(_qq)
        print(lovelive_send)
        await qd.send(Message(lovelive_send), at_sender=True)
