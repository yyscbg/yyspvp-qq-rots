# -*- coding:utf-8 -*-
"""
@Time: 2022/9/1下午11:15
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: yys_proxy.py
@Detail: 代理模块
"""
import random
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

try:
    from configs.all_config import proxy_url, http_prefix
except Exception as e:
    raise ImportError("configs.all_config error")


class ProxyTool:
    def __init__(self):
        self.proxy_list = []
        self.get_proxies()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(30))
    def get_proxies(self):
        try:
            if proxy_url is None:
                raise ValueError('proxy_url must be set')
            rs_json = requests.get(proxy_url).json()
            if rs_json:
                self.proxy_list = rs_json["data"][1]["proxy"]
        except Exception as e:
            raise ValueError(f"代理商出错：{e}")

    def get_proxy(self, _num=5):
        while True:
            try:
                ip = self.proxy_list[random.randint(0, len(self.proxy_list))]
                proxies = {
                    "http": "{}{}".format(http_prefix, ip),
                    "https": "{}{}".format(http_prefix, ip)
                }
                return proxies
            except Exception as e:
                if _num == 0:
                    return False
                # 刷新代理
                self.get_proxies()
                print(f"重试获取代理：{e}")
                _num -= 1


if __name__ == '__main__':
    proxy = ProxyTool().get_proxy()
    print(proxy)
