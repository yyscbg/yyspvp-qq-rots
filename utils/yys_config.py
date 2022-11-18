# -*- coding:utf-8 -*-
"""
@Time: 2022/9/5下午22:18
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: yys_config.py
@Detail:
"""
import os
import yaml
from shutil import ReadError


class YamlConfig:
    @staticmethod
    def get_yaml_config(yaml_path, key_name: str = None):
        """
        获取yaml文件配置
        :param yaml_path: yaml文件路径
        :param key_name: 键名
        :return dict
        """
        if not os.path.exists(yaml_path):
            raise FileNotFoundError("check <yaml_path>, don't exist")
        try:
            with open(yaml_path, mode="r+", encoding='utf-8') as yaml_file:
                yaml_data = yaml_file.read()
                covert_data = yaml.safe_load(yaml_data)
                if key_name is not None:
                    covert_data = covert_data[key_name]
        except Exception as e:
            raise ReadError(f"read <{yaml_path}> experience problems: {e.__doc__} detail: {e.__str__()}")
        return covert_data

    @classmethod
    def create_yaml_config(cls, yaml_path, config: dict, mode="w+"):
        """
        创建yaml文件（覆盖更新）
        :param yaml_path: yaml文件路径
        :param config: 配置字典
        :param mode: 默认模式'w+'
        :return bool
        """
        exist_config = cls.get_yaml_config(yaml_path)
        if exist_config:
            for new_key, new_value in config.items():
                exist_config[new_key] = new_value
        else:
            exist_config = config

        with open(yaml_path, mode=mode, encoding='utf-8') as yaml_file:
            yaml.dump(exist_config, yaml_file)

        flag = False
        if os.path.exists(yaml_path):
            flag = True
        return flag
