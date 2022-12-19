# -*- coding:utf-8 -*-
"""
@Time: 2022/12/1916:59
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: yys_cal_about.py
@Detail: 
"""

import json
import math

ATTRS = (
    '生命', '防御', '攻击',
    '生命加成', '防御加成', '攻击加成',
    '速度', '暴击', '暴击伤害',
    '效果命中', '效果抵抗'
)

ATTRS_SGL = {
    ATTRS[3]: (0.08, '(固){} {:.0%}'),
    ATTRS[4]: (0.16, '(固){} {:.0%}'),
    ATTRS[5]: (0.08, '(固){} {:.0%}'),
    ATTRS[7]: (0.08, '(固){} {:.0%}'),
    ATTRS[9]: (0.08, '(固){} {:.0%}'),
    ATTRS[10]: (0.08, '(固){} {:.0%}')
}  # 首领御魂固有属性（即单件效果，普通御魂无单件效果）值、可读化

ATTRS_POS = (
    (ATTRS[2],),
    (ATTRS[3], ATTRS[4], ATTRS[5], ATTRS[6]),
    (ATTRS[1],),
    (ATTRS[3], ATTRS[4], ATTRS[5], ATTRS[9], ATTRS[10]),
    (ATTRS[0],),
    (ATTRS[3], ATTRS[4], ATTRS[5], ATTRS[7], ATTRS[8])
)  # 每个位置的主属性

ATTRS_MAIN = {
    ATTRS[0]: ((
                   (35, 12), (69, 23), (137, 46), (206, 69), (274, 92), (342, 114)
               ), '{} {:.0f}'),
    ATTRS[1]: ((
                   (2, 1), (3, 2), (6, 3), (8, 4), (11, 5), (14, 6)
               ), '{} {:.0f}'),
    ATTRS[2]: ((
                   (9, 3), (17, 6), (33, 11), (49, 17), (65, 22), (81, 27)
               ), '{} {:.0f}'),
    ATTRS[3]: ((
                   (0.01, 0.01), (0.02, 0.01), (0.04, 0.02),
                   (0.06, 0.02), (0.08, 0.02), (0.1, 0.03)
               ), '{} {:.0%}'),
    ATTRS[4]: ((
                   (0.01, 0.01), (0.02, 0.01), (0.04, 0.02),
                   (0.06, 0.02), (0.08, 0.02), (0.1, 0.03)
               ), '{} {:.0%}'),
    ATTRS[5]: ((
                   (0.01, 0.01), (0.02, 0.01), (0.04, 0.02),
                   (0.06, 0.02), (0.08, 0.02), (0.1, 0.03)
               ), '{} {:.0%}'),
    ATTRS[6]: ((
                   (2, 1), (4, 1), (6, 2), (8, 2), (10, 2), (12, 3)
               ), '{} {:.0f}'),
    ATTRS[7]: ((
                   (0.01, 0.01), (0.02, 0.01), (0.04, 0.02),
                   (0.06, 0.02), (0.08, 0.02), (0.1, 0.03)
               ), '{} {:.0%}'),
    ATTRS[8]: ((
                   (0.02, 0.02), (0.03, 0.02), (0.05, 0.03),
                   (0.09, 0.03), (0.11, 0.04), (0.14, 0.05)
               ), '{} {:.0%}'),
    ATTRS[9]: ((
                   (0.01, 0.01), (0.02, 0.01), (0.04, 0.02),
                   (0.06, 0.02), (0.08, 0.02), (0.1, 0.03)
               ), '{} {:.0%}'),
    ATTRS[10]: ((
                    (0.01, 0.01), (0.02, 0.01), (0.04, 0.02),
                    (0.06, 0.02), (0.08, 0.02), (0.1, 0.03)
                ), '{} {:.0%}')
}  # 一至六星御魂主属性初始值 & 加点值、可读化

ATTRS_SUB = {
    ATTRS[0]: (114, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%df}'),
    ATTRS[1]: (5, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%df}'),
    ATTRS[2]: (27, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%df}'),
    ATTRS[3]: (0.03, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}'),
    ATTRS[4]: (0.03, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}'),
    ATTRS[5]: (0.03, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}'),
    ATTRS[6]: (3, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%df}'),
    ATTRS[7]: (0.03, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}'),
    ATTRS[8]: (0.04, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}'),
    ATTRS[9]: (0.04, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}'),
    ATTRS[10]: (0.04, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}')
}  # 一至六星御魂副属性初始值 / 加点值、加点系数范围、可读化
HEROES_PANEL = {
    '炼狱茨木童子': {
        '攻击': 3323.2, '防御': 379.26, '生命': 10253.8,
        '速度': 112, '暴击': 0.15, '暴击伤害': 1.5,
        '效果命中': 0, '效果抵抗': 0
    },
    '玉藻前': {
        '攻击': 3350, '防御': 352.8, '生命': 12532.2,
        '速度': 110, '暴击': 0.12, '暴击伤害': 1.6,
        '效果命中': 0, '效果抵抗': 0
    },
    '黑童子': {
        '攻击': 3376.8, '防御': 383.67, '生命': 9912.04,
        '速度': 109, '暴击': 0.09, '暴击伤害': 1.5,
        '效果命中': 0, '效果抵抗': 0
    },
    '阿修罗': {
        '攻击': 4127, '防御': 428, '生命': 11279,
        '速度': 119, '暴击': 0.10, '暴击伤害': 1.5,
        '效果命中': 0, '效果抵抗': 0
    }
}  # 式神基础面板


