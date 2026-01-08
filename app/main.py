import threading
import queue
import time
import RPi.GPIO as GPIO
import app.buzzer as buzzer

# import testjs
import my_agent.agent as agent
# 
from app.ai_client import call_agent
from app.soundtext import speak
import time

from app.soundtext import SoundText
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
# 

from app.timercontroller import TimerController
from app.jsonlisten import JSONCheckerThread
from app.timerthread import TimerThread
from app.ringmanager import RingManager
from app.buttonthread import ButtonThread


from app.hailo.basic_pipelines.dect import user_app_callback_class, run_with_usb_interruptible

BUZZER_FREQ = 2000  # Hz
buzzer.BUZZER_FREQ = 2000
BUZZER_PIN = 36     # BOARD 編號
BUTTON_PIN = 15
buzzer.BUZZER_DUTY = 80
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUZZER_PIN, GPIO.OUT) #buzzer
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) #button
buzzer._buzzer_pwm = GPIO.PWM(BUZZER_PIN, BUZZER_FREQ)

# car pin
Motor_R1_Pin = 16
Motor_R2_Pin = 18
Motor_L1_Pin = 11
Motor_L2_Pin = 13


GPIO.setup(Motor_R1_Pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor_R2_Pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor_L1_Pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor_L2_Pin, GPIO.OUT, initial=GPIO.LOW)

# PWM
Motor_R1_PWM = GPIO.PWM(Motor_R1_Pin, 1000)
Motor_R2_PWM = GPIO.PWM(Motor_R2_Pin, 1000)
Motor_L1_PWM = GPIO.PWM(Motor_L1_Pin, 1000)
Motor_L2_PWM = GPIO.PWM(Motor_L2_Pin, 1000)

Motor_R1_PWM.start(0)
Motor_R2_PWM.start(0)
Motor_L1_PWM.start(0)
Motor_L2_PWM.start(0)

carPWM = [Motor_R1_PWM, Motor_R2_PWM, Motor_L1_PWM, Motor_L2_PWM]


def GPIOcleanup():
    try:
        buzzer.buzzer_pff()
    except:
        pass
    GPIO.cleanup()

def on_paragraph(text: str): # 之後要改成ubunto適用的
    """
    當使用者說完一整段話後，這個函式會被呼叫
    text 參數就是完整的語音文字（string）
    """
    print(f"\n!!!!!!使用者說的段落：{text}\n")
    answer = call_agent(text)
    print(answer)
    speak(answer)
    # speak("測試")
    
st = SoundText(
    vosk_model_path=str(r"/home/pi/IoT_Finalproject/vosk-model-small-en-us-0.15"),
    hotword="hello",
    google_lang="zh-TW",
    phrase_time_limit=None,  # 用靜音判斷段落結束（像 Google 輸入）
    input_device_index=0,  # 若抓錯麥克風，可指定
)
#threads
global_stop = threading.Event()

timer_thread = None
timer_stop_event = None

#dect control
dect_stop = threading.Event()
dect_start = threading.Event()

#buzzer controler
ring_manager = RingManager(buzzer.buzzer_on, buzzer.buzzer_off, global_stop)
ring_manager.start()

#button
button_thread = ButtonThread(BUTTON_PIN, ring_manager, dect_stop, global_stop)
button_thread.start()

#main thread control
main_stop = threading.Event()
dect_data = user_app_callback_class()

#car thread
from app.carthread import CarThread
from app.carrrrrrr import CarMotor
car_stop = threading.Event()

# TimerController
timer_ctrl = TimerController(TimerThread, dect_start, ring_manager)
timer_ctrl.start()

# JSONChecker
json_path = "timelist.json"
json_checker = JSONCheckerThread(json_path, timer_ctrl, global_stop, interval=1.0)
json_checker.start()



def main():
    st.start(on_paragraph)
    main_stop.clear()
    while not main_stop.is_set():
        try:
            print('[MAIN]---------------waiting for timer-------------')
            dect_start.wait()
            # wake up
            dect_start.clear()
            if main_stop.is_set() :
                break
            dect_stop.clear()
            car_stop.clear()
            carThread = CarThread(dect_data, CarMotor(0.5, carPWM), car_stop)
            print('[MAIN]---------------start detection---------------')  
            carThread.start()
            # run until dect_stop.is_set()
            run_with_usb_interruptible(user_data = dect_data, stop_event = dect_stop)
            print('[MAIN]---------------stop detection----------------')
            car_stop.set()
        except KeyboardInterrupt:
            print("[MAIN] END")
            main_stop.set()
        except SystemExit as e:
            print('[MAIN] thread exit(0)')
            car_stop.set()
            print('[MAIN]---------------stop detection----------------')
    GPIOcleanup()
    car_stop.set()
    global_stop.set()
    print("[MAIN] exit")

if __name__ == "__main__":
    main()
