# my_agent/agent.py
import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo  # Python 3.9+

from google.adk.agents import Agent   # 有的範例是 from google.adk.agents.llm_agent import Agent
BASE_DIR = Path(__file__).resolve().parent.parent   # 專案根目錄
TIME_FILE = BASE_DIR / "timelist.json"     

def add_alarm_time(alarm_time: str) -> dict:
    """
    新增一筆鬧鐘時間到 timelist.json。

    參數:
        alarm_time (str): 鬧鐘時間字串，例如 "07:30" 或 "2025-12-10 07:30:00"。

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

root_agent = Agent(
    name="time_agent",
    model="gemini-2.5-flash",  # 或你用的其他 Gemini 模型
    description="負責告訴使用者現在時間的 agent。",
    instruction=(
        "你是一個時間小幫手。\n"
        "當使用者說「現在幾點」時，一定要呼叫 get_current_time。\n"
        "當使用者說要新增鬧鐘時，請呼叫 add_alarm_time。\n"
        "\n"
        "如果使用者給的是相對時間，例如：\n"
        "「一個小時後」、「30 分鐘後」、「兩個小時後」\n"
        "你必須先用『現在的台北時間（Asia/Taipei）』計算出實際的時間，\n"
        "再把『計算完成的時間字串』傳給 add_alarm_time。\n"
        "\n"
        "例如：\n"
        "現在是 10:00，使用者說「一個小時後」，\n"
        "你要傳入 alarm_time=\"11:00\"。\n"
        "\n"
        "回答請使用繁體中文。"
    ),
    tools=[get_current_time,add_alarm_time,    
           
           
           ],  # ⬅ 把新 function 加進來
)
