# -*- coding:utf-8 -*-
"""
@Time: 2022/9/1下午10:58
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: yys_elasticsearch.py
@Detail: ES模块
"""

from elasticsearch import Elasticsearch
from elasticsearch import TransportError
from elasticsearch import helpers


class ElasticSearch:
    def __init__(self, hosts, auth=""):
        """
        构造函数
        :param hosts:
        :param auth:
        """
        es = Elasticsearch(hosts, http_auth=auth)
        self.es = es

    def es_create(self, index_name, body={}):
        """
        创建索引
        :param index_name:
        :param body:
        :return:
        """
        ret = self.es.indices.create(index=index_name, ignore=400, body=body)
        return ret

    def es_index(self, index_name, doc_type, body, _id=-1):
        """
        索引
        :param index_name:
        :param doc_type:
        :param body:
        :param _id:
        :return:
        """
        try:
            ret = 0
            if id == -1:
                ret = self.es.index(index=index_name, doc_type=doc_type, body=body)
            else:
                ret = self.es.index(index=index_name, doc_type=doc_type, body=body, id=_id)

        except TransportError as e:
            print(e.info)

        return ret

    def es_set_max_windows(self, max_num=50000000):
        """
        设置窗口
        :param max_num:
        :return:
        """
        self.es.indices.put_settings(body={'index': {'max_result_window': max_num}})

    def es_index_bulk(self, actions, index_name='', n_timeout=120):
        """
        批量更新数据
        :param actions:
        :param index_name:
        :param n_timeout:
        :return:
        """
        if index_name == '':
            ret = helpers.bulk(self.es, actions, request_timeout=n_timeout)
        else:
            ret = helpers.bulk(self.es, actions, index=index_name, request_timeout=n_timeout)

        return ret

    def es_update_one_data(self, index_name, doc_type, id, data):
        """
        更新一条数据
        :param index_name:
        :param doc_type:
        :param id:
        :param data:
        :return:
        """
        self.es.update(index=index_name, doc_type=doc_type, id=id, body=data)

    def es_search(self, index_name, body={}, request_timeout=30):
        ret = self.es.search(index=index_name, body=body, request_timeout=request_timeout)
        return ret

    def es_close(self, index_name):
        self.es.indices.close(index=index_name)

    def es_delete(self, index_name):
        ret = self.es.indices.delete(index_name)
        return ret
