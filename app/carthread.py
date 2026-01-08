import threading
import queue
import time

class CarThread(threading.Thread):
    def __init__(self, user_data, car, stop_event):
        super().__init__(daemon=True)
        self.user_data = user_data
        self.car = car
        self.stop_event = stop_event

        # ===== 參數設定 =====
        self.HORIZ_TH = 0.10
        self.W_LARGE  = 0.50
        self.W_SMALL  = 0.20
        self.CONF_TH  = 0.5

        self.rotateDir = 1
        self.rotateDegree = 0
        self.MAX_ROTATE = 5
        self.waitCount = 0
        self.errorCount = 0

    def run(self):
        print("Control loop thread started.")
        self.stop_event.clear()
        try:
            while not self.stop_event.is_set():
                try:
                    target = self.user_data.q.get(timeout=0.5)
                    #print(f"get target Acc, target = ${target}")
                    # ===== 無偵測目標 =====
                    if target is None:
                        self.errorCount += 1
                        #print(f"no person! errorCount: {self.errorCount}")

                        if self.errorCount < 200:
                            continue

                        self.waitCount -= 1
                        if self.waitCount > 0:
                            continue

                        self.waitCount = 20

                        if self.rotateDegree == self.MAX_ROTATE:
                            self.rotateDir = -1
                        elif self.rotateDegree == -self.MAX_ROTATE:
                            self.rotateDir = 1

                        self.rotateDegree += self.rotateDir

                        if self.rotateDir == 1:
                            self.car.rotateLeft(0.075)
                        else:
                            self.car.rotateRight(0.075)

                        continue
                    # 1) 信心度過濾
                    if target.get("confidence", 0) < self.CONF_TH:
                        continue
                    cx = target["cx"]
                    cy = target["cy"]
                    x1, y1, x2, y2 = target["bbox"]

                    w = x2 - x1   # 物件框在 X 方向的寬度 (0~1)
                    h = y2 - y1   # 高度，目前沒用到但先保留
    
                    # ===== 左右軸判斷 =====
                    offset_x = cx - 0.5
                    if offset_x > self.HORIZ_TH:
                        lr = "right"      # 人在畫面偏右
                        lr_action = 1  # 機器人要「向右」轉
                    elif offset_x < -self.HORIZ_TH:
                        lr = "left"       # 人在畫面偏左
                        lr_action = -1
                    else:
                        lr = "center"
                        lr_action = 0
    
                    # ===== 前後軸判斷（用框的寬度 w）=====
                    # 大於某個寬度 → 向前
                    # 小於某個寬度 → 向後
                    if w > self.W_LARGE:
                        fb = "forward"
                        fb_action = 1
                    elif w < self.W_SMALL:
                        fb = "backward"
                        fb_action = -1
                    else:
                        fb = "stay"
                        fb_action = 0
    
                    # ✅ 同時輸出兩個軸的動作
    
    
                    errorCount = 0
                    if lr_action == 1 and fb_action == 1:
                        self.car.turnLeft()
                    elif lr_action == -1 and fb_action == 1:
                        self.car.turnRight()
                    elif lr_action == 0 and fb_action == 1:
                        self.car.forward()
                    # 🔧 這裡接馬達控制：
                    # 例：差速驅動（左右輪）
                    # 左右決定轉向，前後決定速度
                    #
                    # base_speed = 50   # 基礎速度，自己調
                    # turn_speed = 30   # 轉向補償
                    #
                    # left_speed  = 0
                    # right_speed = 0
                    # 前後
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
                    print('queue is empty')
                    continue
        finally:
            print("Control loop exit")
            self.car.stop()

