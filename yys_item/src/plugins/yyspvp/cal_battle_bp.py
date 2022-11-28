# -*- coding:utf-8 -*-
"""
@Time: 2022/11/24下午1:52
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: cal_battle_bp.py
@Detail: 计算斗技ban位
"""
import json

from utils.common_functions import read_Or_request_json_file, select_sql

# datas = read_Or_request_json_file(f_type="shishen")
# infos = json.dumps(datas, ensure_ascii=False)
# with open("shishen.json", "w", encoding="utf-8") as f:
#     f.write(infos)

shishen_json = read_Or_request_json_file("shishen.json")
common_ban_postion = [
    {"_id": 255, "name": "阎魔"},
    {"_id": 261, "name": "镰鼬"},
    {"_id": 288, "name": "彼岸花"},
    {"_id": 316, "name": "白藏主"},
    {"_id": 330, "name": "不知火"},
    {"_id": 341, "name": "鬼王酒吞童子"},
    {"_id": 344, "name": "云外镜"},
    {"_id": 352, "name": "缚骨清姬"},
    {"_id": 356, "name": "千姬"},
    {"_id": 357, "name": "初翎山风"},
    {"_id": 362, "name": "蝉冰雪女"},
    {"_id": 363, "name": "帝释天"},
    {"_id": 366, "name": "空相面灵气"},
    {"_id": 372, "name": "因幡辉夜姬"},
    {"_id": 383, "name": "神堕八岐大蛇"},
    {"_id": 385, "name": "大夜摩天阎魔"},
    {"_id": 388, "name": "心狩鬼女红叶"},
    {"_id": 389, "name": "须佐之男"},
    {"_id": 390, "name": "神启荒"},
]


def get_player_battle_list(uid):
    sql = f"select battle_list, d_battle_list from yys_pvp.yys_games where uid='{uid}'"
    infos = select_sql(sql)
    _datas = []
    for info in infos:
        battle_list = json.loads(info["battle_list"])
        d_battle_list = json.loads(info["d_battle_list"])
        all_battle = battle_list + d_battle_list
        list(map(lambda x: _datas.append(x), all_battle))

    return list(set(_datas))


def calculate_ban_position(uid, _common_ban_postion=None):
    """计算ban位"""
    all_shishen = get_player_battle_list(uid)
    if _common_ban_postion is None:
        _common_ban_postion = common_ban_postion
    return [_ for _ in _common_ban_postion if _["_id"] not in all_shishen]


if __name__ == '__main__':
    uid = "21332540"
    uid = "21328842"
    uid = "21330611"
    uid = "21278010"
    uid = "21280767"

    uid = "21330342"
    uid = "21330099"
    uid = "21332358"
    uid = "21279865"
    uid = "21275217"
    uid = "21276847"
    uid = "21333141"
    uid = "21403028"
    dt = calculate_ban_position(uid)
    print(dt)
