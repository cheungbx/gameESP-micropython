# tetris.py
#
# ESP8266 (node MCU D1 mini)  micropython game for Tetris
# by Billy Cheung  2019 08 31
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
# n.c.   - D6  (=GPIO13=HMOSI)
#
# GPIO5    D1——   On to read ADC for Btn
# GPIO4    D2——   On to read ADC for Paddle
#
# buttons   A0
# A0 VCC-9K-U-9K-L-12K-R-9K-D-9K-A-12K-B-9K-GND
#
import gc
import sys
gc.collect()
import utime
from utime import sleep_ms
#import network
from math import sqrt
# all dislplay, buttons, paddle, sound logics are in gameESP.mpy module
from gameESP import *
g=gameESP()

g.frameRate = 30
g.bgm = 3
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

# size = width, height = 200, 400
size = width, height = 30, 60
# color = {'black': (0, 0, 0), 'white':(255, 255, 255)}
color ={'black': 0, 'white':1}
sqrsize = 3
occupied_squares = []
top_of_screen = (2, 2)
top_x, top_y = top_of_screen[0], top_of_screen[1]
num_block = 4
pen_size = 1
mov_delay, r_delay = 200, 50
board_centre = int(width/2)+2
no_move = 0
score = 0
life = 0
shape_blcks = []
shape_name = ""
new_shape_blcks = []
new_shape_name = ""
occupied_squares = []

def reset_board():
    global shape_blcks, shape_name, occupied_squares
    shape_blcks = []
    shape_name = ""
    occupied_squares = []
    g.display.fill(0)
    g.display.rect(top_x-1, top_y-1, width+2, height+2,1)

def drawScore () :
  global score, life
  g.display.text('S:{}'.format (score), 40,0,1)
  g.display.text('L:{}'.format (life),  90,0,1)

def draw_shape():
    '''this draws list of blocks or a block to the background and blits
    background to screen'''

    if isinstance(shape_blcks,list):
        for blck in shape_blcks:
            g.display.rect(blck[0], blck[1], sqrsize, sqrsize, 1)
    else:
        g.display.rect(shape_blcks[0], shape_blcks[1], sqrsize, sqrsize,1)

def row_filled(row_no):
    global occupied_squares
    '''check if a row is fully occupied by a shape block'''

    for x_coord in range(top_x, width+top_x, sqrsize):

        if (x_coord, row_no) in occupied_squares:
            continue
        else:
            return False
    return True


def delete_row(row_no):
    '''removes all squares on a row from the occupied_squares list and then
    moves all square positions which have y-axis coord less than row_no down
    board'''
    global occupied_squares
    g.display.fill(0)
    g.display.rect(top_x-1, top_y-1, width+2, height+2,1)
    new_buffer = []
    x_coord, y_coord = 0, 1
    for sqr in occupied_squares:
        if sqr[y_coord] != row_no:
            new_buffer.append(sqr)
    occupied_squares = new_buffer
    for index in range(len(occupied_squares)):
        if occupied_squares[index][y_coord] < row_no:
            occupied_squares[index] = (occupied_squares[index][x_coord],
                                    occupied_squares[index][y_coord] + sqrsize)
    for sqr in occupied_squares:
        g.display.rect(sqr[x_coord], sqr[y_coord], sqrsize, sqrsize, 1)

def move(direction):
    global shape_blcks
    '''input:- list of blocks making up a tetris shape
    output:- list of blocks making up a tetris shape
    function moves the input list of blocks that make up shape and then checks
    that the  list of blocks are all in positions that are valide. position is
    valid if it has not been occupied previously and is within the tetris board.
    If move is successful, function returns the moved shape and if move is not
    possible, function returns a false'''
    directs = {'down':(no_move, sqrsize), 'left':(-sqrsize, no_move),
        'right':(sqrsize, no_move), 'pause': (no_move, no_move)}
    delta_x, delta_y = directs[direction]

    for index in range(num_block):
        shape_blcks[index] = [shape_blcks[index][0] + delta_x, shape_blcks[index][1]+ delta_y]

    if legal(shape_blcks):
        for index in range(num_block):
            #erase previous positions of block
            g.display.fill_rect(shape_blcks[index][0]-delta_x, shape_blcks[index][1]-delta_y, sqrsize, sqrsize, 0)
        return True
    else:
        # undo the move, as it's not legal (being blocked by existing blocks)
        for index in range(num_block):
            shape_blcks[index] = [shape_blcks[index][0]-delta_x, shape_blcks[index][1]- delta_y]
        return False


