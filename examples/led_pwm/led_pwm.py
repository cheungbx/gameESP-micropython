from machine import Pin, PWM
from micropython import const

import time

LED_PIN = const(2)
led = Pin(LED_PIN, Pin.OUT)
pwm1 = PWM(led, freq=1000, duty=0)

while True:
    for dValue in range(0, 1023, 100):
        pwm1.duty(dValue)
        time.sleep(0.1)

    for dValue in range(1023, 0, -100):
        pwm1.duty(dValue)
        time.sleep(0.1)
