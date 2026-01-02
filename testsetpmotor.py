import RPi.GPIO as GPIO
import time

# === 基本設定 ===
GPIO.setmode(GPIO.BOARD)
PINS = [31, 38, 33, 37]   # 接到 ULN2003 的 IN1~IN4
for p in PINS:
    GPIO.setup(p, GPIO.OUT)
    GPIO.output(p, 0)

# 半步進序列（28BYJ-48 + ULN2003 常用）
HALF_STEP_SEQ = [
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1],
]

STEPS_PER_REV = 4096           # 一圈大約 4096 半步（視實際可微調）
DEG_PER_STEP  = 360.0 / STEPS_PER_REV

# 參數：偏移量與對應最大角度
OFFSET_MAX = 1000.0             # 偏移量範圍 -OFFSET_MAX ~ +OFFSET_MAX
ANGLE_MAX  = 180.0             # 對應最大旋轉角度（度）

def step_once(seq):
    """執行一次 8 半步的序列"""
    for pattern in seq:
        for pin, val in zip(PINS, pattern):
            GPIO.output(pin, val)
        time.sleep(0.005)      # 越小越快，但可能會失步

def rotate_by_offset(offset):
    """
    offset: 在 -OFFSET_MAX ~ +OFFSET_MAX 之間
    正數 -> 順時針，負數 -> 逆時針（視接線而定）
    """
    # 限制範圍
    if offset >  OFFSET_MAX: offset =  OFFSET_MAX
    if offset < -OFFSET_MAX: offset = -OFFSET_MAX

    # 線性映射到角度
    angle = offset / OFFSET_MAX * ANGLE_MAX

    # 角度轉成步數
    steps = int(angle / DEG_PER_STEP)

    if steps == 0:
        return

    if steps > 0:
        seq = HALF_STEP_SEQ                # 正轉
    else:
        seq = list(reversed(HALF_STEP_SEQ))# 反轉

    for _ in range(abs(steps)):
        step_once(seq)

try:
    # 範例：給一個偏移量
    offset = 1      # 在 -100 ~ +100 之間
    rotate_by_offset(offset)

finally:
    GPIO.cleanup()
