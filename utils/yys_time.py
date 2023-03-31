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
    """
    获取当前时间戳
    :param is_second: 是否返回秒级时间戳，默认为 True
    :return: Unix 时间戳，单位为秒或毫秒
    """
    if is_second:
        return int(datetime.datetime.now().timestamp())
    else:
        return int(datetime.datetime.now().timestamp() * 1000)


def datetime_to_timestamp(str_time):
    """
    把日期时间字符串转换为 Unix 时间戳
    :param str_time: 日期时间字符串，格式为 "%Y-%m-%d %H:%M:%S"
    :return: Unix 时间戳（秒数）
    """
    dt = datetime.datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S')
    return int(dt.timestamp())


def timestamp_to_datetime(timestamp):
    """
    把 Unix 时间戳转换为日期时间字符串
    :param timestamp: Unix 时间戳（秒数）
    :return: 日期时间字符串，格式为 "%Y-%m-%d %H:%M:%S"
    """
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def get_now():
    """
    获取当前时间
    :return: 日期时间字符串，格式为 "%Y-%m-%d %H:%M:%S"
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_now_date():
    """
    获取当前日期
    :return: 日期对象（datetime.date）
    """
    return datetime.datetime.now().date()


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


def get_offset_date(offset=1, unit="days", date_str=None, date_format="%Y-%m-%d"):
    """
    获取过去或未来指定时间偏移量后的日期
    :param offset: 时间偏移量
    :param unit: 时间偏移单位，默认为 "days"
    :param date_str: 基准日期字符串，例如 "2022-01-01"
    :param date_format: 日期字符串格式，默认为 "%Y-%m-%d"
    :return: 指定偏移量后的日期字符串
    """
    if not date_str:
        base_date = datetime.datetime.now().date()
    else:
        try:
            base_date = datetime.datetime.strptime(date_str, date_format).date()
        except ValueError:
            raise ValueError("Invalid date string format: {}".format(date_str))

    if unit == "days":
        delta = datetime.timedelta(days=offset)
    elif unit == "hours":
        delta = datetime.timedelta(hours=offset)
    elif unit == "minutes":
        delta = datetime.timedelta(minutes=offset)
    elif unit == "seconds":
        delta = datetime.timedelta(seconds=offset)
    else:
        raise ValueError("Invalid time unit: {}".format(unit))

    offset_date = base_date + delta
    return offset_date.strftime(date_format)


def get_before_Or_after_few_times(current_time=None, **kwargs):
    """获取过去未来若干时间
    :param current_time: 当前时间
    :param kwargs: 支持(days=0, seconds=0, microseconds=0,milliseconds=0, minutes=0, hours=0, weeks=0)
    """
    if current_time is None:
        current_time = datetime.datetime.now()
    elif isinstance(current_time, str):
        # 转为datetime对象
        current_time = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")

    delta = datetime.timedelta(**kwargs)
    future_time = current_time + delta

    return future_time.strftime("%Y-%m-%d %H:%M:%S")


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
    print(current_day)
    return current_day


def new_get_weekly_date(num=1, operator="-", weekday=6):
    """
    获取过去、未来特定星期几的日期
    :param num: 几周，默认为 1
    :param operator: 操作符（"+"表示未来，"-"表示过去），默认为 "-"
    :param weekday: 星期几，0=Monday, 1=Tuesday, ..., 6=Sunday，默认为 6（即周日）
    :return: 日期对象（datetime.date）
    """
    current_day = datetime.date.today()
    days_to_go = (weekday - current_day.weekday()) % 7 + 7 * (num - 1)
    if operator == "-":
        days_to_go = -days_to_go
    result_day = current_day + datetime.timedelta(days=days_to_go)
    return result_day


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
    dt = get_before_Or_after_few_times('2023-03-29 14:41:20', hours=10)
    print(dt)
