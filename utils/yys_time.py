# -*- coding:utf-8 -*-
"""
@Time: 2022/8/1下午22:10
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: yys_time.py
@Detail: 时间相关函数
"""
import time
import datetime
import calendar


def get_current_timestamp(is_second=True):
    # 获取当前时间戳：默认秒级
    timestamp = time.time()
    if not is_second:
        timestamp = int(round(timestamp * 1000))
    return timestamp


def datetime_to_timestamp(str_time):
    return time.mktime(time.strptime(str_time, '%Y-%m-%d %H:%M:%S'))


def timestamp_to_datetime(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))


def get_now():
    # 获取当前时间
    # datetime.datetime.now()
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def get_now_date():
    # 获取当前日期
    return datetime.date.today()


def get_few_days(days=1, today=None):
    # 获取过去、未来间隔日期,如指定当前today则以该日期 +- days间隔
    if not today:
        today = datetime.datetime.now()
    else:
        split_flag = "-"
        if split_flag not in today:
            split_flag = "/"
        today = datetime.date(*map(int, today.split(split_flag)))
    return today + datetime.timedelta(days=days)


def get_weekly_date(num=1, operator="-", week=calendar.SUNDAY):
    """
    获取过去、未来特定星期几的日期
    :param num: 几周
    :param operator: 操作符（"+"表示未来，"-"表示过去）
    :param week: 0=calendar.Monday, 6=calendar.SUNDAY
    """
    current_day = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    i = 0
    while True:
        if current_day.weekday() == week:
            i += 1
            if i == num:
                break
        exec(f'_day = current_day {operator} one_day')
        current_day = locals().get('_day')
    # print(current_day)
    return current_day


def get_last_day(today=None, num=7):
    """
    获取上周一的日期，不传today则用今天的日期
    """
    if not today:
        today = datetime.datetime.now()
    weekday = today.weekday()
    return today - datetime.timedelta(days=weekday + num)


def judge_time(time_flag=True):
    now_hour = datetime.datetime.now().hour
    now_day = time.strftime("%Y-%m-%d", time.localtime())
    time_interval_min = now_day + " 22:00:00"
    time_interval_max = now_day + " 23:59:59"

    if 15 <= now_hour <= 22 and time_flag:
        time_interval_min = now_day + " 12:00:00"
        time_interval_max = now_day + " 19:59:59"
    elif now_hour <= 15 or not time_flag:
        yesterday = str(datetime.date.today() + datetime.timedelta(-1))
        time_interval_min = yesterday + " 22:00:00"
        time_interval_max = now_day + " 09:59:59"

    return [time_interval_min, time_interval_max]


if __name__ == '__main__':
    """
    import datetime
    a = 'Tue Jan 07 10:29:38 +0000 2020'
    print(datetime.datetime.strptime(a, '%a %b %d %H:%M:%S +0000 %Y'))
    """
    dt = get_last_day(num=-1)
    print(judge_time(True))
