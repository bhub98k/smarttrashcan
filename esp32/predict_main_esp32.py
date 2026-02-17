import cv2
from ultralytics import YOLO
import os
import time
import socket

print('Welcome',end='')
model = YOLO('new.pt')
print('.',end='')
def setcamera(cap):
    cap.set(6,cv2.VideoWriter.fourcc('M','J','P','G'))
video_path = 'http://192.168.50.196/cam.mjpeg'
cap = cv2.VideoCapture(video_path)
setcamera(cap)
print('.',end='')

HOST = '0.0.0.0'
PORT = 80
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)

        while True:
            data = conn.recv(1024)
            if data=='Alert':
                time.sleep(1)
                print('ON')
                success, frame = cap.read()
                success, frame = cap.read()
                success, frame = cap.read()
                results = model(frame)

                annotated_frame = results[0].plot()
                for result in results:
                    to_port=str(result.probs.top5[0]).strip()
                    conf=result.probs.top5conf
                #print(to_port,end='  ')
                #print(conf)
                print(to_port.encode())
                conn.send(to_port)
                print('done')
                
                cv2.imshow("YOLOv8 Inference", annotated_frame)
                cv2.waitKey(1000)
            
            print('None')
            if cv2.waitKey(1)  == 27:
                break
        cap.release()
        #cv2.destroyAllWindows()
        print('quit')




'''
alu_can         : 0
plastic_bottles : 1
tetra_pack      : 2

const int trigPin = 9;
const int echoPin = 10;

const int servoPin = 6;
const int servoPin1 = 11;
'''