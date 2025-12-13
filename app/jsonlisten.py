import threading
import os

class JSONCheckerThread(threading.Thread):
    def __init__(self, json_path: str, timer_controller, stop_event: threading.Event, interval=1.0):
        super().__init__(daemon=True)
        self.json_path = json_path
        self.timer_controller = timer_controller
        self.stop_event = stop_event
        self.interval = interval
        self._last_mtime = None

    def run(self):
        print("[JSONCHECKER] started")

        if os.path.exists(self.json_path):
            self._last_mtime = os.path.getmtime(self.json_path)

        while not self.stop_event.is_set():
            try:
                if os.path.exists(self.json_path):
                    mtime = os.path.getmtime(self.json_path)
                    if self._last_mtime is not None and mtime != self._last_mtime:
                        print("[JSONCHECKER] json changed -> restart timer")
                        self._last_mtime = mtime
                        self.timer_controller.restart()
            except Exception as e:
                print("[JSONCHECKER] error:", e)

            self.stop_event.wait(self.interval)

        print("[JSONCHECKER] stopped")
