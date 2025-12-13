import os
import platform
import subprocess
import tempfile
from pathlib import Path
from gtts import gTTS

import queue
import traceback
import json
import threading
import time
from typing import Callable, Optional

import pyaudio
import speech_recognition as sr
from vosk import Model, KaldiRecognizer

#輸入字串 然後會撥放
def speak(text: str, lang: str = "zh-TW") -> None:
    text = (text or "").strip()
    if not text:
        return

    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp_path = Path(tmp.name)
    tmp.close()

    try:
        gTTS(text=text, lang=lang).save(str(tmp_path))

        system = platform.system().lower()
        if system == "windows":
            # 用 Windows 預設播放器開啟 mp3（會立即返回，不會阻塞）
            os.startfile(str(tmp_path))
        else:
            subprocess.run(["mpv", "--no-video", str(tmp_path)], check=False)
    finally:
        # Windows 用 startfile 播放時檔案可能還在被使用，先不立刻刪
        if platform.system().lower() != "windows":
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass
#以下是speech to text

class SoundText:
    """
    Ubuntu / Linux 可用的語音模組（介面與 Windows 版相同）：

    功能流程：
    1) 背景用 Vosk + PyAudio 持續監聽 hotword
    2) 聽到 hotword 後：
       - 先暫時關閉 Vosk 的麥克風串流（避免裝置被佔用）
       - 使用 SpeechRecognition + Google 做「段落式語音輸入」
    3) 將段落文字（string）透過 callback 回傳
    4) 重新打開 Vosk 串流，回到 hotword 監聽
    """

    def __init__(
        self,
        vosk_model_path: str,
        hotword: str = "hello",
        sample_rate: int = 16000,
        frames_per_buffer: int = 4000,
        hotword_cooldown_sec: float = 1.5,    # hotword 冷卻時間（避免重複觸發）
        google_lang: str = "zh-TW",
        paragraph_timeout_sec: float = 6.0,   # 等待使用者開始說話的時間
        phrase_time_limit: Optional[float] = None,  # None = 靜音判斷段落結束（像 Google 輸入）
        input_device_index: Optional[int] = None,   # 指定麥克風裝置（不指定就用預設）
    ):
        # === 基本設定 ===
        self.hotword = hotword.lower().strip()
        self.sample_rate = sample_rate
        self.frames_per_buffer = frames_per_buffer
        self.hotword_cooldown_sec = hotword_cooldown_sec

        self.google_lang = google_lang
        self.paragraph_timeout_sec = paragraph_timeout_sec
        self.phrase_time_limit = phrase_time_limit
        self.input_device_index = input_device_index

        # === Vosk（hotword 偵測）===
        self._model = Model(vosk_model_path)
        self._vosk = KaldiRecognizer(self._model, self.sample_rate)

        # === SpeechRecognition（Google 段落輸入）===
        self._sr = sr.Recognizer()
        # 影響「停多久算一句結束」的體感（可依需求調整）
        self._sr.pause_threshold = 0.8
        self._sr.non_speaking_duration = 0.3

        # === PyAudio（麥克風 I/O）===
        self._p: Optional[pyaudio.PyAudio] = None
        self._stream = None
        self._audio_lock = threading.Lock()

        # === 執行緒與狀態 ===
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._on_text: Optional[Callable[[str], None]] = None

        self._last_fire = 0.0
        self._state_lock = threading.Lock()
        self._state = "IDLE"  # IDLE / PARAGRAPH
        

    # ===================== 對外 API =====================

    def start(self, on_text: Callable[[str], None]) -> None:
        """啟動背景 hotword 監聽（非阻塞），呼叫後主程式會立刻繼續跑。"""
        if self._thread and self._thread.is_alive():
            return

        self._on_text = on_text
        self._stop_evt.clear()

        with self._audio_lock:
            self._ensure_audio_open()

        self._thread = threading.Thread(target=self._hotword_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """停止背景監聽並釋放音訊資源。"""
        self._stop_evt.set()
        if self._thread:
            self._thread.join(timeout=1.5)

        with self._audio_lock:
            self._close_audio()

    # ===================== 狀態管理 =====================

    def _set_state(self, s: str) -> None:
        with self._state_lock:
            self._state = s

    def _get_state(self) -> str:
        with self._state_lock:
            return self._state

    # ===================== 音訊資源管理 =====================

    def _ensure_audio_open(self) -> None:
        """確保 PyAudio 串流已開啟。"""
        if self._p is None:
            self._p = pyaudio.PyAudio()

        if self._stream is None:
            self._stream = self._p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.frames_per_buffer,
                input_device_index=self.input_device_index,
            )
            self._stream.start_stream()

    def _close_audio(self) -> None:
        """安全關閉 PyAudio 串流與 PyAudio 物件。"""
        try:
            if self._stream:
                try:
                    self._stream.stop_stream()
                except Exception:
                    pass
                try:
                    self._stream.close()
                except Exception:
                    pass
        finally:
            self._stream = None

        try:
            if self._p:
                try:
                    self._p.terminate()
                except Exception:
                    pass
        finally:
            self._p = None

    # ===================== Hotword 監聽迴圈 =====================

    def _hotword_loop(self) -> None:
        """背景執行緒：持續監聽 hotword。"""
        while not self._stop_evt.is_set():
            # 段落輸入期間先不要偵測 hotword，避免重複觸發
            if self._get_state() != "IDLE":
                time.sleep(0.02)
                continue

            with self._audio_lock:
                if self._stream is None:
                    self._ensure_audio_open()
                stream = self._stream

            try:
                data = stream.read(self.frames_per_buffer, exception_on_overflow=False)
            except Exception:
                time.sleep(0.05)
                continue

            if self._vosk.AcceptWaveform(data):
                result = json.loads(self._vosk.Result() or "{}")
                text = (result.get("text") or "").lower().strip()
                normalized = text.replace(" ", "")
                print("【Vosk 聽到】:", normalized)
                if not text:
                    continue

                now = time.time()
                
                if self.hotword in normalized and (now - self._last_fire) >= self.hotword_cooldown_sec:
                    print("成功開啟助理")
                    self._last_fire = now
                    # 段落輸入用新執行緒處理，避免卡住 hotword loop
                    threading.Thread(target=self._do_paragraph_capture, daemon=True).start()

    # ===================== 段落式語音輸入（Google） =====================

    def _do_paragraph_capture(self) -> None:
        """觸發後擷取一整段話，並回傳 string。"""
        if self._get_state() != "IDLE":
            return

        self._set_state("PARAGRAPH")

        # 為了避免音訊裝置被占用，先關閉 Vosk 這邊的串流
        with self._audio_lock:
            self._close_audio()

        paragraph = ""
        try:
            with sr.Microphone(sample_rate=self.sample_rate, device_index=self.input_device_index) as source:
                audio = self._sr.listen(
                    source,
                    timeout=self.paragraph_timeout_sec,
                    phrase_time_limit=self.phrase_time_limit,
                )
            paragraph = self._sr.recognize_google(audio, language=self.google_lang).strip()

        except sr.WaitTimeoutError:
            paragraph = ""
        except sr.UnknownValueError:
            paragraph = ""
        except sr.RequestError:
            paragraph = ""
        except Exception:
            paragraph = ""
        finally:
            # 回到 hotword 監聽：重新開啟 Vosk 串流
            with self._audio_lock:
                self._ensure_audio_open()
            self._set_state("IDLE")

        if paragraph and self._on_text:
            self._on_text(paragraph)
