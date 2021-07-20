# ----------------------------------------------------------
# snake.py Game
## Use common game module "gameESP.py" for ESP8266  or ESP32
# by Billy Cheung  2019 10 26import gc
import sys
import gc
gc.collect()
# # print (gc.mem_free())
#import network
import utime
from utime import sleep_ms
# all dislplay, buttons, paddle, sound logics are in gameESP.mpy module
from gameESP import *
g=gameESP()

SNAKE_SIZE    = 4
SNAKE_LENGTH  = 4
SNAKE_EXTENT  = 2
COLS          = 0
ROWS          = 0
OX            = 0
OY            = 0
COLOR_BG      = 0
COLOR_WALL    = 1
COLOR_SNAKE   = 1
COLOR_APPLE   = 1
COLOR_SCORE   = 1
COLOR_LOST_BG = 1
COLOR_LOST_FG = 0
MODE_MENU     = 0
MODE_START    = 1
MODE_READY    = 2
MODE_PLAY     = 3
MODE_LOST     = 4
MODE_GAMEOVER = 5
MODE_EXIT     = 6


# ----------------------------------------------------------
# Game management
# ----------------------------------------------------------

def tick():
    handleButtons()

    if not game['refresh']:
        clearSnakeTail()
    if game['mode'] == MODE_PLAY:
        moveSnake()
        if game['refresh']:
            game['refresh'] = False
        if didSnakeEatApple():
            g.playTone('d6', 20)
            g.playTone('c5', 20)
            g.playTone('f4', 20)
            game['score'] += 1
            game['refresh'] = True
            extendSnakeTail()
            spawnApple()
        if didSnakeBiteItsTail() or didSnakeHitTheWall():
            g.playTone('c4', 500)
            game['mode'] = MODE_LOST
            game['refresh'] = True
    elif game['mode'] == MODE_LOST:
        # print ('LOST')
        game['life'] -= 1

        if game['life'] <= 0 :
            game['mode'] = MODE_GAMEOVER
        else :
            game['mode'] = MODE_START
        # print (game['mode'])
        sleep_ms(1000)
    elif game['mode'] == MODE_GAMEOVER:
        # print('gameOver')
        game['mode'] = MODE_MENU
        g.playTone('c4', 100)
        g.playTone('e4', 100)
        g.playTone('g4', 100)
        sleep_ms(1000)
    elif game['mode'] == MODE_MENU:
        # print('Menu')
        pass
    elif game['mode'] == MODE_START:
        # print ("======================")
        game['refresh'] = True
        resetSnake()
        spawnApple()
        game['mode'] = MODE_READY
        game['score'] = 0
        game['time']  = 0
        if game['demo'] :
            game['demoOn'] = True
    elif game['mode'] == MODE_READY:
        # print ("READY")
        game['refresh'] = False
        moveSnake()
        if snakeHasMoved():
            g.playTone('c5', 100)
            game['mode'] = MODE_PLAY
    elif game['mode'] == MODE_EXIT:
        return
    else:
        handleButtons()

    draw()
    game['time'] += 1


def spawnApple():
    apple['x'] = g.random (1, COLS - 2)
    apple['y'] = g.random (1, ROWS - 2)

def smart():
    if g.random(0,199) < 200 :
        return True
        return False

def noCrash (x,y):
    h = snake['head']
    n = snake['len']
    # hit walls ?
    if x < 0 or x > COLS-1 or y < 0 or y > ROWS-1:
        return False
    # hit snake body ?
    for i in range(n):
        if i !=h and snake['x'][i] == x and snake['y'][i] == y:
            return False
        i = (i + 1) % n
    return True

