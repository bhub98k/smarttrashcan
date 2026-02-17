import RPi.GPIO as GPIO
import time
import cv2
import torch
from ultralytics import YOLO
model = YOLO('best.pt')
print("======================================")
cap = cv2.VideoCapture(0)
GPIO.setmode(GPIO.BCM)
a1_pin = 14
a2_pin = 15
b1_pin = 17
b2_pin = 18
TRIG = 23
ECHO = 24
servo = 12
calibration = 26
GPIO.setup(a1_pin, GPIO.OUT)
GPIO.setup(a2_pin, GPIO.OUT)
GPIO.setup(b1_pin, GPIO.OUT)
GPIO.setup(b2_pin, GPIO.OUT)
GPIO.setup(servo, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(calibration, GPIO.IN)
pwm = GPIO.PWM(servo, 50)
pwm.start(0)
seq = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]
steps_per_rev = 512 
degrees_per_step = 360 / steps_per_rev
steps_90_degrees = int(90 / degrees_per_step)
def set_step(step):
    GPIO.output(a1_pin, step[0] == '1')
    GPIO.output(a2_pin, step[1] == '1')
    GPIO.output(b1_pin, step[2] == '1')
    GPIO.output(b2_pin, step[3] == '1')
def step_motor(steps, delay=0.002):
    for _ in range(steps):
        for step in seq:
            GPIO.output(a1_pin, step[0])
            GPIO.output(a2_pin, step[1])
            GPIO.output(b1_pin, step[2])
            GPIO.output(b2_pin, step[3])
            time.sleep(delay)
def cstep_motor(delay=0.002):
    for step in seq:
        GPIO.output(a1_pin, step[0])
        GPIO.output(a2_pin, step[1])
        GPIO.output(b1_pin, step[2])
        GPIO.output(b2_pin, step[3])
        time.sleep(delay)
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
    step_motor(steps_90_degrees)
    time.sleep(1)
    set_angle(servo,pwm,0)
    time.sleep(1)
    set_angle(servo,pwm,90)
    time.sleep(1)
    step_motor(steps_90_degrees)
    step_motor(steps_90_degrees)
    step_motor(steps_90_degrees)
def drop_plastic_bottles():
    step_motor(steps_90_degrees)
    step_motor(steps_90_degrees)
    time.sleep(1)
    set_angle(servo,pwm,0)
    time.sleep(1)
    set_angle(servo,pwm,90)
    time.sleep(1)
    step_motor(steps_90_degrees)
    step_motor(steps_90_degrees)
def drop_tetra_pack():
    step_motor(steps_90_degrees)
    step_motor(steps_90_degrees)
    step_motor(steps_90_degrees)
    time.sleep(1)
    set_angle(servo,pwm,0)
    time.sleep(1)
    set_angle(servo,pwm,90)
    time.sleep(1)
    step_motor(steps_90_degrees)
def drop_none():
    set_angle(servo,pwm,0)
    time.sleep(1)
    set_angle(servo,pwm,90)
if not cap.isOpened():
    print("Cam Error")
    exit()
while True:
    calibration_state = GPIO.input(calibration)
    if calibration_state == GPIO.LOW:
        cstep_motor()
    else:
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
            pwm.stop
            GPIO.cleanup()
    

