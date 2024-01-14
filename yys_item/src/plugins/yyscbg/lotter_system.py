# -*- coding:utf-8 -*-
"""
@Time: 2023/3/29 14:34
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: lottery_system.py
@Detail:
"""
import json
from termcolor import colored
from collections import OrderedDict
from .yys_parse import *
from .yys_spider import get_equip_detail
from utils.common_functions import format_number, check_platform, get_key_name, format_yuhun_buff


def change_json_key(json_data: dict) -> dict:
    """改变json键名"""
    return {get_key_name(key) or key: value for key, value in json_data.items()}


def get_str(_array, round_num=3):
    return ", ".join([f"{info['yh_type']}: {info['speed']:.{round_num}f}" for info in _array])


def get_suit_str(_array):
    """套装速度"""
    return "\n".join([f"{info['suit_name']}: {round(info['speed_sum'], 3)}" for info in _array])


def get_suit_dict(_array):
    """套装速度"""
    return {info['suit_name']: round(info['speed_sum'], 3) for info in _array}


def compare_json(data1, data2):
    """
    比较两个JSON数据是否一致
    """
    compare_text = []
    if isinstance(data1, dict) and isinstance(data2, dict):
        # 如果两个数据都是字典，则递归地比较它们的每个键值对
        # for key in set(data1.keys()).union(data2.keys()):
        for key in data1.keys():
            if key not in data1 or key not in data2:
                compare_text.append(colored(f"{key} is missing in one of the JSONs", 'red'))
                continue
            value1 = data1[key]
            value2 = data2[key]
            if value1 in ['', None]:
                value1 = '🈚️'
            if value2 in ['', None]:
                value2 = '🈚️'
            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                if value1 != value2:
                    # diff = f"{chr(8593)}" if value2 > value1 else f"{chr(8595)}"
                    diff = f"⬆" if value2 > value1 else f"⬇"
                    color = 'green' if value2 > value1 else 'red'
                    if key in ['yuhun_buff', '御魂加成']:
                        value1 = format_yuhun_buff(value1)
                        value2 = format_yuhun_buff(value2)
                    else:
                        value1 = format_number(value1)
                        value2 = format_number(value2)
                    compare_text.append(colored(f"{key}: {value1} {diff} {value2}", color))
            elif isinstance(value1, str) and isinstance(value2, str):
                if value1 != value2:
                    compare_text.append(colored(f"{key}: {value1} -----> {value2}", 'green'))
            elif isinstance(value1, list) and isinstance(value2, list):
                if value1 != value2:
                    str_flag = False
                    for i in range(len(value1)):
                        if isinstance(value1, str):
                            str_flag = True
                            break
                        elif isinstance(value1, dict) and isinstance(value2, dict):
                            pass
                    if str_flag:
                        set1 = set(value1)
                        set2 = set(value2)
                        difference = set1 - set2
                        compare_text.append(colored(f"{key}: {difference}", 'green'))
            else:
                # 对于其他类型的数据可以直接比较
                if value1 != value2:
                    compare_text.append(colored(f"{key}: {value1} -----> {value2}", 'red'))
    elif isinstance(data1, list) and isinstance(data2, list):
        # 如果两个数据都是列表，则递归地比较它们的每个元素
        if len(data1) != len(data2):
            compare_text.append(colored(f"List length is different: {len(data1)} vs {len(data2)}", 'red'))
        for i in range(len(data1)):
            if not compare_json(data1[i], data2[i]):
                pass
    else:
        # 其他类型的数据可以直接比较
        return data1 == data2

    return compare_text


def get_infos_by_proxy(game_ordersn):
    global proxy_handle
    while True:
        proxies = proxy_handle.get_proxy()
        try:
            infos = get_equip_detail(game_ordersn, proxies=proxies, timeout=5)
            if infos:
                return infos
            proxy_handle.get_proxies()
            print(len(proxy_handle.proxy_list))
        except Exception as e:
            proxy_handle.get_proxies()
            print(f"{e}: 刷新代理: {proxies}")


