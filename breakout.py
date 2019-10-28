# ----------------------------------------------------------
#  Breakout.py  Game
# Use common game module "gameESP.py" for ESP8266  or ESP32
# by Billy Cheung  2019 10 26
#
import gc
import sys
gc.collect()
print (gc.mem_free())
import network
import utime
from utime import sleep_ms,ticks_ms, ticks_us, ticks_diff
from machine import Pin, SPI, PWM, ADC
from math import sqrt
import gameESP
# all dislplay, buttons, paddle, sound logics are in gameESP.mpy module
from gameESP import gameESP, Rect
g=gameESP()
paddle_width = 22
frameRate = 30

class Ball(object):
    """Ball."""

    def __init__(self, x, y, x_speed, y_speed, display, width=2, height=2,
                 frozen=False):
        self.x = x
        self.y = y
        self.x2 = x + width - 1
        self.y2 = y + height - 1
        self.prev_x = x
        self.prev_y = y
        self.width = width
        self.height = height
        self.center = width // 2
        self.max_x_speed = 3
        self.max_y_speed = 3
        self.frozen = frozen
        self.display = display
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.x_speed2 = 0.0
        self.y_speed2 = 0.0
        self.created = ticks_ms()

    def clear(self):
        """Clear ball."""
        self.display.fill_rect(self.x, self.y, self.width, self.height, 0)

    def clear_previous(self):
        """Clear prevous ball position."""
        self.display.fill_rect(self.prev_x, self.prev_y,
                                self.width, self.height, 0)

    def draw(self):
        """Draw ball."""
        self.clear_previous()
        self.display.fill_rect( self.x, self.y,
                                 self.width, self.height,1)

    def set_position(self, paddle_x, paddle_y, paddle_x2, paddle_center):
        bounced = False
        """Set ball position."""
        self.prev_x = self.x
        self.prev_y = self.y
        # Check if frozen to paddle
        if self.frozen:
            # Freeze ball to top center of paddle
            self.x = paddle_x + (paddle_center - self.center)
            self.y = paddle_y - self.height
            if ticks_diff(ticks_ms(), self.created) >= 2000:
                # Release frozen ball after 2 seconds
                self.frozen = False
            else:
                return
        self.x += int(self.x_speed) + int(self.x_speed2)
        self.x_speed2 -= int(self.x_speed2)
        self.x_speed2 += self.x_speed - int(self.x_speed)

        self.y += int(self.y_speed) + int(self.y_speed2)
        self.y_speed2 -= int(self.y_speed2)
        self.y_speed2 += self.y_speed - int(self.y_speed)

        # Bounces off walls
        if self.y < 10:
            self.y = 10
            self.y_speed = -self.y_speed
            bounced = True
        if self.x + self.width >= 125:
            self.x = 125 - self.width
            self.x_speed = -self.x_speed
            bounced = True
        elif self.x < 3:
            self.x = 3
            self.x_speed = -self.x_speed
            bounced = True

        # Check for collision with Paddle
        if (self.y2 >= paddle_y and
           self.x <= paddle_x2 and
           self.x2 >= paddle_x):
            # Ball bounces off paddle
            self.y = paddle_y - (self.height + 1)
            ratio = ((self.x + self.center) -
                     (paddle_x + paddle_center)) / paddle_center
            self.x_speed = ratio * self.max_x_speed
            self.y_speed = -sqrt(max(1, self.max_y_speed ** 2 - self.x_speed ** 2))
            bounced = True

        self.x2 = self.x + self.width - 1
        self.y2 = self.y + self.height - 1
        return bounced


