# -*- coding:utf-8 -*-
"""
@Time: 2022/9/1上午10:53
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: data_parse.py
@Detail: 藏宝阁数据解析
"""
import os
import copy
import json
import requests
from pypinyin import pinyin, Style, lazy_pinyin

from utils.common_functions import get_md5

# 典藏皮肤
dc_skin = [
    "永夜无眠", "炎义丹襟", "莲华一梦", "天曜神行",
    "晴海千花", "华光赤堇", "灭道殉神", "百鬼夜行",
    "琥珀龙魂", "金鳞航梦", "蛉魂梦使", "浮生若梦",
    "星坠之风", "福鲤霓裳", "锦羽金鹏", "胧月",
    "古桥水巷", "花引冥烛", "蝶步韶华", "响魂醉曲",
    "青莲蜕梦", "晴雨伴虹", "青鸾华影", "睦月神祈",
    "紫藤花烬", "化烟", "神宫金社", "海原藏心", "海原藏心·臻藏",
    "永凝珀心", "风宵耀火", "侍怨神婚"
]
# 庭院皮肤
ty_skin = [
    "天穹之境", "烬夜韶阁", "织梦莲庭",
    "暖池青苑", "远海航船", "盛夏幽庭",
    "枫色秋庭", "雪月华庭", "暖春翠庭",
]
# 手办框
shouban_head = [
    "玉面妖狐", "大江山之主", "契", "神意御骨", "麓鸣烁浪",
    "倦鸟眠花", "彼岸天光", "年年有余", "金羽焕夜", "星火漫天",
    "星陨之刻", "九尾幽梦", "无垢莲华", "蛇影裁决", "本味初心",
]
# 限定皮肤卷
cbg_special_skin = {
    "currency_908702": "玉藻前·墨雨胧山兑换券",
    "currency_908703": "空相面灵气·砚隐千面兑换券",
    "currency_413564": ""
}

