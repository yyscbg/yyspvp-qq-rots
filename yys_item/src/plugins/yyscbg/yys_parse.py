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
    "永凝珀心", "风宵耀火", "侍怨神婚", '千鸟晓光',
    "双栖蝶", "镜生万华", "耀世神武", "耀世神武·臻藏",
]

# 庭院皮肤
ty_skin = [
    "天穹之境", "烬夜韶阁", "织梦莲庭",
    "暖池青苑", "远海航船", "盛夏幽庭",
    "枫色秋庭", "雪月华庭", "暖春翠庭",
    "琼夜淬光", "笔墨山河", "绘世洞天",
]
# 手办框
shouban_head = [
    "玉面妖狐", "大江山之主", "契", "神意御骨", "麓鸣烁浪",
    "倦鸟眠花", "彼岸天光", "年年有余", "金羽焕夜", "星火漫天",
    "星陨之刻", "九尾幽梦", "无垢莲华", "蛇影裁决", "本味初心",
    "樱缘花梦头像框",
]
# 限定皮肤卷
cbg_special_skin = {
    "currency_908702": "玉藻前·墨雨胧山兑换券",
    "currency_908703": "空相面灵气·砚隐千面兑换券",
    "currency_413564": "海原藏心",
    "currency_413891": "耀世神武",
    "currency_908740": "匣中少女·巧偶谜匣兑换券",
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

x_hero = [
    "犬夜叉", "陆生", "鬼灯", "桔梗", "杀生丸"
]

tuizhi_head_skin = [
    "超鬼王·蛇神", "月姬之眷", "涅火蝶舞",
    "超鬼王·海国之主", "海潮逆涌·激流", "大江山之战·海伐",
    "超鬼王·大妖试炼", "超鬼王·森林之王", "四季生·惜",
]

interstage_skin = [
    ('currency_1500001', '契光水境'),
    ('currency_1500002', '穹宇垂帘'),
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

    def find_yuhun_mzdk(self, data_info, is_abridge=False):
        """
        查找命中、抵抗满速（筛选四号位、含速度、大于15速、主属性55以上）
        :param data_info:
        :return:
        """
        yuhun_mz = []
        yuhun_dk = []
        index_dk = 1
        index_mz = 1
        for data in data_info["4"]:
            if "速度" in data:
                if data["速度"] > 15:
                    for pos4_name in ["效果抵抗", "效果命中"]:
                        if pos4_name in data:
                            if data[pos4_name] >= 55:
                                speed = round(data["速度"], 2)
                                if is_abridge:
                                    yh_type = get_abridge(data["类型"])
                                else:
                                    yh_type = data["类型"]
                                value = {"yh_type": yh_type, "speed": speed, "uuid": data['uuid']}
                                if "抵抗" in pos4_name:
                                    value.update({"index": index_dk})
                                    index_dk += 1
                                    yuhun_dk.append(value)
                                else:
                                    value.update({"index": index_mz})
                                    index_mz += 1
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
    def cbg_parse(datas, is_yuhun=True, x_hero=x_hero):
        """
        解析数据
        :param datas:  数据
        :param is_yuhun: 御魂
        :param x_hero: 联动种类
        :return:
        """
        equip = datas.get('equip', None)
        if not equip:
            print("no equip")
            return None
        # seller_roleid = equip["seller_roleid"]
        seller_roleid = ""
        allow_bargain = equip['allow_bargain']
        game_ordersn = equip['game_ordersn']
        status_desc = equip["status_desc"]
        diy_desc = equip.get('diy_desc', "")  # 卖家说
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
        # selling_time = equip.get('selling_time')  # 上架时间
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
        ssr_sp_coin = equip_desc.get('currency_490017', 0)  # SP/SSR自选
        gameble_card = equip_desc.get('gameble_card', 0)  # 蓝票
        equips_summary = equip_desc.get('equips_summary', 0)  # 御魂总数
        level_15 = equip_desc.get('level_15', 0)  # 15+御魂
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
        gamble = skin.get('gamble', [])
        gamble_list = [_[1] for _ in gamble]
        yard_list = [ty for ty in ty_skin if ty in list(map(lambda x: x[1], skin.get('yard', [])))]  # 庭院
        head_skin = equip_desc["head_skin"]  # 头像框

        tuizhi_list = [value for key, value in head_skin.items() if value in tuizhi_head_skin]  # 退治框
        shouban_list = [value for key, value in head_skin.items() if value in shouban_head]  # 手办框
        data_skin_hero = [item[1] for item in skin['ss']]
        dc_list = [name for name in dc_skin if name in data_skin_hero]  # 典藏皮肤
        ss_skin_list = [v[1] for key, value in equip_desc['skin'].items() for v in value if key == 'ss']  # 式神皮肤
        yys_skin_list = [v[1] for key, value in equip_desc['skin'].items() for v in value if key == 'yys']  # 主角皮肤
        yzg = equip_desc.get('yzg', {})  # 曜之阁
        yzq = equip_desc.get('currency_900073', 0)  # 曜之契
        yzg_number = (len(yzg.get('effect', [])) + yzq) / 2  # 曜之阁期数
        head_skin_count = equip_desc.get('head_skin_count', [])
        if len(head_skin_count) == 0:
            _zaizhan = ""
            zaizhan_str = ""
            _kejin = []
            tuizhi_head = []
        else:
            # 崽战
            _zaizhan = [f"{str(head_skin_count[x[0]]) + x[1] if head_skin_count.get(x[0], 0) > 1 else x[1]}" for x in
                        zaizhan_list if head_skin_count.get(x[0])]

            zaizhan_str = ", ".join([_ for _ in _zaizhan if _ is not False])
            # 氪金
            _kejin = [f"{x[1]}·(金)" if head_skin_count.get(x[0], 0) > 1 else x[1] for x in kejin_list if
                      x[0] in head_skin_count]

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
        special_skin_str = ""
        special_skin = []
        if special_skin_list:
            special_skin = [f"{cbg_special_skin[k]}" for k, v in special_skin_list.items() if v != 0]
            if special_skin:
                special_skin_str = ", ".join(special_skin)

        cbg_special_skin_list2 = equip_desc.get('cbg_special_skin_list_2', [])
        special_skin_str2 = ""
        special_skin2 = []
        if cbg_special_skin_list2:
            special_skin2 = [f"{cbg_special_skin2[k]}" for k, v in cbg_special_skin_list2.items() if v > 1]
            if special_skin2:
                special_skin_str2 = ", ".join(special_skin2)
        hero_fragment = equip_desc.get('hero_fragment', {})
        # 所有碎片
        all_hero_fragments = [{'num': value['num'], 'name': value['name']} for key, value in hero_fragment.items()]
        # 联动碎片
        x_num = sum([v['num'] for k, v in hero_fragment.items() if v["name"] in x_hero])
        hero_history = equip_desc["hero_history"]
        # 联动已有式神数
        x_dict = hero_history.get('x', {})
        x_have_num = len([1 for k, v in x_dict.items() if isinstance(v, list) and v[1] == 1])
        sp_dict = hero_history.get('sp', {})
        sp_hava_num = sp_dict.get('got', 0)
        ssr_dict = hero_history.get('ssr', {})
        ssr_hava_num = ssr_dict.get('got', 0)
        # sp_flag = 1
        # ssr_flag = 1
        # if sp_dict.get('got', 0) != sp_dict.get('all', 1):
        #     sp_flag = -1
        # if ssr_dict.get('got', 0) != ssr_dict.get('all', 1):
        #     ssr_flag = -1
        # 幕间皮肤
        interstage_skin_list = [_[1] for _ in interstage_skin if equip_desc.get(_[0], 0)]
        # 所有头像框
        # all_skin = equip_desc
        # 所有皮肤

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
            # "selling_time": selling_time,
            "diy_desc": diy_desc,
            "game_ordersn": game_ordersn, "allow_bargain": 1 if allow_bargain else 0,
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
            "yaozhige": yzg_number if yzg_number > 0 else 0,
            "shouban_list": shouban_list,
            "dc_list": dc_list,
            "zaizhan_str": zaizhan_str,
            "zaizhan_list": _zaizhan,
            "kejin_str": kejin_str,
            "tuizhi_list": tuizhi_list,
            "head_skin_list": [value for key, value in head_skin.items()],
            "yys_skin_list": yys_skin_list,
            "ss_skin_list": ss_skin_list,
            "ss_skin_count": len(ss_skin_list) if isinstance(ss_skin_list, list) else 0,
            "sp_coin": sp_coin,
            "ssr_coin": ssr_coin,
            "ssr_sp_coin": ssr_sp_coin,
            "special_skin_str1": special_skin_str,
            "special_skin_list1": special_skin,
            "special_skin_str2": special_skin_str2,
            "special_skin_list2": special_skin2,
            "all_hero_fragments": all_hero_fragments,  # 所有碎片
            "x_num": x_num,  # 联动碎片和
            "x_have_num": x_have_num,  # 联动式神数量
            "sp_hava_num": sp_hava_num,  # sp式神数量
            "ssr_hava_num": ssr_hava_num,  # ssr式神数量
            "gamble_list": gamble_list,  # 召唤屋
            "interstage_skin_list": interstage_skin_list,  # 幕间
        }


def get_speeds_all(data_info):
    """获取所有含有速度御魂"""
    speeds_all = {}
    for i in range(1, 7):
        num = str(i)
        data_info[num] = select_speed(data_info[num])
        speeds_all[num] = list_dict_order_by_key(data_info[num], "速度")
    return speeds_all


def get_full_speed_number(speeds_all, standard_speed=15, is_values=False):
    """获取满速个数"""
    _sum = 0
    result = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": []}
    for pos, value in speeds_all.items():
        temp_standard = standard_speed
        if pos == '2':
            temp_standard = 57 + standard_speed
        for _ in value:
            if _["速度"] >= temp_standard:
                _sum += 1
                result[pos].append(_)
    if not is_values:
        return _sum
    else:
        return _sum, result


def remove_independent_speed(speeds_all, n):
    """移除独立速度"""
    import copy
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
    _sum = 0
    speeds_list = []
    try:
        for i in range(1, 7):
            speed = speeds_all[str(i)][n - 1]["速度"]
            yh_type = speeds_all[str(i)][n - 1]["类型"]
            uuid = speeds_all[str(i)][n - 1]['uuid']
            _sum += speed
            info = {"位置": i, "类型": yh_type, "速度": round(speed, 2), "uuid": uuid}
            speeds_list.append(info)
    except:
        pass
    return _sum, speeds_list


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
                v = v
            elif k == '速度':
                k = "speed"
            speed[k] = v
        yield speed


def get_suit_pos_fast_speed(speeds_all, suit_name="招财猫", is_new=False):
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
                if is_new:
                    speeds_list.append(y)
                else:
                    speeds_list.append({
                        "位置": i,
                        "类型": y["类型"],
                        "速度": round(y["速度"], 2) if y["速度"] else 0,
                        "uuid": y["uuid"]
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
                        sp_sum = round(_sum, 2)
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


def check_include_yuhun(sp_li, uuid_list):
    """检查是否包含特殊御魂"""
    return any(sp['pos'] == 4 and sp['uuid'] in uuid_list for sp in sp_li)


def cal_max_another_three_speed(sp_li, suit_name=None):
    """计算最大3个速度"""
    if suit_name is not None:
        filtered_data = [d for d in sp_li if d['yh_type'] == suit_name]
    else:
        filtered_data = sp_li
    sorted_data = sorted(filtered_data, key=lambda x: x['speed'], reverse=True)
    return sum(round(d['speed'], 4) if d['pos'] != 2 else round(d['speed'] - 57, 4) for d in sorted_data[:3])


def get_speed_info(data_infos, full_speed=155, x_hero=x_hero):
    """
    合并成es索引结构数据
    :param json_data:
    :param full_speed:
    :return:
    """
    parse = CbgDataParser()
    json_data = parse.cbg_parse(data_infos, x_hero=x_hero)
    yuhun_json = parse.init_yuhun(json_data["inventory"])
    # 御魂分组1-6
    data_info = parse.sort_pos(yuhun_json)
    # 查找uuid_json
    uuid_infos = find_yuhun_uuid(data_info)
    uuid_json = choose_best_uuid(uuid_infos)
    json_data.update({"uuid_json": uuid_json})
    # 速度御魂列表
    speeds_all = get_speeds_all(data_info)
    # 满速个数
    full_speed_num, full_speed_value = get_full_speed_number(speeds_all, 15, True)
    json_data.update({"full_speed_num": full_speed_num})
    json_data.update({"full_speed_value": full_speed_value})

    # 除散件一速后独立招财
    # speeds_all2 = remove_independent_speed(speeds_all, 1)
    # zc_sp_list, zc_sp_sum = cal_suit_speed(speeds_all2, speeds_sj_list_2, "招财猫")
    # 命中、抵抗
    mz_info, dk_info = parse.find_yuhun_mzdk(speeds_all)
    mz_uuid = [_['uuid'] for _ in mz_info["value_list"]]
    dk_uuid = [_['uuid'] for _ in dk_info["value_list"]]
    # 二号位
    head_info = parse.find_yuhun_head(speeds_all)

    # 一速
    fast_speed_list = []
    # 前四散件独立套
    for i in range(1, 5):
        # 散件满速、散件列表
        try:
            sj_sum, speeds_sj_list_temp = cal_speed_sum_num(speeds_all, i)
            speed_list = list(filter_chinese(speeds_sj_list_temp))
            fast_speed_list.append({
                # "suit_name": "san_jian",
                # "speed_list": speeds_sj_list,
                "three_sum": round(cal_max_another_three_speed(speed_list), 2),
                "is_mz": 1 if check_include_yuhun(speed_list, mz_uuid) else 0,
                "is_dk": 1 if check_include_yuhun(speed_list, dk_uuid) else 0,
                "suit_name": f"散件{i}",
                "speed_sum": round(sj_sum, 2),
                "speed_list": speed_list,
            })
        except Exception as e:
            if e.__str__() != "list index out of range":
                print(e)
    # 默认筛选套装满速大于150
    sj_sum, speeds_sj_list = cal_speed_sum_num(speeds_all, 1)
    for suit_name in parse.yuhun_list:
        try:
            sp_list, sp_sum = cal_suit_speed(speeds_all, speeds_sj_list, suit_name)
            speed_list = list(filter_chinese(sp_list))
            if sp_sum > full_speed:
                fast_speed_list.append({
                    # "speed_list": sp_list,
                    # "suit_name": get_abridge(suit_name),
                    "three_sum": round(cal_max_another_three_speed(speed_list, suit_name), 2),
                    "is_mz": 1 if check_include_yuhun(speed_list, mz_uuid) else 0,
                    "is_dk": 1 if check_include_yuhun(speed_list, dk_uuid) else 0,
                    "suit_name": suit_name,
                    "speed_sum": round(sp_sum, 2),
                    "speed_list": speed_list,
                })
        except Exception as e:
            if "speeds_sj_list" not in e.__str__():
                print(e)
    json_data.update({
        "speed_infos": {
            "head_info": head_info,
            "mz_info": mz_info,
            "dk_info": dk_info,
        },
        "suit_speed": sorted(fast_speed_list, key=lambda e: e["speed_sum"], reverse=True)
    })
    try:
        data_yuhun_std = extract_data_cbg(data_infos)
        if optimize_data_for_cal(data_yuhun_std):
            dmg_yuhun = pick_dmg_yuhun_all(
                data_yuhun_std,
                common_score=8,  # 普通分数
                special_score=10,  # 逢魔皮分数
                is_speed_limit=True
            )
            json_data.update({"dmg_yuhun": dmg_yuhun})
    except Exception as e:
        print(e)
        json_data.update({"dmg_yuhun": {}})
    del json_data["inventory"]
    return json_data


def find_yuhun_uuid(dts):
    """查找御魂246号uuid"""
    uuid_list = {}
    for k, values in dts.items():
        if k == '2':
            uuid_list["2"] = [item for item in values if '速度' in item.keys() and item['速度'] >= (57 + 15)]
            if len(uuid_list["2"]) == 0:
                uuid_list["2"] = [item for item in values if '速度' in item.keys() and item['速度'] >= 57][:10]

        elif k == '4':
            uuid_list["4"] = []
            for item in values:
                if '速度' in item.keys() and item['速度'] > 15:
                    if '效果抵抗' in item.keys() and item['效果抵抗'] >= 55:
                        uuid_list["4"].append(item)
                    if '效果命中' in item.keys() and item['效果命中'] >= 55:
                        uuid_list["4"].append(item)
        elif k == '6':
            uuid_list["6"] = [item for item in values if '暴击伤害' in item.keys() and item['暴击伤害'] >= 89]
            if len(uuid_list["2"]) == 0:
                uuid_list["6"] = [item for item in values if '暴击伤害' in item.keys() and item['暴击伤害'] >= 55][:10]

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