class Brick(object):
    """Brick."""

    def __init__(self, x, y, color, display, width=12, height=3):
        """Initialize brick.

        Args:
            x, y (int):  X,Y coordinates.
            color (string):  Blue, Green, Pink, Red or Yellow.
            display (SSD1351): OLED g.display.
            width (Optional int): Blick width
            height (Optional int): Blick height
        """
        self.x = x
        self.y = y
        self.x2 = x + width - 1
        self.y2 = y + height - 1
        self.center_x = x + (width // 2)
        self.center_y = y + (height // 2)
        self.color = color
        self.width = width
        self.height = height
        self.display = display
        self.draw()

    def bounce(self, ball_x, ball_y, ball_x2, ball_y2,
               x_speed, y_speed,
               ball_center_x, ball_center_y):
        """Determine bounce for ball collision with brick."""
        x = self.x
        y = self.y
        x2 = self.x2
        y2 = self.y2
        center_x = self.center_x
        center_y = self.center_y
        if ((ball_center_x > center_x) and
           (ball_center_y > center_y)):
            if (ball_center_x - x2) < (ball_center_y - y2):
                y_speed = -y_speed
            elif (ball_center_x - x2) > (ball_center_y - y2):
                x_speed = -x_speed
            else:
                x_speed = -x_speed
                y_speed = -y_speed
        elif ((ball_center_x > center_x) and
              (ball_center_y < center_y)):
            if (ball_center_x - x2) < -(ball_center_y - y):
                y_speed = -y_speed
            elif (ball_center_x - x2) > -(ball_center_y - y):
                x_speed = -x_speed
            else:
                x_speed = -x_speed
                y_speed = -y_speed
        elif ((ball_center_x < center_x) and
              (ball_center_y < center_y)):
            if -(ball_center_x - x) < -(ball_center_y - y):
                y_speed = -y_speed
            elif -(ball_center_x - x) > -(ball_center_y - y):
                y_speed = -y_speed
            else:
                x_speed = -x_speed
                y_speed = -y_speed
        elif ((ball_center_x < center_x) and
              (ball_center_y > center_y)):
            if -(ball_center_x - x) < (ball_center_y - y2):
                y_speed = -y_speed
            elif -(ball_center_x - x) > (ball_center_y - y2):
                x_speed = -x_speed
            else:
                x_speed = -x_speed
                y_speed = -y_speed

        return [x_speed, y_speed]

    def clear(self):
        """Clear brick."""
        self.display.fill_rect(self.x, self.y, self.width, self.height, 0)

    def draw(self):
        """Draw brick."""
        self.display.rect(self.x, self.y, self.width, self.height, 1)


class Life(object):
    """Life."""

    def __init__(self, index, display, width=4, height=6):
        """Initialize life.

        Args:
            index (int): Life number (1-based).
            display (SSD1351): OLED g.display.
            width (Optional int): Life width
            height (Optional int): Life height
        """
        margin = 5
        self.display = display
        self.x = g.display.width - (index * (width + margin))
        self.y = 0
        self.width = width
        self.height = height
        self.draw()

    def clear(self):
        """Clear life."""
        self.display.fill_rect(self.x, self.y, self.width, self.height, 0)

    def draw(self):
        """Draw life."""
        self.display.fill_rect(self.x, self.y,
                                 self.width, self.height,1)


class Paddle(object):
    """Paddle."""

    def __init__(self, display, width, height):
        """Initialize paddle.

        Args:
            display (SSD1306): OLED g.display.
            width (Optional int): Paddle width
            height (Optional int): Paddle height
        """
        self.x = 55
        self.y = 60
        self.x2 = self.x + width - 1
        self.y2 = self.y + height - 1
        self.width = width
        self.height = height
        self.center = width // 2
        self.display = display

    def clear(self):
        """Clear paddle."""
        self.display.fill_rect(self.x, self.y, self.width, self.height, 0)


    def draw(self):
        """Draw paddle."""
        self.display.fill_rect(self.x, self.y,self.width, self.height,1)

    def h_position(self, x):
        """Set paddle position.

        Args:
            x (int):  X coordinate.
        """
        new_x = max(3,min (x, 125-self.width))
        if new_x != self.x :  # Check if paddle moved
            prev_x = self.x  # Store previous x position
            self.x = new_x
            self.x2 = self.x + self.width - 1
            self.y2 = self.y + self.height - 1
            self.draw()
            # Clear previous paddle
            if x > prev_x:
                self.display.fill_rect(prev_x, self.y,
                                        x - prev_x, self.height, 0)
            else:
                self.display.fill_rect(x + self.width, self.y,
                                        (prev_x + self.width) -
                                        (x + self.width),
                                        self.height, 0)
        else:
            self.draw()

class Score(object):
    """Score."""

    def __init__(self, display):
        """Initialize score.

        Args:
            display (SSD1306): OLED g.display.
        """
        margin = 5
        self.display = display
        self.display.text('S:', margin, 0, 1)
        self.x = 20 + margin
        self.y = 0
        self.value = 0
        self.draw()

    def draw(self):
        """Draw score value."""
        self.display.fill_rect(self.x, self.y, 20, 8, 0)
        self.display.text( str(self.value), self.x, self.y,1)

    def game_over(self):
        """Display game_over."""
        self.display.text('GAME OVER', (self.display.width // 2) - 30,
                               int(self.display.height / 1.5), 1)

    def increment(self, points):
        """Increase score by specified points."""
        self.value += points
        self.draw()

def load_level(level, display) :
    global frameRate
    if demo :
      frameRate = 60 + level * 10
    else :
      frameRate = 25 + level * 5
    bricks = []
    for row in range(12, 20 + 6 * level , 6):
        brick_color = 1
        for col in range(8, 112, 15 ):
            bricks.append(Brick(col, row, brick_color, display))

    return bricks

demoOn = False
exitGame = False
while not exitGame :
    paddle_width = 22
    frameRate = 30
    gc.collect()
    print (gc.mem_free())


    gameOver = False
    usePaddle = False
    if demoOn :
        demo = True
    else :
        demo = False


    while True:
        g.display.fill(0)
        g.display.text('BREAKOUT', 0, 0, 1)
        g.display.rect(90,0, g.max_vol*4+2,6,1)
        g.display.fill_rect(91,1, g.vol * 4,4,1)
        g.display.text('A Start  L Quit', 0, 10,  1)
        if usePaddle :
            g.display.text('U Paddle', 0,20,  1)
        else :
            g.display.text('U Button', 0,20,  1)
        if demo :
            g.display.text('D AI-Player', 0,30, 1)
        else :
            g.display.text('D 1-Player', 0,30, 1)
        g.display.text('R Frame/s {}'.format(g.frameRate), 0,40, 1)
        g.display.text('B + U/D Sound', 0, 50, 1)
        g.display.show()

        g.getBtn()
        if g.setVol() :
            pass
        elif g.justReleased(g.btnL) :
            exitGame = True
            gameOver= True
            break
        elif g.justPressed(g.btnA) or demoOn :
            if demo :
                g.display.fill(0)
                g.display.text('DEMO', 5, 0, 1)
                g.display.text('B to Stop', 5, 30, 1)
                g.display.show()
                sleep_ms(1000)
                demoOn = True
            break
        elif g.justPressed(g.btnU) :
            usePaddle =  not usePaddle
        elif g.justPressed(g.btnD) :
            demo = not demo
        elif g.justPressed(g.btnR) :
            if g.pressed(g.btnB) :
                g.frameRate = g.frameRate - 5 if g.frameRate > 5 else 100
            else :
                g.frameRate = g.frameRate + 5 if g.frameRate < 100 else 5

    if not exitGame :
      g.display.fill(0)

      # Generate bricks
      MAX_LEVEL = const(5)
      level = 1
      bricks = load_level(level, g.display)

      # Initialize paddle
      paddle = Paddle(g.display, paddle_width, 3)

      # Initialize score
      score = Score(g.display)

      # Initialize balls
      balls = []
      # Add first ball
      balls.append(Ball(59, 58, -2, -1, g.display, frozen=True))

      # Initialize lives
      lives = []
      for i in range(1, 3):
          lives.append(Life(i, g.display))

      prev_paddle_vect = 0


      g.display.show()


      try:
          while not gameOver :
              g.getBtn()
              if demo :
                if g.justReleased (g.btnB) :
                  g.display.text('Demo stopped', 5, 30, 1)
                  g.display.show()
                  sleep_ms(1000)
                  gameOver = True
                  demoOn = False
                else :
                  paddle.h_position(balls[0].x - 5 + g.random (0,7))
              elif usePaddle :
                paddle.h_position(int(g.getPaddle() // 9.57))
              else :
                paddle_vect = 0
                if g.pressed(g.btnL | g.btnA) :
                  paddle_vect = -1
                elif g.pressed(g.btnR | g.btnB) :
                  paddle_vect = 1
                if paddle_vect != prev_paddle_vect :
                  paddle_vect *= 3
                else :
                  paddle_vect *= 5
                paddle.h_position(paddle.x + paddle_vect)
                prev_paddle_vect = paddle_vect

               # Handle balls
              score_points = 0
              for ball in balls:
                  # move ball and check if bounced off walls and paddle
                  if ball.set_position(paddle.x, paddle.y,paddle.x2, paddle.center):
                      g.playSound(900, 10)
                  # Check for collision with bricks if not frozen
                  if not ball.frozen:
                      prior_collision = False
                      ball_x = ball.x
                      ball_y = ball.y
                      ball_x2 = ball.x2
                      ball_y2 = ball.y2
                      ball_center_x = ball.x + ((ball.x2 + 1 - ball.x) // 2)
                      ball_center_y = ball.y + ((ball.y2 + 1 - ball.y) // 2)

                      # Check for hits
                      for brick in bricks:
                          if(ball_x2 >= brick.x and
                             ball_x <= brick.x2 and
                             ball_y2 >= brick.y and
                             ball_y <= brick.y2):
                              # Hit
                              if not prior_collision:
                                  ball.x_speed, ball.y_speed = brick.bounce(
                                      ball.x,
                                      ball.y,
                                      ball.x2,
                                      ball.y2,
                                      ball.x_speed,
                                      ball.y_speed,
                                      ball_center_x,
                                      ball_center_y)
                                  g.playTone('c6', 10)
                                  prior_collision = True
                              score_points += 1
                              brick.clear()
                              bricks.remove(brick)

                  # Check for missed
                  if ball.y2 > g.display.height - 2:
                      ball.clear_previous()
                      balls.remove(ball)
                      if not balls:
                          # Lose life if last ball on screen
                          if len(lives) == 0:
                              score.game_over()
                              g.playTone('g4', 500)
                              g.playTone('c5', 200)
                              g.playTone('f4', 500)
                              gameOver = True
                          else:
                              # Subtract Life
                              lives.pop().clear()
                              # Add ball
                              balls.append(Ball(59, 58, 2, -3, g.display,
                                           frozen=True))
                  else:
                      # Draw ball
                      ball.draw()
              # Update score if changed
              if score_points:
                  score.increment(score_points)

              # Check for level completion
              if not bricks:
                  for ball in balls:
                      ball.clear()
                  balls.clear()
                  level += 1
                  paddle_width -=2
                  if level > MAX_LEVEL:
                      level = 1
                  bricks = load_level(level, g.display)
                  balls.append(Ball(59, 58, -2, -1, g.display, frozen=True))
                  g.playTone('c5', 20)
                  g.playTone('d5', 20)
                  g.playTone('e5', 20)
                  g.playTone('f5', 20)
                  g.playTone('g5', 20)
                  g.playTone('a5', 20)
                  g.playTone('b5', 20)
                  g.playTone('c6', 20)
              g.display_and_wait()
      except KeyboardInterrupt:
              g.display.cleanup()
      sleep_ms(2000)
if g.ESP32 :
    g.deinit()
    del sys.modules["gameESP"]
gc.collect()
