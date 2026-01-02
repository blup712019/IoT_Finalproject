import RPi.GPIO as GPIO
import time

SERVO_PIN = 12     # <-- 實體腳位 12

GPIO.setmode(GPIO.BOARD)   # 使用 BOARD 編號
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz
pwm.start(0)

def set_angle(angle):
    duty = 2 + angle / 18
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

try:
    set_angle(90)
    time.sleep(2)
finally:
    pwm.stop()
    GPIO.cleanup()