import threading

class KeyListenerThread(threading.Thread):
    def __init__(self, stop_event: threading.Event):
        super().__init__(daemon=True)  # daemon 很重要
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            try:
                cmd = input().strip().lower()
                if cmd == 'q':
                    print("[KeyListener] q pressed, stopping...")
                    self.stop_event.set()
                    break
            except EOFError:
                # stdin 被關閉（例如 systemd / ssh 中斷）
                self.stop_event.set()
                break

