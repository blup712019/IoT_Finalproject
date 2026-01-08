# my_agent/agent.py
import re
import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo  # Python 3.9+

from google.adk.agents import Agent   # 有的範例是 from google.adk.agents.llm_agent import Agent


json_change = False

BASE_DIR = Path(__file__).resolve().parent.parent   # 專案根目錄
TIME_FILE = BASE_DIR / "timelist.json"     

def add_alarm_time(alarm_time: str) -> dict:
    """
    新增一筆鬧鐘時間到 timelist.json。

    參數:
        alarm_time (str): 鬧鐘時間字串，例如 "2025-12-10 07:30:00"。

    timelist.json 格式範例:
    {
      "alarms": [
    "2025-12-12 14:23:45"
        ]
    }
    """
    # 如果檔案不存在，先建立預設結構
    if not TIME_FILE.exists():
        data = {"alarms": []}
    else:
        try:
            with TIME_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = {"alarms": []}
        except Exception as e:
            return {
                "status": "error",
                "message": f"讀取 timelist.json 失敗: {e}",
            }

    alarms = data.setdefault("alarms", [])
    alarms.append(alarm_time)

    try:
        with TIME_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return {
            "status": "error",
            "message": f"寫入 timelist.json 失敗: {e}",
        }

    print(f"[tool] add_alarm_time 被呼叫，新增鬧鐘：{alarm_time}")

    global json_change
    json_change = True
    
    return {
        "status": "success",
        "message": f"已新增鬧鐘時間 {alarm_time}",
        "alarm_time": alarm_time,
        "alarms_count": len(alarms),
    }

def get_current_time() -> dict:
    now = datetime.datetime.now(ZoneInfo("Asia/Taipei"))
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # 這行很重要：用來看「工具有沒有真的被叫到」
    print(f"[tool] get_current_time 被呼叫，現在時間 = {time_str}")

    return {
        "status": "success",
        "current_time": time_str,
    }

def _parse_dt(dt_str: str) -> datetime.datetime:
    """
    解析 "YYYY-MM-DD HH:MM:SS" 成 Asia/Taipei 時區的 aware datetime
    """
    dt_str = (dt_str or "").strip()
    dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    return dt.replace(tzinfo=ZoneInfo("Asia/Taipei"))


def delete_alarms_in_datetime_range(start_dt: str, end_dt: str) -> dict:
    """
    刪除 timelist.json 中落在 [start_dt, end_dt] 區間內的鬧鐘（含邊界）。

    參數:
        start_dt (str): 起始時間，格式 "YYYY-MM-DD HH:MM:SS"
        end_dt   (str): 結束時間，格式 "YYYY-MM-DD HH:MM:SS"

    timelist.json 格式:
    {
      "alarms": ["2025-12-12 19:10:16", ...]
    }

    回傳:
    {
      "status": "success"/"error",
      "deleted": [...],
      "remaining_count": int,
      "message": str
    }
    """
    # 解析輸入時間
    try:
        start = _parse_dt(start_dt)
        end = _parse_dt(end_dt)
    except Exception as ex:
        return {"status": "error", "message": f"時間格式錯誤，請用 YYYY-MM-DD HH:MM:SS。({ex})"}

    if end < start:
        return {"status": "error", "message": "end_dt 不能早於 start_dt。"}

    # 讀檔
    if not TIME_FILE.exists():
        data = {"alarms": []}
    else:
        try:
            with TIME_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = {"alarms": []}
        except Exception as ex:
            return {"status": "error", "message": f"讀取 timelist.json 失敗: {ex}"}

    alarms = data.setdefault("alarms", [])
    if not isinstance(alarms, list):
        alarms = []
        data["alarms"] = alarms

    deleted = []
    kept = []

    for a in alarms:
        try:
            a_dt = _parse_dt(str(a))
        except Exception:
            # 格式不合法的先保留，避免誤刪
            kept.append(a)
            continue

        if start <= a_dt <= end:
            deleted.append(a)
        else:
            kept.append(a)

    data["alarms"] = kept

    # 寫回
    try:
        with TIME_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as ex:
        return {"status": "error", "message": f"寫入 timelist.json 失敗: {ex}"}

    print(f"[tool] delete_alarms_in_datetime_range: {start_dt}~{end_dt}，刪除 {len(deleted)} 筆")

    return {
        "status": "success",
        "deleted": deleted,
        "remaining_count": len(kept),
        "message": f"已刪除 {len(deleted)} 筆鬧鐘（{start_dt} ~ {end_dt}）",
    }

root_agent = Agent(
    name="time_agent",
    model="gemini-2.5-flash",  # 或你用的其他 Gemini 模型
    description="負責告訴使用者現在時間的 agent。",
    instruction=(
        "你是一個時間小幫手。\n"
        "當使用者說「現在幾點」時，一定要呼叫 get_current_time。\n"
        "當使用者說要新增鬧鐘時，請呼叫 add_alarm_time，但如果使用者給的是相對時間，例如：\n"
        "「一個小時後」、「30 分鐘後」、「兩個小時後」\n"
        "你必須先用『現在的台北時間（Asia/Taipei）』計算出實際的時間，\n"
        "再把『計算完成的時間字串』傳給 add_alarm_time。\n"
        "例如：\n"
        "現在是 10:00，使用者說「一個小時後」，\n"
        "你要傳入 alarm_time=\"11:00\"。\n"
        "當使用者說要刪除某時間區段的鬧鐘，請呼叫 delete_alarms_in_datetime_range\n"
        "當使用者說要刪除某時間區段的鬧鐘，例如「刪除 2025-12-12 18:00:00 到 2025-12-12 20:00:00」，"
        "請呼叫 delete_alarms_in_datetime_range(start_dt, end_dt)。"
        "start_dt/end_dt 一律使用 YYYY-MM-DD HH:MM:SS 格式（台北時間 Asia/Taipei）。"
        "如果使用者給的是相對時間，例如：\n"
        "「一個小時後」、「30 分鐘後」、「兩個小時後」\n"
        "你必須先用『現在的台北時間（Asia/Taipei）』計算出實際的時間，\n"
        "再把『計算完成的時間字串』傳給delete_alarms_in_datetime_range"
        "回答請使用繁體中文。"
    ),
    tools=[get_current_time,add_alarm_time,    
           delete_alarms_in_datetime_range,

           ],  # ⬅ 把新 function 加進來
)
