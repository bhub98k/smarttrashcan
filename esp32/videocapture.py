'''
import cv2
import numpy as np
def setcamera(cap):
    cap.set(6,cv2.VideoWriter.fourcc('M','J','P','E','G'))
    cap.set(3,480)
    cap.set(4,640)
cap = cv2.VideoCapture('http://192.168.50.196/cam.mjpeg')
setcamera(cap)
while(True):
    ret, frame = cap.read()
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
'''
'''
import cv2
from urllib.request import urlopen
import numpy as np

url = r'http://192.168.50.196/cam.mjpeg'
while True:
    img_resp = urlopen(url)
    imgnp = np.asarray(bytearray(img_resp.read()), dtype="uint8")
    img = cv2.imdecode(imgnp, -1)
    cv2.imshow("Camera", img)
    if cv2.waitKey(1) == 113:
        break
'''
'''
import cv2 #opencv
import urllib.request #to open and read URL
import numpy as np
 
#OBJECT CLASSIFICATION PROGRAM FOR VIDEO IN IP ADDRESS
 
url = 'http://192.168.50.196/cam-hi.jpg'
#url = 'http://192.168.1.6/'
winName = 'ESP32 CAMERA'
cv2.namedWindow(winName,cv2.WINDOW_AUTOSIZE)
#scale_percent = 80 # percent of original size    #for image processing
 
classNames = []
classFile = 'coco.names'
with open(classFile,'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')
 
configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'
 
net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
#net.setInputSize(480,480)
net.setInputScale(1.0/127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)
 
while(1):
    imgResponse = urllib.request.urlopen (url) # here open the URL
    imgNp = np.array(bytearray(imgResponse.read()),dtype=np.uint8)
    img = cv2.imdecode (imgNp,-1) #decodificamos
 
    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) # vertical
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #black and white
 
    
 
    classIds, confs, bbox = net.detect(img,confThreshold=0.5)
    print(classIds,bbox)
 
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            cv2.rectangle(img,box,color=(0,255,0),thickness = 3) #mostramos en rectangulo lo que se encuentra
            cv2.putText(img, classNames[classId-1], (box[0]+10,box[1]+30), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0),2)
 
 
    cv2.imshow(winName,img) #  show the picture
 
    #wait for ESC to be pressed to end the program
    tecla = cv2.waitKey(5) & 0xFF
    if tecla == 27:
        break
cv2.destroyAllWindows()
'''
'''
import cv2
import requests
from bs4 import BeautifulSoup

img = cv2.imread('http://192.168.50.196/cam-hi.jpg')   # 開啟圖片，預設使用 cv2.IMREAD_COLOR 模式
cv2.imshow('oxxostudio', img)  # 使用名為 oxxostudio 的視窗開啟圖片
cv2.waitKey(0)                 # 按下任意鍵停止
cv2.destroyAllWindows()  
'''

import cv2
import numpy as np

import requests

'''INFO SECTION
- if you want to monitor raw parameters of ESP32CAM, open the browser and go to http://192.168.x.x/status
- command can be sent through an HTTP get composed in the following way http://192.168.x.x/control?var=VARIABLE_NAME&val=VALUE (check varname and value in status)
'''

# ESP32 URL
URL = "http://192.168.50.196/cam.mp4"
AWB = True

# Face recognition and opencv setup
cap = cv2.VideoCapture(URL + ":81/stream")
face_classifier = cv2.CascadeClassifier('.xml') # insert the full path to haarcascade file if you encounter any problem

def set_resolution(url: str, index: int=1, verbose: bool=False):
    try:
        if verbose:
            resolutions = "10: UXGA(1600x1200)\n9: SXGA(1280x1024)\n8: XGA(1024x768)\n7: SVGA(800x600)\n6: VGA(640x480)\n5: CIF(400x296)\n4: QVGA(320x240)\n3: HQVGA(240x176)\n0: QQVGA(160x120)"
            print("available resolutions\n{}".format(resolutions))

        if index in [10, 9, 8, 7, 6, 5, 4, 3, 0]:
            requests.get(url + "/control?var=framesize&val={}".format(index))
        else:
            print("Wrong index")
    except:
        print("SET_RESOLUTION: something went wrong")

def set_quality(url: str, value: int=1, verbose: bool=False):
    try:
        if value >= 10 and value <=63:
            requests.get(url + "/control?var=quality&val={}".format(value))
    except:
        print("SET_QUALITY: something went wrong")

def set_awb(url: str, awb: int=1):
    try:
        awb = not awb
        requests.get(url + "/control?var=awb&val={}".format(1 if awb else 0))
    except:
        print("SET_QUALITY: something went wrong")
    return awb

if __name__ == '__main__':
    set_resolution(URL, index=8)

    while True:
        if cap.isOpened():
            ret, frame = cap.read()

            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)

                faces = face_classifier.detectMultiScale(gray)
                for (x, y, w, h) in faces:
                    center = (x + w//2, y + h//2)
                    frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 4)

            cv2.imshow("frame", frame)

            key = cv2.waitKey(1)

            if key == ord('r'):
                idx = int(input("Select resolution index: "))
                set_resolution(URL, index=idx, verbose=True)

            elif key == ord('q'):
                val = int(input("Set quality (10 - 63): "))
                set_quality(URL, value=val)

            elif key == ord('a'):
                AWB = set_awb(URL, AWB)

            elif key == 27:
                break

    cv2.destroyAllWindows()
    cap.release()