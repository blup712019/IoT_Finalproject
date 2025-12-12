import threading, time
from queue import Queue, Empty

class RingManager(threading.Thread):
    def __init__(self, buzzer_on, buzzer_off, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.q = Queue()
        self.stop_event = stop_event
        self.buzzer_on = buzzer_on
        self.buzzer_off = buzzer_off
        self.ring_cancel = threading.Event()

    def ring(self, seconds=10):
        self.q.put(("ring", seconds))

    def cancel(self):
        # 立刻停止目前響鈴
        self.ring_cancel.set()

    def run(self):
        while not self.stop_event.is_set():
            try:
                cmd, seconds = self.q.get(timeout=0.2)
            except Empty:
                continue

            if cmd == "ring":
                self.ring_cancel.clear()
                self.buzzer_on()

                end = time.time() + seconds
                while time.time() < end and not self.stop_event.is_set() and not self.ring_cancel.is_set():
                    time.sleep(0.05)

                self.buzzer_off()

