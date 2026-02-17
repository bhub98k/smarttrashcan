import RPi.GPIO as GPIO
import time
import cv2
import torch
from ultralytics import YOLO
model = YOLO('best_edge.pt')
print("==================")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("CameError")
    exit()
GPIO.setmode(GPIO.BCM)
TRIG, ECHO = 23, 24
startfix = 3
alu_can_servo, plastic_bottles_servo, tetra_pack_servo, none_servo ,gate= 17, 13, 18, 19, 21
GPIO.setup(alu_can_servo, GPIO.OUT)
GPIO.setup(plastic_bottles_servo, GPIO.OUT)
GPIO.setup(tetra_pack_servo, GPIO.OUT)
GPIO.setup(none_servo, GPIO.OUT)
GPIO.setup(gate, GPIO.OUT)
GPIO.setup(startfix, GPIO.IN)
servo_pins = [alu_can_servo, plastic_bottles_servo, tetra_pack_servo, none_servo, gate]
GPIO.setup([TRIG] + servo_pins, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
pwm_map = {pin: GPIO.PWM(pin, 50) for pin in servo_pins}
for pwm in pwm_map.values():
    pwm.start(0)
def set_angle(servo_pin, pwm, angle):
    duty = 2 + (angle / 18)
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)
def drop_alu_can(): 
    set_angle(alu_can_servo, pwm_map[alu_can_servo], 180)
    time.sleep(0.5)
    set_angle(gate, pwm_map[gate], 50)
    time.sleep(1)
    set_angle(gate, pwm_map[gate], 100)
    time.sleep(0.3)
    set_angle(alu_can_servo, pwm_map[alu_can_servo], 0)
def drop_plastic_bottles(): 
    set_angle(plastic_bottles_servo, pwm_map[plastic_bottles_servo], 180)
    time.sleep(0.5)
    set_angle(gate, pwm_map[gate], 50)
    time.sleep(1)
    set_angle(gate, pwm_map[gate], 100)
    time.sleep(0.3)
    set_angle(plastic_bottles_servo, pwm_map[plastic_bottles_servo], 0)
def drop_tetra_pack(): 
    set_angle(tetra_pack_servo, pwm_map[tetra_pack_servo], 0)
    time.sleep(0.5)
    set_angle(gate, pwm_map[gate], 50)
    time.sleep(1)
    set_angle(gate, pwm_map[gate], 100)
    time.sleep(0.3)
    set_angle(tetra_pack_servo, pwm_map[tetra_pack_servo], 180)
    time.sleep(0.5)
def drop_none():
     set_angle(none_servo, pwm_map[none_servo], 180)
     time.sleep(0.5)
     set_angle(gate, pwm_map[gate], 50)
     time.sleep(1)
     set_angle(gate, pwm_map[gate], 100)
     time.sleep(0.3)
     set_angle(none_servo, pwm_map[none_servo], 0)
def edgemode():
    print("=========edgemode=========")
    time.sleep(0.5)
    ret, frame2 = cap.read()
    ret, frame2 = cap.read()
    if not ret or frame is None:
        print("CamError")
        return
    edge_frame = cv2.Canny(cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY), 36, 36)
    edge_frame_colored = cv2.merge([edge_frame] * 3)
    results = model(edge_frame_colored)
    if not results or len(results[0]) == 0:
        print("No objects")
        return
    top_class = None
    if results[0].probs:
        top_class = str(results[0].probs.top5[0])
    else:
        print("object is ont in model.")
        return
    annotated_frame = results[0].plot()
    if annotated_frame is None:
        print("Error: Annotated")
        return
    cv2.imshow("YOLOv8 Inference", annotated_frame)
    cv2.waitKey(1000) 
    cv2.destroyAllWindows()
    if top_class == "0":
        drop_alu_can()
    elif top_class == "2":
        drop_plastic_bottles()
    elif top_class == "3":
        drop_tetra_pack()
    elif top_class == "1":
        drop_none()
def fixmode():
    set_angle(plastic_bottles_servo, pwm_map[plastic_bottles_servo], 0)  #c_close
    set_angle(tetra_pack_servo, pwm_map[tetra_pack_servo], 180) #D_close
    set_angle(none_servo, pwm_map[none_servo], 0) #A_close
    set_angle(alu_can_servo,pwm_map[alu_can_servo], 180) #B_close
    set_angle(gate, pwm_map[gate], 100) #gate_close
    print("done")
try:
    ret, frame = cap.read()
    if not ret:
        print("CamError")
        exit()
    prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    processing = False
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_diff = cv2.absdiff(prev_gray, gray)
        _, thresh = cv2.threshold(frame_diff, 90, 255, cv2.THRESH_BINARY)
        non_zero_count = cv2.countNonZero(thresh)
        if not processing and non_zero_count > 10000:
            processing = True
            edgemode()
            print("******************")
        if processing and non_zero_count < 3000:
            processing = False
            print("Working")
        if GPIO.input(3) ==GPIO.HIGH:
            fixmode()
        prev_gray = gray

except KeyboardInterrupt:
    print("Stopping")
finally:
    for pwm in pwm_map.values():
        pwm.stop()
    GPIO.cleanup()
    cap.release()
    cv2.destroyAllWindows()
    #set_angle(plastic_bottles_servo, plastic_bottles_pwm, 0)  #c_close
    #set_angle(plastic_bottles_servo, plastic_bottles_pwm, 180)  #c_open
    #set_angle(tetra_pack_servo, tetra_pack_pwm, 0) #D_open
    #set_angle(tetra_pack_servo, tetra_pack_pwm, 180) #D_close
    #set_angle(none_servo, none_pwm, 180) #A_open
    #set_angle(none_servo, none_pwm, 0) #A_close
    #set_angle(alu_can_servo, alu_can_pwm, 180) #B_close
    #set_angle(alu_can_servo, alu_can_pwm, 0) #B_open
    #set_angle(gate, gate_pwm, 100) #gate_close
    #set_angle(gate, gate_pwm, 50) #gate_open

