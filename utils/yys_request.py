# -*- coding:utf-8 -*-
"""
@Time: 2022/8/1下午22:31
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: yys_request.py
@Detail: 请求类
"""

import requests
from tenacity import retry, stop_after_attempt, wait_fixed


class YysRequest:
    def __init__(self):
        pass

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(30))
    def request_get(self, req_url, is_json=False, encoding='utf-8', **kwargs):
        _result = None
        try:
            response = requests.get(
                url=req_url,
                **kwargs
            )
            if response.status_code == 200:
                if is_json:
                    _result = response.json()
                else:
                    _result = response.content.decode(encoding)
        except Exception as e:
            print(e)
        return _result

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(30))
    def request_post(self, req_url, is_json=False, encoding='utf-8', **kwargs):
        _result = None
        try:
            response = requests.post(
                url=req_url,
                **kwargs
            )
            if response.status_code == 200:
                if is_json:
                    _result = response.json()
                else:
                    _result = response.content.decode(encoding)
        except Exception as e:
            print(e)
        return _result


if __name__ == '__main__':
    obj_req = YysRequest()
    # Get html
    # result = obj_req.request_get("https://www.baidu.com")
    # print(result)
    # Get JSON
    # import json
    # data = {"server": 10002, "page": 1}
    # result = obj_req.request_get(
    #     "https://bdapi.gameyw.netease.com/ky59/v1/g37_charts/topuids?",
    #     is_json=True,
    #     data=json.dumps(data),
    # )
    # print(result)
    # Post json
    # result = obj_req.request_post(
    #     "https://yysrank.ahrisy.com/api/player",
    #     is_json=True,
    #     data={"server": 15003},
    # )
    # print(result)
