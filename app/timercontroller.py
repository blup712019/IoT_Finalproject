import threading

class TimerController:
    def __init__(self, timer_thread_cls, dect_stop: threading.Event, ring_manager):
        self._timer_thread_cls = timer_thread_cls
        self._ring_manager = ring_manager
        self._dect_stop = dect_stop
        self._lock = threading.Lock()
        self._thread = None
        self._stop_event = None

    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                return

            self._stop_event = threading.Event()
            self._thread = self._timer_thread_cls(self._stop_event, self._dect_stop, self._ring_manager)
            self._thread.start()
            print("[TIMER_CTRL] started")

    def kill(self):
        with self._lock:
            if not self._thread:
                return

            print("[TIMER_CTRL] stopping...")
            self._stop_event.set()
            self._thread.join(timeout=3)

            self._thread = None
            self._stop_event = None
            print("[TIMER_CTRL] stopped")

    def restart(self):
        # 把 restart 做成「原子操作」，避免同時被呼叫兩次
        with self._lock:
            print("[TIMER_CTRL] restarting...")
            if self._thread:
                self._stop_event.set()
                self._thread.join(timeout=3)

            self._stop_event = threading.Event()
            self._thread = self._timer_thread_cls(self._stop_event, self._dect_stop, self._ring_manager)
            self._thread.start()
            print("[TIMER_CTRL] restarted")
