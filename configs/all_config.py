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

if platform.system() == 'Linux':
    base_config_file = "/home/yys/yys_project/config.yaml"
    if not os.path.exists(base_config_file):
        base_config_file = "/www/wwwroot/yys_project/backend/config.yaml"
else:
    base_config_file = os.path.join(reduce(lambda x, _: os.path.dirname(x), range(2), __file__), 'config.yaml')

print(base_config_file)

all_config = YamlConfig.get_yaml_config(base_config_file)
# mysql配置
mysql_config = all_config["mysql_config"]
# 飞书配置
robot_key = all_config["feishu"]["robot_key"]
# redis配置
redis_config = all_config["redis_config"]

# 机器人路径
# bots_path = all_config["bots_path"]
# es配置
es_config = all_config.get("es_config")
