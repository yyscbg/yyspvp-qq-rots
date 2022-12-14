# -*- coding:utf-8 -*-
"""
@Time: 2022/9/1上午10:53
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: data_parse.py
@Detail: 藏宝阁数据解析
"""
import os
import json
import hashlib
import requests
from pypinyin import pinyin, Style, lazy_pinyin


def get_md5(_str):
    m = hashlib.md5()
    m.update(bytes(_str, encoding='utf-8'))
    return m.hexdigest()


def select_speed(dts):
    """
    选中速度
    :param dts:
    :return:
    """
    for dt in dts:
        if "速度" not in dt:
            dt["速度"] = 0
        yield dt


def get_abridge(_str, is_all=True):
    """
    中文缩写或全拼
    :param _str:
    :return:
    """
    if is_all is not True:
        return ''.join(list(map(lambda x: x[0], pinyin(_str, style=Style.FIRST_LETTER))))
    else:
        return '_'.join(lazy_pinyin(_str))


def list_dict_order_by_key(list_data, key, revrese=True):
    """
    list中的dict按照某个key排序
    # 另一种方法
    # from operator import itemgetter
    # trends = sorted(trends,key = itemgetter('速度'),reverse = True)
    :param list_data:
    :param key:
    :param revrese:
    :return:
    """
    return sorted(list_data, key=lambda e: e[key], reverse=revrese)


