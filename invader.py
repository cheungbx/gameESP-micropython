# invaders.py
#
# Use common game module "gameESP.py" for ESP8266  or ESP32
# by Billy Cheung  2019 10 26
# Use gamePico.py for Raspberry Pi Pico
# by eduardofilo   2021 07 19
#
#
import gc
import sys
gc.collect()
print (gc.mem_free())
import utime
from utime import sleep_ms
#import network
from math import sqrt
# all dislplay, buttons, paddle, sound logics are in GameESP.mpy module
from gameESP import *
g=gameESP()

# songbuf = [ g.songStart, NotesorFreq , timeunit,
#             freq1, duration1, freq2, duration2,
#             g.songLoop  or g.songEnd]
# Notes or Freq : False=song coded frequencies (Hz), True=song coded in notes, e.g. 'f4' 'f#4')
# timeunit = value to multiple durations with that number of milli-seconds. Default 1 milli-second.
# freq1 can be replaced with note, e.g. [g.songStart, 'c4', 200,'d4', 200,'e4',300,'f4', 300,'f#4': 300,'g4',300,g.songEnd]
# freq1 = 0 for silence notes
# duration1 is multipled with tempo to arrive at a duration for the  note in millseconds

g.frameRate = 30
g.bgm = 1
g.maxBgm = 3
bgmBuf= [
    [g.songStart, False, 1, g.songEnd],
    # Empire Strikes Back
    [ g.songStart,True, 100, 0, 4,
    'g3',1,0,1,'g3',1,0,1,'g3',1,0,1,'c4',8,'g4',8,0,4,'f4',2,'e4',2,'d4',2,'c5',8,'g4',8, 0,4, 'f4',2,'e4',2,'d4',2,'c5',8,'g4',8,0,4,'f4',2,'e4',2,'f4',2,'d4',8,0,8,
    'g3',1,0,1,'g3',1,0,1,'g3',1,0,1,'c4',8,'g4',8,0,4,'f4',2,'e4',2,'d4',2,'c5',8,'g4',8, 0,4, 'f4',2,'e4',2,'d4',2,'c5',8,'g4',8,0,4,'f4',2,'e4',2,'f4',2,'d4',8,0,8,
    'g3',1,0,1,'g3',1,0,1,'a3',4,0,4,'f4',2,'e4',2,'d4',2,'c4',1,0,1,'c4',2,'d4',1,'e4',1,'d4',2,'a3',2,'b3',4,
    'g3',1,0,1,'g3',1,0,1,'a3',4,0,4,'f4',2,'e4',2,'d4',2,'c4',1,0,1,'g4',2,0,1,'d4',1,'d4',4,0,4,
    'g3',1,0,1,'g3',1,0,1,'a3',4,0,4,'f4',2,'e4',2,'d4',2,'c4',1,0,1,'c4',2,'d4',1,'e4',1,'d4',2,'a3',2,'b3',4,
    'e4',1,0,1,'e4',2,'a4',2,'g4',2,'f4',2,'e4',2,'d4',2,'c4',2,'b3',2,'a3',2,'e4',8, 0, 8,
    g.songLoop],
    # The Imperial March
    [ g.songStart,False, 1, 0, 400,
    440, 400, 0, 100, 440, 400, 0, 100, 440, 400, 0,100, 349, 350, 523, 150,   440, 500, 349, 350, 523, 150, 440, 650, 0,500, 659, 500, 659, 500, 659, 500,  698, 350, 523, 150, 415, 500, 349, 350, 523, 150, 440, 650, 0, 500,
    880, 500, 440, 300, 440, 150, 880, 500, 830, 325, 784, 175, 740, 125, 698, 125,  740, 250, 0, 325,  445, 250, 622, 500, 587, 325,   554, 175,   523, 125,  466, 125,   523, 250,  0, 350,
    349, 250,  415, 500, 349, 350, 440, 125, 523, 500, 440, 375,   523, 125, 659, 650, 0, 500,349, 250,  415, 500, 349, 375, 523, 125, 440, 500,  349, 375,   523, 125, 440, 650,0, 650,
    880, 500, 440, 300, 440, 150, 880, 500, 830, 325, 784, 175, 740, 125, 698, 125,  740, 250, 0, 325,  445, 250, 622, 500, 587, 325,   554, 175,   523, 125,  466, 125,   523, 250,  0, 350,
    349, 250,  415, 500, 349, 350, 440, 125, 523, 500, 440, 375,   523, 125, 659, 650, 0, 500,349, 250,  415, 500, 349, 375, 523, 125, 440, 500,  349, 375,   523, 125, 440, 650,0, 650,
    g.songLoop],
    # Tetris
    [ g.songStart,False,200, 0, 4,
    659,2, 494, 1, 523,1, 587,2, 523, 1, 493, 1, 440, 2, 440, 1, 523,1, 659,2,587,1,523,1,493,2, 493,1,523,1,587,2,659,2,523,2,440,2,440,2,0,2,587, 1,698,1,880,2,783,1,698,1,659,2,523,1,659,2,587,1,523,1,493,2,493,1,523,1,587,2,659,2,523,2,440,2,440,2,0,2,
    329,4,261,4,293,4,246,4,261,4,220,4,207,4,246,4,329,4,261,4,293,4,246,4,261,2,329,2,440,4,415,6,0,2,
    g.songLoop]
    ]

