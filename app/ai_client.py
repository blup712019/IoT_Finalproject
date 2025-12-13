# ai_client.py
from dotenv import load_dotenv
from pathlib import Path
import asyncio
import re
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.adk.models.google_llm import _ResourceExhaustedError
import time
from my_agent.agent import root_agent
from dotenv import load_dotenv
_session = None
# 讀取 my_agent/.env
PROJECT_ROOT = Path(__file__).resolve().parents[1]   # .../你的專案根目錄
env_path = PROJECT_ROOT / "my_agent" / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# 建立 InMemoryRunner（整個程式共用一個）
runner = InMemoryRunner(
    agent=root_agent,
    app_name="iot_final_app",
)


async def _ask_my_agent(session_id: str, user_text: str) -> str:
    """內部 async 函式，用來真的跟 agent 對話一次。"""
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_text)],
    )

    last_text = ""

    for event in runner.run(
        user_id="user-001",
        session_id=session_id,
        new_message=content,
    ):
        if getattr(event, "content", None) and event.content.parts:
            part = event.content.parts[0]
            if getattr(part, "text", None):
                last_text = part.text

    return last_text


def create_session():
    """建立一個 session 物件，回傳整個 session（裡面有 id）。"""
    session = asyncio.run(
        runner.session_service.create_session(
            app_name="iot_final_app",
            user_id="user-001",
        )
    )
    return session


def call_my_agent(session_id: str, user_text: str) -> str:
    for _ in range(3):  # 最多重試 3 次
        try:
            return asyncio.run(_ask_my_agent(session_id, user_text))
        except _ResourceExhaustedError as e:
            # 從錯誤訊息抓 retryDelay（例如 "Please retry in 13.43s." 或 "retryDelay': '13s'")
            msg = str(e)
            m = re.search(r"retry in ([0-9]+(\.[0-9]+)?)s", msg)
            if not m:
                m = re.search(r"retryDelay['\"]:\s*'(\d+)s'", msg)

            wait_sec = float(m.group(1)) if m else 15.0
            time.sleep(wait_sec + 0.5)  # 多等一點保險
            continue
        except Exception as e:
            return f"AI 呼叫失敗：{e}"

    return "我現在太多人使用了（配額限制），請稍後再試一次。"

def call_agent(user_text: str):
    global _session
    if _session is None:
        _session = create_session()
    return call_my_agent(session_id=_session.id, user_text=user_text)
