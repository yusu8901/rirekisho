import streamlit as st
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
import openai

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors

import tempfile

# OpenAI APIキーを設定 (実際のキーを 'your-api-key' の部分に入れてください)
import os
api_key = os.getenv("OPENAI_API_KEY")


# ChatGPTで履歴書の詳細をフォーマットする関数
def get_formatted_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

# Streamlitインターフェース
st.title("履歴書生成チャットボット")
st.write("このチャットボットは、入力に基づいて履歴書を作成するお手伝いをします。")

# 初期入力の収集
company_homepage = st.text_input("志望先のホームページ")
profile_picture = st.file_uploader("プロフィール写真をアップロード", type=["jpg", "jpeg", "png"])
hurigana= st.text_input("ふりがな")
name = st.text_input("氏名")
birthdate = st.date_input("生年月日")
phone = st.text_input("電話番号")
mail = st.text_input("メールアドレス")
address = st.text_input("住所")
education = st.text_area("学歴（例：大学、学位、卒業年）")
work_experience = st.text_area("職歴（例：職種、会社、期間）")
skills = st.text_area("スキル（例：ソフトウェア、言語）")
licenses = st.text_area("免許・資格")
personal_statement = st.text_area("自己PR（自己紹介、志望動機）")

# ChatGPTを使用して自己PRをフォーマット
if personal_statement:
    formatted_statement = get_formatted_text(f"履歴書用にフォーマットしてください: {personal_statement}")
else:
    formatted_statement = get_formatted_text("履歴書用の自己紹介を生成してください。")

# 収集したデータをユーザーに確認用に表示
st.write("### 履歴書情報のプレビュー")
st.write(f"**氏名:** {name}")
st.write(f"**ふりがな:**{hurigana}")
st.write(f"**生年月日:** {birthdate}")
st.write(f"**電話番号:** {phone}")
st.write(f"**メールアドレス:** {mail}")
st.write(f"**住所:** {address}")
st.write(f"**学歴:**\n{education}")
st.write(f"**職歴:**\n{work_experience}")
st.write(f"**スキル:**\n{skills}")
st.write(f"**免許・資格:**\n{licenses}")
st.write(f"**自己PR:** {formatted_statement}")

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
    pdf_canvas.drawString(285, 770, '    年         月         日現在')

    # (3)証明写真 & プロフィール
    data = [
        [f'ふりがな: {hurigana}', '   男  ・  女'],  
        [f'氏名: \n\n　　{name}', ''],
        [f'生年月日　　　　　　　　　　{birthdate}　　　　　　　　　　年　　　月　　　日生　（満　　　歳）', '']
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

    # 以降省略...

    # (5)住所
    data = [
        ['ふりがな', f'電話: {phone}'],
        [f'連絡先（〒　　　ー　　　　）\n {address}', f'E-mail: {mail}'],
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

    # (6)学歴・職歴
    data = [
            ['        年', '   月', '                                            学歴・職歴'],
            [' ', ' ', f'{education} '],
            [' ', ' ', f'{work_experience} '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' ']
        ]
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
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            ['        年', '   月', '                                            免許・資格'],
            [' ', ' ', f'{licenses} '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
        ]
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
            [f'志望の動機、自己PR、趣味、特技など\n {skills}','通勤時間',''],
            ['','                        約　　　　時間　　　　分',''],
            ['','扶養家族（配偶者を除く）',''],
            ['','                              　　　　    　　　　人',''],
            ['','配偶者','配偶者の扶養義務'],
            ['','       有    ・    無','       有    ・    無'],
            ['本人希望記入欄（特に待遇・職種・勤務時間・その他についての希望などがあれば記入）','',''],
            ['','','']

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
        ]))
    table.wrapOn(pdf_canvas, 20*mm, 20*mm)
    table.drawOn(pdf_canvas, 20*mm, 20*mm)

    # 2枚目終了
    pdf_canvas.showPage()

# Streamlitアプリケーション

st.write("下のボタンをクリックすると、履歴書フォーマットのPDFが生成されます。")

if st.button("PDFを生成"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        filename = tmpfile.name
        make(filename)

        with open(filename, "rb") as f:
            st.download_button(
                label="ダウンロードする",
                data=f,
                file_name="resume.pdf",
                mime="application/pdf"
            )
