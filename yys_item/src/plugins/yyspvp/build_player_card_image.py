# -*- coding:utf-8 -*-
"""
@Time: 2022/11/20上午2:06
@Author: kasper
@Email: yyscbg@gmail.com
@FileName: html_cart_build_image.py
@Detail: 
"""
import os
import time
from functools import reduce

from build_image import BuildImage
from picture_watermark import Font, Watermark

base_path = reduce(lambda x, _: os.path.dirname(x), range(4), __file__)

css_code = """
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Poppins', sans-serif;
    }
    body {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background: linear-gradient(45deg, #fbda61, #ff5acd);
    }
    .card {
        text-align: center;
        position: relative;
        width: 350px;
        height: 400px;
        background: #fff;
        border-radius: 20px;
        box-shadow: 0 35px 80px rgba(0, 0, 0, 0.15);
        transition: 0.5s;
    }
    .details {
        padding: 30px;
        text-align: center;
        transition: 0.5s;
        /**transform: translateY(1px);**/
    }

    .details h2 span {
        font-size: 0.75em;
        font-weight: 500;
        opacity: 0.5;
    }
      
    .details .data {
        display: flex;
        justify-content: space-between;
        margin: 10px 0;
    }

    .details .data h3 {
        font-size: 1em;
        color: #555;
        line-height: 1.2em;
        font-weight: 600;
    }

    .details .data h3 span {
        font-size: 0.85em;
        font-weight: 400;
        opacity: 0.5;
    }
      
    .battle {
        text-align: center;
        height: 100px;
        border: none;
        outline: none;
        font-size: .9em;
        font-weight: 500;
        background: #fff;
        cursor: pointer;
    } 
    .battle-image{
        margin-left: 12px;
        margin-bottom: 30px;
    }
    img {
        height: 45px; 
        float: left;
    }
    .battle-title {
        color: #999;
        font-size: 0.9em;
        font-weight: 500;
        margin-bottom: 10px;
    }
"""

bd_img = BuildImage(css_code=css_code)


def wait_build_image(_file, num=3):
    """等待制图"""
    while True:
        time.sleep(num)
        if os.path.exists(_file):
            return True


def build_card_image(infos):
    """生成卡片图"""
    if not isinstance(infos, dict):
        raise ValueError(f"{infos} not a dict")
    date_range = infos.get('date_range', "")
    role_name = infos.get('role_name', "")
    server_name = infos.get('server_name', "")
    rank = infos.get('rank', 0)
    score = infos.get('score', 0)
    all_counts = infos.get('all_counts', 0)
    win_rate = infos.get('win_rate', 0)
    image_src_list = infos.get('image_src_list', [])
    image_1 = image_src_list[0]
    image_2 = image_src_list[1]
    image_3 = image_src_list[2]
    image_4 = image_src_list[3]
    image_5 = image_src_list[4]
    image_6 = image_src_list[5]
    bj_rate = "xx"
    steal_flower = "xx"
    html_code = f"""
        <!DOCTYPE html>
        <html lang="en">
            <head><title>阴阳师玩家战绩信息</title></head>
        <body>
            <div class="card"><br>
            <p>时间截止</p>
            <span style="color: #999;">{date_range}</span>
            <div class="details">
                <h2>{role_name}<br><span>{server_name}</span></h2>
                <div class="data">
                    <h3>{rank}<br><span>Rank</span></h3>
                    <h3>{score}<br><span>Score</span></h3>
                    <h3>{all_counts}<br><span>Counts</span></h3>
                    <h3>{win_rate}%<br><span>Win Rate</span></h3>
                </div>
                <div class="battle">
                    <p class="battle-title">常用阵容</p>
                    <div class="battle-image">
                        <img  src="{image_1}" >
                        <img  src="{image_2}" >
                        <img  src="{image_3}" >
                        <img  src="{image_4}" >
                        <img  src="{image_5}" >
                        <img  src="{image_6}">
                    </div>
                </div>
                <!-- <div class="data">
                    <h3><br><span></span></h3>
                    <h3>{bj_rate}%<br><span>蚌精</span></h3>
                    <h3>{steal_flower}%<br><span>偷花</span></h3>
                    <h3><br><span></span></h3>
                </div> -->
            </div>
          </div>
        </body>
        </html>
    """

    image_path = os.path.join(base_path, "image")
    image_file = "temp_card" + str(time.time() * 1000)[:13] + "." + ".png"
    save_image_file = os.path.join(image_path, "temp_cut_card_" + str(time.time() * 1000)[:13] + ".png")

    try:
        # 生成卡片
        bd_img.make_image(image_file, html_code)
        if wait_build_image(image_file, num=3):
            # 修剪图片
            bd_img.cut_image(image_file, save_image_file, [3840/2-352, 2160/2-400, 3840/2+352, 2160/2+400])
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


if __name__ == '__main__':
    infos = {
        'date_range': "xasdfasdfasd",
        'role_name': "xadsf",
        'server_name': "两心无间",
        'rank': 1,
        'score': 123,
        'all_counts': 0,
        'win_rate': 0,
        "image_src_list": [
            "https://ok.166.net/gameyw-misc/opd/squash/yys/icon/330.jpg",
            "https://ok.166.net/gameyw-misc/opd/squash/20220727/125009-vas95edl7s.jpg",
            "https://ok.166.net/gameyw-misc/opd/squash/yys/icon/272.jpg",
            "https://ok.166.net/gameyw-misc/opd/squash/20201202/141318-lqy9e734zb.jpg",
            "https://ok.166.net/gameyw-misc/opd/squash/20220809/144502-bmpevdssfc.png",
            "https://g.166.net/assets/img/yys/yys/12.jpg"
        ]
    }
    build_card_image(infos)