class CbgDataParser:
    """藏宝阁数据解析"""

    def __init__(self, yuhun_json_file="./yuhun.json"):
        if not os.path.exists(yuhun_json_file):
            self.yuhun_list = self.get_yuhun_list()
        else:
            with open(yuhun_json_file, "r") as fi:
                self.yuhun_list = json.loads(fi.read())
        if not self.yuhun_list:
            raise ValueError("yuhun_list must exist")

    @staticmethod
    def get_yuhun_list():
        """获取御魂列表"""
        try:
            YUHUN_URL = "https://s.166.net/config/bbs_yys/yuhun.json"
            yuhun_info = requests.get(YUHUN_URL).json()
            return [v["name"] for k, v in yuhun_info.items()]
        except requests.exceptions as e:
            print(f"御魂列表获取失败：{e}")

    @staticmethod
    def sort_pos(dts):
        """
        御魂分组
        :param dts:
        :return:
        """
        result = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": []}
        for i in dts:
            if i["位置"] == "1":
                result["1"].append(i)
            elif i["位置"] == "2":
                result["2"].append(i)
            elif i["位置"] == '3':
                result["3"].append(i)
            elif i["位置"] == "4":
                result["4"].append(i)
            elif i["位置"] == "5":
                result["5"].append(i)
            else:
                result["6"].append(i)
        return result

    @staticmethod
    def set_speed_infos(value_list):
        """设置速度数据"""
        sum_value = len(value_list)
        max_info = {"yh_type": None, "max_value": None}
        if sum_value > 0:
            value_list = list_dict_order_by_key(value_list, "speed", True)
            max_info = {"yh_type": value_list[0]["yh_type"], "max_value": value_list[0]["speed"]}
        return {"sum_value": sum_value, "max_info": max_info, "value_list": value_list}

    def find_yuhun_head(self, data_info):
        """
        查找二号位满速
        :param data_info:
        :return:
        """
        head_info = []
        for data in data_info["2"]:
            if "速度" in data:
                if data["速度"] > 72:
                    speed = round(data["速度"] - 57, 5)
                    # yh_type = get_abridge(data["类型"])
                    yh_type = data["类型"]
                    value = {"yh_type": yh_type, "speed": speed}
                    head_info.append(value)
        return self.set_speed_infos(head_info)

    def find_yuhun_mzdk(self, data_info):
        """
        查找命中、抵抗满速（筛选四号位、含速度、大于15速、主属性55以上）
        :param data_info:
        :return:
        """
        yuhun_mz = []
        yuhun_dk = []
        for data in data_info["4"]:
            if "速度" in data:
                if data["速度"] > 15:
                    for pos4_name in ["效果抵抗", "效果命中"]:
                        if pos4_name in data:
                            if data[pos4_name] >= 55:
                                speed = round(data["速度"], 8)
                                # yh_type = get_abridge(data["类型"])
                                yh_type = data["类型"]
                                value = {"yh_type": yh_type, "speed": speed}
                                if "抵抗" in pos4_name:
                                    yuhun_dk.append(value)
                                else:
                                    yuhun_mz.append(value)
                                break
        mz_infos = self.set_speed_infos(yuhun_mz)
        dk_infos = self.set_speed_infos(yuhun_dk)
        return mz_infos, dk_infos

    @staticmethod
    def cal_yuhun(rattrs):
        """
        计算御魂数值
        :param rattrs:
        :return:
        """
        en_names = [
            'attackAdditionRate', 'attackAdditionVal', 'critPowerAdditionVal',
            'critRateAdditionVal', 'debuffEnhance', 'debuffResist',
            'defenseAdditionRate', 'defenseAdditionVal', 'maxHpAdditionRate',
            'maxHpAdditionVal', 'speedAdditionVal'
        ]
        cn_names = [
            '攻击加成', '攻击', '暴击伤害', '暴击',
            '效果命中', '效果抵抗', '防御加成',
            '防御', '生命加成', '生命', '速度'
        ]
        base_value = {
            '攻击加成': 3, '攻击': 27, '暴击伤害': 4, '暴击': 3,
            '效果抵抗': 4, '效果命中': 4, '防御加成': 3,
            '防御': 5, '生命加成': 3, '生命': 114, '速度': 3
        }
        names_map = dict(list(zip(en_names, cn_names)))
        res = {}
        for prop, v in rattrs:
            prop = names_map[prop]
            if prop not in res:
                res[prop] = 0
            res[prop] += v
        return [[p, round(res[p] * base_value[p], 5)] for p in res]

    def init_yuhun(self, inventory):
        """
        初始化御魂
        :param inventory: json中字段名
        :return:
        """
        mitama_attrs_all = []
        for mitama_id in inventory:
            mitama_info = inventory[mitama_id]
            if int(mitama_info['level']) < 15:
                continue
            mitama_pos = str(mitama_info['pos'])
            mitama_name = mitama_info['name']
            mitama_attrs = dict()
            if 'rattr' in mitama_info:
                # 主属性从attrs获取
                base_prop = mitama_info['attrs'][0]
                mitama_attrs[base_prop[0]] = float(base_prop[1].replace('%', ''))
                # 副属性由rattr的强化记录进行推导
                for prop, value in self.cal_yuhun(mitama_info['rattr']):
                    if prop not in mitama_attrs:
                        mitama_attrs[prop] = value
                    else:
                        mitama_attrs[prop] += value
            else:
                for prop, value in mitama_info['attrs']:
                    value = int(value.replace('%', ''))
                    if prop not in mitama_attrs:
                        mitama_attrs[prop] = value
                    else:
                        mitama_attrs[prop] += value

            mitama_attrs["位置"] = mitama_pos
            mitama_attrs["类型"] = mitama_name
            mitama_attrs_all.append(mitama_attrs)

        return mitama_attrs_all

    @staticmethod
    def cal_time(n_seconds: int):
        """
        计算加成时间
        :param n_seconds: 秒
        :return:
        """
        hour = round(n_seconds / 3600, 2)
        if hour >= 24:
            return str(round(hour / 24, 1)) + "d"
        else:
            return str(hour) + "h"

    @staticmethod
    def cbg_parse(datas, is_yuhun=True):
        """藏宝阁数据解析"""
        equip = datas.get('equip', None)
        if not equip:
            print("no equip")
            return None

        # seller_roleid = equip["seller_roleid"]
        seller_roleid = ""
        status_desc = equip["status_desc"]
        equip_desc = equip["equip_desc"]
        fair_show_end_time = equip["fair_show_end_time"]  # 公示期
        platform_type = equip["platform_type"]  # 平台类型 1:ios 2:android
        equip_level = equip["equip_level"]  # 等级
        highlights = equip["highlights"]  # 高亮文字
        server_name = equip["server_name"]  # 区名
        equip_server_sn = equip["equip_server_sn"]  # 区id
        desc_sumup_short = equip["desc_sumup_short"]  # 短描述
        price = equip["price"] / 100  # 价格
        seller_name = equip["seller_name"]  # 卖家
        new_roleid = get_md5(str(equip_server_sn) + seller_name)  # 区+名字
        # selling_time = equip["selling_time"]  # 上架时间
        create_time = equip["create_time"]  # 时间
        collect_num = equip["collect_num"]  # 收藏
        equip_desc = json.loads(equip["equip_desc"])
        sign_days = equip_desc["sign_days"]  # 签到时间
        yuhun_buff = equip_desc.get('yuhun_buff', -1)  # 御魂加成
        money = equip_desc.get('money', 0)  # 金币
        goyu = equip_desc.get('goyu', 0)  # 勾玉
        hunyu = equip_desc.get('hunyu', 0)  # 魂玉
        strength = equip_desc.get('strength', 0)  # 体力
        gameble_card = equip_desc.get('gameble_card', 0)  # 结界卡
        equips_summary = equip_desc["equips_summary"]  # 御魂总数
        level_15 = equip_desc["level_15"]  # 15+御魂

        currency_900217 = equip_desc.get('currency_900217', 0)  # 逆鳞
        currency_900218 = equip_desc.get('currency_900218', 0)  # 逢魔之魂
        currency_900041 = equip_desc.get('currency_900041', 0)  # 痴卷
        ar_gamble_card = equip_desc.get('ar_gamble_card', 0)  # 现实符咒
        currency_900073 = equip_desc.get('currency_900073', 0)  # 蓝票
        inventory = None
        if is_yuhun:
            inventory = equip_desc.get('inventory', None)  # 御魂

        # skin = equip_desc["skin"]                                             # 皮肤 dict
        # gouyu_card = equip_desc.get('gouyu_card', 0)                          # 太鼓
        # pvp_score = equip_desc["pvp_score"]                                   # 斗技分数
        # honor_score = equip_desc["honor_score"]                               # 荣誉
        # redheart = equip_desc["redheart"]                                     # 友情
        # currency_900188 = equip_desc.get('currency_900188', 0)                # 金御札
        # currency_900273 = equip_desc.get('currency_900273', 0)                # 樱饼
        # currency_960010 = equip_desc.get('currency_960010', 0)                # 魅力
        # currency_900120 = equip_desc.get('currency_900120', 0)                # 式神挑战卷
        # currency_900215 = equip_desc.get('currency_900215', 0)                # 御灵之境
        # currency_900216 = equip_desc.get('currency_900216', 0)                # 鳞片
        # currency_906058 = equip_desc.get('currency_906058', 0)                # 皮肤卷
        # currency_906058 = equip_desc.get('currency_906058', 0)                # sp皮肤卷
        # currency_900007 = equip_desc.get('currency_900007', 0)                # 百鬼夜行门票

        return {
            "new_roleid": new_roleid,
            "seller_roleid": seller_roleid,
            "equip_name": seller_name,
            "server_name": server_name,
            "create_time": create_time,
            "status_des": status_desc,
            "collect_num": collect_num,
            "fair_show_end_time": fair_show_end_time,
            "platform_type": platform_type,
            "equip_level": equip_level,
            "highlights": ",".join(highlights),
            "equip_server_sn": equip_server_sn,
            "desc_sumup_short": desc_sumup_short,
            "price": price,
            "sign_days": sign_days,
            "yuhun_buff": yuhun_buff,
            "level_15": level_15,
            "money": money,
            "goyu": goyu,
            "hunyu": hunyu,
            "strength": strength,
            "gameble_card": gameble_card,
            "equips_summary": equips_summary,
            "currency_900217": currency_900217,
            "currency_900218": currency_900218,
            "currency_900041": currency_900041,
            "ar_gamble_card": ar_gamble_card,
            "inventory": inventory,
            "currency_900073": currency_900073
        }


