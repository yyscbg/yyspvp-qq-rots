# -*- coding:utf-8 -*-
"""
@Time: 2022/9/1下午10:58
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: yys_elasticsearch.py
@Detail: ES模块
"""
import sys
from datetime import date, datetime
from urllib.parse import quote_plus, quote, urlencode, urlparse, unquote
from elasticsearch import Elasticsearch, Transport, TransportError, helpers
from elasticsearch.client.utils import query_params

PY2 = sys.version_info[0] == 2
string_types = str, bytes
map = map

SKIP_IN_PATH = (None, "", b"", [], ())


def quote_plus(string, safe='', encoding=None, errors=None):
    """Like quote(), but also replace ' ' with '+', as required for quoting
    HTML form values. Plus signs in the original string are escaped unless
    they are included in safe. It also does not have safe default to '/'.
    """
    # Check if ' ' in string, where string may either be a str or bytes.  If
    # there are no spaces, the regular quote will produce the right answer.
    if ((isinstance(string, str) and ' ' not in string) or
            (isinstance(string, bytes) and b' ' not in string)):
        return quote(string, safe, encoding, errors)
    if isinstance(safe, str):
        space = ' '
    else:
        space = b' '
    string = quote(string, safe + space, encoding, errors)
    return string.replace(' ', '+')


def make_path(*parts):
    """
    Create a URL string from parts, omit all `None` values and empty strings.
    Convert lists and tuples to comma separated values.
    """
    # TODO: maybe only allow some parts to be lists/tuples ?
    return "/" + "/".join(
        # preserve ',' and '*' in url for nicer URLs in logs
        quote_plus(_escape(p), b",*")
        for p in parts
        if p not in SKIP_IN_PATH
    )


def _escape(value):
    """
    Escape a single value of a URL string or a query parameter. If it is a list
    or tuple, turn it into a comma-separated string first.
    """

    # make sequences into comma-separated stings
    if isinstance(value, (list, tuple)):
        value = ",".join(value)

    # dates and datetimes into isoformat
    elif isinstance(value, (date, datetime)):
        value = value.isoformat()

    # make bools into true/false strings
    elif isinstance(value, bool):
        value = str(value).lower()

    # don't decode bytestrings
    elif isinstance(value, bytes):
        return value

    # encode strings to utf-8
    if isinstance(value, string_types):
        if not PY2 and isinstance(value, str):
            return value.encode("utf-8")

    return str(value)


class ElasticSearch(Elasticsearch):
    def __init__(self, hosts, auth="", **kwargs):
        """
        构造函数
        :param hosts:
        :param auth:
        """
        super(ElasticSearch, self).__init__(hosts=hosts, transport_class=Transport, http_auth=auth, **kwargs)

    def es_create(self, index_name, body={}):
        """
        创建索引
        :param index_name:
        :param body:
        :return:
        """
        return self.indices.create(index=index_name, ignore=400, body=body)

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
            if _id == -1:
                ret = self.index(index=index_name, doc_type=doc_type, body=body)
            else:
                ret = self.index(index=index_name, doc_type=doc_type, body=body, id=_id)

        except TransportError as e:
            print(e.info)

        return ret

    def es_set_max_windows(self, max_num=50000000):
        """
        设置窗口
        :param max_num:
        :return:
        """
        self.indices.put_settings(body={'index': {'max_result_window': max_num}})

    def es_index_bulk(self, actions, index_name='', n_timeout=120):
        """
        批量更新数据
        :param actions:
        :param index_name:
        :param n_timeout:
        :return:
        """
        if index_name == '':
            ret = helpers.bulk(self, actions, request_timeout=n_timeout)
        else:
            ret = helpers.bulk(self, actions, index=index_name, request_timeout=n_timeout)

        return ret

    # @query_params(
    #     "_source",
    #     "_source_exclude",
    #     "_source_excludes",
    #     "_source_include",
    #     "_source_includes",
    #     "fields",
    #     "if_seq_no",
    #     "if_primary_term",
    #     "lang",
    #     "parent",
    #     "refresh",
    #     "retry_on_conflict",
    #     "routing",
    #     "timeout",
    #     "timestamp",
    #     "ttl",
    #     "version",
    #     "version_type",
    #     "wait_for_active_shards",
    # )
    # def es_update(self, index_name, _id, body=None, params=None):
    #     """
    #     更新一条数据
    #     :param index_name:
    #     :param _id:
    #     :param body:
    #     :param params:
    #     :return:
    #     """
    #     for param in (index_name, _id):
    #         if param in SKIP_IN_PATH:
    #             raise ValueError("Empty value passed for a required argument.")
    #     _path = make_path(index_name, "_update", _id)
    #     print(_path)
    #     return self.transport.perform_request(
    #         "POST", _path, params=params, body=body
    #     )
    def es_update(self, index_name, doc_id, update_body):
        return self.update(index=index_name, id=doc_id, body=update_body)

    def es_search(self, index_name, body={}, request_timeout=30):
        return self.search(index=index_name, body=body, request_timeout=request_timeout)

    def es_close(self, index_name):
        self.indices.close(index=index_name)

    def es_delete(self, index_name):
        return self.indices.delete(index_name)
