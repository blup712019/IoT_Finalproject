# main.py
from ai_client import call_agent
from soundtext import speak
import time
import winsound
from soundtext import SoundText

def on_paragraph(text: str): # 之後要改成ubunto適用的
    """
    當使用者說完一整段話後，這個函式會被呼叫
    text 參數就是完整的語音文字（string）
    """
    print(f"\n📝 使用者說的段落：{text}\n")
    answer = call_agent(text)
    speak(answer)
    
    winsound.MessageBeep(winsound.MB_OK)

if __name__ == "__main__":
    st = SoundText(
        vosk_model_path=r".\vosk-model-small-en-us-0.15",
        hotword="hello",
        google_lang="zh-TW",
        phrase_time_limit=None,  # 用靜音判斷段落結束（像 Google 輸入）
        input_device_index=0,  # 若抓錯麥克風，可指定
    )
    # 啟動背景監聽（非阻塞）
    st.start(on_paragraph)
    try:
        while True:
            # 主程式照樣做其他事情
            print("主程式執行中...")
            time.sleep(1)

    except KeyboardInterrupt:
        st.stop()
        print("程式結束")
