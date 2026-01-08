import json
import threading
import time
from datetime import datetime
from app.ringmanager import RingManager

JSON_FILE = "timelist.json"
FMT = "%Y-%m-%d %H:%M:%S"
def load_times_as_seconds():
    now = time.time()
    future_events = [] # 之後要回傳的: [[ts, status], ...]
    future_strs = []      # 給 JSON 清除用，仍然只存「原本時間字串」

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        obj = json.load(f)

    alarms = obj.get("alarms", [])

    for tstr in alarms:
        try:
            dt = datetime.strptime(tstr, FMT)
            ts = dt.timestamp()

            # 只保留「原本時間 > 現在時間 + 2 秒」的鬧鐘
            if ts > now + 2:
                # 記錄這個鬧鐘字串（用來寫回 JSON）
                future_strs.append(tstr)

                # 1) 主事件：原本時間，狀態 0
                future_events.append([ts, 0])

                # 2) 前置事件：原本時間 - 60 秒，狀態 1
                pre_ts = ts - 60

                # 如果前置時間已經 < 現在時間，則調整成 現在時間 + 2
                if pre_ts < now:
                    pre_ts = now + 2

                future_events.append([pre_ts, 1])

        except ValueError:
            # 格式錯誤的也直接丟掉
            pass

    # 若有過期或錯誤資料，寫回乾淨版本
    if len(future_strs) != len(alarms):
        obj["alarms"] = future_strs
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
        print("[TIMER] expired alarms cleaned")
    future_events.sort(key=lambda x: x[0])
    return future_events   # [[ts, status], ...]

def remove_time_from_json(ts):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        obj = json.load(f)

    alarms = obj.get("alarms", [])
    target = datetime.fromtimestamp(ts).strftime(FMT)

    obj["alarms"] = [t for t in alarms if t != target]

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


class TimerThread(threading.Thread):
    def __init__(self, stop_event: threading.Event
    , dect_start: threading.Event
    , ring_manager=None):
        super().__init__()
        self.stop_event = stop_event
        self.ring_manager = ring_manager
        self.dect_start = dect_start

    def pre_action(self, ts):
        # 車車 thread
        # TODO: 這裡寫你在「鬧鐘前 60 秒」要做的事情
        # ts 是「原本時間 - 60」或你調整成 now+2 的那個時間點
        print(f"[TIMER] pre_action at {datetime.fromtimestamp(ts)}")\
        
    def run(self):
        print("[TIMER] init")
        times = load_times_as_seconds()   # [[ts, status], ...]

        while not self.stop_event.is_set():
            if not times:
                print("[TIMER] no more alarms, exit")
                break

            next_ts, status = times[0]    # 拆成時間 + 狀態
            wait_sec = max(0, next_ts - time.time())

            print(f"[TIMER] sleep {wait_sec:.1f}s (status={status})")
            interrupted = self.stop_event.wait(wait_sec)
            if interrupted:
                print("[TIMER] interrupted, exit")
                break

            # 到時間了，依狀態決定要做什麼
            if status == 0:
                # 原本要做的事
                print("[TIMER] status 0: call ring manager and start detection")
                
                self.ring_manager.ring(600)

                # 只有主事件才從 JSON 移除鬧鐘
                remove_time_from_json(next_ts)

            elif status == 1:
                # 之後要寫的「前 60 秒」的處理
                print("[TIMER] status 1: do pre-action")
                self.dect_start.set()

            else:
                print(f"[TIMER] unknown status={status}, skip")

            # 移除目前這個事件（不管是 pre 還是 main）
            times.pop(0)

        print("[TIMER] end")
        


