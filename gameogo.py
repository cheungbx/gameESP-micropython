# gameESP.py
# for ESP32 Odroid-go
# common micropython module for ESP32 game board designed by Billy Cheung (c) 2019 08 31
# --usage--
# Using this common micropython game module, you can write micropython games to run
# either on the SPI OLED or I2C OLED without chaning a line of code.
# You only need to set the following line in gameESP.py file at the __init__ function
#        self.useSPI = True  # for SPI display , with buttons read through ADC
#        self.useSPI = False  # for I2C display, and individual hard buttons
#
# Note:  esp32 without the PSRAM only have 100K of RAM and is very bad at running .py micropython source code files
# with its very limited CPU onboard memory of 100K
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
#       g=GameESP()
#
#
#
#-----------------------------------------
'''
ESP32 Game board

TFT ILI9341 SPI
================
VCC     -  3V3
GND     -  GND
D0/SCK  -  IO18-VSPI-SCK
D1/MOSI -  IO23-VSPI-MOSI
RES     -  IO4 for ESP32
DC      -  IO21
CS      -  IO5-VSPI CS0
LED/BLK -  IO14

MISO    -  IO19-VSPI-MISO (not required for OLED)

TF Card Odroid-go
================
CS     -   IO22 VSPI CS1
MOSI   -   IO23 VSPI MOSI
MISO   -   IO19 VSPI SCK
SCK    -   IO18 VSPI MISO

Power
======
GND-100K-IO36(VP)-100K-VBat(3.7V)
GND-0.1uF-IO36

Audio
======
Speaker- - GND
Speaker+ - 10K VR- IO26

Paddle
======
GND
VN/IO39
4.7K-VCC


D-PAD Buttons
=============
tie one end to 3V3
UP        IO35-10K-GND
Down-10K  IO35
Left      IO34-10K-GND
Right-10K IO34

Other Buttons
============
tie one end to GND
Menu      IO13
Volume    IO00-10K-3v3
Select    IO27
Start     IO39(VN)-10K-3v3
B         IO33
A         IO32

'''
import utime
from utime import sleep_ms,ticks_ms, ticks_us, ticks_diff
from machine import Pin, SPI, PWM, ADC
from random import getrandbits, seed



# MicroPython SSD1306 OLED driver, I2C and SPI interfaces

from micropython import const
import time
import ustruct
import framebuf

TFT_DC_PIN = const(21)
TFT_CS_PIN = const(5)
TFT_LED_PIN = const(14)
TFT_MOSI_PIN = const(23)
TFT_MISO_PIN = const(19)
TFT_SCLK_PIN = const(18)

BUTTON_A_PIN = const(32)
BUTTON_B_PIN = const(33)
BUTTON_MENU_PIN = const(13)
BUTTON_SELECT_PIN = const(27)
BUTTON_VOLUME_PIN = const(0)
BUTTON_START_PIN = const(39)
BUTTON_JOY_Y_PIN = const(35)
BUTTON_JOY_X_PIN = const(34)
BUTTON_DEBOUNCE_MS = const(5)

SPEAKER_PIN = const(26)
SPEAKER_DAC_PIN = const(25)
SPEAKER_TONE_CHANNEL = const(0)

BATTERY_PIN = const(36)
BATTERY_RESISTANCE_NUM = const(2)

def height():
    return 8

def max_width():
    return 6

def hmap():
    return False

def reverse():
    return False

def monospaced():
    return True

def min_ch():
    return 0

def max_ch():
    return 255