cbg_special_skin2 = {
    "currency_412197": "狮子狂歌(限定)",
    "currency_413003": "净魂狐焰(限定)",
    "currency_413222": "炽火钢躯(限定)"
}
# 崽战
zaizhan_list = [
    ("901224", "战·百鬼之主"), ("901154", "百鬼之主"),
    ("901225", "战·大阴阳师"), ("901153", "大阴阳师"),
    ("901152", "京都名士")
]
# 氪金
kejin_list = [
    ("901130", "京都之主"), ("901240", "鲤跃金松")
]
yaozhige_list = [
    "金曜符纸", "琉金凤蝶", "金霜之叶", "金之华坠",
    "金鳞云龙", "金瞳妖影", "凤鸣金羽", "御风金影",
    "流金纸扇·守", "璃金纸伞·狱", "金凰法杖·陨", "散金箭矢·诛",
    "流金纸扇·星", "璃金纸伞·疾", "金凰法杖·卜", "散金箭矢·影",
    "随云吟啸", "寇梢含枝", "青羽衔铃", "影山豹形", "隐金游龙",
    "迷金掠蝶", "辰落虚凰", "杏鸣穿金", "流金纸扇·灭",
    "璃金纸伞·蝶", "金凰法杖·咒", "散金箭矢·探",
]


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
            pos = i["位置"]
            if pos in result:
                result[pos].append(i)
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

    def find_yuhun_head(self, data_info, is_abridge=True, min_value=15):
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
                    if is_abridge:
                        yh_type = get_abridge(data["类型"])
                    else:
                        yh_type = data["类型"]
                    value = {"yh_type": yh_type, "speed": speed}
                    head_info.append(value)
        return self.set_speed_infos(head_info)

    def find_yuhun_mzdk(self, data_info, is_abridge=True):
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
                                if is_abridge:
                                    yh_type = get_abridge(data["类型"])
                                else:
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
            mitama_pos = str(mitama_info['pos'])  # 位置pos
            mitama_name = mitama_info['name']  # 御魂名称
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
            mitama_attrs['uuid'] = mitama_info['uuid']
            mitama_attrs["位置"] = mitama_pos
            mitama_attrs["类型"] = mitama_name
            mitama_attrs_all.append(mitama_attrs)

        return mitama_attrs_all

    @staticmethod
    def cal_time(n_seconds: int) -> str:
        """
        计算加成时间
        :param n_seconds: 秒
        :return:
        """
        hour = round(n_seconds / 3600, 2)
        time_str = f"{round(hour / 24, 1)}d" if hour >= 24 else f"{hour}h"
        return time_str

    @staticmethod
    def cbg_parse(datas, is_yuhun=True):
        """藏宝阁数据解析"""
        equip = datas.get('equip', None)
        if not equip:
            print("no equip")
            return None

        # seller_roleid = equip["seller_roleid"]
        seller_roleid = ""
        game_ordersn = equip["game_ordersn"]
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
        fengzidu = equip_desc.get('fengzidu', 0)  # 风姿度
        sign_days = equip_desc["sign_days"]  # 签到时间
        yuhun_buff = equip_desc.get('yuhun_buff', -1)  # 御魂加成
        money = equip_desc.get('money', 0)  # 金币
        goyu = equip_desc.get('goyu', 0)  # 勾玉
        hunyu = equip_desc.get('hunyu', 0)  # 魂玉
        strength = equip_desc.get('strength', 0)  # 体力
        ssr_coin = equip_desc.get('ssr_coin', 0)  # SSR未收录
        sp_coin = equip_desc.get('sp_coin', 0)  # SP未收录
        gameble_card = equip_desc.get('gameble_card', 0)  # 蓝票
        equips_summary = equip_desc["equips_summary"]  # 御魂总数
        level_15 = equip_desc["level_15"]  # 15+御魂
        currency_900217 = equip_desc.get('currency_900217', 0)  # 逆鳞
        currency_900218 = equip_desc.get('currency_900218', 0)  # 逢魔之魂
        currency_900041 = equip_desc.get('currency_900041', 0)  # 痴卷
        ar_gamble_card = equip_desc.get('ar_gamble_card', 0)  # 现实符咒
        lbscards = equip_desc.get('lbscards', {})  # 结界卡
        lbscards_sum = 0
        if lbscards:
            for k, v in lbscards.items():
                lbscards_sum += int(v["num"])
        skin = equip_desc["skin"]  # 皮肤 dict
        yard_list = [ty for ty in ty_skin if ty in list(map(lambda x: x[1], skin.get('yard', [])))]  # 庭院
        yaozhige = int((len(skin["guard"]) - 4) / 2)
        head_skin = equip_desc["head_skin"]  # 头像框
        shouban_list = [value for key, value in head_skin.items() if value in shouban_head]  # 手办框
        data_skin_hero = [item[1] for item in skin['ss']]
        dc_list = [name for name in dc_skin if name in data_skin_hero]  # 典藏皮肤
        yzg = equip_desc["yzg"]  # 曜之阁
        yzq = equip_desc["currency_900073"]  # 曜之契
        yzg_number = (len(yzg.get('effect', [])) + yzq) / 2  # 曜之阁期数
        head_skin_count = equip_desc["head_skin_count"]
        ss_skin_count = [v[1] for key, value in equip_desc['skin'].items() for v in value if key == 'ss']  # 式神皮肤总数
        # 崽战
        _zaizhan = list(
            map(
                lambda x: f"{str(head_skin_count[x[0]]) + x[1] if head_skin_count[x[0]] > 1 else x[1]}" if x[
                                                                                                               0] in head_skin_count else False,
                zaizhan_list
            )
        )
        zaizhan_str = ", ".join([_ for _ in _zaizhan if _ is not False])
        # 氪金
        _kejin = list(
            map(
                lambda x: f"{x[1] + '·(金)' if head_skin_count[x[0]] > 1 else x[1]}" if x[
                                                                                            0] in head_skin_count else False,
                kejin_list
            )
        )
        yzg_str = f"{int(yzg_number)}期曜之阁" if yzg_number != 0 else ""
        if len(yzg_str) == 0:
            kejin_str = ", ".join([_ for _ in _kejin if _ is not False])
        else:
            kejin_str = yzg_str

        inventory = None
        if is_yuhun:
            inventory = equip_desc.get('inventory', None)  # 御魂
        # 限定皮肤兑换券
        special_skin_list = equip_desc.get('cbg_special_skin_list', [])
        cbg_special_skin_list2 = equip_desc.get('cbg_special_skin_list_2', [])
        special_skin_str2 = ""
        special_skin_str = ""
        try:
            if special_skin_list:
                special_skin = [f"{cbg_special_skin[k]}" for k, v in special_skin_list.items() if v != 0]
                if special_skin:
                    special_skin_str = ", ".join(special_skin)
            if cbg_special_skin_list2:
                special_skin2 = [f"{cbg_special_skin2[k]}" for k, v in cbg_special_skin_list2.items() if v > 1]
                if special_skin2:
                    special_skin_str2 = ", ".join(special_skin2)
        except Exception as e:
            print(e)

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
        hero_history = equip_desc["hero_history"]
        sp_dict = hero_history.get('sp', {})
        ssr_dict = hero_history.get('ssr', {})
        sp_flag = 1
        ssr_flag = 1
        if sp_dict.get('got', 0) != sp_dict.get('all', 1):
            sp_flag = -1
        if ssr_dict.get('got', 0) != ssr_dict.get('all', 1):
            ssr_flag = -1
        return {
            "game_ordersn": game_ordersn,
            "new_roleid": new_roleid, "seller_roleid": seller_roleid,
            "equip_name": seller_name, "server_name": server_name,
            "create_time": create_time, "status_des": status_desc,
            "collect_num": collect_num, "fair_show_end_time": fair_show_end_time,
            "platform_type": platform_type, "equip_level": equip_level,
            "highlights": ",".join(highlights), "equip_server_sn": equip_server_sn,
            "desc_sumup_short": desc_sumup_short, "price": price,
            "sign_days": sign_days, "yuhun_buff": yuhun_buff,
            "level_15": level_15, "money": money, "goyu": goyu,
            "hunyu": hunyu, "strength": strength, "gameble_card": gameble_card,
            "equips_summary": equips_summary, "currency_900217": currency_900217,
            "currency_900218": currency_900218, "currency_900041": currency_900041,
            "ar_gamble_card": ar_gamble_card, "inventory": inventory,
            "lbscards_sum": lbscards_sum, "fengzidu": fengzidu,
            "yard_list": yard_list,
            "yaozhige": yaozhige if yaozhige > 0 else None,
            "shouban_list": shouban_list,
            "dc_list": dc_list,
            "zaizhan_str": zaizhan_str,
            "kejin_str": kejin_str,
            "ss_skin_count": len(ss_skin_count) if isinstance(ss_skin_count, list) else 0,
            "sp_coin": sp_coin,
            "ssr_coin": ssr_coin,
            "special_skin_str1": special_skin_str,
            "special_skin_str2": special_skin_str2,
            "ssr_flag": ssr_flag,
            "sp_flag": sp_flag
        }


