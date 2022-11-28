# -*- coding:utf-8 -*-
"""
@Time: 2022/11/20下午1:26
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: build_image.py
@Detail: 
"""
import os
from PIL import Image
from html2image import Html2Image


class BuildImage:
    def __init__(self, html_code=None, css_code=None):
        self.html_code = html_code
        self.css_code = css_code
        self.hti = Html2Image()

    def make_image(self, image_name="temp.png", html_code=None, css_code=None, xy_size=(1920, 1080)):
        """
        生成图
        :param image_name: 图片名
        :param html_code: html代码
        :param css_code: css代码
        :param xy_size: 尺寸
        :return:
        """
        try:
            html_code = html_code if html_code else self.html_code
            css_code = css_code if css_code else self.css_code
            self.hti.screenshot(html_str=html_code, css_str=css_code, save_as=image_name, size=xy_size)
            if os.path.exists(image_name):
                return True
        except Exception as e:
            print(e)
        return False

    @staticmethod
    def cut_image(image_file, save_image_file=None, ltrb: list = None):
        """
        修剪图片
        :param image_file: 源文件
        :param save_image_file: 目标文件,默认None,覆盖源文件
        :param ltrb: type->list: [left, top, right, bottom] 坐标，默认None
        :return:
        """
        if not os.path.exists(image_file):
            raise FileNotFoundError(f"{image_file} not exists")
        img_src = Image.open(image_file)
        width, height = img_src.size
        # print(width, height)
        if isinstance(ltrb, list):
            left = ltrb[0] if ltrb[0] else (width / 2 - 600)
            top = ltrb[1] if ltrb[1] else 0
            right = ltrb[2] if ltrb[2] else (width / 2 + 600)
            bottom = ltrb[3] if ltrb[3] else height
        else:
            left = width / 2 - 600
            top = 0
            right = width / 2 + 600
            bottom = 500
        im = img_src.crop((left, top, right, bottom))
        if save_image_file is None:
            save_image_file = image_file
        im.save(save_image_file)