_font = \
	b'\x00\x00\x00\x00\x00'\
	b'\x3E\x5B\x4F\x5B\x3E'\
	b'\x3E\x6B\x4F\x6B\x3E'\
	b'\x1C\x3E\x7C\x3E\x1C'\
	b'\x18\x3C\x7E\x3C\x18'\
	b'\x1C\x57\x7D\x57\x1C'\
	b'\x1C\x5E\x7F\x5E\x1C'\
	b'\x00\x18\x3C\x18\x00'\
	b'\xFF\xE7\xC3\xE7\xFF'\
	b'\x00\x18\x24\x18\x00'\
	b'\xFF\xE7\xDB\xE7\xFF'\
	b'\x30\x48\x3A\x06\x0E'\
	b'\x26\x29\x79\x29\x26'\
	b'\x40\x7F\x05\x05\x07'\
	b'\x40\x7F\x05\x25\x3F'\
	b'\x5A\x3C\xE7\x3C\x5A'\
	b'\x7F\x3E\x1C\x1C\x08'\
	b'\x08\x1C\x1C\x3E\x7F'\
	b'\x14\x22\x7F\x22\x14'\
	b'\x5F\x5F\x00\x5F\x5F'\
	b'\x06\x09\x7F\x01\x7F'\
	b'\x00\x66\x89\x95\x6A'\
	b'\x60\x60\x60\x60\x60'\
	b'\x94\xA2\xFF\xA2\x94'\
	b'\x08\x04\x7E\x04\x08'\
	b'\x10\x20\x7E\x20\x10'\
	b'\x08\x08\x2A\x1C\x08'\
	b'\x08\x1C\x2A\x08\x08'\
	b'\x1E\x10\x10\x10\x10'\
	b'\x0C\x1E\x0C\x1E\x0C'\
	b'\x30\x38\x3E\x38\x30'\
	b'\x06\x0E\x3E\x0E\x06'\
	b'\x00\x00\x00\x00\x00'\
	b'\x00\x00\x5F\x00\x00'\
	b'\x00\x07\x00\x07\x00'\
	b'\x14\x7F\x14\x7F\x14'\
	b'\x24\x2A\x7F\x2A\x12'\
	b'\x23\x13\x08\x64\x62'\
	b'\x36\x49\x56\x20\x50'\
	b'\x00\x08\x07\x03\x00'\
	b'\x00\x1C\x22\x41\x00'\
	b'\x00\x41\x22\x1C\x00'\
	b'\x2A\x1C\x7F\x1C\x2A'\
	b'\x08\x08\x3E\x08\x08'\
	b'\x00\x80\x70\x30\x00'\
	b'\x08\x08\x08\x08\x08'\
	b'\x00\x00\x60\x60\x00'\
	b'\x20\x10\x08\x04\x02'\
	b'\x3E\x51\x49\x45\x3E'\
	b'\x00\x42\x7F\x40\x00'\
	b'\x72\x49\x49\x49\x46'\
	b'\x21\x41\x49\x4D\x33'\
	b'\x18\x14\x12\x7F\x10'\
	b'\x27\x45\x45\x45\x39'\
	b'\x3C\x4A\x49\x49\x31'\
	b'\x41\x21\x11\x09\x07'\
	b'\x36\x49\x49\x49\x36'\
	b'\x46\x49\x49\x29\x1E'\
	b'\x00\x00\x14\x00\x00'\
	b'\x00\x40\x34\x00\x00'\
	b'\x00\x08\x14\x22\x41'\
	b'\x14\x14\x14\x14\x14'\
	b'\x00\x41\x22\x14\x08'\
	b'\x02\x01\x59\x09\x06'\
	b'\x3E\x41\x5D\x59\x4E'\
	b'\x7C\x12\x11\x12\x7C'\
	b'\x7F\x49\x49\x49\x36'\
	b'\x3E\x41\x41\x41\x22'\
	b'\x7F\x41\x41\x41\x3E'\
	b'\x7F\x49\x49\x49\x41'\
	b'\x7F\x09\x09\x09\x01'\
	b'\x3E\x41\x41\x51\x73'\
	b'\x7F\x08\x08\x08\x7F'\
	b'\x00\x41\x7F\x41\x00'\
	b'\x20\x40\x41\x3F\x01'\
	b'\x7F\x08\x14\x22\x41'\
	b'\x7F\x40\x40\x40\x40'\
	b'\x7F\x02\x1C\x02\x7F'\
	b'\x7F\x04\x08\x10\x7F'\
	b'\x3E\x41\x41\x41\x3E'\
	b'\x7F\x09\x09\x09\x06'\
	b'\x3E\x41\x51\x21\x5E'\
	b'\x7F\x09\x19\x29\x46'\
	b'\x26\x49\x49\x49\x32'\
	b'\x03\x01\x7F\x01\x03'\
	b'\x3F\x40\x40\x40\x3F'\
	b'\x1F\x20\x40\x20\x1F'\
	b'\x3F\x40\x38\x40\x3F'\
	b'\x63\x14\x08\x14\x63'\
	b'\x03\x04\x78\x04\x03'\
	b'\x61\x59\x49\x4D\x43'\
	b'\x00\x7F\x41\x41\x41'\
	b'\x02\x04\x08\x10\x20'\
	b'\x00\x41\x41\x41\x7F'\
	b'\x04\x02\x01\x02\x04'\
	b'\x40\x40\x40\x40\x40'\
	b'\x00\x03\x07\x08\x00'\
	b'\x20\x54\x54\x78\x40'\
	b'\x7F\x28\x44\x44\x38'\
	b'\x38\x44\x44\x44\x28'\
	b'\x38\x44\x44\x28\x7F'\
	b'\x38\x54\x54\x54\x18'\
	b'\x00\x08\x7E\x09\x02'\
	b'\x18\xA4\xA4\x9C\x78'\
	b'\x7F\x08\x04\x04\x78'\
	b'\x00\x44\x7D\x40\x00'\
	b'\x20\x40\x40\x3D\x00'\
	b'\x7F\x10\x28\x44\x00'\
	b'\x00\x41\x7F\x40\x00'\
	b'\x7C\x04\x78\x04\x78'\
	b'\x7C\x08\x04\x04\x78'\
	b'\x38\x44\x44\x44\x38'\
	b'\xFC\x18\x24\x24\x18'\
	b'\x18\x24\x24\x18\xFC'\
	b'\x7C\x08\x04\x04\x08'\
	b'\x48\x54\x54\x54\x24'\
	b'\x04\x04\x3F\x44\x24'\
	b'\x3C\x40\x40\x20\x7C'\
	b'\x1C\x20\x40\x20\x1C'\
	b'\x3C\x40\x30\x40\x3C'\
	b'\x44\x28\x10\x28\x44'\
	b'\x4C\x90\x90\x90\x7C'\
	b'\x44\x64\x54\x4C\x44'\
	b'\x00\x08\x36\x41\x00'\
	b'\x00\x00\x77\x00\x00'\
	b'\x00\x41\x36\x08\x00'\
	b'\x02\x01\x02\x04\x02'\
	b'\x3C\x26\x23\x26\x3C'\
	b'\x1E\xA1\xA1\x61\x12'\
	b'\x3A\x40\x40\x20\x7A'\
	b'\x38\x54\x54\x55\x59'\
	b'\x21\x55\x55\x79\x41'\
	b'\x21\x54\x54\x78\x41'\
	b'\x21\x55\x54\x78\x40'\
	b'\x20\x54\x55\x79\x40'\
	b'\x0C\x1E\x52\x72\x12'\
	b'\x39\x55\x55\x55\x59'\
	b'\x39\x54\x54\x54\x59'\
	b'\x39\x55\x54\x54\x58'\
	b'\x00\x00\x45\x7C\x41'\
	b'\x00\x02\x45\x7D\x42'\
	b'\x00\x01\x45\x7C\x40'\
	b'\xF0\x29\x24\x29\xF0'\
	b'\xF0\x28\x25\x28\xF0'\
	b'\x7C\x54\x55\x45\x00'\
	b'\x20\x54\x54\x7C\x54'\
	b'\x7C\x0A\x09\x7F\x49'\
	b'\x32\x49\x49\x49\x32'\
	b'\x32\x48\x48\x48\x32'\
	b'\x32\x4A\x48\x48\x30'\
	b'\x3A\x41\x41\x21\x7A'\
	b'\x3A\x42\x40\x20\x78'\
	b'\x00\x9D\xA0\xA0\x7D'\
	b'\x39\x44\x44\x44\x39'\
	b'\x3D\x40\x40\x40\x3D'\
	b'\x3C\x24\xFF\x24\x24'\
	b'\x48\x7E\x49\x43\x66'\
	b'\x2B\x2F\xFC\x2F\x2B'\
	b'\xFF\x09\x29\xF6\x20'\
	b'\xC0\x88\x7E\x09\x03'\
	b'\x20\x54\x54\x79\x41'\
	b'\x00\x00\x44\x7D\x41'\
	b'\x30\x48\x48\x4A\x32'\
	b'\x38\x40\x40\x22\x7A'\
	b'\x00\x7A\x0A\x0A\x72'\
	b'\x7D\x0D\x19\x31\x7D'\
	b'\x26\x29\x29\x2F\x28'\
	b'\x26\x29\x29\x29\x26'\
	b'\x30\x48\x4D\x40\x20'\
	b'\x38\x08\x08\x08\x08'\
	b'\x08\x08\x08\x08\x38'\
	b'\x2F\x10\xC8\xAC\xBA'\
	b'\x2F\x10\x28\x34\xFA'\
	b'\x00\x00\x7B\x00\x00'\
	b'\x08\x14\x2A\x14\x22'\
	b'\x22\x14\x2A\x14\x08'\
	b'\xAA\x00\x55\x00\xAA'\
	b'\xAA\x55\xAA\x55\xAA'\
	b'\x00\x00\x00\xFF\x00'\
	b'\x10\x10\x10\xFF\x00'\
	b'\x14\x14\x14\xFF\x00'\
	b'\x10\x10\xFF\x00\xFF'\
	b'\x10\x10\xF0\x10\xF0'\
	b'\x14\x14\x14\xFC\x00'\
	b'\x14\x14\xF7\x00\xFF'\
	b'\x00\x00\xFF\x00\xFF'\
	b'\x14\x14\xF4\x04\xFC'\
	b'\x14\x14\x17\x10\x1F'\
	b'\x10\x10\x1F\x10\x1F'\
	b'\x14\x14\x14\x1F\x00'\
	b'\x10\x10\x10\xF0\x00'\
	b'\x00\x00\x00\x1F\x10'\
	b'\x10\x10\x10\x1F\x10'\
	b'\x10\x10\x10\xF0\x10'\
	b'\x00\x00\x00\xFF\x10'\
	b'\x10\x10\x10\x10\x10'\
	b'\x10\x10\x10\xFF\x10'\
	b'\x00\x00\x00\xFF\x14'\
	b'\x00\x00\xFF\x00\xFF'\
	b'\x00\x00\x1F\x10\x17'\
	b'\x00\x00\xFC\x04\xF4'\
	b'\x14\x14\x17\x10\x17'\
	b'\x14\x14\xF4\x04\xF4'\
	b'\x00\x00\xFF\x00\xF7'\
	b'\x14\x14\x14\x14\x14'\
	b'\x14\x14\xF7\x00\xF7'\
	b'\x14\x14\x14\x17\x14'\
	b'\x10\x10\x1F\x10\x1F'\
	b'\x14\x14\x14\xF4\x14'\
	b'\x10\x10\xF0\x10\xF0'\
	b'\x00\x00\x1F\x10\x1F'\
	b'\x00\x00\x00\x1F\x14'\
	b'\x00\x00\x00\xFC\x14'\
	b'\x00\x00\xF0\x10\xF0'\
	b'\x10\x10\xFF\x10\xFF'\
	b'\x14\x14\x14\xFF\x14'\
	b'\x10\x10\x10\x1F\x00'\
	b'\x00\x00\x00\xF0\x10'\
	b'\xFF\xFF\xFF\xFF\xFF'\
	b'\xF0\xF0\xF0\xF0\xF0'\
	b'\xFF\xFF\xFF\x00\x00'\
	b'\x00\x00\x00\xFF\xFF'\
	b'\x0F\x0F\x0F\x0F\x0F'\
	b'\x38\x44\x44\x38\x44'\
	b'\x7C\x2A\x2A\x3E\x14'\
	b'\x7E\x02\x02\x06\x06'\
	b'\x02\x7E\x02\x7E\x02'\
	b'\x63\x55\x49\x41\x63'\
	b'\x38\x44\x44\x3C\x04'\
	b'\x40\x7E\x20\x1E\x20'\
	b'\x06\x02\x7E\x02\x02'\
	b'\x99\xA5\xE7\xA5\x99'\
	b'\x1C\x2A\x49\x2A\x1C'\
	b'\x4C\x72\x01\x72\x4C'\
	b'\x30\x4A\x4D\x4D\x30'\
	b'\x30\x48\x78\x48\x30'\
	b'\xBC\x62\x5A\x46\x3D'\
	b'\x3E\x49\x49\x49\x00'\
	b'\x7E\x01\x01\x01\x7E'\
	b'\x2A\x2A\x2A\x2A\x2A'\
	b'\x44\x44\x5F\x44\x44'\
	b'\x40\x51\x4A\x44\x40'\
	b'\x40\x44\x4A\x51\x40'\
	b'\x00\x00\xFF\x01\x03'\
	b'\xE0\x80\xFF\x00\x00'\
	b'\x08\x08\x6B\x6B\x08'\
	b'\x36\x12\x36\x24\x36'\
	b'\x06\x0F\x09\x0F\x06'\
	b'\x00\x00\x18\x18\x00'\
	b'\x00\x00\x10\x10\x00'\
	b'\x30\x40\xFF\x01\x01'\
	b'\x00\x1F\x01\x01\x1E'\
	b'\x00\x19\x1D\x17\x12'\
	b'\x00\x3C\x3C\x3C\x3C'\
	b'\x00\x00\x00\x00\x00'

