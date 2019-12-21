# menu.py.
# startup menu and launcher for other python programs
#
# Use common game module "gameESP.py" for ESP8266  or ESP32
# by Billy Cheung  2019 10 26

import os
import sys
import gc
gc.collect()
print (gc.mem_free())
from machine import Pin, ADC
from utime import sleep_ms, ticks_ms, ticks_diff
module_name = ""
tone_dur = 10

def do_menu (g) :
  global module_name, vol, max_vol

  # all dislplay, buttons, paddle, sound logics are in game8266.mpy module


  SKIP_NAMES = ("boot", "main", "menu","gameESP")


  files = [item[0] for item in os.ilistdir(".") if item[1] == 0x8000]


  module_names = [
      filename.rsplit(".", 1)[0]
      for filename in files
      if (filename.endswith(".py") or  filename.endswith(".mpy") ) and not filename.startswith("_")
  ]
  module_names = [module_name for module_name in module_names if not module_name in SKIP_NAMES]
  module_names.sort()
  tot_file = len(module_names)
  tot_rows = const(5)
  screen_pos = 0
  file_pos = 0


  g.display.fill(0)
  g.display.text('Micropython Menu', 0, 0, 1)
  g.display.text('U/D to Select', 0, 20, 1)
  g.display.text('A to Launch', 0, 30, 1)
  g.display.text('B+L to exit', 0, 40, 1)
  g.display.text('Press U to start', 0, 50, 1)
  g.display.show()
  sleep_ms(1000)

  # wait till all buttons are released
  g.getBtn()
  while not g.Btns :
    sleep_ms(10)
    g.getBtn()

  launched = False
  while not launched :
    gc.collect()
    g.display.fill(0)
    g.display.text('M:{}'.format(gc.mem_free()), 0, 0, 1)
    g.display.rect(90,0, g.max_vol*4+2,6,1)
    g.display.fill_rect(91,1, g.vol * 4,4,1)
    i = 0
    for j in range (file_pos, min(file_pos+tot_rows, tot_file)) :
      current_row = 12 + 10 *i
      if i == screen_pos :
        g.display.fill_rect(0, current_row, 127, 10, 1)
        g.display.text(str(j) + " " + module_names[j],0 , current_row, 0)
      else:
        g.display.fill_rect(0, current_row, 127, 10, 0)
        g.display.text(str(j) + " " + module_names[j], 0, current_row, 1)
      i+=1
    g.display.show()
    g.getBtn()

    if g.justPressed(g.btnU):
        if g.pressed(g.btnB):
            g.vol = min (g.vol+1, g.max_vol)
            g.playTone('e4', tone_dur)
        else :
            if screen_pos > 0 :
                screen_pos -= 1
            else :
                if file_pos > 0 :
                    file_pos = max (0, file_pos - tot_rows)
                    screen_pos=tot_rows-1
        g.playTone('c4', tone_dur)


    if g.justPressed(g.btnD):
        if g.pressed(g.btnB):
            g.vol= max (g.vol-1, 0)
            g.playTone('d4', tone_dur)
        else :
            if screen_pos < min(tot_file - file_pos - 1, tot_rows -1) :
                screen_pos = min(tot_file-1, screen_pos + 1)
            else :
                if file_pos + tot_rows < tot_file :
                  file_pos = min (tot_file, file_pos + tot_rows)
                  screen_pos=0
        g.playTone('e4', tone_dur)

    if g.justReleased(g.btnA):
        g.playTone('c5', tone_dur)
        g.display.fill(0)
        g.display.text("launching " , 5, 20, 1)
        g.display.text(module_names[file_pos + screen_pos], 5, 40, 1)
        g.display.show()
        sleep_ms(1000)
        module_name = module_names[file_pos + screen_pos]
        return True

    if g.pressed(g.btnB) and g.justPressed(g.btnL):
        g.playTone('d5', tone_dur)
        launched = True
        g.display.fill(0)
        g.display.text("Menu exited", 5, 24, 1)
        g.display.show()
        return False
    g.display.show()
    sleep_ms(10)


go_on = True
from gameESP import *
g=gameESP()
ESP32 = g.ESP32

while go_on :

  go_on = do_menu(g)
  if ESP32 :
    g.deinit()
    del sys.modules["gameESP"]

  if go_on :
    gc.collect()
    module = __import__(module_name)
    del sys.modules[module_name]
    gc.collect()

  if ESP32 :
      from gameESP import *
      g=gameESP()
