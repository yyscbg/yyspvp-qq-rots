# -*- coding:utf-8 -*-
"""
@Time: 2022/9/5下午11:24
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: all_config.py
@Detail: 
"""
import os
import platform
from functools import reduce
from utils.yys_config import YamlConfig


base_config_file = os.path.join(reduce(lambda x, _: os.path.dirname(x), range(2), __file__), 'config.yaml')
print(base_config_file)
all_config = YamlConfig.get_yaml_config(base_config_file)
# mysql配置
mysql_config = all_config["mysql_config"]
# 飞书配置
robot_key = all_config["feishu"]["robot_key"]
# redis配置
redis_config = all_config["redis_config"]
# 藏宝阁json下载路径
dir_path = all_config["data_dir"]
# 代理配置
proxy_url = all_config.get('proxy_url', None)
http_prefix = all_config.get('http_prefix', None)
# es配置
es_config = all_config.get("es_config")
# 藏宝阁
yyscbg_mappings = all_config.get("yyscbg_mappings")
# 历史
yys_history_mappings = all_config.get("yys_history_mappings")
# 斗技
yyspvp_mappings = all_config.get("yyspvp_mappings")

# 快代理
kdl_proxy = all_config.get("kdl_proxy")

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
    "焰心踏冰",
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