_mvfont = memoryview(_font)

def get_width(s):
    return len(s)*6

def get_ch(ch):
    ordch = ord(ch)
    offset = ordch*5
    buf = bytearray(6)
    buf[0] = 0
    buf[1:]=_mvfont[offset:offset+5]
    return buf, 6

_RDDSDR = const(0x0f) # Read Display Self-Diagnostic Result
_SLPOUT = const(0x11) # Sleep Out
_GAMSET = const(0x26) # Gamma Set
_DISPOFF = const(0x28) # Display Off
_DISPON = const(0x29) # Display On
_CASET = const(0x2a) # Column Address Set
_PASET = const(0x2b) # Page Address Set
_RAMWR = const(0x2c) # Memory Write
_RAMRD = const(0x2e) # Memory Read
_MADCTL = const(0x36) # Memory Access Control
_VSCRSADD = const(0x37) # Vertical Scrolling Start Address
_PIXSET = const(0x3a) # Pixel Format Set
_PWCTRLA = const(0xcb) # Power Control A
_PWCRTLB = const(0xcf) # Power Control B
_DTCTRLA = const(0xe8) # Driver Timing Control A
_DTCTRLB = const(0xea) # Driver Timing Control B
_PWRONCTRL = const(0xed) # Power on Sequence Control
_PRCTRL = const(0xf7) # Pump Ratio Control
_PWCTRL1 = const(0xc0) # Power Control 1
_PWCTRL2 = const(0xc1) # Power Control 2
_VMCTRL1 = const(0xc5) # VCOM Control 1
_VMCTRL2 = const(0xc7) # VCOM Control 2
_FRMCTR1 = const(0xb1) # Frame Rate Control 1
_DISCTRL = const(0xb6) # Display Function Control
_INTFACE = const(0xf6) # Interface
_ENA3G = const(0xf2) # Enable 3G
_PGAMCTRL = const(0xe0) # Positive Gamma Control
_NGAMCTRL = const(0xe1) # Negative Gamma Control

