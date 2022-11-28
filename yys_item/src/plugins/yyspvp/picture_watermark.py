# -*- coding:utf-8 -*-
"""
@Time: 2022/11/15上午9:12
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: picture_watermark.py
@Detail: 图片加水印
"""
import os
from PIL import Image, ImageFont, ImageDraw


class Font:
    """字体"""

    def __init__(self, path, size=30):
        self.font_size = size
        self.font_path = path


class Watermark:
    """水印"""

    def __init__(self, image_file, text, save_image_file=None):
        """
        :param image_file: 源图片
        :param text: 水印文字
        :param save_image_file: 保存图片，默认None，覆盖源文件
        """
        if not os.path.exists(image_file):
            raise FileNotFoundError(f"{image_file} not found")
        self.text = text
        self.save_image_file = save_image_file if save_image_file is not None else image_file
        self.image = Image.open(image_file)

    def watermark_to_image(self, font: Font, fill=(0, 0, 0, 100), text_xy=None):
        """
        图片添加水印
        :param font: Font类, 字体和尺寸
        :param fill: 颜色和透明度
        :return:
        """
        new_font = ImageFont.truetype(font.font_path, font.font_size)
        # 将图片转换为RGBA图片
        layer = self.image.convert('RGBA')
        # 依照目标图片大小生成一张新的图片 参数[模式,尺寸,颜色(默认为0)]
        text_overlay = Image.new('RGBA', layer.size)
        # 画图
        image_draw = ImageDraw.Draw(text_overlay)
        if text_xy is None:
            # 获得字体大小
            text_size_x, text_size_y = image_draw.textsize(self.text, font=new_font)
            # 设置文本位置 此处是右下角显示
            text_xy = (layer.size[0] - text_size_x, layer.size[1] - text_size_y)
        # 设置位置、文字、字体、颜色和透明度
        image_draw.text(text_xy, self.text, font=new_font, fill=fill)
        marked_img = Image.alpha_composite(layer, text_overlay)
        marked_img.save(self.save_image_file)


def test():
    image_file = "test.png"
    save_image_file = "test2.png"
    font_size = 32
    font_path = "typeface/yahei/MSYH.TTC"
    font = Font(font_path, font_size)
    text = "QQ群：627691185"
    watermark = Watermark(image_file, text, save_image_file)
    watermark.watermark_to_image(font)


if __name__ == '__main__':
    test()
