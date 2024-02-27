from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time

import json

with open('secret.json') as f:
    secret = json.load(f)

KEY = secret['KEY']
ENDPOINT = secret['ENDPOINT']

#認証させる
computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

def get_tags(filepath):
    local_image = open(filepath, "rb")

    tags_result = computervision_client.tag_image_in_stream(local_image)
    tags = tags_result.tags
    tags_name = []
    for tag in tags:
        tags_name.append(tag.name)
        
    return tags_name

def detect_objects(filepath):
    local_image = open(filepath, "rb")

    detect_objects_results = computervision_client.detect_objects_in_stream(local_image)
    objects = detect_objects_results.objects
    return objects

import streamlit as st
from PIL import ImageDraw #画像に描画する
from PIL import ImageFont #画像にテキストを描画するために使用

st.title('物体検出アプリ')

# 拡張子を指定し、imgフォルダに保存後パスを渡す
# st.file_uploaderでは、ファイルのパスが取得できない。
# そのため、一度imgフォルダに指定画像を保存し、そのパスを取得する。
#  取得できたパスを関数に渡し処理する

uploaded_file = st.file_uploader('Choose an image...', type=['jpg', 'png'])
if uploaded_file is not None:
    img = Image.open(uploaded_file)
    img_path = f'img/{uploaded_file.name}'
    img.save(img_path)
    objects = detect_objects(img_path)

    #　描画
    draw = ImageDraw.Draw(img)
    for object in objects:
        x = object.rectangle.x
        y = object.rectangle.y
        w = object.rectangle.w
        h = object.rectangle.h
        caption = object.object_property

        #矩形に書き込むフォントの情報を作成
        font = ImageFont.truetype(font='./Ubuntu-LightItalic.ttf', size=100)
        #text_w, text_h = draw.textlength(caption, font=font)  #captionで取得したtextのサイズを代入

        #drawモジュールのrectangle
        #fill=Noneは矩形を塗りつぶさない
        draw.rectangle([(x,y), (x+w, y+h)], fill=None, outline='green', width=15)
        #draw.rectangle([(x,y), (x+text_w, y+text_h)], fill='green')   #greenで塗りつぶし
        draw.text((x,y), caption, fill='white', font=font)            #draw.textでgreenの上にtextを描画

    st.image(img)

    tags_name = get_tags(img_path)
    tags_name = ', '.join(tags_name)   #タグに , を結合させる

    st.markdown('**認識されたコンテンツタグ**')
    st.markdown(f'> {tags_name}')

    #一度保存したファイルを削除
    import os
    os.remove(img_path)
