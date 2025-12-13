import threading
import time
import app.buzzer as buzzer

# import testjs
import my_agent.agent as agent

from app.timerthread import TimerThread
from app.ringmanager import RingManager
from app.buttonthread import ButtonThread

BUTTON_PIN = 15
#threads
global_stop = threading.Event()

timer_thread = None
timer_stop_event = None

ring_manager = RingManager(buzzer.buzzer_on, buzzer.buzzer_off, global_stop)
ring_manager.start()

button_thread = ButtonThread(BUTTON_PIN, ring_manager, global_stop)
button_thread.start()



def start_timer():
    global timer_thread, timer_stop_event

    print("timer start")
    # 避免重複啟動
    if timer_thread and timer_thread.is_alive():
        print("[MAIN] timer already running")
        return
    timer_stop_event = threading.Event()
    timer_thread = TimerThread(timer_stop_event, ring_manager)
    timer_thread.start()
    print("[MAIN] timer started")


def kill_timer():
    global timer_thread, timer_stop_event

    if not timer_thread:
        return
    print("[MAIN] stopping timer...")
    timer_stop_event.set()      # 通知 thread 結束
    timer_thread.join()         # 等它收尾
    timer_thread = None
    timer_stop_event = None
    print("[MAIN] timer stopped")

def restart_timer():
    print("resttttttart")
    kill_timer()
    start_timer()

def main():
    start_timer()

    try:
        while True:
            # cmd = input("cmd (r=reload, q=quit): ").strip()
            # if cmd == "r":
            #     print("[MAIN] reload alarms")
            #     restart_timer()
            # elif cmd == "q":
            #     break

            if  agent.json_change:
                print("[MAIN] reload alarms")
                restart_timer()
                agent.json_change = False

            # time.sleep(3)
            # agent.add_alarm_time("2025-12-13 16:20:00")
            
            

    except KeyboardInterrupt:
        print("END")

    finally:
        kill_timer()
        buzzer.cleanup()
        print("[MAIN] exit")

if __name__ == "__main__":
    main()
