# -*- coding:utf-8 -*-
"""
@Time: 2022/9/1上午10:53
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: yys_spider.py
@Detail: 藏宝阁爬虫
"""
import re
import requests
import urllib3

try:
    from configs.all_config import kdl_proxy
except ImportError:
    raise ImportError

urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 5


class YysCbgSpider:
    """
    藏宝阁爬虫
    """

    def __init__(self):
        self.headers = {
            # 'authority': 'yys.cbg.163.com',
            # 'pragma': 'no-cache',
            # 'cache-control': 'no-cache',
            # 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            # 'accept': 'application/json, text/javascript, */*; q=0.01',
            # 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            # 'x-requested-with': 'XMLHttpRequest',
            # 'sec-ch-ua-mobile': '?0',
            # 'sec-ch-ua-platform': '"macOS"',
            # 'origin': 'https://yys.cbg.163.com',
            # 'sec-fetch-site': 'same-origin',
            # 'sec-fetch-mode': 'cors',
            # 'sec-fetch-dest': 'empty',
            # 'accept-language': 'zh-CN,zh;q=0.9',
        }

    @staticmethod
    def get_accid(content: str):
        """
        正则关键id
        :param content:
        :return:
        """
        # 兼容区服
        return re.findall(r"[0-9]+-\d{1, 2}-[0-9A-Z]+", content)

    def get_data(self, data, max_times=3, **kwargs):
        """
        获取数据
        :param data:
        :param kwargs:
        :return:
        """
        _ctimes = 0
        # while True:
        try:
            _ctimes += 1
            headers = kwargs.pop("headers", self.headers)
            # print(headers, data)
            response = requests.post(
                'https://yys.cbg.163.com/cgi/api/get_equip_detail',
                data=data,
                headers=headers,
                **kwargs
            )

            if response.status_code == 200:
                res = response.json()
                if res.get("status", -1) != 1:
                    # continue
                    return False
                return res
            print(response.status_code)
            print(response.json())
        except requests.exceptions.ConnectionError:
            if _ctimes >= max_times:
                return False
            # res.status_code = "Connection refused"


def get_equip_detail(ordersn: str = None, cbg_url: str = None, **kwargs):
    """
    获取数据详情
    :param ordersn:
    :param cbg_url:
    :param kwargs:
    :return:
    """
    if not any([ordersn, cbg_url]):
        raise ValueError("At least one parameter is required")

    spider = YysCbgSpider()
    if cbg_url:
        ordersn = spider.get_accid(cbg_url)[0]
    server_id = int(ordersn.split('-')[1])
    payload = f"serverid={server_id}&ordersn={ordersn}"
    return spider.get_data(data=payload, **kwargs)


def get_infos_by_kdl(game_ordersn, max_num=5):
    num = 0
    while True:
        try:
            username = kdl_proxy["username"]
            password = kdl_proxy["password"]
            proxy_ip = kdl_proxy["proxy_ip"]
            proxies = {
                "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip},
                "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip}
            }
            infos = get_equip_detail(game_ordersn, proxies=proxies, timeout=10)
            if infos:
                return infos
            if num >= max_num:
                break
            num += 1
        except Exception as e:
            print(f"{e}: 刷新代理: {proxies}: {game_ordersn}")


if __name__ == '__main__':
    url = "https://yys.cbg.163.com/cgi/mweb/equip/3/202207021401616-3-LAYIQNLHGAWRL3"
    url = "https://yys.cbg.163.com/cgi/mweb/equip/7/202211091201616-7-Z3VMTFBMHISOHI"
    url = "https://yys.cbg.163.com/cgi/mweb/equip/11/202212090901616-11-4E1Y8DJCKGP6J"
    game_ordersn = "202207021401616-3-LAYIQNLHGAWRL3"
    game_ordersn = "202212042101616-12-OTUU52VLMAQHO"  # 战百鬼
    game_ordersn = "202212031101616-12-ZHGU5BC5FIK5B"  # 百鬼
    game_ordersn = "202212062301616-7-UJAJOUMZ9VF2HD"
    game_ordersn = "202212011901616-7-6UJHVYKUPPJ1ZU"
    game_ordersn = "202212121001616-21-UJ3FHTEZR3AKY"
    game_ordersn = "202302010401616-3-2F4PRPI0EC2WIH"
    game_ordersn = "202302051901616-22-XQVQKSGSH7FYT"
    game_ordersn = "202201030401616-22-J8CZGX6CQYPWC"

    # infos = get_equip_detail(game_ordersn)
    infos = get_infos_by_kdl(game_ordersn)
    print(infos)