def get_speeds_all(data_info):
    """获取所有含有速度御魂"""
    speeds_all = {}
    for i in range(1, 7):
        num = str(i)
        data_info[num] = select_speed(data_info[num])
        speeds_all[num] = list_dict_order_by_key(data_info[num], "速度")
    return speeds_all


def get_full_speed_number(speeds_all, standard_speed=15):
    """获取满速个数"""
    _sum = 0
    for pos, value in speeds_all.items():
        temp_standard = standard_speed
        if pos == '2':
            temp_standard = 57 + standard_speed
        for _ in value:
            if _["速度"] >= temp_standard:
                _sum += 1
    return _sum


def remove_independent_speed(speeds_all, n):
    """移除独立速度"""
    new_speeds_all = copy.deepcopy(speeds_all)
    for i in range(1, 7):
        for x in range(n):
            del new_speeds_all[str(i)][n - 1]
    return new_speeds_all


def cal_speed_sum_num(speeds_all, n):
    """
    计算独立散件速度
    :param speeds_all: 含有速度所有御魂列表
    :param n:
    :return:
    """
    try:
        _sum = 0
        speeds_list = []
        for i in range(1, 7):
            speed = speeds_all[str(i)][n - 1]["速度"]
            yh_type = speeds_all[str(i)][n - 1]["类型"]
            _sum += speed
            info = {"位置": i, "类型": yh_type, "速度": round(speed, 8)}
            speeds_list.append(info)

        return _sum, speeds_list
    except:
        return 0, 0


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


def get_suit_pos_fast_speed(speeds_all, suit_name="招财猫"):
    """
    获取套装各个位置最快速度
    :param speeds_all:
    :param suit_name:
    :return:
    """
    speeds_list = []
    for i in range(1, 7):
        for y in speeds_all[str(i)]:
            if y["类型"] == suit_name:
                speeds_list.append({
                    "位置": i,
                    "类型": y["类型"],
                    "速度": round(y["速度"], 8) if y["速度"] else 0
                })
                break
    return speeds_list


def cal_suit_speed(speeds_all, speed_sj_list, suit_name="招财猫"):
    """
    计算套装一速
    :param speeds_all:  所有速度御魂
    :param speed_sj_list:   散件速度数组
    :param suit_name: 御魂类型
    :return:
    """
    sp_list = []
    sp_sum = 0
    compare = [1, 2, 3, 4, 5, 6]
    speed_list = get_suit_pos_fast_speed(speeds_all, suit_name)
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