def handleButtons():
  global SNAKE_SIZE
  g.getBtn()

  if game['mode'] == MODE_MENU :
    sleep_ms(10)
    if g.setVol() :
        pass
    elif g.justPressed(g.btnU):
        SNAKE_SIZE = 4 if SNAKE_SIZE == 2 else 6 if SNAKE_SIZE == 4 else 2
        g.playTone('c5', 100)
    elif g.justPressed(g.btnR) :
        g.playTone('d5', 100)
        if g.pressed(g.btnB) :
            g.frameRate = g.frameRate - 5 if g.frameRate > 5 else 100
        else :
            g.frameRate = g.frameRate + 5 if g.frameRate < 100 else 5
    elif g.justPressed(g.btnD):
        game['demo'] = not game['demo']
        g.playTone('e5', 100)
    elif g.justReleased(g.btnA) or game['demoOn'] :
        game['mode'] = MODE_START
        game['life'] = 3
        game['reset'] = True
        g.playTone('f5', 100)
        if game['demo'] :
            g.display.fill(0)
            g.display.text('DEMO', 5, 0, 1)
            g.display.text('B to Stop', 5, 30, 1)
            g.display.show()
            sleep_ms(1000)

    elif g.pressed(g.btnL) :
        game['mode'] = MODE_EXIT
        g.playTone('g5', 100)
  else :
    if game['demo'] :
        if g.justReleased (g.btnB):
            game['demoOn'] = False
            game['mode'] = MODE_GAMEOVER
            g.playTone('g5', 100)
            g.playTone('f5', 100)
            g.playTone('e5', 100)

        #get snake's head position

        h = snake['head']
        Hx = snake['x'][h]
        Hy = snake['y'][h]
        #get snake's neck position
        # # print ("h={} {}:{}  C={} R={}".format (h,Hx,Hy, COLS, ROWS))

        # move closer to the apple, if smart enough
        if Hx < apple['x'] and smart() and noCrash(Hx+1, Hy):
            dirSnake(1, 0)
            # # print ("A")
        elif Hx > apple['x'] and smart() and noCrash(Hx-1, Hy):
            dirSnake(-1, 0)
            # # print ("B")
        elif Hy < apple['y'] and smart() and noCrash(Hx, Hy+1):
            dirSnake(0, 1)
            # # print ("C")
        elif Hy > apple['y'] and smart() and noCrash(Hx, Hy-1):
            dirSnake(0, -1)
            # # print ("D")
        elif  noCrash(Hx+1, Hy):
            dirSnake(1, 0)
            # # print ("E")
        elif noCrash(Hx-1, Hy):
            dirSnake(-1, 0)
            # # print ("F")
        elif noCrash(Hx, Hy+1):
            dirSnake(0, 1)
            # # print ("G")
        elif noCrash(Hx, Hy-1):
            dirSnake(0, -1)
            # # print ("H")
    else :
        if g.justPressed (g.btnL):
            dirSnake(-1, 0)
        elif g.justPressed(g.btnR):
            dirSnake(1, 0)
        elif g.justPressed(g.btnU):
            dirSnake(0, -1)
        elif g.justPressed(g.btnD):
            dirSnake(0, 1)
        elif g.justPressed(g.btnA):
            if snake['vx'] == 1:
                dirSnake(0, 1)
            elif snake['vx'] == -1:
                dirSnake(0, -1)
            elif snake['vy'] == 1:
                dirSnake(-1, 0)
            elif snake['vy'] == -1:
                dirSnake(1, 0)
            elif snake['vx']==0 and snake['vy']==0 :
                dirSnake(0, 1)
        elif g.justPressed(g.btnB):
            if snake['vx'] == 1:
                dirSnake(0, -1)
            elif snake['vx'] == -1:
                dirSnake(0, 1)
            elif snake['vy'] == 1:
                dirSnake(1, 0)
            elif snake['vy'] == -1:
                dirSnake(-1, 0)
            elif snake['vx']==0 and snake['vy']==0 :
                dirSnake(1, 0)




# ----------------------------------------------------------
# Snake management
# ----------------------------------------------------------

def resetSnake():
    global COLS, ROWS, OX, OY
    COLS          = (g.screenW  - 4) // SNAKE_SIZE
    ROWS          = (g.screenH - 4) // SNAKE_SIZE
    OX            = (g.screenW  - COLS * SNAKE_SIZE) // 2
    OY            = (g.screenH - ROWS * SNAKE_SIZE) // 2
    x = COLS // SNAKE_SIZE
    y = ROWS // SNAKE_SIZE
    snake['vx'] = 0
    snake['vy'] = 0
    # print (game['reset'])
    if game['reset'] :
        game['reset'] = False
        s = SNAKE_LENGTH
    else :
        s = snake['len']

    snake['x'] = []
    snake['y'] = []
    for _ in range(s):
        snake['x'].append(x)
        snake['y'].append(y)
        snake['head'] = s - 1
        snake['len']  = s


def dirSnake(dx, dy):
    snake['vx'] = dx
    snake['vy'] = dy

def moveSnake():
    h = snake['head']
    x = snake['x'][h]
    y = snake['y'][h]
    h = (h + 1) % snake['len']
    snake['x'][h] = x + snake['vx']
    snake['y'][h] = y + snake['vy']
    snake['head'] = h

def snakeHasMoved():
    return snake['vx'] or snake['vy']

def didSnakeEatApple():
    h = snake['head']
    return snake['x'][h] == apple['x'] and snake['y'][h] == apple['y']

def extendSnakeTail():
    i = snake['head']
    n = snake['len']
    i = (i + 1) % n
    x = snake['x'][i]
    y = snake['y'][i]
    for _ in range(SNAKE_EXTENT):
        snake['x'].insert(i, x)
        snake['y'].insert(i, y)
    snake['len'] += SNAKE_EXTENT

