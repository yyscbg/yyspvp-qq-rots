# -*- coding:utf-8 -*-
"""
@Time: 2022/9/1下午11:15
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: yys_proxy.py
@Detail: 代理模块
"""
import base64
import json
import random
import requests
from tenacity import retry, stop_after_attempt, wait_fixed


class KDLProxy:
    """快代理"""

    def __init__(self, username, password):
        self.secret_key = "ct9sy8er98fu73q9rmwrjdpfephkwltg"
        self.secret_id = 'o67hfcmlogwfy5vpzq6d'
        self.account_secret_id = 'u8xnxokgwzmimmikm16g'
        self.account_secret_key = 'kg947kx877tpk727k8cj5qdbltuztfsq'
        # 生成base64验证串
        # self.proxy_authorization = base64.b64encode(f'{username}:{password}')

    def set_header(self, headers=None):
        """
        设置请求头
        :param headers: 默认None
        :return: headers
        """
        temp_heders = {}
        proxy_authorization = {"Proxy-Authorization": self.proxy_authorization}
        gzip = {"Accept-Encoding": "gzip"}
        if headers is None:
            temp_heders.update(proxy_authorization)
            temp_heders.update(gzip)
            headers = temp_heders
        else:
            headers.update(proxy_authorization)
            headers.update(gzip)
        return headers

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(30))
    def get_api_token(self):
        """获取API Token"""
        url = "https://auth.kdlapi.com/api/get_secret_token"
        response = requests.post(
            url,
            data={
                "secret_id": self.secret_id,
                "secret_key": self.secret_key
            }
        )
        try:
            if response.status_code == 200:
                json_data = response.json()
                return json_data.get('data', {}).get('secret_token', "")
            else:
                return False
        except Exception as e:
            print(e)

    def get_ip(self, signature=None):
        """
        获取当前隧道IP
        :param signature: 签名（api-secret-token）
        :return:
        """
        signature = "os2gp7bumqmcgf3e209shcg33p"
        if signature is None:
            signature = self.get_api_token
        if not signature:
            raise ValueError("signature must be")
        url = f"https://tps.kdlapi.com/api/gettps/?secret_id={self.secret_id}" \
              f"&num=1&signature={signature}&pt=1&format=json&sep=1"
        response = requests.get(url)
        try:
            if response.status_code == 200:
                print(response.json())
                json_data = response.json()
                return json_data
            else:
                return False
        except Exception as e:
            print(e)

    def get_current_ip(self):
        signature = "os2gp7bumqmcgf3e209shcg33p"
        url = f"https://tps.kdlapi.com/api/gettpsip/?secret_id={self.secret_id}" \
              f"&num=1&signature={signature}&pt=1&format=json&sep=1"
        response = requests.get(url)
        try:
            if response.status_code == 200:
                json_data = response.json()
                return json_data
            else:
                return False
        except Exception as e:
            print(e)


class ProxyTool:
    def __init__(self, proxy_url=None, http_prefix=None):
        self.http_prefix = http_prefix if http_prefix else None
        self.proxy_url = proxy_url if proxy_url else None
        if not self.http_prefix or not self.proxy_url:
            raise ValueError("代理配置出错")
        self.proxy_list = []

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def get_proxies(self):
        try:
            if self.proxy_url is None:
                raise ValueError('proxy_url must be set')
            rs_json = requests.get(self.proxy_url, timeout=5).json()
            if rs_json:
                self.proxy_list = rs_json["data"][1]["proxy"]
        except Exception as e:
            raise ValueError(f"代理商出错：{e}")

    def get_proxy(self, _num=5):
        while True:
            try:
                if len(self.proxy_list) > 0:
                    ip = self.proxy_list[random.randint(0, len(self.proxy_list) - 1)]
                    proxies = {
                        "http": "{}{}".format(self.http_prefix, ip),
                        "https": "{}{}".format(self.http_prefix, ip)
                    }
                    return proxies
                self.get_proxies()
            except Exception as e:
                if _num == 0:
                    return False
                # 刷新代理
                self.get_proxies()
                print(f"重试获取代理：{e}")
                _num -= 1


if __name__ == '__main__':
    pass
    # username = "t17175936220344"
    # password = "12zv7mmd"
    # kdl = KDLProxy(username, password)
    # # kdl.get_api_token()
    # kdl.get_ip()
    # # kdl.get_current_ip()
    # proxy_ip = "i599.kdltps.com:15818"
    # proxies = {
    #     "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip},
    #     "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip}
    # }
    # res = requests.get("https://baidu.com", proxies=proxies)
    # print(res.text)