def get_speed_info(json_data, full_speed=155):
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
    # 速度御魂列表
    speeds_all = get_speeds_all(data_info)
    # 满速个数
    full_speed_num = get_full_speed_number(speeds_all, 15)
    data.update({"full_speed_num": full_speed_num})
    # 二号位
    head_info = parse.find_yuhun_head(speeds_all, False)
    # 命中、抵抗
    mz_info, dk_info = parse.find_yuhun_mzdk(speeds_all, False)
    # 散件满速、散件列表
    sj_sum, speeds_sj_list = cal_speed_sum_num(speeds_all, 1)
    sj_sum2, speeds_sj_list_2 = cal_speed_sum_num(speeds_all, 2)

    # 除散件一速后独立招财
    speeds_all2 = remove_independent_speed(speeds_all, 1)
    zc_sp_list, zc_sp_sum = cal_suit_speed(speeds_all2, speeds_sj_list_2, "招财猫")

    # 散件一速
    fast_speed_list = [
        {
            "suit_name": "散件",
            "speed_sum": sj_sum,
            "speed_list": list(filter_chinese(speeds_sj_list)),
        },
        {
            "suit_name": "除散件外独立招财",
            "speed_sum": zc_sp_sum,
            "speed_list": list(filter_chinese(zc_sp_list)),
        }
    ]
    # print(fast_speed_list)
    # 独立招财
    # 默认筛选套装满速大于155
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
    data.update({
        "speed_infos": {
            "head_info": head_info,
            "mz_info": mz_info,
            "dk_info": dk_info,
        },
        "suit_speed": sorted(fast_speed_list, key=lambda e: e["speed_sum"], reverse=True)
    })
    return data


def find_yuhun_uuid(dts):
    """查找御魂246号uuid"""
    uuid_list = {}
    for k, values in dts.items():
        if k == '2':
            uuid_list["2"] = []
            for item in values:
                if '速度' in item.keys() and item['速度'] >= (57 + 15):
                    uuid_list["2"].append(item)
        elif k == '4':
            uuid_list["4"] = []
            for item in values:
                if '速度' in item.keys() and item['速度'] > 15:
                    if '效果抵抗' in item.keys() and item['效果抵抗'] >= 55:
                        uuid_list["4"].append(item)
                    if '效果命中' in item.keys() and item['效果命中'] >= 55:
                        uuid_list["4"].append(item)
        elif k == '6':
            uuid_list["6"] = []
            for item in values:
                if '暴击伤害' in item.keys() and item['暴击伤害'] >= 89:
                    uuid_list["6"].append(item)

    uuid_list['2'] = list_dict_order_by_key(uuid_list['2'], "速度", True)
    uuid_list['4'] = list_dict_order_by_key(uuid_list['4'], "速度", True)
    uuid_list['6'] = list_dict_order_by_key(uuid_list['6'], "暴击伤害", True)
    return uuid_list


def choose_best_uuid(infos: dict):
    """
    选择最优uuid：先找头尾满速，然后找6号为爆伤
    :return:
    """
    uuid_json = []
    pos_2 = infos.get('2', [])
    pos_4 = infos.get('4', [])
    pos_6 = infos.get('6', [])
    if pos_2:
        for pos in pos_2:
            uuid_json.append(pos['uuid'])
    if pos_4:
        for pos in pos_4:
            uuid_json.append(pos['uuid'])
    if pos_6:
        for pos in pos_6:
            uuid_json.append(pos['uuid'])
    return uuid_json


if __name__ == '__main__':
    game_ordersn = "202212042101616-12-OTUU52VLMAQHO"
    game_ordersn = "202212090901616-11-4E1Y8DJCKGP6J"
    # game_ordersn = "202212092301616-12-4KCXKCSVWCKGM"
    game_ordersn = "202212031101616-12-ZHGU5BC5FIK5B"  # 百鬼之主
    # game_ordersn = "202210302101616-12-Q4GEFZSWWJUNV"
    # game_ordersn = "202211091201616-7-Z3VMTFBMHISOHI"
    file = game_ordersn + ".json"
    with open(file, "r") as f:
        json_data = json.loads(f.read())
    equip_desc = json.loads(json_data["equip"]["equip_desc"])

    del equip_desc["inventory"]
    del equip_desc["hero_fragment"]
    del equip_desc["lbscards"]
    del equip_desc["hero_count_dict"]
    del equip_desc["heroes"]
    del equip_desc["prefab_team"]  # 预设阵容

    print(equip_desc)
