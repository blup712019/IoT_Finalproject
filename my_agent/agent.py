# my_agent/agent.py
import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo  # Python 3.9+

from google.adk.agents import Agent   # 有的範例是 from google.adk.agents.llm_agent import Agent
BASE_DIR = Path(__file__).resolve().parent.parent   # 專案根目錄
TIME_FILE = BASE_DIR / "timelist.json"     

def add_current_time_record() -> dict:
    """
    將現在時間新增一筆到 timelist.json。
    
    timelist.json 格式：
    {
        "records": [
            "YYYY-MM-DD HH:MM:SS",
            ...
        ]
    }

    回傳：
    {
        "status": "success" / "error",
        "message": "說明文字",
        "added_time": "YYYY-MM-DD HH:MM:SS"  # 若成功會有
    }
    """
    now = datetime.datetime.now(ZoneInfo("Asia/Taipei"))
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # 如果檔案不存在，先建立預設結構
    if not TIME_FILE.exists():
        data = {"records": []}
    else:
        try:
            with TIME_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            # 防呆：如果結構不是我們要的，就重建
            if not isinstance(data, dict) or "records" not in data:
                data = {"records": []}
        except Exception as e:
            # 讀檔或解析 JSON 失敗
            return {
                "status": "error",
                "message": f"讀取 timelist.json 失敗: {e}"
            }

    # 加入一筆新的時間
    data.setdefault("records", [])
    data["records"].append(time_str)

    # 寫回檔案
    try:
        with TIME_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return {
            "status": "error",
            "message": f"寫入 timelist.json 失敗: {e}"
        }

    print(f"[tool] add_current_time_record 被呼叫，寫入 {time_str}")

    return {
        "status": "success",
        "message": "已新增一筆現在時間到 timelist.json",
        "added_time": time_str,
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
        "你是一個時間小幫手。"
        "當使用者問『現在幾點』、『現在時間』之類的問題時，"
        "一定要呼叫 get_current_time 這個工具，不要自己編時間。"
        "回答時請用自然語言，並把工具回傳的 current_time 顯示出來。"
    ),
    tools=[get_current_time, add_current_time_record],  # ⬅ 把新 function 加進來
)
