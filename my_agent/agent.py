# my_agent/agent.py
import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent   # 有的範例是 from google.adk.agents.llm_agent import Agent

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
    tools=[get_current_time],
)