xMargin = const (5)
yMargin = const(10)
screenL = const (5)
screenR = const(117)
screenT = const (10)
screenB = const (58)
dx = 5
vc = 3
gunW= const(5)
gunH = const (5)
invaderSize = const(4)
invaders_rows = const(5)
invaders_per_row = const(11)



def setUpInvaders ():
    y = yMargin
    while y < yMargin + (invaderSize+2) * invaders_rows :
      x = xMargin
      while x < xMargin + (invaderSize+2) * invaders_per_row :
        invaders.append(Rect(x,y,invaderSize, invaderSize))
        x = x + invaderSize + 2
      y = y + invaderSize + 2

def drawSpaceships (posture) :
  if posture :
    for i in spaceships :
      g.display.fill_rect(i.x+2, i.y, 5 , 3, 1)
      g.display.fill_rect(i.x, i.y+1, 9, 1, 1)
      g.display.fill_rect(i.x+1, i.y+1, 2, 1, 0)
  else :
    for i in spaceships :
      g.display.fill_rect(i.x+2, i.y, 5 , 3, 1)
      g.display.fill_rect(i.x, i.y+1, 9, 1, 1)
      g.display.fill_rect(i.x+5, i.y+1, 2, 1, 0)

def drawInvaders (posture) :
  if posture :
    for i in invaders :
        g.display.fill_rect(i.x, i.y, invaderSize , invaderSize, 1)
        g.display.fill_rect(i.x+1, i.y+2, invaderSize-2, invaderSize-2, 0)
  else :
      for i in invaders :
        g.display.fill_rect(i.x, i.y, invaderSize , invaderSize, 1)
        g.display.fill_rect(i.x+1, i.y, invaderSize-2, invaderSize-2, 0)
def drawGun () :
  g.display.fill_rect(gun.x+2, gun.y, 1, 2,1)
  g.display.fill_rect(gun.x, gun.y+2, gunW, 3,1)

def drawBullets () :
  for b in bullets:
    g.display.fill_rect(b.x, b.y, 1,3,1)

def drawAbullets () :
  for b in aBullets:
    g.display.fill_rect(b.x, b.y, 1,3,1)

def drawScore () :
  g.display.text('S:{}'.format (score), 0,0,1)
  g.display.text('L:{}'.format (level), 50,0,1)
  for i in range (0, life) :
    g.display.fill_rect(92 + (gunW+2)*i, 0, 1, 2,1)
    g.display.fill_rect(90 + (gunW+2)*i, 2, gunW, 3,1)