def legal(blcks):
    '''input: list of shape blocks
    checks whether a shape is in a legal portion of the board as defined in the
    doc of 'move' function'''

    for index in range(num_block):
        new_x = blcks[index][0]
        new_y = blcks[index][1]
        if (((new_x, new_y) in occupied_squares or new_y >= height) or
            (new_x >= width or new_x < top_x)):
            return False

    return True


def create_newshape(start_x=board_centre, start_y=2):
    '''A shape is a list of four rectangular blocks.
    Input:- coordinates of board at which shape is to be created
    Output:- a list of the list of the coordinates of constituent blocks of each
    shape relative to a reference block and shape name. Reference block  has
    starting coordinates of start_x and start_y. '''
    global shape_blcks, shape_name, new_shape_blcks, new_shape_name
    shape_blcks = new_shape_blcks
    shape_name = new_shape_name

    shape_names = ['S', 'O', 'I', 'L', 'T']
    shapes = {'S':[(start_x + 1*sqrsize, start_y + 2*sqrsize),
        (start_x, start_y), (start_x, start_y + 1*sqrsize),(start_x + 1*sqrsize,
                                                    start_y + 1*sqrsize)],

        'O':[(start_x + 1*sqrsize, start_y + 1*sqrsize), (start_x, start_y),
            (start_x, start_y + 1*sqrsize), (start_x + 1*sqrsize, start_y)],

        'I':[(start_x, start_y + 3*sqrsize), (start_x, start_y),
            (start_x, start_y + 2*sqrsize), (start_x, start_y + 1*sqrsize)],

        'L':[(start_x + 1*sqrsize, start_y + 2*sqrsize), (start_x, start_y),
            (start_x, start_y + 2*sqrsize), (start_x, start_y + 1*sqrsize)],

        'T':[(start_x + 1*sqrsize, start_y + 1*sqrsize),(start_x, start_y),
            (start_x - 1*sqrsize, start_y + 1*sqrsize),(start_x,
                                                        start_y + 1*sqrsize)]
        }
    a_shape = g.random(0, 4)
    new_shape_blcks = shapes[shape_names[a_shape]]
    new_shape_name = shape_names[a_shape]

    g.display.fill_rect(40, top_y+15, 60, 40,0 )
    if isinstance(new_shape_blcks, list):
        for blck in new_shape_blcks:
            g.display.rect(blck[0]+40, blck[1]+15, sqrsize, sqrsize, 1)
    else:
        g.display.rect(new_shape_blcks[0+40], new_shape_blcks[1]+15, sqrsize, sqrsize,1)

def rotate():
    '''input:- list of shape blocks
    ouput:- list of shape blocks
    function tries to rotate ie change orientation of blocks in the shape
    and this applied depending on the shape for example if a 'O' shape is passed
    to this function, the same shape is returned because the orientation of such
    shape cannot be changed according to tetris rules'''
    if shape_name == 'O':
        return shape_blcks
    else:
        #global no_move, occupied_squares, background

        ref_shape_ind = 3 # index of block along which shape is rotated
        start_x, start_y = (shape_blcks[ref_shape_ind][0],
                            shape_blcks[ref_shape_ind][1])
        save_blcks = shape_blcks
        Rshape_blcks = [(start_x + start_y-shape_blcks[0][1],
                        start_y - (start_x - shape_blcks[0][0])),
        (start_x + start_y-shape_blcks[1][1],
         start_y - (start_x - shape_blcks[1][0])),
        (start_x + start_y-shape_blcks[2][1],
         start_y - (start_x - shape_blcks[2][0])),
        (shape_blcks[3][0], shape_blcks[3][1])]

        if legal(Rshape_blcks):
            for index in range(num_block): # erase the previous shape
                g.display.fill_rect(shape_blcks[index][0], shape_blcks[index][1],sqrsize, sqrsize, 0)
            return Rshape_blcks
        else:
            return shape_blcks

