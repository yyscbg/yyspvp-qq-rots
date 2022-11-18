# -*- coding:utf-8 -*-
"""
@Time: 2022/8/2下午22:06
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: yys_redis.py
@Detail: 自定义redis类
"""
import json
from redis import Redis, StrictRedis
from redis.connection import BlockingConnectionPool

HEAD = "head"
TAIL = "tail"


class YysRedis:
    def __init__(self, **kwargs):
        """
        :param host: 主机ip
        :param port: 端口
        :param password: 密码
        """
        self.redis_type = None
        try:
            self.conn = Redis(connection_pool=BlockingConnectionPool(decode_responses=True, **kwargs))
        except (ConnectionError, TimeoutError) as e:
            print(e)

    def set_redis_type(self, redis_type):
        if redis_type == TAIL:
            self.redis_type = "r"
        if redis_type == HEAD:
            self.redis_type = "l"

    def get_redis_info(self, **kwargs):
        """
        获取redis服务器相关信息
        :param host: 主机ip
        :param port: 端口
        :param password: 密码
        """
        redis_info = StrictRedis(**kwargs).info()
        return redis_info

    def get_redis_memory_info(self, **kwargs):
        """
        获取redis服务器内存相关信息
        :param host: 主机ip
        :param port: 端口
        :param password: 密码
        """
        info = self.get_redis_info(**kwargs)
        memory_info = {
            'used_memory': info['used_memory'],
            'used_memory_rss': info['used_memory_rss'],
            'used_memory_lua': info['used_memory_lua'],
            'used_memory_peak': info['used_memory_peak']
        }
        return memory_info

    # 单个插入
    def add(self, name, value, _head=True):
        """
        单个插入数据
        :param :name 键名
        :param :value 值
        :param :_head 默认从头插入，反之尾部插入
        """
        if _head:
            self.set_redis_type(HEAD)
        else:
            self.set_redis_type(TAIL)
        value_str = json.dumps(value, ensure_ascii=False)
        try:
            exec(f'self.conn.{self.redis_type}push(name, value_str)')
        except Exception as e:
            print(e)
            return False
        return True

    def read(self, name, start=0, end=-1):
        """
        读取redis
        :param :name 键名
        :param :start 起始位置
        :param :end 结束位置
        """
        result = self.conn.lrange(name, start, end)
        return [json.loads(i) for i in result]

    def update(self, name, value, index=-1):
        """
        更新
        :param name: 键名
        :param value: 转换的变量值
        :param index: 下标，默认修改最后一个
        """
        value_str = json.dumps(value, ensure_ascii=False)
        try:
            result = self.conn.lset(name, index, value_str)
        except Exception as e:
            print(str(e))
            return False
        return result

    def llen(self, name):
        """
        获取key长度
        :param :name key name
        """
        return self.conn.llen(name)

    def get_names(self):
        """
        获取key name列表
        """
        return self.conn.keys()

    def delete(self, *names):
        """
        删除 一个或多个key
        :param :names 一个key或list keys
        """
        # if self.conn.flushdb():
        if self.conn.delete(*names):
            print('successfully deleted')
        else:
            print('failed to delete')

    def batch_pick(self, name, num, _head=False):
        """
        批量取出
        :param :name 名称
        :param :num 取出数量
        :param :_head 从头部取出，默认True，反之从尾部取
        """
        _size = self.llen(name)
        with self.conn.pipeline(transaction=False) as p:
            if num < _size:
                if _head:
                    p.lrange(name, 0, num - 1)
                    p.ltrim(name, num, -1)
                else:
                    p.lrange(name, _size - num, _size)
                    p.ltrim(name, 0, _size - num - 1)
                data, flag = p.execute()
                # redis_log.i nfo(f"batch pick is {flag}")
            else:
                p.lrange(name, 0, _size)
                [data] = p.execute()
                self.delete(name)
            return [json.loads(i) for i in data]

    def batch_pop(self, name, num=100, pop_head=True):
        """
        批量取出 默认从头取数据
        :param name: 键名
        :param num: 取出数量
        """
        if pop_head:
            self.set_redis_type(HEAD)
        else:
            self.set_redis_type(TAIL)

        with self.conn.pipeline(transaction=False) as p:
            while self.llen(name) > 0:
                if num < self.llen(name):
                    number = num
                else:
                    number = self.llen(name)

                for i in range(number):
                    exec(f'p.{self.redis_type}pop(name)')
                break

            list_ret = []
            for i in p.execute():
                if (i != None):
                    list_ret.append(json.loads(i))

            return list_ret

    def batch_push(self, name, values: list, push_head=False):
        """
        批量插入 默认从尾部插入
        :param name: 键名
        :param values: 插入list变量值
        """
        if push_head:
            self.set_redis_type(HEAD)
        else:
            self.set_redis_type(TAIL)

        with self.conn.pipeline(transaction=False) as p:
            for value in values:
                value_str = json.dumps(value, ensure_ascii=False)
                exec(f'p.{self.redis_type}push(name, value_str)')
            p.execute()

    def pexpireat(self, key_name, expire_time) -> int:
        """
        设置键过期时间
        :param key_name: 键名
        :param expire_time: 过期时间戳, 13位
        :return: 设置成功返回 1, 当key_name不存在或者不能为key_name设置过期时间时返回 0
        """
        ret = self.conn.pexpireat(key_name, expire_time)
        return ret

    def exists(self, key_name) -> int:
        """
        判断key是否存在
        :param key_name: 键名
        :return: 若key_name存在返回 1，否则返回 0
        """
        ret = self.conn.exists(key_name)
        return ret

    def close(self):
        self.conn.close()


def test():
    key_name = "ads"
    redis_host = "127.0.0.1"
    redis_port = 6379
    client = YysRedis(host=redis_host, port=redis_port)
    memory_info = client.get_redis_memory_info(host=redis_host)
    print(f"{redis_host}内存信息：{memory_info}")
    key_name_li = client.get_names()
    print(f"key name list is {key_name_li}")
    # 单个插入
    client.add(key_name, {"d": 4})
    values = []
    for i in range(10):
        value = {"a": i, "b": 2 * i}
        values.append(value)
    # 批量插入 默认从尾插入
    client.batch_push(key_name, values)
    # 获取长度
    num = client.llen(key_name)
    print(f"{key_name} size is {num}")
    # 读取
    data = client.read(key_name, 1, 2)
    print(f"读取数据：{data}")
    # 修改
    print(f"修改成功: {client.update(key_name, {'cc': 1})}")
    # 批量取出 默认从头取
    data = client.batch_pop(key_name, 2)
    print(f"批量取出(默认从头取):{data}")
    # 批量取出 默认尾巴取
    data = client.batch_pick(key_name, 8, _head=False)
    print(f"批量取出(默认尾巴取): {data}")
    # 清空
    # client.delete(key_name)


if __name__ == '__main__':
    test()