def didSnakeBiteItsTail():
    h = snake['head']
    n = snake['len']
    x = snake['x'][h]
    y = snake['y'][h]
    i = (h + 1) % n
    for _ in range(n-1):
        if snake['x'][i] == x and snake['y'][i] == y:
            return True
        i = (i + 1) % n
    return False



def didSnakeHitTheWall():
    h = snake['head']
    x = snake['x'][h]
    y = snake['y'][h]
    return x < 0 or x == COLS or y < 0 or y == ROWS

# ----------------------------------------------------------
# Graphic display
# ----------------------------------------------------------

def draw():
    if game['mode'] == MODE_MENU:
        drawGameMenu()
    else :
        if game['mode'] == MODE_LOST:
            if game['life'] == 0 :
                drawGameover()
        elif game['refresh']:
            clearScreen()
            drawWalls()
            drawSnake()
        else:
            drawSnakeHead()
        drawScore()
        drawApple()
    g.display.show()

def clearScreen():
    color = COLOR_LOST_BG if game['mode'] == MODE_LOST else COLOR_BG
    g.display.fill(color)

def drawGameMenu():
    global SNAKE_SIZE
    clearScreen()
    g.display.text('Snake', 0, 0, 1)
    g.display.rect(90,0, g.max_vol*4+2,6,1)
    g.display.fill_rect(91,1, g.vol * 4,4,1)

    g.display.text("A START   U+D EXIT",0,10,1)
    if game['demo'] :
        g.display.text('D AI-Player', 0,20, 1)
    else :
        g.display.text('D 1-PLAYER', 0,20, 1)
    g.display.text("U SIZE {}".format(SNAKE_SIZE),0,30,1)
    g.display.text("R FRAME {}".format(g.frameRate),0,40,1)
    g.display.text("B + U/D VOLUME",0,50,1)


def drawGameover():
    g.display.fill_rect(20,20,100,30,0)
    g.display.text("GAME OVER",20,20,1)


def drawWalls():
    color = COLOR_LOST_FG if game['mode'] == MODE_LOST else COLOR_WALL
    g.display.rect(0, 0, g.screenW, g.screenH,color)

def debugSnake():
    n = snake['len']
    i = snake['head']
    for _ in range(n):

        # # print(snake['x'][i], snake['y'][i])
        if (i - 1) < 0 :
            i=n-1
        else :
            i-=1


def drawSnake():
    isTimeToBlink = game['time'] % 4 < 2
    color = COLOR_LOST_FG if game['mode'] == MODE_LOST and isTimeToBlink else COLOR_SNAKE
    h = snake['head']
    n = snake['len']
    for i in range(n):
        if i == h :
          drawBox(snake['x'][i], snake['y'][i], color)
        else :
          drawDot(snake['x'][i], snake['y'][i], color)

def drawSnakeHead():
    h = snake['head']
    drawBox(snake['x'][h], snake['y'][h], COLOR_SNAKE)

def clearSnakeTail():
    h = snake['head']
    n = snake['len']
    t = (h + 1) % n
    drawDot(snake['x'][t], snake['y'][t], COLOR_BG)

def drawScore():
    g.display.text('S {}'.format(game['score'] ),5,0,1)
    g.display.text('L {}'.format( game['life'] ),80,0,1)

def drawApple():
    drawBox(apple['x'], apple['y'], COLOR_APPLE)
    g.display.rect(OX + apple['x']* SNAKE_SIZE + int(SNAKE_SIZE/2), OY + apple['y'] * SNAKE_SIZE-1, 1,1, COLOR_APPLE)

def drawDot(x, y, color):
    g.display.fill_rect(OX + x * SNAKE_SIZE, OY + y * SNAKE_SIZE, SNAKE_SIZE, SNAKE_SIZE,color)

def drawBox(x, y, color):
    g.display.rect(OX + x * SNAKE_SIZE, OY + y * SNAKE_SIZE, SNAKE_SIZE, SNAKE_SIZE,color)


# ----------------------------------------------------------
# Initialization
# ----------------------------------------------------------


game = {
    'mode':    MODE_MENU,
    'score':   0,
    'life':    0,
    'time':    0,
    'refresh': True,
    'reset':   True,
    'demo':    False,
    'demoOn' : False
}

snake = {
    'x':    [],
    'y':    [],
    'head': 0,
    'len':  0,
    'vx':   0,
    'vy':   0
}

apple = { 'x': 0, 'y': 0 }

# ----------------------------------------------------------
# Main loop
# ----------------------------------------------------------
while game['mode'] != MODE_EXIT :
  tick()
  g.display_and_wait()

if g.ESP32 :
    g.deinit()
    del sys.modules["gameESP"]
gc.collect()
