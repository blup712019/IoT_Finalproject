import RPi.GPIO as GPIO
import time

vertical = 0
horizon = 0
tt = 0.1
class CarMotor:
    global vertical,horizon
    def __init__(self, t=tt):
        # 腳位（BOARD 模式）
        self.Motor_R1_Pin = 16
        self.Motor_R2_Pin = 18
        self.Motor_L1_Pin = 11
        self.Motor_L2_Pin = 13

        self.t = t  # 動作時間

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.Motor_R1_Pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.Motor_R2_Pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.Motor_L1_Pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.Motor_L2_Pin, GPIO.OUT, initial=GPIO.LOW)

        # PWM
        self.Motor_R1_PWM = GPIO.PWM(self.Motor_R1_Pin, 1000)
        self.Motor_R2_PWM = GPIO.PWM(self.Motor_R2_Pin, 1000)
        self.Motor_L1_PWM = GPIO.PWM(self.Motor_L1_Pin, 1000)
        self.Motor_L2_PWM = GPIO.PWM(self.Motor_L2_Pin, 1000)

        self.Motor_R1_PWM.start(0)
        self.Motor_R2_PWM.start(0)
        self.Motor_L1_PWM.start(0)
        self.Motor_L2_PWM.start(0)

    def stop(self):
        self.Motor_R1_PWM.ChangeDutyCycle(0)
        self.Motor_R2_PWM.ChangeDutyCycle(0)
        self.Motor_L1_PWM.ChangeDutyCycle(0)
        self.Motor_L2_PWM.ChangeDutyCycle(0)

    def forward(self, sleep=tt):

        self.Motor_R1_PWM.ChangeDutyCycle(80)
        self.Motor_R2_PWM.ChangeDutyCycle(0)
        self.Motor_L1_PWM.ChangeDutyCycle(80)
        self.Motor_L2_PWM.ChangeDutyCycle(0)
        time.sleep(self.t)
        self.stop()

    def backward(self, sleep=tt):
        self.Motor_R1_PWM.ChangeDutyCycle(0)
        self.Motor_R2_PWM.ChangeDutyCycle(80)
        self.Motor_L1_PWM.ChangeDutyCycle(0)
        self.Motor_L2_PWM.ChangeDutyCycle(80)
        time.sleep(self.t)
        self.stop()

    def turnRight(self, sleep=tt):
        self.Motor_R1_PWM.ChangeDutyCycle(95)
        self.Motor_R2_PWM.ChangeDutyCycle(0)
        self.Motor_L1_PWM.ChangeDutyCycle(65)
        self.Motor_L2_PWM.ChangeDutyCycle(0)
        time.sleep(self.t)
        self.stop()

    def turnLeft(self, sleep=tt):
        self.Motor_R1_PWM.ChangeDutyCycle(65)
        self.Motor_R2_PWM.ChangeDutyCycle(0)
        self.Motor_L1_PWM.ChangeDutyCycle(95)
        self.Motor_L2_PWM.ChangeDutyCycle(0)
        time.sleep(self.t)
        self.stop()

    def rotateRight(self, sleep=tt):
        self.Motor_R1_PWM.ChangeDutyCycle(75)
        self.Motor_R2_PWM.ChangeDutyCycle(0)
        self.Motor_L1_PWM.ChangeDutyCycle(0)
        self.Motor_L2_PWM.ChangeDutyCycle(75)
        time.sleep(self.t)
        self.stop()

    def rotateLeft(self, sleep=tt):
        self.Motor_R1_PWM.ChangeDutyCycle(0)
        self.Motor_R2_PWM.ChangeDutyCycle(75)
        self.Motor_L1_PWM.ChangeDutyCycle(75)
        self.Motor_L2_PWM.ChangeDutyCycle(0)
        time.sleep(self.t)
        self.stop()


    def cleanup(self):
        self.stop()
        GPIO.cleanup()
