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

# TimerController
timer_ctrl = TimerController(TimerThread, ring_manager)
timer_ctrl.start()

# JSONChecker
json_path = "timelist.json"
json_checker = JSONCheckerThread(json_path, timer_ctrl, global_stop, interval=1.0)
json_checker.start()

def main():

    try:
        while True:
            cmd = input("q=quit, r=restart: ").strip()
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
        buzzer.cleanup()
        print("[MAIN] exit")

if __name__ == "__main__":
    main()