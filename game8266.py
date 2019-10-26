# gameESP.py for esp8266
# common micropython module for ESP8266 game board designed by Billy Cheung (c) 2019 08 31
# --usage--
# Using this common micropython game module, you can write micropython games to run
# either on the SPI OLED or I2C OLED without chaning a line of code.
# You only need to set the following line in gameESP.py file at the __init__ function
#        self.useSPI = True  # for SPI display , with buttons read through ADC
#        self.useSPI = False  # for I2C display, and individual hard buttons
#
# Note:  esp8266 is very bad at running .py micropython source code files
# with its very limited CPU onboard memory of 32K
# so to run any program with > 300 lines of micropython codes combined (including all modules),
# you need to convert source files into byte code first to avoid running out of memory.
# Install a version of the  mpy-cross micropython pre-compiler that can run in your system (available from github).
# Type this command to convert gameESP.py to the byte code file gameESP.mpy  using mpy-cross.
#        mpy-cross gameESP.py
# then copy the gameESP.mpy file to the micropython's import directory on the flash
# create your game and leaverge the functions to display, read buttons and paddle and make sounds
# from the gameESP class module.
# Add this line to your micropython game source code (examples attached, e.g. invader.py)
#       from gameESP import gameESP, Rect
#       g=gameESP()
#
#
#
#-----------------------------------------
# SPI version of game board layout
# ----------------------------------------
# micropython game hat module to use SSD1306 SPI OLED, 6 buttons and a paddle
# SPI display runs 5 times faster than I2C  display in micropython and you need this speeds
# for games with many moving graphics (e.g. space invdader, breakout).
#
# Buttons are read through A0 using many resistors in a  Voltage Divider circuit
# ESP8266 (node MCU D1 mini)  micropython
#
# SPI OLED
# GND
# VCC
# D0/Sck - D5 (=GPIO14=HSCLK)
# D1/MOSI- D7 (=GPIO13=HMOSI)
# RES    - D0 (=GPIO16)
# DC     - D4 (=GPIO2)
# CS     - D3 (=GPIO0)
# Speaker
# GPIO15   D8  Speaker
# n.c.   - D6  (=GPIO12=HMISO)
#
# The ADC(0) (aka A0) is used to read both paddles and Buttons
# these two pins together control whether buttons or paddle will be read
# GPIO5    D1—— PinBtn
# GPIO4    D2—— pinPaddle
# To read buttons - Pin.Btn.On()  Pin.Paddle.off()
# To read paddle  - Pin.Btn.Off()  Pin.Paddle.on()
#
# buttons are connected in series to create a voltage dividor
# Each directional and A , B button when pressed will connect that point of
# the voltage dividor to A0 to read the ADC value to determine which button is pressed.
# resistor values are chosen to ensure we have at least a gap of 10 between each button combinations.
# L, R, U, D, can be pressed individually but not toghether.
# A, B, can be pressed invididually but not together.
# any one of A or B, can be pressed together with any one of L,R,U,D
# so you can move the gun using L,R, U,D, while shooting with A or B.
#
# refer to the schematics on my github for how to hook it up
#
# 3.3V-9K-Up-9K-Left-12K-Right-9K-Down-9K-A button-12K-B Button-9K-GND
#
#-----------------------------------------
# I2C version of game board layout
# ----------------------------------------
# mocropython game hat module to use SSD1306 I2C OLED, 6 buttons and a paddle
# I2C display runs 5 times slower than I2C display in micropython.
# Games with many moving graphics (e.g. space invdader, breakout) will run slower.
#
# Buttons are read through indvidial GPIO pins (pulled high).
#
# I2C OLED SSD1306
# GPIO4   D2---  SDA OLED
# GPIO5   D1---  SCL  OLED
#
# Speaker
# GPIO15  D8     Speaker
#
# Buttons are connect to GND when pressed
# GPIO12  D6——   Left  
# GPIO13  D7——   Right     
# GPIO14  D5——   UP    
# GPIO2   D4——   Down    
# GPIO0   D3——   A
# GPIO16  D0——   B
# * GPIO16 cannot be pulled high by softeware, connect a 10K resisor to VCC to pull high

import utime
from utime import sleep_ms,ticks_ms, ticks_us, ticks_diff
from machine import Pin, SPI,I2C, PWM, ADC
import ssd1306
from random import getrandbits, seed