def cal_speed_sum_num(data_info, n):
    """
    计算独立散件速度
    :param data_info:
    :param n:
    :return:
    """
    speeds_all = {}
    for i in range(1, 7):
        num = str(i)
        data_info[num] = select_speed(data_info[num])
        speeds_all[num] = list_dict_order_by_key(data_info[num], "速度")

    _sum = 0
    speeds_list = []
    for i in range(1, 7):
        # pos = i
        speed = speeds_all[str(i)][n - 1]["速度"]
        yh_type = speeds_all[str(i)][n - 1]["类型"]
        _sum += speed
        info = {"位置": i, "类型": yh_type, "速度": round(speed, 8)}
        speeds_list.append(info)

    return speeds_all, _sum, speeds_list


def filter_chinese(sp_li):
    """
    过滤中文改为缩写，为了减少存储
    :param sp_li:
    :return:
    """
    for sp in sp_li:
        speed = {}
        for k, v in sp.items():
            if k == "位置":
                k = "pos"
            elif k == "类型":
                k = "yh_type"
                # v = get_abridge(v)
            else:
                k = "speed"
            speed[k] = v
        yield speed


def cal_suit_speed(speeds_all, speed_sj_list, suit_name="招财猫"):
    """
    计算套装一速
    :param speeds_all:  所有速度御魂
    :param speed_sj_list:   散件速度数组
    :param suit_name: 御魂类型
    :return:
    """
    speed_list = []
    sp_list = []
    for i in range(1, 7):
        pos = i
        for y in speeds_all[str(pos)]:
            # speed = 0
            if y["类型"] == suit_name:
                speed = y["速度"]
                _type = y["类型"]
                speed_zc = {
                    "位置": pos,
                    "类型": _type,
                    "速度": round(speed, 8) if speed else 0
                }
                speed_list.append(speed_zc)
                break
    # print(speed_zc_list)
    sp_sum = 0
    compare = [1, 2, 3, 4, 5, 6]
    lens = len(speed_list)
    for a in range(0, lens):
        for b in range(a + 1, lens):
            for c in range(b + 1, lens):
                for d in range(c + 1, lens):
                    a1 = speed_list[a]["速度"]
                    a1_pos = speed_list[a]["位置"]

                    b1 = speed_list[b]["速度"]
                    b1_pos = speed_list[b]["位置"]

                    c1 = speed_list[c]["速度"]
                    c1_pos = speed_list[c]["位置"]

                    d1 = speed_list[d]["速度"]
                    d1_pos = speed_list[d]["位置"]

                    delete = [a1_pos, b1_pos, c1_pos, d1_pos]
                    result = list(set(compare).difference(set(delete)))
                    e = result[0] - 1
                    f = result[1] - 1
                    e1 = speed_sj_list[e]["速度"]
                    f1 = speed_sj_list[f]["速度"]
                    _sum = a1 + b1 + c1 + d1 + e1 + f1
                    if _sum >= sp_sum:
                        sp_sum = round(_sum, 8)
                        sp_list = [
                            speed_list[a],
                            speed_list[b],
                            speed_list[c],
                            speed_list[d],
                            speed_sj_list[e],
                            speed_sj_list[f]
                        ]
                        sp_list = list_dict_order_by_key(sp_list, "位置", False)

    return sp_list, sp_sum


