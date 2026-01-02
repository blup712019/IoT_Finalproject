import threading
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


BUZZER_FREQ = 2000  # Hz
buzzer.BUZZER_FREQ = 2000
BUZZER_PIN = 36     # BOARD 編號
BUTTON_PIN = 15
buzzer.BUZZER_DUTY = 80
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUZZER_PIN, GPIO.OUT) #buzzer
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) #button
buzzer._buzzer_pwm = GPIO.PWM(BUZZER_PIN, BUZZER_FREQ)
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
    # 啟動背景監聽（非阻塞）



#threads
global_stop = threading.Event()

timer_thread = None
timer_stop_event = None

ring_manager = RingManager(buzzer.buzzer_on, buzzer.buzzer_off, global_stop)
ring_manager.start()

button_thread = ButtonThread(BUTTON_PIN, ring_manager, global_stop)
button_thread.start()

# TimerController
timer_ctrl = TimerController(TimerThread, ring_manager)
timer_ctrl.start()

# JSONChecker
json_path = "timelist.json"
json_checker = JSONCheckerThread(json_path, timer_ctrl, global_stop, interval=1.0)
json_checker.start()

def main():
    st.start(on_paragraph)
    try:
        while True:
            cmd = input("q=quit, r=restart: ").strip()

            # if cmd == "m":
            # agent.add_alarm_time("2025-12-13 20:30:00")

            if cmd == "r":
                timer_ctrl.restart()
            elif cmd == "q":
                break
            
            # if  agent.json_change:
            #     print("[MAIN] reload alarms")
            #     restart_timer()
            #     agent.json_change = False

    except KeyboardInterrupt:
        print("END")

    finally:
        GPIOcleanup()
        print("[MAIN] exit")

if __name__ == "__main__":
    main()
