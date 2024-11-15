import streamlit as st

from io import BytesIO
from PIL import Image
import openai

from PIL import Image

from datetime import date

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors

from streamlit_cropper import st_cropper

import requests
from bs4 import BeautifulSoup

import tempfile

from datetime import date

# OpenAI APIキーを設定 (実際のキーを 'your-api-key' の部分に入れてください)
from dotenv import load_dotenv
import os
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# ChatGPTで履歴書の詳細をフォーマットする関数
def get_formatted_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

# 生年月日入力後に年齢を自動計算する関数
def calculate_age(birth_year, birth_month, birth_day):
    today = date.today()
    age = today.year - birth_year - ((today.month, today.day) < (birth_month, birth_day))
    return age

# 郵便番号から住所を取得する関数
def get_address_from_postcode(post_code):
    try:
        response = requests.get(f"https://api.zipaddress.net/?zipcode={post_code}")
        response.raise_for_status()
        data = response.json()
        if data['code'] == 200:
            return data['data']['fullAddress']
        else:
            return "住所が見つかりません"
    except requests.exceptions.RequestException as e:
        return f"エラーが発生しました: {e}"


#ホームページ情報取得
def get_page_text(url):
    try:
        # 指定されたURLにリクエストを送信
        response = requests.get(url)
        response.raise_for_status()  # ステータスコードがエラーの場合、例外を発生

        # HTMLを解析してテキストを取得
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(strip=True)  # ページ全体のテキストを取得
        return page_text

    except requests.exceptions.RequestException as e:
        return f"エラーが発生しました: {e}"
    




# Streamlitインターフェース
st.title("履歴書生成AI")
st.write("入力に基づいて履歴書を作成するお手伝いをします。")

# 初期入力の収集
company_homepage = st.text_input("志望先の会社理念ページURL")
profile_picture = st.file_uploader("プロフィール写真をアップロード", type=["jpg", "jpeg", "png"])
# 画像をトリミングする関数
def crop_image(image, crop_box):
    return image.crop(crop_box)

# トリミングボックスの指定（例: 左上から右下までの座標）
crop_box = (50, 50, 250, 250)  # 必要に応じて調整

# 証明写真の処理
if profile_picture:

    image = Image.open(profile_picture)
    width, height = image.size
    aspect_ratio = (width, height)  # 画像の比率に合わせる

    # Create a column layout for the cropper and preview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("写真をクロップしてください:")
        # Define cropping parameters
        aspect_ratio = (3, 4)  # Standard resume photo ratio
        cropped_img = st_cropper(
            image,
            realtime_update=True,
            box_color='#0000FF',
            
            return_type='image'
        )
    
    with col2:
        st.write("クロップ後のプレビュー:")
        # Resize the cropped image to standard resume photo size
        target_size = (30*mm, 40*mm)  # Standard resume photo size
        preview_image = cropped_img.copy()
        preview_image.thumbnail((int(target_size[0]*3), int(target_size[1]*3)))  # Larger for preview
        st.image(preview_image)
        
        # Store the cropped image in session state
        st.session_state.cropped_image = cropped_img


hurigana= st.text_input("ふりがな")
name = st.text_input("氏名")
options =['男','女']
sex = st.selectbox("性別",options)

st.write("生年月日")
col1, col2, col3 = st.columns([1, 1, 1])
birthdate_year = col1.number_input("年", min_value=1900, max_value=2030, step=1)
birthdate_month = col2.number_input("月", min_value=1, max_value=12, step=1)
birthdate_day = col3.number_input("日", min_value=1, max_value=31, step=1)
age = calculate_age(birthdate_year, birthdate_month, birthdate_day)

#1つ目電話番号、メールアドレス、郵便番号、住所
phone = st.text_input("電話番号1")

mail = st.text_input("メールアドレス1")

post_code=st.text_input("郵便番号1(○○○-○○○○)")
# 郵便番号から住所を自動取得
if post_code:
    address = get_address_from_postcode(post_code)
else:
    address = ""

# 住所入力
address_hurigana= st.text_input("住所ふりがな1")
address = st.text_input("住所1", value=address)

#2つ目電話番号、メールアドレス、郵便番号、住所
phone2 = st.text_input("電話番号2(任意)")
mail2= st.text_input("メールアドレス2(任意)")
post_code2=st.text_input("郵便番号2(○○○-○○○○)(任意)")
if post_code2:
    address2 = get_address_from_postcode(post_code2)