class gameESP():
    max_vol = 6
    duty={0:0,1:1,2:3,3:5,4:10,5:70,6:512}
    tones = {
        'c4': 262,
        'd4': 294,
        'e4': 330,
        'f4': 349,
        'f#4': 370,
        'g4': 392,
        'g#4': 415,
        'a4': 440,
        "a#4": 466,
        'b4': 494,
        'c5': 523,
        'c#5': 554,
        'd5': 587,
        'd#5': 622,
        'e5': 659,
        'f5': 698,
        'f#5': 740,
        'g5': 784,
        'g#5': 831,
        'a5': 880,
        'b5': 988,
        'c6': 1047,
        'c#6': 1109,
        'd6': 1175,
        ' ': 0
    }

    def __init__(self):
        # True =  SPI display, False = I2C display
        self.ESP32 = False
        self.useSPI = True
        self.timer = 0
        self.vol = int(self.max_vol/2) + 1
        seed(ticks_us())
        self.btnU = 1 << 1
        self.btnL = 1 << 2
        self.btnR = 1 << 3
        self.btnD = 1 << 4
        self.btnA = 1 << 5
        self.btnB = 1 << 6
        self.frameRate = 30
        self.screenW = 128
        self.screenH = 64
        self.Btns = 0
        self.lastBtns = 0
        self.adc = ADC(0)
        self.PinBuzzer = Pin(15, Pin.OUT)
        if self.useSPI :
            # configure oled display SPI SSD1306
            self.hspi = SPI(1, baudrate=8000000, polarity=0, phase=0)
            #DC, RES, CS
            self.display = ssd1306.SSD1306_SPI(128, 64, self.hspi, Pin(2), Pin(16), Pin(0))
            self.pinBtn = Pin(5, Pin.OUT)
            self.pinPaddle = Pin(4, Pin.OUT)
        else :  # I2C display

            # configure oled display I2C SSD1306
            self.i2c = I2C(-1, Pin(5), Pin(4))   # SCL, SDA
            self.display = ssd1306.SSD1306_I2C(128, 64, self.i2c)
            self.PinBtnL = Pin(12, Pin.IN, Pin.PULL_UP)
            self.PinBtnR = Pin(13, Pin.IN, Pin.PULL_UP)
            self.PinBtnU = Pin(14, Pin.IN, Pin.PULL_UP)
            self.PinBtnD = Pin(2, Pin.IN, Pin.PULL_UP)
            self.PinBtnA = Pin(0, Pin.IN, Pin.PULL_UP)
            self.PinBtnB = Pin(16, Pin.IN) #GPIO 16 always pull down cannot pull up

    def deinit(self) :
        pass

    def getPaddle (self) :
      if self.useSPI :
          self.pinPaddle.on()
          self.pinBtn.off()
          sleep_ms(1)
      return self.adc.read()

    def pressed (self,btn) :
      return (self.Btns & btn)

    def justPressed (self,btn) :
      return (self.Btns & btn) and not (self.lastBtns & btn)

    def justReleased (self,btn) :
      return (self.lastBtns & btn) and not (self.Btns & btn)

    def getBtn(self) :
      self.lastBtns = self.Btns
      self.Btns = 0
      if self.useSPI :
          # SPI board, record each key pressed based on the  ADC value
          self.pinPaddle.off()
          self.pinBtn.on()

          a0=self.adc.read()
          if a0  < 570 :
            if a0 < 362 :
              if a0 > 176 :
                if a0 > 277 :
                  self.Btns |= self.btnU | self.btnA
                elif a0 > 241 :
                  self.Btns |= self.btnL
                else :
                  self.Btns |= self.btnU | self.btnD
              elif a0 > 68:
                self.Btns |= self.btnU
            else :
              if a0 > 485 :
                if a0 > 531 :
                  self.Btns |= self.btnD
                else :
                  self.Btns |= self.btnU | self.btnB
              else:
                if a0 > 443 :
                  self.Btns |= self.btnL | self.btnA
                else :
                  self.Btns |= self.btnR
          else:
              if a0 < 737 :
                if a0 < 661 :
                  if a0 > 615 :
                    self.Btns |= self.btnD | self.btnA
                  else :
                    self.Btns |= self.btnR | self.btnA
                elif a0 > 683 :
                  self.Btns |= self.btnA
                else :
                  self.Btns |= self.btnL | self.btnB
              elif a0 < 841 :
                if a0 > 805 :
                  self.Btns |= self.btnD | self.btnB
                else :
                  self.Btns |= self.btnR | self.btnB
              elif a0 > 870 :
                self.Btns |= self.btnB
              else :
                self.Btns |= self.btnA | self.btnB

      else : # I2C board, read buttons directly
           self.Btns = self.Btns | (not self.PinBtnU.value()) << 1 | (not self.PinBtnL.value()) << 2 | (not self.PinBtnR.value()) << 3 | (not self.PinBtnD.value()) << 4 | (not self.PinBtnA.value()) << 5 | (not self.PinBtnB.value())<< 6
      return self.Btns
      print (self.Btns)

    def  setVol(self) :
        if self.pressed(self.btnB):
            if self.justPressed(self.btnU) :
                self.vol= min (self.vol+1, self.max_vol)
                self.playTone('c4', 100)
                return True
            elif self.justPressed(self.btnD) :
                self.vol= max (self.vol-1, 0)
                self.playTone('d4', 100)
                return True

        return False

    def playTone(self, tone, tone_duration, rest_duration=0):
        beeper = PWM(self.PinBuzzer, freq=self.tones[tone], duty=self.duty[self.vol])
        sleep_ms(tone_duration)
        beeper.deinit()
        sleep_ms(rest_duration)

    def playSound(self, freq, tone_duration, rest_duration=0):
        beeper = PWM(self.PinBuzzer, freq, duty=self.duty[self.vol])
        sleep_ms(tone_duration)
        beeper.deinit()
        sleep_ms(rest_duration)

    def random (self, x, y) :
        return  getrandbits(10) % (y+1) + x

    def display_and_wait(self) :
        self.display.show()
        timer_dif = int(1000/self.frameRate) - ticks_diff(ticks_ms(), self.timer)
        if timer_dif > 0 :
            sleep_ms(timer_dif)
        self.timer=ticks_ms()


class Rect (object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


    def move (self, vx, vy) :
        self.x = self.x + vx
        self.y = self.y + vy


    def colliderect (self, rect1) :
      if (self.x + self.w   > rect1.x and
        self.x < rect1.x + rect1.w  and
        self.y + self.h > rect1.y and
        self.y < rect1.y + rect1.h) :
        return True
      else:
        return False
