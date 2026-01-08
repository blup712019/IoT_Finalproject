import RPi.GPIO as GPIO
import time

vertical = 0
horizon = 0
tt = 0.1

class CarMotor:
    global vertical,horizon
    def __init__(self, t=tt, carPWM=None):
        self.carPWM = carPWM
        self.t = t  # 動作時間
        self.Motor_R1_PWM = carPWM[0]
        self.Motor_R2_PWM = carPWM[1]
        self.Motor_L1_PWM = carPWM[2]
        self.Motor_L2_PWM = carPWM[3]
       
    def stop(self):
        print("CarMotor.stop")
        self.Motor_R1_PWM.ChangeDutyCycle(0)
        self.Motor_R2_PWM.ChangeDutyCycle(0)
        self.Motor_L1_PWM.ChangeDutyCycle(0)
        self.Motor_L2_PWM.ChangeDutyCycle(0)

    def forward(self, sleep=tt):

        print("CarMotor.forward")
        self.Motor_R1_PWM.ChangeDutyCycle(80)
        self.Motor_R2_PWM.ChangeDutyCycle(0)
        self.Motor_L1_PWM.ChangeDutyCycle(80)
        self.Motor_L2_PWM.ChangeDutyCycle(0)
        time.sleep(self.t)
        self.stop()

    def backward(self, sleep=tt):
        print("CarMotor.backward")
        self.Motor_R1_PWM.ChangeDutyCycle(0)
        self.Motor_R2_PWM.ChangeDutyCycle(80)
        self.Motor_L1_PWM.ChangeDutyCycle(0)
        self.Motor_L2_PWM.ChangeDutyCycle(80)
        time.sleep(self.t)
        self.stop()

    def turnRight(self, sleep=tt):
        print("CarMotor.right")
        self.Motor_R1_PWM.ChangeDutyCycle(95)
        self.Motor_R2_PWM.ChangeDutyCycle(0)
        self.Motor_L1_PWM.ChangeDutyCycle(65)
        self.Motor_L2_PWM.ChangeDutyCycle(0)
        time.sleep(self.t)
        self.stop()

    def turnLeft(self, sleep=tt):
        print("CarMotor.left")
        self.Motor_R1_PWM.ChangeDutyCycle(65)
        self.Motor_R2_PWM.ChangeDutyCycle(0)
        self.Motor_L1_PWM.ChangeDutyCycle(95)
        self.Motor_L2_PWM.ChangeDutyCycle(0)
        time.sleep(self.t)
        self.stop()

    def rotateRight(self, sleep=tt):
        print("CarMotor.rotateRight")
        self.Motor_R1_PWM.ChangeDutyCycle(75)
        self.Motor_R2_PWM.ChangeDutyCycle(0)
        self.Motor_L1_PWM.ChangeDutyCycle(0)
        self.Motor_L2_PWM.ChangeDutyCycle(75)
        time.sleep(self.t)
        self.stop()

    def rotateLeft(self, sleep=tt):
        print("CarMotor.rotateLeft")
        self.Motor_R1_PWM.ChangeDutyCycle(0)
        self.Motor_R2_PWM.ChangeDutyCycle(75)
        self.Motor_L1_PWM.ChangeDutyCycle(75)
        self.Motor_L2_PWM.ChangeDutyCycle(0)
        time.sleep(self.t)
        self.stop()


    def cleanup(self):
        self.stop()
        GPIO.cleanup()
