import threading

start_detect_event = threading.Event()
stop_detect_event = threading.Event()
global_stop = threading.Event()

def main_loop(app_callback, user_data):
    try:
        while not global_stop.is_set():
            print("[MAIN] waiting timer...")
            start_detect_event.wait()         # 睡到 timer 喚醒
            start_detect_event.clear()
            if global_stop.is_set():
                break

            stop_detect_event.clear()
            print("[MAIN] start detection")
            run_with_usb_interruptible(app_callback, user_data, stop_detect_event)
            print("[MAIN] back to waiting")
    finally:
        global_stop.set()
        stop_detect_event.set()

