# buzzer.py
import RPi.GPIO as GPIO

_buzzer_pwm = None
BUZZER_FREQ = 2000
BUZZER_DUTY = 50

def buzzer_on(freq=BUZZER_FREQ):
    _buzzer_pwm.ChangeFrequency(freq)
    _buzzer_pwm.start(BUZZER_DUTY)

def buzzer_off():
    _buzzer_pwm.stop()