else:
    address2 = ""

address_hurigana2= st.text_input("住所2ふりがな(任意)")
address2 = st.text_input("住所2(任意)", value=address2)


# 学歴入力欄
st.write("学歴")
if "education" not in st.session_state:
    st.session_state.education = [{"year": "", "month": "", "description": ""}]
if "education_count" not in st.session_state:
    st.session_state.education_count = 1  # 初期値は1つ目のエントリ

# ボタンが押されたときの処理
if st.button("学歴を追加") and st.session_state.education_count < 19:
    st.session_state.education.append({"year": "", "month": "", "description": ""})
    st.session_state.education_count += 1  # カウントをインクリメント

# 学歴入力欄の表示
for i, education_entry in enumerate(st.session_state.education):
    col1, col2, col3 = st.columns([1, 1, 2])
    education_entry["year"] = col1.text_input(f"学歴 {i + 1} - 年", value=education_entry["year"], key=f"education_year_{i}")
    education_entry["month"] = col2.text_input(f"学歴 {i + 1} - 月", value=education_entry["month"], key=f"education_month_{i}")
    education_entry["description"] = col3.text_input(f"学歴 {i + 1} - 詳細", value=education_entry["description"], key=f"education_description_{i}")



# 必要なエントリ数に満たない場合、空のエントリを追加
while len(st.session_state.education) < st.session_state.education_count:
    st.session_state.education.append({"year": "", "month": "", "description": ""})


# 職歴入力欄
st.write("職歴")
if "work_experience" not in st.session_state:
    st.session_state.work_experience = [{"year": "", "month": "", "description": ""}]
if "work_experience_count" not in st.session_state:
    st.session_state.work_experience_count = 1  # 初期値は1つ目のエントリ

# ボタンが押されたときの処理
if st.button("職歴を追加") and st.session_state.work_experience_count < 8:
    st.session_state.work_experience.append({"year": "", "month": "", "description": ""})
    st.session_state.work_experience_count += 1  # カウントをインクリメント

# 職歴入力欄の表示
for i, work_entry in enumerate(st.session_state.work_experience):
    col1, col2, col3 = st.columns([1, 1, 2])
    work_entry["year"] = col1.text_input(f"職歴 {i + 1} - 年", value=work_entry["year"], key=f"work_year_{i}")
    work_entry["month"] = col2.text_input(f"職歴 {i + 1} - 月", value=work_entry["month"], key=f"work_month_{i}")
    work_entry["description"] = col3.text_input(f"職歴 {i + 1} - 詳細", value=work_entry["description"], key=f"work_description_{i}")



# 必要なエントリ数に満たない場合、空のエントリを追加
while len(st.session_state.work_experience) < st.session_state.work_experience_count:
    st.session_state.work_experience.append({"year": "", "month": "", "description": ""})



# 免許・資格入力欄
st.write("免許・資格")
if "licenses" not in st.session_state:
    st.session_state.licenses = [{"year": "", "month": "", "description": ""}]
if "licenses_count" not in st.session_state:
    st.session_state.licenses_count = 1  # 初期値は1つ目のエントリ

# ボタンが押されたときの処理
if st.button("免許・資格を追加") and st.session_state.licenses_count < 19:
    st.session_state.licenses.append({"year": "", "month": "", "description": ""})
    st.session_state.licenses_count += 1  # カウントをインクリメント

# 免許・資格入力欄の表示
for i, license_entry in enumerate(st.session_state.licenses):
    col1, col2, col3 = st.columns([1, 1, 2])
    license_entry["year"] = col1.text_input(f"免許・資格 {i + 1} - 年", value=license_entry["year"], key=f"license_year_{i}")
    license_entry["month"] = col2.text_input(f"免許・資格 {i + 1} - 月", value=license_entry["month"], key=f"license_month_{i}")
    license_entry["description"] = col3.text_input(f"免許・資格 {i + 1} - 詳細", value=license_entry["description"], key=f"license_description_{i}")



# 必要なエントリ数に満たない場合、空のエントリを追加
while len(st.session_state.licenses) < st.session_state.licenses_count:
    st.session_state.licenses.append({"year": "", "month": "", "description": ""})

