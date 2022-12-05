# -*- coding:utf-8 -*-
"""
@Time: 2022/11/15上午9:28
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: html_generate_picture.py
@Detail: html生成图片
"""

import os
import time
from functools import reduce

from .build_image import BuildImage
from .picture_watermark import Font, Watermark

bd_img = BuildImage()

base_path = reduce(lambda x, _: os.path.dirname(x), range(4), __file__)


def make_table_image(thead, title, table_content, image_name="./temp.png", _size=(1920, 1080)):
    """生成表格图"""
    html_code = f"""
        <body> 
            <br>
            <table width="25%"  class="table">
                <caption style="margin-bottom: 10px; color: gray;">{title}</caption>
                <thead>
                    <tr>
                        <th>{thead}</th>
                        <th>星数或分数</th>
                    </tr>
                </thead>
                {table_content}
            </table>
        </body>
    """
    css_code = """
        table
        {
            border-collapse: collapse;
            margin: 0 auto;
            text-align: center;
        }
        table td, table th
        {
            border: 1px solid #cad9ea;
            color: #666;
            height: 30px;
        }
        table thead th
        {
            background-color: #CCE8EB;
            width: 100px;
        }
        table tr:nth-child(odd)
        {
            background: #fff;
        }
        body, table tr:nth-child(even)
        {
            background: #F5FAFA;
        }
    """
    return bd_img.make_image(image_name, html_code=html_code, css_code=css_code, xy_size=_size)


def wait_build_image(_file, num=3):
    """等待制图"""
    while True:
        time.sleep(num)
        if os.path.exists(_file):
            return True


def run_image(datas, title, _type=None):
    """生成图片"""
    table_content = ""
    if _type == "all_blue":
        # 全服蓝帽子
        for data in datas:
            score = data["score"]
            dt_time = data["server_name"]
            __content = f"<tr><td>{dt_time}</td><td>{score}</td></tr>"
            table_content += __content
    else:
        for data in datas:
            score = data["score"]
            dt_time = data["date_range"]
            __content = f"<tr><td>{dt_time}</td><td>{score}</td></tr>"
            table_content += __content

    image_path = os.path.join(base_path, "image")
    image_file = "temp" + str(time.time() * 1000)[:13] + "." + ".png"
    save_image_file = os.path.join(image_path, "temp_cut_" + str(time.time() * 1000)[:13] + ".png")

    try:
        # 生成表格图
        if _type == "all_blue":
            _size = [False, False, False, False]
            make_table_image("区名", title, table_content, image_name=image_file, _size=(1920, 2520))
        else:
            _size = None
            make_table_image("日期", title, table_content, image_name=image_file)

        if wait_build_image(image_file, num=3):
            # 修剪图片
            bd_img.cut_image(image_file, save_image_file, _size)

        if wait_build_image(save_image_file, num=1):
            # 上水印
            font_size = 32
            font_path = os.path.join(base_path, "typeface/yahei/MSYH.TTC")
            font = Font(font_path, font_size)
            text = "QQ群：627691185"
            _fn = save_image_file.split(".")
            new_save_image_file = _fn[0] + "_" + str(time.time() * 1000)[:13] + "." + _fn[1]
            watermark = Watermark(save_image_file, text, new_save_image_file)
            print(save_image_file, new_save_image_file)
            watermark.watermark_to_image(font)
            time.sleep(3)
        if wait_build_image(new_save_image_file, num=3):
            os.remove(image_file)
            os.remove(save_image_file)
            return new_save_image_file
    except Exception as e:
        print(e)
        return False
