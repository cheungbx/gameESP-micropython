from machine import Pin
from micropython import const

import time

LED_PIN = const(2)
led = Pin(LED_PIN, Pin.OUT)

while True:
    led.value(1)
    time.sleep(0.5)
    led.value(0)
    time.sleep(0.5)
