# buttonthread.py
import threading
import time
import RPi.GPIO as GPIO

class ButtonThread(threading.Thread):
    def __init__(self, button_pin: int, ring_manager, dect_stop: threading.Event ,stop_event: threading.Event, debounce_sec: float = 0.3):
        super().__init__(daemon=True)
        self.button_pin = button_pin
        self.ring_manager = ring_manager
        self.stop_event = stop_event
        self.debounce_sec = debounce_sec
        self.dect_stop = dect_stop

    def run(self):
        print("[BUTTON] listener started")
        last_state = GPIO.input(self.button_pin)

        while not self.stop_event.is_set():
            state = GPIO.input(self.button_pin)

            # HIGH -> LOW：按下
            if last_state == GPIO.HIGH and state == GPIO.LOW:
                print("[BUTTON] pressed -> cancel")
                try:
                    self.ring_manager.cancel()
                    self.dect_stop.set()
                except Exception as e:
                    print("[BUTTON] cancel failed:", e)

                time.sleep(self.debounce_sec)  # 簡單防彈跳

            last_state = state
            time.sleep(0.02)

        print("[BUTTON] listener stopped")

