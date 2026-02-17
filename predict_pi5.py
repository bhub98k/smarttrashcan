import RPi.GPIO as GPIO
import time
import cv2
import torch
from ultralytics import YOLO
model = YOLO('best.pt')
print("======================================")
cap = cv2.VideoCapture(0)
GPIO.setmode(GPIO.BCM)
TRIG = 23
ECHO = 24
alu_can_servo = 12
plastic_bottles_servo = 13
tetra_pack_servo = 18
none_servo = 19
GPIO.setup(alu_can_servo, GPIO.OUT)
GPIO.setup(plastic_bottles_servo, GPIO.OUT)
GPIO.setup(tetra_pack_servo, GPIO.OUT)
GPIO.setup(none_servo, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
alu_can_pwm = GPIO.PWM(alu_can_servo, 50)
plastic_bottles_pwm = GPIO.PWM(plastic_bottles_servo, 50)
tetra_pack_pwm = GPIO.PWM(tetra_pack_servo, 50)
none_pwm = GPIO.PWM(none_servo, 50)
alu_can_pwm.start(0)
plastic_bottles_pwm.start(0)
tetra_pack_pwm.start(0)
none_pwm.start(0)
def set_angle(servo_pin, pwm, angle):
    duty = 2 + (angle / 18)
    GPIO.output(servo_pin, True) 
    pwm.ChangeDutyCycle(duty) 
    time.sleep(1) 
    GPIO.output(servo_pin, False) 
    pwm.ChangeDutyCycle(0)
def measure_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.2)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2 
    return round(distance, 2)
def drop_alu_can():
    set_angle(alu_can_servo,alu_can_pwm,0)
def drop_plastic_bottles():
    set_angle(plastic_bottles_servo,plastic_bottles_pwm,10)
def drop_tetra_pack():
    set_angle(tetra_pack_servo,tetra_pack_pwm,20)
def drop_none():
    set_angle(none_servo,none_pwm,30)
if not cap.isOpened():
    print("Cam Error")
    exit()
while True:
    try:
        dist = measure_distance()
        ret, frame = cap.read()
        if ret:
            cv2.imshow(" ", frame)
            cv2.waitKey(1000)
            annotated_frame = results[0].plot()
            results = model.predict(source=frame, conf=0.5, show=False)
            for result in results:
                to_port=str(result.probs.top5[0])
                conf=result.probs.top5conf
            print(to_port,end='  ')
            print(conf)
            cv2.imshow("YOLOv8 Inference", annotated_frame)
            while to_port==0:
                drop_alu_can()
                continue
            while to_port==0:
                drop_plastic_bottles()
                continue
            while to_port==0:
                drop_tetra_pack()
                continue
            while to_port==0:
                drop_none()
                continue
        else:
            print("NO Sign")
    except:
        alu_can_pwm.stop
        plastic_bottles_pwm.stop
        tetra_pack_pwm.stop
        none_pwm.stop
        GPIO.cleanup()