exitGame = False
demoOn = False
while not exitGame:
  gameOver = False
  usePaddle = False
  if demoOn :
      demo = True
  else :
      demo = False
  life = 3

  g.startSong(bgmBuf[g.bgm])
  #menu screen
  while True:
    g.display.fill(0)
    g.display.text('Invaders', 0, 0, 1)
    g.display.rect(90,0, g.max_vol*4+2,6,1)
    g.display.fill_rect(91,1, g.vol * 4,4,1)
    g.display.text('A Start B+L Quit', 0, 10,  1)
    if usePaddle :
        g.display.text('U Paddle', 0,20,  1)
    else :
        g.display.text('U Button', 0,20,  1)
    if demo :
        g.display.text('D AI-Player', 0,30, 1)
    else :
        g.display.text('D 1-Player', 0,30, 1)
    g.display.text('R Frame/s {}'.format(g.frameRate), 0,40, 1)
    if g.bgm :
        g.display.text('L Music {}'.format(g.bgm), 0, 50, 1)
    else :
        g.display.text('L Music Off', 0, 50, 1)
#   g.display.text('B + U/D Sound', 0, 60, 1)
    g.display.show()
    sleep_ms(10)
    g.getBtn()
    if g.setVol() :
        pass
    elif g.setFrameRate() :
        pass
    elif g.pressed(g.btnB) and g.justPressed (g.btnL) :
        exitGame = True
        gameOver= True
        break
    elif g.justPressed(g.btnA) or demoOn :
        if demo :
            demoOn = True
            g.display.fill(0)
            g.display.text('DEMO', 5, 0, 1)
            g.display.text('B+L to Stop', 5, 30, 1)
            g.display.show()
            sleep_ms(1000)
        break
    elif g.justPressed(g.btnU) :
        usePaddle =  not usePaddle
    elif g.justPressed(g.btnD) :
        demo = not demo
    elif g.justPressed(g.btnL) :
        g.bgm = 0 if g.bgm >= g.maxBgm else g.bgm + 1
        if g.bgm :
            g.startSong(bgmBuf[g.bgm])
        else :
            g.stopSong()
  #reset the game
  score = 0
  frameCount = 0
  level = 0
  loadLevel = True
  postureA = False
  postureS = False
  # Chance from 1 to 128
  aBulletChance = 0
  spaceshipChance = 1

  while not gameOver:

    lost = False
    frameCount = (frameCount + 1 ) % 120
    g.display.fill(0)

    if loadLevel :
      loadLevel = False
      spaceships = []
      invaders = []
      bullets = []
      aBullets = []
      setUpInvaders()
      gun = Rect(screenL+int((screenR-screenL)/2), screenB, gunW, gunH)
      aBulletChance = 5 + level * 5



    #generate space ships
    if g.random (0,99) < spaceshipChance and len(spaceships) < 1 :
      spaceships.append(Rect(0,9, 9, 9))

    if len(spaceships) :
      if not frameCount % 3 :
        postureS = not postureS
        # move spaceships once every 4 frames
        for i in spaceships:
          i.move(2,0)
          if i.x >= screenR :
            spaceships.remove(i)
      if not g.bgm :
          # only play sound effect if no background music
          if frameCount % 20 == 10 :
            g.playTone ('e5', 20)
          elif frameCount % 20 == 0 :
            g.playTone ('c5', 20)


    if not frameCount % 15 :
      postureA = not postureA
      # move Aliens once every 15 frames
      if not g.bgm :
          # only play sound effect if no background music
          if postureA :
              g.playSound (80, 10)
          else:
              g.playSound (120, 10)
      for i in invaders:
        if i.x > screenR or i.x < screenL :
            dx = -dx
            for alien in invaders :
              alien.move (0, invaderSize)
              if alien.y + alien.h > gun.y :
                lost = True
                loadLevel = True
                g.playTone ('f4',300)
                g.playTone ('d4',100)
                g.playTone ('c5',100)
                break
            break

      for i in invaders :
        i.move (dx, 0)


    g.getBtn()

    if g.pressed (g.btnB) and g.justReleased(g.btnL) :
        gameOver= True
        demoOn = False
        break

    if demo :

        if g.random (0,1) and len(bullets) < 2:
            bullets.append(Rect(gun.x+3, gun.y-1, 1, 3))
            g.playSound (200,5)
            g.playSound (300,5)
            g.playSound (400,5)

        if g.random(0,1) :
            vc = 3
        else :
            vc = -3

        if (vc + gun.x + gunW) < g.screenW and (vc + gun.x)  >= 0 :
           gun.move (vc, 0)

    # Real player
    elif g.pressed (g.btnA | g.btnB) and len(bullets) < 2:
      bullets.append(Rect(gun.x+3, gun.y-1, 1, 3))
      g.playSound (200,5)
      g.playSound (300,5)
      g.playSound (400,5)
    # move gun


    elif usePaddle :
      gun.x = int(g.getPaddle() / (1024/(screenR-screenL)))
      gun.x2 = gun.x+gunW-1
    else :
      if g.pressed (g.btnL) and gun.x - 3 > 0 :
        vc = -3
      elif g.pressed(g.btnR) and (gun.x + 3 + gunW ) < g.screenW :
        vc = 3
      else :
        vc = 0
      gun.move (vc, 0)

    # move bullets

    for b in bullets:
      b.move(0,-3)
      if b.y < 0 :
        bullets.remove(b)
      else :
        for i in invaders:
          if i.colliderect(b) :
            invaders.remove(i)
            bullets.remove(b)
            score +=1
            g.playTone ('c6',10)
            break
        for i in spaceships :
          if i.colliderect(b) :
            spaceships.remove(i)
            bullets.remove(b)
            score +=10
            g.playTone ('b4',30)
            g.playTone ('e5',10)
            g.playTone ('c4',30)
            break

    # Launch Alien bullets
    for i in invaders:
      if g.random (0,1000) * len (invaders) * 10 < aBulletChance and len(aBullets) < 3 :
        aBullets.append(Rect(i.x+2, i.y, 1, 3))

    # move Alien bullets
    for b in aBullets:
      b.move(0,3)
      if b.y > g.screenH  :
        aBullets.remove(b)
      elif b.colliderect(gun) :
        lost = True
        #print ('{} {} {} {} : {} {} {} {}'.format(b.x,b.y,b.x2,b.y2,gun.x,gun.y,gun.x2,gun.y2))
        aBullets.remove(b)
        g.playTone ('c5',30)
        g.playTone ('e4',30)
        g.playTone ('b4',30)
        break

    drawSpaceships (postureS)
    drawInvaders (postureA)
    drawGun()
    drawBullets()
    drawAbullets()
    drawScore()


    if len(invaders) == 0 :
      level += 1
      loadLevel = True
      g.playTone ('c4',100)
      g.playTone ('d4',100)
      g.playTone ('e4',100)
      g.playTone ('f4',100)
      g.playTone ('g4',100)
      g.bgm = 0 if g.bgm >= g.maxBgm else g.bgm + 1
      if g.bgm :
        g.startSong(bgmBuf[g.bgm])

    if lost :
      lost = False;
      life -= 1
      g.playTone ('f4',100)
      g.playTone ('g4',100)
      g.playTone ('c4',100)
      g.playTone ('d4',100)
      sleep_ms (1000)
      if life < 0 :
        gameOver = True

    if gameOver :
      g.display.fill_rect (3, 15, 120,20,0)
      g.display.text ("GAME OVER", 5, 20, 1)
      g.playTone ('b4',300)
      g.playTone ('e4',100)
      g.playTone ('c4',100)
      g.display.show()
      sleep_ms(2000)

    g.display_and_wait()

g.deinit()
if g.ESP32 :
      del sys.modules["gameESP"]
gc.collect()