_CHUNK = const(1024) #maximum number of pixels per spi write

def color565(r, g, b):
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3

class ILI9341:

    width = 320
    height = 240

    def __init__(self, spi, cs, dc, rst=None):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        # self.rst = rst
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        # self.rst.init(self.rst.OUT, value=0)
        # self.reset()
        self.init()
        self._scroll = 0
        self._buf = bytearray(_CHUNK * 2)
        self._colormap = bytearray(b'\x00\x00\xFF\xFF') #default white foregraound, black background
        self._x = 0
        self._y = 0
        self._font = GLCDFONT
        self.scrolling = False

    def set_color(self,fg,bg):
        self._colormap[0] = bg>>8
        self._colormap[1] = bg & 255
        self._colormap[2] = fg>>8
        self._colormap[3] = fg & 255

    def set_pos(self,x,y):
        self._x = x
        self._y = y

    def reset_scroll(self):
        self.scrolling = False
        self._scroll = 0
        self.scroll(0)

    def set_font(self, font):
        self._font = font

    def init(self):
        for command, data in (
            (_RDDSDR, b"\x03\x80\x02"),
            (_PWCRTLB, b"\x00\xcf\x30"),
            (_PWRONCTRL, b"\x64\x03\x12\x81"),
            (_DTCTRLA, b"\x85\x00\x78"),
            (_PWCTRLA, b"\x39\x2c\x00\x34\x02"),
            (_PRCTRL, b"\x20"),
            (_DTCTRLB, b"\x00\x00"),
            (_PWCTRL1, b"\x1b"),
            (_PWCTRL2, b"\x12"),
            (_VMCTRL1, b"\x3e\x3c"),
            (_VMCTRL2, b"\x91"),
            (_MADCTL, b"\xa8"),
            (_PIXSET, b"\x55"),
            (_FRMCTR1, b"\x00\x1b"),
            (_DISCTRL, b"\x0a\xa2\x27"),
            (_INTFACE, b"\x01\x30"),
            (_ENA3G, b"\x00"),
            (_GAMSET, b"\x01"),
            (_PGAMCTRL, b"\x0f\x31\x2b\x0c\x0e\x08\x4e\xf1\x37\x07\x10\x03\x0e\x09\x00"),
            (_NGAMCTRL, b"\x00\x0e\x14\x03\x11\x07\x31\xc1\x48\x08\x0f\x0c\x31\x36\x0f")):
            self._write(command, data)
        self._write(_SLPOUT)
        time.sleep_ms(120)
        self._write(_DISPON)

    # def reset(self):
    #     self.rst(0)
    #     time.sleep_ms(50)
    #     self.rst(1)
    #     time.sleep_ms(50)

    def _write(self, command, data=None):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def _writeblock(self, x0, y0, x1, y1, data=None):
        self._write(_CASET, ustruct.pack(">HH", x0, x1))
        self._write(_PASET, ustruct.pack(">HH", y0, y1))
        self._write(_RAMWR, data)

    def _readblock(self, x0, y0, x1, y1):
        self._write(_CASET, ustruct.pack(">HH", x0, x1))
        self._write(_PASET, ustruct.pack(">HH", y0, y1))
        if data is None:
            return self._read(_RAMRD, (x1 - x0 + 1) * (y1 - y0 + 1) * 3)

    def _read(self, command, count):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        data = self.spi.read(count)
        self.cs(1)
        return data

    def pixel(self, x, y, color=None):
        if color is None:
            r, b, g = self._readblock(x, y, x, y)
            return color565(r, g, b)
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return
        self._writeblock(x, y, x, y, ustruct.pack(">H", color))

    def fill_rect (self, x, y, w, h, color=None):
        x = min(self.width - 1, max(0, x))
        y = min(self.height - 1, max(0, y))
        w = min(self.width - x, max(1, w))
        h = min(self.height - y, max(1, h))
        if color:
            color = ustruct.pack(">H", color)
        else:
            color = self._colormap[0:2] #background
        for i in range(_CHUNK):
            self._buf[2*i]=color[0]; self._buf[2*i+1]=color[1]
        chunks, rest = divmod(w * h, _CHUNK)
        self._writeblock(x, y, x + w - 1, y + h - 1, None)
        if chunks:
            for count in range(chunks):
                self._data(self._buf)
        if rest != 0:
            mv = memoryview(self._buf)
            self._data(mv[:rest*2])

    def rect(self, x, y, w, h, color):
         self.fill_rect(x, y, w, 1, color)
         self.fill_rect(x, y+h-1, w, 1, color)
         self.fill_rect(x, y, 1, h, color)
         self.fill_rect(x+w-1, y, 1, h, color)

    def fill(self, color):
        self.fill_rect(0, 0, self.width, self.height, color)

    def erase(self):
        self.fill_rect(0, 0, self.width, self.height)

    def blit(self, bitbuff, x, y, w, h):
        x = min(self.width - 1, max(0, x))
        y = min(self.height - 1, max(0, y))
        w = min(self.width - x, max(1, w))
        h = min(self.height - y, max(1, h))
        chunks, rest = divmod(w * h, _CHUNK)
        self._writeblock(x, y, x + w - 1, y + h - 1, None)
        written = 0
        for iy in range(h):
            for ix in range(w):
                index = ix+iy*w - written
                if index >=_CHUNK:
                    self._data(self._buf)
                    written += _CHUNK
                    index   -= _CHUNK
                c = bitbuff.pixel(ix,iy)
                self._buf[index*2] = self._colormap[c*2]
                self._buf[index*2+1] = self._colormap[c*2+1]
        rest = w*h - written
        if rest != 0:
            mv = memoryview(self._buf)
            self._data(mv[:rest*2])

    def chars(self, str, x, y):
        str_w  = self._font.get_width(str)
        div, rem = divmod(self._font.height(),8)
        nbytes = div+1 if rem else div
        buf = bytearray(str_w * nbytes)
        pos = 0
        for ch in str:
            glyph, char_w = self._font.get_ch(ch)
            for row in range(nbytes):
                index = row*str_w + pos
                for i in range(char_w):
                    buf[index+i] = glyph[nbytes*i+row]
            pos += char_w
        fb = framebuf.FrameBuffer(buf,str_w, self._font.height(), framebuf.MONO_VLSB)
        self.blit(fb,x,y,str_w,self._font.height())
        return x+str_w

    def scroll(self, dy):
        self._scroll = (self._scroll + dy) % self.height
        self._write(_VSCRSADD, ustruct.pack(">H", self._scroll))

    def next_line(self, cury, char_h):
        global scrolling
        if not self.scrolling:
            res = cury + char_h
            self.scrolling = (res >= self.height)
        if self.scrolling:
            self.scroll(char_h)
            res = (self.height - char_h + self._scroll)%self.height
            self.fill_rectangle(0, res, self.width, self._font.height())
        return res

    def write(self, text): #does character wrap, compatible with stream output
        curx = self._x; cury = self._y
        char_h = self._font.height()
        width = 0
        written = 0
        for pos, ch in enumerate(text):
            if ch == '\n':
                if pos>0:
                    self.chars(text[written:pos],curx,cury)
                curx = 0; written = pos+1; width = 0
                cury = self.next_line(cury,char_h)
            else:
                char_w = self._font.get_width(ch)
                if curx + width + char_w >= self.width:
                    self.chars(text[written:pos], curx,cury)
                    curx = 0 ; written = pos; width = char_h
                    cury = self.next_line(cury,char_h)
                else:
                    width += char_w
        if written<len(text):
            curx = self.chars(text[written:], curx,cury)
        self._x = curx; self._y = cury


    def print(self, text): #does word wrap, leaves self._x unchanged
        cury = self._y; curx = self._x
        char_h = self._font.height()
        char_w = self._font.max_width()
        lines = text.split('\n')
        for line in lines:
            words = line.split(' ')
            for word in words:
                if curx + self._font.get_width(word) >= self.width:
                    curx = self._x; cury = self.next_line(cury,char_h)
                    while self._font.get_width(word) > self.width:
                        self.chars(word[:self.width//char_w],curx,cury)
                        word = word[self.width//char_w:]
                        cury = self.next_line(cury,char_h)
                if len(word)>0:
                    curx = self.chars(word+' ', curx,cury)
            curx = self._x; cury = self.next_line(cury,char_h)
        self._y = cury


class gameESP():
    max_vol = 6
    duty={0:0,1:0.05,2:0.1,3:0.5,4:1,5:2,6:70}
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
        self.ESP32 = True
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
        self.btnUval = 0
        self.btnDval = 0
        self.btnLval = 0
        self.btnRval = 0
        self.btnAval = 0
        self.btnBval = 0
        self.frameRate = 30
        self.screenW = 128
        self.screenH = 64
        self.Btns = 0
        self.lastBtns = 0

        self.PinBuzzer = Pin(26, Pin.OUT)

        # configure oled display SPI SSD1306
        self.spi = SPI(2, baudrate=14500000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
#        display = Display(spi, rst=Pin(4), dc=Pin(21), cs=Pin(5), )
        #DC, RES, CS
        self.lcd = ILI9341(SPI(2, baudrate=40000000,
                               miso=Pin(TFT_MISO_PIN, Pin.IN),
                               mosi=Pin(TFT_MOSI_PIN, Pin.OUT),
                               sck=Pin(TFT_SCLK_PIN, Pin.OUT)),
                           cs=Pin(TFT_CS_PIN, Pin.OUT),
                           dc=Pin(TFT_DC_PIN, Pin.OUT))
        self.PinBtnA  = Pin(32, Pin.IN, Pin.PULL_UP)
        self.PinBtnB  = Pin(33, Pin.IN, Pin.PULL_UP)
        self.adcX = ADC(34)
        self.adcY = ADC(35)
        self.adc = ADC(39)
        self.adcX.atten(ADC.ATTN_11DB)
        self.adcY.atten(ADC.ATTN_11DB)
        self.adc.atten(ADC.ATTN_11DB)


    def deinit(self) :
      self.adc.deinit()
      self.adcX.deinit()
      self.adcY.deinit()
      if self.useSPI :
        self.spi.deinit()

    def getPaddle (self) :
      # ESP32 - 142 to 3155
      return max ( min (int (self.adc.read() / 2.935) - 48, 1023),0)

    def pressed (self,btn) :
      return (self.Btns & btn)

    def justPressed (self,btn) :
      return (self.Btns & btn) and not (self.lastBtns & btn)

    def justReleased (self,btn) :
      return (self.lastBtns & btn) and not (self.Btns & btn)

    def getBtn(self) :

        self.btnAval = not self.PinBtnA.value()
        self.btnBval = not self.PinBtnB.value()

        val = self.adcX.read()
        self.btnLval = 1 if val > 2500  else 0
        self.btnRval = 1 if 1500 < val < 2000 else 0

        val = self.adcY.read()
        self.btnUval = 1 if val > 2500  else 0
        self.btnDval = 1 if 1500 < val < 2000 else 0

        self.lastBtns = self.Btns
        self.Btns = 0
        self.Btns = self.Btns | self.btnUval << 1 | self.btnLval << 2 | self.btnRval << 3 | self.btnDval << 4 | self.btnAval << 5 | self.btnBval << 6
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
