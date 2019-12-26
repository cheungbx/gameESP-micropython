# gameESP-micropython
# Simple MicroPython game modules and sample games for ESP8266 and ESP32 
#
# gameESP.py for esp8266 or esp32
# if you are using esp8266 boards, copy game8266.py as gameESP.py or use mpy-cross to compile to gameESP.mpy
# if you are using esp32 boards, copy game32.py as gameESP.py or use mpy-cross to compile to gameESP.mpy
#
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
# ESP8266 SPI SSD1306 version of game board layout
# ----------------------------------------
![Game8266%20I2C](https://github.com/cheungbx/gameesp-micropython/blob/master/game8266_SPI.jpg) 
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
# CS     - Hard wired to ground.
# Speaker
# GPIO15   D8  Speaker
# n.c.   - D6  (=GPIO12=HMISO)
#
# The ADC(0) (aka A0) is used to read both paddles and Buttons
# these two pins together control whether buttons or paddle will be read
# GPIO5    D1—— PinBtn
# GPIO4    D2—— pinPaddle
# GPIO0    D3-- PinPaddle2

# To read buttons - Pin.Btn.On()  Pin.Paddle.off() Pin.Paddle2.off()
# To read paddle  - Pin.Btn.Off()  Pin.Paddle.on() Pin.Paddle2.off()
# To read paddle2 - Pin.Btn.Off()  Pin.Paddle.off() Pin.Paddle2.on()
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
# ESP8266 I2C SSD1306 version of game board layout
# ----------------------------------------
![Game8266%20I2C](https://github.com/cheungbx/gameesp-micropython/blob/master/game8266_I2C.jpg) 
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
# GPIO16   D0——  B
#  GPIO16 cannot be pulled high by softeware, connect a 10K resisor to VCC to pull high
#
#
#==================================================================================
# ESP32 Game board
# -----------------
# The pin layout is exactly the same as that of the Odroid-Go
# so this library can be used on the micropython firmware of the Odroid-Go
#
#------------------------
# ESP32 OLED SPI SSD1306
# ==============
# VCC     -  3.3V
# GND     -  GND
# D0/SCK  -  IO18-VSPI-SCK
# D1/MOSI -  IO23-VSPI-MOSI
# RES     -  IO4 for ESP32
# DC      -  IO21
# CS      -  IO5-VSPI CS0
# LED/BLK -  IO14
#
# MISO    -  IO19-VSPI-MISO (not required for OLED)
#
#
# TF Card Odroid-go (optional)
# ================
# CS -      IO22 VSPI CS1
# MOSI - IO23 VSPI MOSI
# MISO -  IO19 VSPI SCK
# SCK -   IO18 VSPI MISO
#
# ESP32 OLED I2C SSD1306
# ================
# VCC  -  3.3V
# GND   - GND
# SCL -   IO 22
# SDA     IO 21

# Audio
# ======
# Speaker- - GND
# Speaker+ - 10K VR- IO26

# Paddle (10K VR)
# ======
# left   GND
# middle VN/IO39
# right  VCC


# D-PAD Buttons
# =============
# tie one end to 3V3
# UP        IO35-10K-GND
# Down-10K  IO35
# Left      IO34-10K-GND
# Right-10K IO34

# Other Buttons
# ============
# tie one end to GND
# Menu      IO13
# Volume    IO00-10K-3v3
# Select    IO27
# Start     IO39(VN)-10K-3v3
# B         IO33
# A         IO32

