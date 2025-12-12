import pyaudio, audioop, time

RATE = 16000
CHUNK = 4000

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("開始讀取麥克風，對著麥克風說話（Ctrl+C 結束）")
try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        rms = audioop.rms(data, 2)  # 音量大小（越大越吵）
        print("音量:", rms)
        time.sleep(0.05)
except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
p.terminate()
print("結束")