def get_infos_data(infos):
    parse = CbgDataParser()
    try:
        data = parse.cbg_parse(infos)
        data["price"] = int(data["price"])
    except Exception as e:
        print(e)
        return
    # # 计算6号位暴击爆伤
    # data_yuhun_std = extract_data_cbg(infos)
    # optimize_data_for_cal(data_yuhun_std)
    # # 计算6号位暴击、爆伤
    # dmg_yuhun_6 = pick_dmg_yuhun(
    #     data_yuhun_std,
    #     is_speed_limit=True,
    #     dmg_kinds=['暴击伤害'],
    #     common_score=8,  # 普通分数
    #     special_score=11,  # 逢魔皮分数
    #     special_kinds=['荒骷髅', '鬼灵歌伎', '土蜘蛛']
    # )
    # # 6号位数量
    # dmg_yuhun_6_num = len(dmg_yuhun_6)
    # dmg_yuhun_6_str = "、 ".join(list(map(lambda _: f"{_['kind']}:{_['score_dmg']}分", dmg_yuhun_6)))
    data["platform_type"] = check_platform(data["platform_type"])
    try:
        yuhun_json = parse.init_yuhun(data["inventory"])
        # 御魂分组1-6
        data_info = parse.sort_pos(yuhun_json)
        # 速度御魂列表
        speeds_all = get_speeds_all(data_info)
        full_speed_num = get_full_speed_number(speeds_all, 15)
        data.update({"full_speed_num": full_speed_num})
        zc_speed_list = get_suit_pos_fast_speed(speeds_all, "招财猫")
        hl_speed_list = get_suit_pos_fast_speed(speeds_all, "火灵")
        bj_speed_list = get_suit_pos_fast_speed(speeds_all, "蚌精")
        rnss_speed_list = get_suit_pos_fast_speed(speeds_all, "日女巳时")
        gq_speed_list = get_suit_pos_fast_speed(speeds_all, "共潜")
        # 散件满速、散件列表
        sj_sum, speeds_sj_list = cal_speed_sum_num(speeds_all, 1)
        mz_info, dk_info = parse.find_yuhun_mzdk(speeds_all, False)
        # 二号位
        head_info = parse.find_yuhun_head(speeds_all, False)
    except Exception as e:
        print(e)
    # 散件一速
    fast_speed_list = [
        {
            "suit_name": "散件",
            "speed_sum": sj_sum,
            "speed_list": speeds_sj_list,
        }
    ]

    for suit_name in parse.yuhun_list:
        if suit_name in ["招财猫", "火灵", "蚌精", "共潜", "日女巳时"]:
            sp_list, sp_sum = cal_suit_speed(speeds_all, speeds_sj_list, suit_name)
            fast_speed_list.append({
                "suit_name": suit_name,
                "speed_sum": round(sp_sum, 4),
                "speed_list": sp_list,
            })

    data.update({
        "speed_infos": {
            "head_info": head_info,
            "mz_info": mz_info,
            "dk_info": dk_info,
        },
        "suit_speed": sorted(fast_speed_list, key=lambda e: e["speed_sum"], reverse=True)
    })
    data.update({
        "zc_speed_list": zc_speed_list
    })
    data.update({
        "hl_speed_list": hl_speed_list
    })
    data.update({
        "bj_speed_list": bj_speed_list
    })
    data.update({
        "gq_speed_list": gq_speed_list
    })
    data.update({
        "rnss_speed_list": rnss_speed_list
    })
    # data.update({
    #     "dmg_yuhun_6_str": dmg_yuhun_6_str
    # })
    # data.update({
    #     "dmg_yuhun_6_num": dmg_yuhun_6_num
    # })
    return data


def diffrent_data(json1, json2):
    js1 = change_json_key(json1)
    speed_infos = js1["speed_infos"]
    head_info = speed_infos["head_info"]
    mz_info = speed_infos["mz_info"]
    dk_info = speed_infos["dk_info"]
    del js1['speed_infos']
    temp1_json = OrderedDict()
    temp1_json.update({"二号位个数": len(head_info["value_list"])})
    temp1_json.update({"二号位": get_str(head_info["value_list"])})
    temp1_json.update({"命中满速个数": len(mz_info["value_list"])})
    temp1_json.update({"命中满速": get_str(mz_info["value_list"])})
    temp1_json.update({"抵抗满速个数": len(dk_info["value_list"])})
    temp1_json.update({"抵抗满速": get_str(dk_info["value_list"])})
    temp1_json.update(get_suit_dict(js1["suit_speed"]))
    for key, v in js1.items():
        temp1_json[key] = v

    js2 = change_json_key(json2)
    speed_infos = js2["speed_infos"]
    head_info = speed_infos["head_info"]
    mz_info = speed_infos["mz_info"]
    dk_info = speed_infos["dk_info"]
    del js2['speed_infos']
    temp2_json = OrderedDict()
    temp2_json.update({"二号位个数": len(head_info["value_list"])})
    temp2_json.update({"二号位": get_str(head_info["value_list"])})
    temp2_json.update({"命中满速个数": len(mz_info["value_list"])})
    temp2_json.update({"命中满速": get_str(mz_info["value_list"])})
    temp2_json.update({"抵抗满速个数": len(dk_info["value_list"])})
    temp2_json.update({"抵抗满速": get_str(dk_info["value_list"])})
    temp2_json.update(get_suit_dict(js2["suit_speed"]))
    for key, v in js2.items():
        temp2_json[key] = v
    print(temp1_json['散件'])
    print(temp2_json['散件'])
    return compare_json(temp1_json, temp2_json)