def get_speed_info(json_data, full_speed=150):
    """
    合并成es索引结构数据
    :param json_data:
    :param full_speed:
    :return:
    """
    parse = CbgDataParser()
    data = parse.cbg_parse(json_data)
    yuhun_json = parse.init_yuhun(data["inventory"])
    # 御魂分组1-6
    data_info = parse.sort_pos(yuhun_json)
    # 速度御魂列表、散件满速、散件列表
    speeds_all, sj_sum, speeds_sj_list = cal_speed_sum_num(data_info, 1)
    # 命中、抵抗
    mz_info, dk_info = parse.find_yuhun_mzdk(speeds_all)
    # 二号位
    head_info = parse.find_yuhun_head(speeds_all)

    fast_speed_list = [{
        # "suit_name": "san_jian",
        "suit_name": "散件",
        "speed_sum": sj_sum,
        "speed_list": list(filter_chinese(speeds_sj_list)),
        # "speed_list": speeds_sj_list,
    }]
    # 默认筛选套装满速大于150
    for suit_name in parse.yuhun_list:
        sp_list, sp_sum = cal_suit_speed(speeds_all, speeds_sj_list, suit_name)
        if sp_sum > full_speed:
            fast_speed_list.append({
                # "suit_name": get_abridge(suit_name),
                "suit_name": suit_name,
                "speed_sum": round(sp_sum, 4),
                "speed_list": list(filter_chinese(sp_list)),
                # "speed_list": sp_list,
            })
    del data["inventory"]
    data.update({
        "speed_infos": {
            "head_info": head_info,
            "mz_info": mz_info,
            "dk_info": dk_info,
        },
        "suit_speed": sorted(fast_speed_list, key=lambda e: e["speed_sum"], reverse=True)
    })
    return data


if __name__ == '__main__':
    game_ordersn = "202210302101616-12-Q4GEFZSWWJUNV"
    from configs.all_config import dir_path

    file = os.path.join(dir_path, game_ordersn + ".json")
    with open(file, "r") as f:
        json_data = json.loads(f.read())
    # info = get_speed_info(json_data, 0)
    # print(info)
    # print(len(info["suit_speed"]))
    parse = CbgDataParser()
    data = parse.cbg_parse(json_data, is_yuhun=False)
    print(data)
