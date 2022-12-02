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


class YysCbgSpider:
    """
    藏宝阁爬虫
    """

    def __init__(self):
        self.headers = {
            'authority': 'yys.cbg.163.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'x-requested-with': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'sec-ch-ua-platform': '"macOS"',
            'origin': 'https://yys.cbg.163.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept-language': 'zh-CN,zh;q=0.9',
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

    def get_data(self, data, **kwargs):
        """
        获取数据
        :param data:
        :param kwargs:
        :return:
        """
        try:
            headers = kwargs.pop("headers", self.headers)
            response = requests.post(
                'https://yys.cbg.163.com/cgi/api/get_equip_detail',
                data=data,
                headers=headers,
                **kwargs
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(e)


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


if __name__ == '__main__':
    url = "https://yys.cbg.163.com/cgi/mweb/equip/12/202210302101616-12-Q4GEFZSWWJUNV"
    game_ordersn = "202210302101616-12-Q4GEFZSWWJUNV"
    infos = get_equip_detail(game_ordersn)
    print(infos)
    # from yyscbg.yys_io import write_local_file, write_infos_to_redis
    # write_local_file(infos, game_ordersn + ".json")
    # write_infos_to_redis([infos], "yyscbg_json")