def score_attrs(item, attrs_useful):
    """计算御魂分数

    对于一颗普通六星御魂，其分数为每条有效副属性分数之和，最低 0 分，最高 9 分；
    而一颗首领六星御魂，其固有属性也会参与评分，分三种情况，固有属性为：
        防御加成
    此类总分 0~15 分；固有属性为：
        生命加成、攻击加成、暴击
    此类总分 0~12 分；固有属性为：
        效果命中、效果抵抗
    此类总分 0~11 分。
    对于低星普通御魂，由于初始副属性条数最高不会达到 4，所以其分数上限天然低；
    对于低星首领御魂，由于各星级属性成长差异，而固有属性值不随星级变动，
    所以其分数上限也会随星级变动。

    Args:
        item (dict): 单颗御魂的元数据
        attrs_useful (list): 有效副属性集（固有属性也视为副属性）

    Returns:
        int: 返回分数（最低 0 分）
    """
    total_score = 0
    attrs = {attr['attr']: attr['value'] for attr in item['attrs']['subs']}
    if 'sgl' in item['attrs']:
        if item['attrs']['sgl']['attr'] in attrs:
            attrs[item['attrs']['sgl']['attr']] += item['attrs']['sgl']['value']
        else:
            attrs[item['attrs']['sgl']['attr']] = item['attrs']['sgl']['value']
    for attr, value in attrs.items():
        if attr in attrs_useful:
            total_score += score_attr(attr, item['star'], value)
    return total_score


def score_attr(attr, star, value):
    """计算副属性分数

    对于一条副属性，初始值和每次加点（满级最多加点 5 次）均视为 1 分，最低 1 分，最高 6 分；
    对于视为副属性的固有属性，其分数随星级波动。如荒骷髅：
        ...
        (固)暴击 8%
    其固有属性值分数为 3 分（六星）、
    4 分（五星、四星）、5 分（三星）、6 分（二星）、7 分（一星）。

    分数还会随判定算法波动，如六星御魂副属性
        攻击加成 +14.8%
    可为高成长的 5 分（严格），也可为低成长的 6 分（宽容）。

    重要：本程序沿用 v2.0 起的严格算法。

    Args:
        attr (str): 副属性名
        star (int): 星级，1~6
        value (float): 副属性值

    Returns:
        int: 返回分数（最低 1 分）
    """
    grow = ATTRS_SUB[attr][:2]
    # return int(min(value // (grow[0] * grow[1][star - 1][0]), 6))  # 宽容
    return math.ceil(value / (grow[0] * grow[1][star - 1][1]))  # 严格


def optimize_data_for_cal(data):
    if not data:
        return False
    for item in data:
        item['main2'] = {
            item['attrs']['main']['attr']: item['attrs']['main']['value']
        }
        item['subs2'] = {attr['attr']: attr['value']
                         for attr in item['attrs']['subs']}
        item['sgl2'] = {}
        if 'sgl' in item['attrs']:
            item['sgl2'] = {
                item['attrs']['sgl']['attr']: item['attrs']['sgl']['value']
            }
        attrs_dmg = [ATTRS[5], ATTRS[6], ATTRS[7], ATTRS[8]]
        item['score_dmg'] = score_attrs(item, attrs_dmg)
    return True


def format_dmg_yuhun_str(subs2):
    """格式化输出御魂字符"""
    return [f"      {k}: {round(v * 100, 2) if v < 1 else round(v, 2)}" for k, v in subs2.items()]


def pick_dmg_yuhun(datas, **kwargs):
    """选出输出御魂"""
    pos_list = kwargs.get('pos_list', [6])
    common_score = kwargs.get('common_score', 7)
    special_score = kwargs.get('special_score', 10)
    dmg_kinds = kwargs.get('dmg_kinds', ['暴击', '暴击伤害'])
    common_kinds = kwargs.get('common_kinds', ["狂骨", '破势', '海月火玉'])
    special_kinds = kwargs.get('special_kinds', ['荒骷髅', '鬼灵歌伎', '土蜘蛛', '地震鲶', '蜃气楼'])
    yuhun_kind = kwargs.get('yuhun_kind',
                            ["狂骨", '破势', '海月火玉', '荒骷髅', '鬼灵歌伎', '土蜘蛛', '地震鲶', '蜃气楼'])

    result = []
    for dt in datas:
        if dt['kind'] in yuhun_kind and dt['pos'] in pos_list and dt['attrs']['main']['attr'] in dmg_kinds:
            if dt['score_dmg'] >= common_score and dt['kind'] in common_kinds:
                result.append(dt)
            if dt['score_dmg'] >= special_score and dt['kind'] in special_kinds:
                result.append(dt)
    return result


