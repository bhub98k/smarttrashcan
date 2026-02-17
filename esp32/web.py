from flask import Flask, request, jsonify
import os
import base64
from datetime import datetime
import cv2
from ultralytics import YOLO
import time

model = YOLO('new.pt')

app = Flask(__name__)

# 设置保存图像的目录
IMAGE_SAVE_DIR = 'received_images'
if not os.path.exists(IMAGE_SAVE_DIR):
    os.makedirs(IMAGE_SAVE_DIR)

@app.route('/')
def index():
    return 'running'

@app.route('/client')
def client_a():
    return '''import requests<br>
import base64<br>

def encode_image(image_path):
<br>&nbsp;&nbsp;&nbsp;&nbsp;with open(image_path, "rb") as image_file:
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
<br>&nbsp;&nbsp;&nbsp;&nbsp;return encoded_string<br>

image_file_path = "imgpath"     #  <======= change your imgpath<br>

server_url = "http://192.168.1.186:8787/upload"<br>

image_data = encode_image(image_file_path)<br>

payload = {"image": image_data}<br>
<br>
response = requests.post(server_url, json=payload)<br>
<br>
print(response.text)<br>
'''

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({'status': 'fail', 'message': 'No image data found in request'}), 400

        # 获取Base64编码的图像数据
        image_data = data['image']
        # 解码Base64图像数据
        image_bytes = base64.b64decode(image_data)
        
        # 生成保存文件名
        filename = datetime.now().strftime('%Y%m%d_%H%M%S') + '.jpg'
        filepath = os.path.join(IMAGE_SAVE_DIR, filename)
        
        # 保存图像文件
        with open(filepath, 'wb') as image_file:
            image_file.write(image_bytes)
            frame=cv2.imread(filepath)
            results=model(frame)
            annotated_frame = results[0].plot()
            for result in results:
                to_port=str(result.probs.top5[0]).strip()
            #cv2.imshow('',annotated_frame)
            #cv2.waitKey(1000)
            #cv2.destroyAllWindows()

        return jsonify(int(to_port))
        #return jsonify({'result': to_port , 'status': 'success', 'message': 'Image received successfully', 'filename': filename}), 200
    except Exception as e:
        return jsonify({'status': 'fail', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8787)
