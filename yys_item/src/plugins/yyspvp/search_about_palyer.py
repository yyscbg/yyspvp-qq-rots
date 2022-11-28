# -*- coding:utf-8 -*-
"""
@Time: 2022/11/18上午2:47
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: search_about_palyer.py
@Detail: 查询关于玩家数据
"""
import json
import pandas as pd

from utils.yys_redis import YysRedis
from utils.yys_elasticsearch import ElasticSearch
from utils.common_functions import select_sql, read_Or_request_json_file, get_shishen_name
from configs.all_config import es_config, redis_config

redis_client = YysRedis(
    host=redis_config["host"],
    port=redis_config["port"],
    password=redis_config["password"],
    db=2
)

es_ip = es_config["es_ip"]
auth = es_config["auth"]
index_name = "yyspvp_index"
es = ElasticSearch(es_ip, auth=auth)
shishen_json = read_Or_request_json_file(f_type='shishen')
# 添加主角
yys_hero = {
    "10": {"id": 10, "name": "晴明", "icon": "https://g.166.net/assets/img/yys/yys/10.jpg"},
    "11": {"id": 11, "name": "神乐", "icon": "https://g.166.net/assets/img/yys/yys/11.jpg"},
    "12": {"id": 12, "name": "八百比丘尼", "icon": "https://g.166.net/assets/img/yys/yys/12.jpg"},
    "13": {"id": 13, "name": "源博雅", "icon": "https://g.166.net/assets/img/yys/yys/13.jpg"}
}
for k, v in yys_hero.items():
    shishen_json[k] = v


def es_search_player_infos(**args):
    """es查询玩家数据"""
    role_name = args.get('role_name', None)
    week_date = args.get('week_date', None)
    body = {
        "track_total_hits": True,
        "from": 0,
        "size": 10,
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "role_name": role_name
                        }
                    },
                    {
                        "term": {
                            "week_date": week_date
                        }
                    }
                ]
            }
        },
        "sort": {
            "score": {
                "order": "desc"
            }
        }
    }
    infos = es.es_search(index_name, body=body)
    return infos


def format_es_data(dts):
    """格式化索引结果"""
    if len(dts) == 0:
        return False
    if dts["hits"].get('hits', 0) == 0:
        return False
    hits = dts["hits"]["hits"]
    datas = []
    for hit in hits:
        datas.append(hit["_source"])
    return datas


def cal_common_lineup(uid):
    """计算常用阵容"""
    sql = f"select info_md5, battle_list from yys_pvp.yys_games where uid='{uid}'"
    infos = select_sql(sql)
    result = []
    for info in infos:
        battle_list = json.loads(info["battle_list"])
        for battle in battle_list:
            # result.append(get_shishen_name(shishen_json, battle))
            result.append(battle)

    pds = pd.DataFrame(pd.Series(result)).apply(pd.value_counts)
    for index, data in pds.iterrows():
        yield [index, data.values[0]]


def get_shishen_image(_id):
    try:
        image = shishen_json[str(_id)]["icon"]
    except Exception as e:
        image = ""
    return image


def master_shift_right(dts):
    """主角数据右移"""
    master = []
    _datas = []
    for index, dt in enumerate(dts):
        if dt[0] in [10, 11, 12, 13]:
            if len(master) == 0:
                master.append(dt)
        else:
            if len(_datas) < 5:
                _datas.append(dt)
            else:
                break
    _datas.append(master[0])
    return _datas


if __name__ == '__main__':
    pass
    # week_date = "2022-11-20"
    # infos = es_search_player_infos(role_name="青", week_date=week_date)
    # infos = format_es_data(infos)
    dts = list(cal_common_lineup("21280004"))
    dts = master_shift_right(dts)
    image_list = [get_shishen_image(dt[0]) for dt in dts]
    print(image_list)