def check_data_cbg(data):
    """检查 JSON 数据是否为藏宝阁数据

    Args:
        data (dict): JSON 数据

    Returns:
        bool: 合法返回 True
    """
    return (data and isinstance(data, dict)
            and 'equip' in data and 'equip_desc' in data['equip'])


def extract_data_cbg(data):
    """从藏宝阁数据中抽取御魂数据集并封装为标准格式

    藏宝阁数据包含商品信息和游戏帐号本体信息，整个数据文件封装为 dict：
        {
            'status': ...,
            'equip': {
                'equip_desc': {
                    'inventory': {...},
                    ...
                },
                ...
            }
        }
    御魂数据在 inventory。

    Args:
        data (dict): 藏宝阁导出文件的 JSON 数据

    Returns:
        list: 返回封装为标准格式的御魂数据集
    """
    if not check_data_cbg(data):
        return []
    data_game = json.loads(
        data['equip']['equip_desc']
    )  # 非 dict，而是 str
    data_yuhun = list(
        data_game['inventory'].values()
    )  # 非 list，而是以御魂 ID 为 key 的 dict
    return list(map(meta_cbg2std, data_yuhun))


def main_attr(attr, star, level):
    """主属性成长

    计算主属性目标等级的值。结果只有两种情况：整数、整百分数（即精确到小数点后两位）

    重要：Python 浮点数运算可能产生“不确定尾数”，如
        0.1 + 0.03 * 15 = 0.5499999999999999
    所以使用 round(x, 2) 消除影响。

    Args:
        attr (str): 主属性名
        star (int): 星级，1~6
        level (int): 等级

    Returns:
        float: 返回目标等级的主属性值
    """
    grow = ATTRS_MAIN[attr][0][star - 1]
    return round(grow[0] + grow[1] * level, 2)


def meta_cbg2std(item):
    """将藏宝阁格式元数据重封装为标准格式

    Args:
        item (dict): 藏宝阁数据中单颗御魂的元数据

    Returns:
        dict: 标准格式的御魂元数据
    """
    attrs_id_name = {
        'maxHpAdditionVal': ATTRS[0], 'defenseAdditionVal': ATTRS[1],
        'attackAdditionVal': ATTRS[2], 'maxHpAdditionRate': ATTRS[3],
        'defenseAdditionRate': ATTRS[4], 'attackAdditionRate': ATTRS[5],
        'speedAdditionVal': ATTRS[6], 'critRateAdditionVal': ATTRS[7],
        'critPowerAdditionVal': ATTRS[8], 'debuffEnhance': ATTRS[9],
        'debuffResist': ATTRS[10]
    }  # 属性 ID - 名字表
    attrs_base_r = (
        (ATTRS[2], ATTRS[5]),
        (ATTRS[1], ATTRS[4]),
        (ATTRS[0], ATTRS[3]),
        (ATTRS[6], ATTRS[8], ATTRS[9]),
        (ATTRS[7], ATTRS[10])
    )  # 源数据 base_rindex 键对应的全部属性，结合 pos 键可确定主属性
    attr_m = list(set(ATTRS_POS[item['pos'] - 1])
                  & set(attrs_base_r[item['base_rindex']]))[0]
    item_std = {
        'id': item['uuid'],
        'kind': item['name'],
        'pos': item['pos'],
        'star': item['qua'],
        'level': item['level'],
        'attrs': {
            'main': {
                'attr': attr_m,
                'value': main_attr(attr_m, item['qua'], item['level'])
            },
            'subs': []
        }
    }
    attrs_sub = {}
    for grow in item['rattr']:
        if grow[0] in attrs_sub:
            attrs_sub[grow[0]] += grow[1]
        else:
            attrs_sub[grow[0]] = grow[1]
    for attr_id, value_ratio in attrs_sub.items():
        item_std['attrs']['subs'].append({
            'attr': attrs_id_name[attr_id],
            'value': ATTRS_SUB[attrs_id_name[attr_id]][0] * value_ratio
        })
    if 'single_attr' in item:
        item_std['attrs']['sgl'] = {
            'attr': item['single_attr'][0],
            'value': ATTRS_SGL[item['single_attr'][0]][0]
        }
    return item_std


if __name__ == '__main__':
    base_path = "/Users/yingquanliu/PycharmProjects/development/yys/yys_project/yyscbg/datas/"
    game_ordersn = "202212031101616-12-ZHGU5BC5FIK5B"  # 百鬼之主
    file = game_ordersn + ".json"
    with open(base_path + file, "r") as f:
        json_data = json.loads(f.read())
    data_yuhun_std = extract_data_cbg(json_data)
    optimize_data_for_cal(data_yuhun_std)
    pick_dmg_yuhun(data_yuhun_std)
