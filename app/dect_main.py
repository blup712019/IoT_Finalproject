# app/dect_main.py
import threading
import queue

from app.carrrrrrr import CarMotor
from app.hailo.basic_pipelines.dect import run_with_usb, user_app_callback_class, run_with_usb_interruptible

user_data = user_app_callback_class()
stop_event = threading.Event()
car = CarMotor(t=0.5)
def control_loop():
    """在背景執行：讀 q 的內容並輸出機器人要做的動作"""
    print("Control loop started. (type q + Enter to quit)\n")

    HORIZ_TH = 0.10   # 左右判斷閾值（cx 與 0.5 的差距）
    W_LARGE  = 0.50   # 物件框寬度 > 這個值 → 向前
    W_SMALL  = 0.20   # 物件框寬度 < 這個值 → 向後
    CONF_TH  = 0.5    # 信心度門檻
    
    rotateDir = 1
    rotateDegree = 0
    MAX_ROTATE = 5
    waitCount = 0
    errorCount = 0
    try:
        while not stop_event.is_set():
            try:
                target = user_data.q.get(timeout=0.5)
                if target == None:
                    errorCount+=1
                    print(f"no person!, errorCount: ${errorCount}")
                    if errorCount < 114 :
                        continue
                    waitCount -= 1
                    if(waitCount > 0):
                        continue
                    waitCount = 20
                    if rotateDegree == MAX_ROTATE :
                        rotateDir = -1
                    elif rotateDegree == -MAX_ROTATE:
                        rotateDir = 1
                    rotateDegree += rotateDir
                    if rotateDir == 1:
                        print("rotate Left")
                        car.rotateLeft(0.10)
                    elif rotateDir == -1:
                        print("rotate right")
                        car.rotateRight(0.10)
                    continue 

                # 1) 信心度過濾
                if target.get("confidence", 0) < CONF_TH:
                    continue
                cx = target["cx"]
                cy = target["cy"]
                x1, y1, x2, y2 = target["bbox"]

                w = x2 - x1   # 物件框在 X 方向的寬度 (0~1)
                h = y2 - y1   # 高度，目前沒用到但先保留

                # ===== 左右軸判斷 =====
                offset_x = cx - 0.5
                if offset_x > HORIZ_TH:
                    lr = "right"      # 人在畫面偏右
                    lr_action = 1  # 機器人要「向右」轉
                elif offset_x < -HORIZ_TH:
                    lr = "left"       # 人在畫面偏左
                    lr_action = -1
                else:
                    lr = "center"
                    lr_action = 0

                # ===== 前後軸判斷（用框的寬度 w）=====
                # 大於某個寬度 → 向前
                # 小於某個寬度 → 向後
                if w > W_LARGE:
                    fb = "forward"
                    fb_action = 1
                elif w < W_SMALL:
                    fb = "backward"
                    fb_action = -1
                else:
                    fb = "stay"
                    fb_action = 0

                # ✅ 同時輸出兩個軸的動作


                errorCount = 0
                if lr_action == 1 and fb_action == 1:
                    car.turnLeft()
                elif lr_action == -1 and fb_action == 1:
                    car.turnRight()
                elif lr_action == 0 and fb_action == 1:
                    car.forward()
                print(f"${lr} ${fb}")

                # 🔧 這裡接馬達控制：
                # 例：差速驅動（左右輪）
                # 左右決定轉向，前後決定速度
                #
                # base_speed = 50   # 基礎速度，自己調
                # turn_speed = 30   # 轉向補償
                #
                # left_speed  = 0
                # right_speed = 0
                #
                # # 前後
                # if fb == "forward":
                #     left_speed  += base_speed
                #     right_speed += base_speed
                # elif fb == "backward":
                #     left_speed  -= base_speed
                #     right_speed -= base_speed
                #
                # # 左右
                # if lr == "left":
                #     left_speed  -= turn_speed
                #     right_speed += turn_speed
                # elif lr == "right":
                #     left_speed  += turn_speed
                #     right_speed -= turn_speed
                #
                # motor.set_speed(left_speed, right_speed)

            except queue.Empty:
                continue
    finally:
        print("Control loop exit")


def keyboard_loop():
    """VNC 下 Ctrl+C 可能失效，提供 q+Enter 退出"""
    while True:
        cmd = input()
        if cmd.strip().lower() == "q":
            stop_event.set()
            break


stop_dect_event = threading.Event()

def main():
    """給外部 import 用的進入點，也給這個檔案自己跑用"""
    # 背景：控制 loop + 鍵盤退出
    threading.Thread(target=control_loop, daemon=True).start()
    threading.Thread(target=keyboard_loop, daemon=True).start()

    # 視覺 pipeline 一定要在 main thread 跑
    run_with_usb(user_data=user_data)

    # run_with_usb 結束才會走到這裡
    stop_event.set()


# 直接 `python app/dect_main.py` 時也能跑
if __name__ == "__main__":
    main()
