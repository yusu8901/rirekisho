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
from dotenv import load_dotenv
import os
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = st.secrets["OPENAI_API_KEY"]


# ChatGPTで履歴書の詳細をフォーマットする関数
def get_formatted_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

# Streamlitインターフェース
st.title("履歴書生成AI")
st.write("入力に基づいて履歴書を作成するお手伝いをします。")

# 初期入力の収集
company_homepage = st.text_input("志望先のホームページ")
profile_picture = st.file_uploader("プロフィール写真をアップロード", type=["jpg", "jpeg", "png"])
hurigana= st.text_input("ふりがな")
name = st.text_input("氏名")
options =['男','女']
sex = st.selectbox("性別",options)
birthdate = st.date_input("生年月日")
phone = st.text_input("電話番号")
mail = st.text_input("メールアドレス")
post_code=st.text_input("郵便番号")
address = st.text_input("住所")
education = st.text_area("学歴（例：大学、学位、卒業年）")
work_experience = st.text_area("職歴（例：職種、会社、期間）")
skills = st.text_area("スキル（例：ソフトウェア、言語）")
licenses = st.text_area("免許・資格")
personal_statement = st.text_area("自己PR（自己紹介、志望動機）")

# # ChatGPTを使用して自己PRをフォーマット（初回実行のみ）
# if "formatted_statement" not in st.session_state:
#     if personal_statement:
#         personal_statement = get_formatted_text(
#             f"履歴書の自己PR欄に使用するため、簡潔で魅力的な文章に200文字程度で編集してください。出力は本文のみで、他の文章は出力しないでください。: {personal_statement}"
#         )
#     else:
#         personal_statement = get_formatted_text(
#             f"履歴書の自己PR欄に書く文章を200文字程度で生成してください。{skills}{licenses}を参考にしてください。出力は本文のみで、他の文章は出力しないでください。"
#         )



# 収集したデータをユーザーに確認用に表示
st.write("### 履歴書情報のプレビュー")
st.markdown(f"**氏名:** {name}")
st.markdown(f"**ふりがな:** {hurigana}")
st.markdown(f"**性別:** {sex}")
st.markdown(f"**生年月日:** {birthdate}")

st.markdown(f"**電話番号:** {phone}")
st.markdown(f"**メールアドレス:** {mail}")
st.markdown(f"**郵便番号:**{post_code}")
st.markdown(f"**住所:** {address}")
st.markdown(f"**学歴:**\n{education}")
st.markdown(f"**職歴:**\n{work_experience}")
st.markdown(f"**スキル:**\n{skills}")
st.markdown(f"**免許・資格:**\n{licenses}")


# 「自己PR文の再生成」ボタンの動作
if st.button("自己PR文のAI編集"):
    if personal_statement:
        personal_statement = get_formatted_text(
            f"履歴書の自己PR欄に使用するため、簡潔で魅力的な文章に200文字程度で編集してください。出力は本文のみで、他の文章は出力しないでください。: {personal_statement}"
        )
    else:
        personal_statement = get_formatted_text(
            f"履歴書の自己PR欄に書く文章を200文字程度で生成してください。{skills}{licenses}を参考にしてください。出力は本文のみで、他の文章は出力しないでください。"
        )

st.markdown(f"**自己PR:** {personal_statement}")

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

    # (3)証明写真
    # tableを作成
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
        [f'生年月日　　{birthdate}　　　　　　　　　　年　　　月　　　日生　（満　　　歳）', '']
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
            [f'志望の動機、自己PR、趣味、特技など\n {final_formatted_statement}','通勤時間',''],
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
    def insert_line_breaks(text, line_length=22):
        return '\n'.join([text[i:i+line_length] for i in range(0, len(text), line_length)])
    
    final_formatted_statement= insert_line_breaks(personal_statement)

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
