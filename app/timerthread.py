import json
import threading
import time
from datetime import datetime
from app.ringmanager import RingManager

JSON_FILE = "timelist.json"
FMT = "%Y-%m-%d %H:%M:%S"
def load_times_as_seconds():
    now = time.time()
    future_times = []
    future_strs = []

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        obj = json.load(f)

    alarms = obj.get("alarms", [])

    for tstr in alarms:
        try:
            dt = datetime.strptime(tstr, FMT)
            ts = dt.timestamp()
            if ts > now:
                future_times.append(ts)
                future_strs.append(tstr)
        except ValueError:
            # 格式錯誤的也直接丟掉
            pass

    # 若有過期或錯誤資料，寫回乾淨版本
    if len(future_strs) != len(alarms):
        obj["alarms"] = future_strs
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)
        print("[TIMER] expired alarms cleaned")

    future_times.sort()
    return future_times

def remove_time_from_json(ts):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        obj = json.load(f)

    alarms = obj.get("alarms", [])
    target = datetime.fromtimestamp(ts).strftime(FMT)

    obj["alarms"] = [t for t in alarms if t != target]

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

class TimerThread(threading.Thread):
    def __init__(self, stop_event: threading.Event, ring_manager=None):
        super().__init__()
        self.stop_event = stop_event
        self.ring_manager = ring_manager

    def run(self):
        print("[TIMER] init")
        times = load_times_as_seconds()

        while not self.stop_event.is_set():
            if not times:
                print("[TIMER] no more alarms, exit")
                break

            next_ts = times[0]
            wait_sec = max(0, next_ts - time.time())

            print(f"[TIMER] sleep {wait_sec:.1f}s")
            interrupted = self.stop_event.wait(wait_sec)
            if interrupted:
                print("[TIMER] interrupted, exit")
                break

            # 到時間了
            print("call ring manager")
            self.ring_manager.ring(600)
            
            # 移除第一個
            times.pop(0)
            remove_time_from_json(next_ts)

        print("[TIMER] end")
        


