import streamlit as st

from io import BytesIO
from PIL import Image
import openai

from resume_pdf import make

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors

import requests
from bs4 import BeautifulSoup

import tempfile

from datetime import date



# 初期設定
def make(filename):
    pdf_canvas = set_info(filename)
    print_string(pdf_canvas)
    pdf_canvas.save()  # 保存
    return filename

def set_info(filename):
    pdf_canvas = canvas.Canvas(filename)
    pdf_canvas.setAuthor("")  # 作者
    pdf_canvas.setTitle("")  # 表題
    pdf_canvas.setSubject("")  # 件名
    return pdf_canvas

# 履歴書フォーマット作成
def print_string(pdf_canvas):
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    width, height = A4

    # (1)履歴書 タイトル
    font_size = 24
    pdf_canvas.setFont('HeiseiKakuGo-W5', font_size)
    pdf_canvas.drawString(60, 770, '履  歴  書')

    # (2)作成日
    font_size = 10
    pdf_canvas.setFont('HeiseiKakuGo-W5', font_size)
    # 今日の日付を取得
    today = date.today()
    # 年 月 日形式でフォーマット
    formatted_date = today.strftime("%Y年 %m月 %d日")
    pdf_canvas.drawString(285, 770, f' {formatted_date}現在')

    # (3)証明写真
    # tableを作成
    if profile_picture:
        image = Image.open(profile_picture)
        image = image.resize((100, 130))  # 画像サイズを調整
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image_file:
            image.save(temp_image_file.name)
            pdf_canvas.drawImage(temp_image_file.name, 145*mm, 235*mm, width=30*mm, height=40*mm)
    else:
        data = [
                ['    証明写真'],
            ]
        table = Table(data, colWidths=30*mm, rowHeights=40*mm) # tableの大きさ
        table.setStyle(TableStyle([                              # tableの装飾
                ('FONT', (0, 0), (0, 0), 'HeiseiKakuGo-W5', 12), # フォントサイズ
                ('BOX', (0, 0), (0, 0), 1, colors.black),        # 罫線
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),            # フォント位置
            ]))
        table.wrapOn(pdf_canvas, 145*mm, 235*mm) # table位置
        table.drawOn(pdf_canvas, 145*mm, 235*mm)

    # (4)プロフィール
    data = [
        [f'ふりがな: {hurigana}', f' {sex}  '],  
        [f'氏名: \n\n　　{name}', ''],
        [f'生年月日　　　　　　　　　{birthdate_year}年　{birthdate_month}月　　{birthdate_day}日生　（満　　{age}歳）', '']
    ]

    table = Table(data, colWidths=(100*mm, 20*mm), rowHeights=(7*mm, 20*mm, 7*mm))
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (1, 2), 'HeiseiKakuGo-W5', 8),
        ('BOX', (0, 0), (1, 2), 1, colors.black),
        ('INNERGRID', (0, 0), (1, 2), 1, colors.black),
        ('SPAN', (0, 2), (1, 2)),
        ('SPAN', (1, 0), (1, 1)),
        ('VALIGN', (0, 0), (1, 2), 'MIDDLE'),
        ('VALIGN', (0, 1), (0, 1), 'TOP'),
    ]))

    # テーブルの描画位置指定
    table.wrapOn(pdf_canvas, 20*mm, 232*mm)
    table.drawOn(pdf_canvas, 20*mm, 232*mm)

    

    # (5)住所
    data = [
        ['ふりがな', f'電話: {phone}'],
        [f'連絡先（〒{post_code}）\n {address}', f'E-mail: \n{mail}'],
        ['ふりがな', '電話'],
        ['連絡先（〒　　　ー　　　　）', 'E-mail'],
    ]
    table = Table(data, colWidths=(120*mm, 40*mm), rowHeights=(7*mm, 20*mm, 7*mm, 20*mm))
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (1, 3), 'HeiseiKakuGo-W5', 9),
        ('BOX', (0, 0), (1, 3), 1, colors.black),
        ('INNERGRID', (0, 0), (1, 3), 1, colors.black),
        ('VALIGN', (0, 0), (1, 2), 'MIDDLE'),
        ('VALIGN', (0, 1), (1, 1), 'TOP'),
        ('VALIGN', (0, 3), (1, 3), 'TOP'),
    ]))
    table.wrapOn(pdf_canvas, 20*mm, 178*mm)
    table.drawOn(pdf_canvas, 20*mm, 178*mm)

    # 学歴データの準備（不足するエントリには空データを追加）
    education_data = []
    for i in range(19):  # 最大19エントリ
        if i < len(st.session_state.education):
            year = st.session_state.education[i]["year"]
            month = st.session_state.education[i]["month"]
            description = st.session_state.education[i]["description"]
            education_data.append([f'{year}', f'{month}', f'{description}'])
        else:
            education_data.append(["", "", ""])  # 空データ

    # 職歴データの準備
    work_experience_data = []
    for i in range(9):
        if i < len(st.session_state.work_experience):
            year = st.session_state.work_experience[i]["year"]
            month = st.session_state.work_experience[i]["month"]
            description = st.session_state.work_experience[i]["description"]
            work_experience_data.append([f'{year}', f'{month}', f'{description}'])
        else:
            work_experience_data.append(["", "", ""])

    # 免許・資格データの準備
    license_data = []
    for i in range(7):
        if i < len(st.session_state.licenses):
            year = st.session_state.licenses[i]["year"]
            month = st.session_state.licenses[i]["month"]
            description = st.session_state.licenses[i]["description"]
            license_data.append([f'{year}', f'{month}', f'{description}'])
        else:
            license_data.append(["", "", ""])


    # (6)学歴・職歴


    data = [
            ['        年', '   月', '                                            学歴・職歴'],  
    ]
    data.extend(education_data)  # 学歴データを追加

        
    table = Table(data, colWidths=(25*mm, 14*mm, 121*mm), rowHeights=7.5*mm)
    table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'HeiseiKakuGo-W5', 11),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
    table.wrapOn(pdf_canvas, 20*mm, 20*mm)
    table.drawOn(pdf_canvas, 20*mm, 20*mm)

    pdf_canvas.showPage()

    # (7)学歴・職歴、免許・資格
    data = [ 
            ['        年', '   月', '                                            学歴・職歴'],
    ]
    data.extend(work_experience_data)  # 職歴データを追加
    data.append(['        年', '   月', '                                            免許・資格'])
    data.extend(license_data)  # 免許・資格データを追加

    table = Table(data, colWidths=(25*mm, 14*mm, 121*mm), rowHeights=7.5*mm)
    table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'HeiseiKakuGo-W5', 11),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
    table.wrapOn(pdf_canvas, 20*mm, 132*mm)
    table.drawOn(pdf_canvas, 20*mm, 132*mm)
   
    # (8)そのほか
    data = [
            [f'志望の動機、自己PR、趣味、特技など\n {final_formatted_statement}','通勤時間',''],
            ['',f'                        約　{commuting_hours}時間　{commuting_minutes}分',''],
            ['','扶養家族（配偶者を除く）',''],
            ['',f'                              　　　　    　{dependents}人',''],
            ['','配偶者','配偶者の扶養義務'],
            ['',f'       {has_partner}',f'       {partner_support}'],
            ['本人希望記入欄（特に待遇・職種・勤務時間・その他についての希望などがあれば記入）','',''],
            [f'{final_personal_request}','','']

        ]
    table = Table(data, colWidths=(90*mm, 35*mm, 35*mm), rowHeights=(8*mm, 10*mm, 8*mm, 10*mm, 8*mm, 10*mm, 8*mm, 50*mm))
    table.setStyle(TableStyle([
            ('FONT', (0, 0), (2, 7), 'HeiseiKakuGo-W5', 10),
            ('BOX', (0, 0), (2, 7), 1, colors.black),
            ('LINEBEFORE', (1, 0), (1, 5), 1, colors.black),
            ('LINEBEFORE', (2, 4), (2, 5), 1, colors.black),
            ('LINEABOVE', (1, 2), (2, 2), 1, colors.black),
            ('LINEABOVE', (1, 4), (2, 4), 1, colors.black),
            ('LINEABOVE', (0, 6), (2, 6), 1, colors.black),
            ('LINEABOVE', (0, 7), (2, 7), 1, colors.black),
            ('VALIGN', (0, 0), (2, 5), 'TOP'),
            ('VALIGN', (0, 6), (2, 6), 'MIDDLE'),
            ('VALIGN', (0, 7), (2, 7), 'TOP'),
        ]))
    table.wrapOn(pdf_canvas, 20*mm, 20*mm)
    table.drawOn(pdf_canvas, 20*mm, 20*mm)

    # 2枚目終了
    pdf_canvas.showPage()