commuting_hours = st.number_input("通勤時間（時間）", min_value=0, max_value=24, step=1)
commuting_minutes = st.number_input("通勤時間（分）", min_value=0, max_value=55, step=5)
dependents = st.number_input("扶養家族（人数）", min_value=0, step=1)
has_partner = st.radio("配偶者", options=["有", "無"])
partner_support = st.radio("配偶者の扶養義務", options=["有", "無"])
skills = st.text_area("スキル（例：ソフトウェア、言語）")
personal_statement = st.text_area("自己PR（自己紹介、志望動機）")
personal_request = st.text_area("本人希望記入欄（特に待遇・職種・勤務時間・その他についての希望などがあれば記入）")


# 収集したデータをユーザーに確認用に表示
st.write("### 履歴書情報のプレビュー")
st.markdown(f"**氏名:** {name}")
st.markdown(f"**ふりがな:** {hurigana}")
st.markdown(f"**性別:** {sex}")
st.markdown(f"**生年月日:** {birthdate_year}年{birthdate_month}月{birthdate_day}日")
st.markdown(f"**年齢:** {age}歳")
st.markdown(f"**電話番号1:** {phone}")
st.markdown(f"**メールアドレス1:** {mail}")
st.markdown(f"**郵便番号1:**{post_code}")
st.markdown(f"**住所ふりがな1：**{address_hurigana}")
st.markdown(f"**住所1:** {address}")
st.markdown(f"**電話番号2:** {phone2}")
st.markdown(f"**メールアドレス2:** {mail2}")
st.markdown(f"**郵便番号2:**{post_code2}")
st.markdown(f"**住所ふりがな2：**{address_hurigana2}")
st.markdown(f"**住所2:** {address2}")
st.write("**学歴:**")
for entry in st.session_state.education:
    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{entry['year']}年 {entry['month']}月 - {entry['description']}")
# データを表示（確認用）
st.write("**職歴:**")
for entry in st.session_state.work_experience:
    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{entry['year']}年 {entry['month']}月 - {entry['description']}")

st.write(f"**通勤時間:** 　約{commuting_hours}時間 {commuting_minutes}分")
st.write(f"扶養家族の人数: {dependents}人")
st.write(f"**配偶者**:　 {has_partner}")
st.write(f"**配偶者の扶養義務**:　 {partner_support}")
st.markdown(f"**スキル:**\n{skills}")
st.write("**免許・資格**")
for entry in st.session_state.licenses:
    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{entry['year']}年 {entry['month']}月 - {entry['description']}")
st.markdown(f"**本人希望記入欄:** {personal_request}")

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
        # クロップされた画像を使用
        cropped_image = st.session_state.cropped_image
        cropped_image = cropped_image.resize((100, 130))  # 画像サイズを調整
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image_file:
            cropped_image.save(temp_image_file.name)
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
        [f'ふりがな: {address_hurigana}', f'電話: {phone}'],
        [f'連絡先（〒{post_code}）\n {address}', f'E-mail: \n{mail}'],
        [f'ふりがな: {address_hurigana2}', f'電話: {phone2}'],
        [f'連絡先（〒{post_code2}）\n {address2}', f'E-mail: \n{mail2}'],
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

# Streamlitアプリケーション

st.write("\下のボタンをクリックすると、履歴書フォーマットのPDFが生成されます。自己PRはAIによって編集されます。")

if st.button("自己PR生成・履歴書生成"):
    about_company = get_page_text(company_homepage)

    if personal_statement:
        formatted_statement = get_formatted_text(
            f"履歴書の自己PR欄に使用するため、簡潔で魅力的な文章に200文字程度で編集してください。出力は本文のみで、他の文章は絶対に出力しないでください。編集前文[{personal_statement}],スキル：[{skills}]志望先会社概要[{about_company}]"
        )
    else:
        formatted_statement = get_formatted_text(
            f"履歴書の自己PR欄に使用するため、簡潔で魅力的な文章を200文字程度で生成してください。スキル：{skills}、志望先会社概要：{about_company}を参考にしてください。出力は本文のみで、他の文章は絶対に出力しないでください。"
        )
    st.markdown(f"**自己PR:** {formatted_statement}")

    def insert_line_breaks(text, line_length):
        return '\n'.join([text[i:i+line_length] for i in range(0, len(text), line_length)])
    
    final_formatted_statement= insert_line_breaks(formatted_statement,22)
    final_personal_request = insert_line_breaks(personal_request,43)

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

