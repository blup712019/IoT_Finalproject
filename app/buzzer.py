# buzzer.py
import RPi.GPIO as GPIO

BUZZER_PIN = 36      # BOARD 編號
BUZZER_FREQ = 2000  # Hz

GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

_buzzer_pwm = GPIO.PWM(BUZZER_PIN, BUZZER_FREQ)

def buzzer_on(freq=BUZZER_FREQ):
    _buzzer_pwm.ChangeFrequency(freq)
    _buzzer_pwm.start(50)

def buzzer_off():
    _buzzer_pwm.stop()

def cleanup():
    try:
        _buzzer_pwm.stop()
    except:
        pass
    GPIO.cleanup()