exitGame = False
demo = False
while not exitGame:

  g.startSong(bgmBuf[g.bgm])

  #menu screen
  while True:
    g.display.fill(0)
    g.display.text('Tetris', 0, 0, 1)
    g.display.rect(90,0, g.max_vol*4+2,6,1)
    g.display.fill_rect(91,1, g.vol * 4,4,1)
    g.display.text('A Start B+L Quit', 0, 10,  1)
    if demo :
        g.display.text('D AI-Player', 0,20, 1)
    else :
        g.display.text('D 1-Player', 0,20, 1)
    g.display.text('R Frame/s {}'.format(g.frameRate), 0,30, 1)
    if g.bgm :
        g.display.text('L Music {}'.format(g.bgm), 0, 40, 1)
    else :
        g.display.text('L Music Off', 0, 40, 1)
    g.display.text('B + U/D Loudness', 0, 50, 1)
    g.display.show()

    g.getBtn()
    if g.setVol() :
        pass
    elif g.setFrameRate() :
        pass
    elif g.pressed(g.btnB) and g.justPressed(g.btnL) :
        exitGame = True
        gameOver= True
        break
    elif g.justPressed(g.btnA) :
        if demo :
            g.display.fill(0)
            g.display.text('DEMO', 5, 0, 1)
            g.display.text('B to Stop', 5, 30, 1)
            g.display.show()
            sleep_ms(1000)
        break
    elif g.justPressed(g.btnD) :
        demo = not demo
    elif g.justPressed(g.btnL) :
        g.bgm = 0 if g.bgm >= g.maxBgm else g.bgm + 1
        if g.bgm :
            g.startSong(bgmBuf[g.bgm])
        else :
            g.stopSong()
    sleep_ms(10)


  life = 3
  Score = 0
  reset_board()
  create_newshape()
  gameOver = False
  # game loop
  while not gameOver:
    drawScore()
    create_newshape()
    extramoves = 3
    l_of_blcks_ind = blck_x_axis = 0
    shape_name_ind = blck_y_axis = 1

    move_dir = 'down' #default move direction
    game = 'playing'  #default game state play:- is game paused or playing

    if legal(shape_blcks):
        draw_shape()
    else:
        life -= 1
        if life <= 0 :
            gameOver = True
            break
        else :
           g.playTone('g4', 100)
           g.playTone('e4', 100)
           g.playTone('c4', 100)
           g.display.show()
           sleep_ms(2000)
           reset_board()
           g.bgm = 0 if g.bgm >= g.maxBgm else g.bgm + 1
           if g.bgm :
                g.startSong(bgmBuf[g.bgm])
           continue

    while True:
        mov_delay = 150
        move_dir  = 'down'
        g.getBtn()
        if game == 'paused':
            if g.justPressed(g.btnB) :
                g.playTone('c4', 100)
                g.playTone('e4', 100)
                game = 'playing'
        else:
            if g.justPressed(g.btnB) :
                g.playTone('e4', 100)
                g.playTone('f4', 100)
                game = 'paused'
                move_dir  = 'pause'
            elif g.pressed(g.btnU) and g.pressed(g.btnD) :
                gameOver = True
                break
            elif g.pressed(g.btnD) :
                mov_delay = 10
                move_dir  = 'down'
            elif g.justPressed(g.btnA | g.btnU) :
                shape_blcks = rotate()
                draw_shape()
                g.display.show()
                sleep_ms(r_delay)
                continue
            elif g.pressed(g.btnL | g.btnR):
                move_dir = 'left' if g.pressed(g.btnL) else 'right'
                mov_delay = 50
                move (move_dir)
                draw_shape()
                g.display.show()
                sleep_ms(mov_delay)
                continue

            moved = move( move_dir)
            draw_shape()
            sleep_ms(mov_delay)

            '''if block did not move and the direction for movement is down
            then shape has come to rest so we can exit loop and then a new
            shape is generated. if direction for movement is sideways and
            block did not move it should be moved down rather'''
            if not moved and move_dir == 'down':
              extramoves = extramoves - 1
              if extramoves <= 0 :
                for block in shape_blcks:
                    occupied_squares.append((block[0],block[1]))
                break


            draw_shape()
            g.display.show()

            for row_no in range (height - sqrsize + top_y, 0, -sqrsize):
                if row_filled(row_no):
                    delete_row(row_no)
                    score+=10
                    drawScore()
                    g.display.show()
                    g.playTone('c4', 100)
                    g.playTone('e4', 100)
                    g.playTone('g4', 100)
                    g.playTone('e4', 100)
                    g.playTone('c4', 100)
            g.display.show()

  if gameOver :
       g.display.fill_rect(20,20, 80, 35,0)
       g.display.text("Game Over", 30,30,1)
       g.display.show()
       g.playTone('c4', 100)
       g.playTone('e4', 100)
       g.playTone('g4', 100)
       sleep_ms(2000)
if g.ESP32 :
    g.deinit()
    del sys.modules["gameESP"]
gc.collect()
