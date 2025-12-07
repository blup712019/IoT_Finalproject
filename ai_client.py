# ai_client.py
from dotenv import load_dotenv
from pathlib import Path
import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

from my_agent.agent import root_agent


# 讀取 my_agent/.env
env_path = Path(__file__).parent / "my_agent" / ".env"
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
    """
    對外暴露的同步函式：
    - 給一個 session_id
    - 給一段文字
    - 回傳 AI 的文字回應
    """
    return asyncio.run(_ask_my_agent(session_id, user_text))

def call_agent(user_text: str):
    session = create_session()
    return call_my_agent(session_id=session.id, user_text=user_text)
