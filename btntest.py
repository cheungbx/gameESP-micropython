# btntests.py
# button , paddle, speaker and display tester for game board
# Use common game module "gameESP.py" for ESP8266  or ESP32
# by Billy Cheung  2019 10 26
#
#  ESP32 Game board (follow same pin layout as the Odroid_go)

# OLED SPI
# ========
# VCC    -        3V3
# GND    -       GND
# D0/SCK  -   IO18-VSPI-SCK
# D1/MOSI  - IO23-VSPI-MOSI
# RES        -    IO4 for ESP32
# DC         -      IO21
# CS          -      IO5-VSPI CS0
# LED/BLK -    IO14

# MISO     -      IO19-VSPI-MISO

# Audio
# ======
# Speaker-  GND
# Speaker+ - 10K VR- IO26

# Paddle (10K VR)
# ======
# GND
# VN/IO39
# -VCC
#
# D-PAD Buttons
# =============
# tie one end to 3V3
# UP              IO35-10K-GND
# Down-10K IO35
# Left            IO34-10K-GND
# Right-10K IO34

# Other Buttons
# ============
# tie one end to GND
# Menu    IO13
# Volume IO00-10K-3v3
# Select   IO27
# Start     IO39(VN)-10K-3v3
# B           IO33
# A           IO32
#

import gc
import sys
gc.collect()
print (gc.mem_free())
import network
import utime
from utime import sleep_ms,ticks_ms, ticks_us, ticks_diff
from machine import  ADC
# all dislplay, buttons, paddle, sound logics are in game32.mpy module
from gameESP import *
g=gameESP()
tone_dur = 20

# while not (pressed(btnL) and pressed(btnA)):
while True :



  g.display.fill(0)
  g.display.text("B+L=Exit", 40,54,1)

  g.getBtn()
  g.setVol()

  if g.ESP32 :
      # get ESP32  button's ADC value
      g.display.text ("X:{}".format(g.adcX.read()), 0,10,1)
      g.display.text ("Y:{}".format(g.adcY.read()), 60,10,1)

      g.display.text ("P:{}".format(g.getPaddle()), 0,0,1)
      g.display.text ("Vol:{}".format(g.vol),60 ,0,1)
  else :
      #get ESP8266 button's ADC valu
      g.display.text ("Btn:{}".format(g.adc.read()), 0,0,1)
      g.display.text ("Vol:{}".format(g.vol),60 ,0,1)

      g.display.text ("P:{}".format(g.getPaddle()), 0,10,1)
      g.display.text ("P2:{}".format(g.getPaddle2()), 60,10,1)






  if g.pressed(g.btnB) and g.justReleased(g.btnL):
     g.display.text("Bye!",10, 30,1)
     g.playTone('e4', tone_dur)
     g.playTone('c4', tone_dur)
     g.display.show()
     break

  if g.pressed (g.btnU):
     g.display.text("U",20, 20,1)
     g.playTone('c4', tone_dur)
  else :
     g.display.text(":",20, 20,1)
  if g.pressed(g.btnL):
     g.display.text("L",0, 35,1)
     g.playTone('d4', tone_dur)
  else :
     g.display.text(":",0, 35,1)
  if g.pressed(g.btnR):
     g.display.text("R",40, 35,1)
     g.playTone('e4', tone_dur)
  else :
     g.display.text(":",40, 35,1)

  if g.pressed(g.btnD):
     g.display.text("D",20, 50,1)
     g.playTone('f4', tone_dur)

  else :
     g.display.text(":",20, 50,1)
  if g.pressed(g.btnA):
     g.display.text("A",80, 40,1)
     g.playTone('c5', tone_dur)
  else :
     g.display.text(":",80, 40,1)
  if g.pressed(g.btnB):
    g.display.text("B",100, 30,1)
    g.playTone('d5', tone_dur)
  else :
     g.display.text(":",100, 30,1)



  g.display.show()
  sleep_ms(5)

if g.ESP32 :
    g.deinit()
    del sys.modules["gameESP"]
gc.collect()
