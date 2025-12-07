# main.py
from ai_client import call_agent

if __name__ == "__main__":
    question = input("請輸入要問 agent 的內容（例如：現在幾點）：")
    answer = call_agent(question)

    print("\n===== Agent 回覆 =====")
    print(answer)
