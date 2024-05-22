#  MAIN FILE
try:
    import os
    import time
    import pygame
    import colored
    import sys
    import screeninfo
    import json
    import resources.pygameResources as assets
    import threading
    from random import *
    from screeninfo import get_monitors
    from resources.pygameResources import sfx
    from keywords import *
    from Constants import *

except ImportError:
    print("ImportError >> Please run 'pip install -r requirements.txt' in this project's directory.")
    exit()

#######################################################################################################################

#~WINDOW INIT~
pygame.init()
pygame.mixer.init()

pygame.display.set_caption('SuperPong')
clock = pygame.time.Clock()
screen = pygame.display.set_mode((W_WIDTH, W_HEIGHT), FLAGS)
score_font = pygame.font.Font(".\\resources\\pong-score.ttf", size=CONFIG["settings"]["font_size"])
running = True
leftPowerupList = ["Score Multiplier", "Enlarge Paddle", "Paddle Speed Boost"]
rightPowerupList = ["Score Multiplier", "Enlarge Paddle", "Paddle Speed Boost"]
channel = pygame.mixer.Channel(1)
MAIN_SCREEN_COLOR = Colors.BLUE_TINT


display_info = pygame.display.Info()
screen_width = display_info.current_w
screen_height = display_info.current_h

if DEBUG_MODE:
    print_debug("screen is", screen_width, "in width")
    print_debug("screen is",  screen_height, "in height")

if screen_width == 1920 and screen_height == 1080:
    screen_resolution_sem = 1        #1 = Full HD monitor

elif screen_width == 2560 and screen_height == 1440:
    screen_resolution_sem = 2        #2 = 2K monitor

else:
    screen_resolution_sem = 3        #3 = Possibly 4K or other
    screen_resolution = f"Other ({screen_width}x{screen_height})"
    print(f"Screen resolution: {screen_resolution}")

######################################################################################################################

class Paddle:
    def __init__(self, x, y, width, height, side, speed):
        self.x = x
        self.y = y
        self.side = side
        self.width = width
        self.height = height
        self.speed = speed

    def draw_right(self, win):
        pygame.draw.rect(win, Colors.MEGA_LIGHT_BLUE, (self.x, self.y, self.width, self.height))

    def draw_left(self, win):
        pygame.draw.rect(win, Colors.MEGA_LIGHT_RED, (self.x, self.y, self.width, self.height))

left_paddle = Paddle(LEFT_PADDLE_SPACING, W_HEIGHT/2 - (PADDLE_HEIGHT * LEFT_PADDLE_HEIGHT_MULT)/2, PADDLE_WIDTH, PADDLE_HEIGHT * LEFT_PADDLE_HEIGHT_MULT, "LEFT", PADDLE_SPEED)
right_paddle = Paddle(W_WIDTH - RIGHT_PADDLE_SPACING - PADDLE_WIDTH, W_HEIGHT/2 - (PADDLE_HEIGHT * RIGHT_PADDLE_HEIGHT_MULT)/2, PADDLE_WIDTH, PADDLE_HEIGHT * RIGHT_PADDLE_HEIGHT_MULT, "RIGHT", PADDLE_SPEED)

#######################################################################################################################

if screen_resolution_sem == 1:
    ball_velocity_x = 1050 * W_PERC / TPS
    ball_velocity_y = -100 * W_PERC / TPS
    velocity_inc_flat = 28 * W_PERC / TPS

elif screen_resolution_sem == 2:
    ball_velocity_x = 1350 * W_PERC / TPS
    ball_velocity_y = -100 * W_PERC / TPS
    velocity_inc_flat = 32 * W_PERC / TPS

else:
    ball_velocity_x = 1740 * W_PERC / TPS
    ball_velocity_y = -100 * W_PERC / TPS
    velocity_inc_flat = 32 * W_PERC / TPS


right_score_increment = 0
left_score_increment = 0

random_value_red_x = randint(50, 950) / 1000
random_value_red_y = randint(50, 950) / 1000
random_value_blue_x = random_value_red_x * randint(50, 950) / 1000
random_value_blue_y = random_value_red_y * randint(50, 950) / 1000

class Ball:
    def __init__(self, x, y, ball_velocity_x, ball_velocity_y, radius, ball_color):
        self.x = x
        self.y = y
        self.radius = BALL_RADIUS
        self.x_vel = ball_velocity_x
        self.y_vel = ball_velocity_y
        self.ball_color = ball_color

    def reset(self):
        self.x = W_WIDTH // 2
        self.y = W_HEIGHT // 2

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

        if self.y + self.radius > W_HEIGHT:  # lower barrier
            self.y_vel *= -1
            self.y = W_HEIGHT - self.radius
            self.y_vel = self.y_vel - (velocity_inc_flat / 4)
            sfx.play(assets.MARGIN_HIT_SOUND)
        elif self.y - self.radius < 0:
            self.y_vel *= -1
            self.y = self.radius
            self.y_vel = self.y_vel - (velocity_inc_flat / 4)
            sfx.play(assets.MARGIN_HIT_SOUND)

        #LEFT PADDLE COLLISION - 1/8 = upper side,  7/8 = lower side
        if left_paddle.x - PADDLE_WIDTH <= self.x - self.radius <= left_paddle.x + left_paddle.width and left_paddle.y - self.radius < self.y < left_paddle.y + left_paddle.height + self.radius:
            if self.y < left_paddle.y + left_paddle.height * 1 / 8:
                self.y_vel = (-1) * ball_velocity_x + velocity_inc_flat

            elif self.y < left_paddle.y + left_paddle.height * 2 / 8:
                self.y_vel = (-3/5) * ball_velocity_x

            elif self.y < left_paddle.y + left_paddle.height * 3 / 8:
                self.y_vel = (-3 / 10) * ball_velocity_x

            elif self.y < left_paddle.y + left_paddle.height * 4 / 8:
                self.y_vel = ball_velocity_y
            elif self.y < left_paddle.y + left_paddle.height * 5 / 8:
                self.y_vel = (3 / 10) * ball_velocity_x

            elif self.y < left_paddle.y + left_paddle.height * 6 / 8:
                self.y_vel = (3 / 5) * ball_velocity_x

            elif self.y > left_paddle.y + left_paddle.height * 7 / 8:
                self.y_vel = 1 * ball_velocity_x - velocity_inc_flat

            sfx.play(assets.PADDLE_HIT_SOUND)
            self.x_vel *= - 1
            self.x_vel += velocity_inc_flat
            self.x = left_paddle.x + PADDLE_WIDTH + self.radius + 1 * W_PERC

        if self.x <= 0:   #Left_side
            RIGHT_SCORE.inc(1 + right_score_increment)
            self.reset()
            self.moving = False
            self.x_vel = - ball_velocity_x
            self.y_vel = ball_velocity_y
            sfx.play(assets.WIN_LOSE_ROUND_SOUND)

        #RIGHT PADDLE COLLISION
        if right_paddle.x + PADDLE_WIDTH >= self.x + ball.radius >= right_paddle.x and right_paddle.y - self.radius < self.y < right_paddle.y + right_paddle.height + self.radius:

            if self.y < right_paddle.y + right_paddle.height * 1 / 8:
                self.y_vel = (-1) * ball_velocity_x + velocity_inc_flat

            elif self.y < right_paddle.y + right_paddle.height * 2 / 8:
                self.y_vel = (-3/5) * ball_velocity_x

            elif self.y < right_paddle.y + right_paddle.height * 3 / 8:
                self.y_vel = (-3 / 10) * ball_velocity_x
            elif self.y < right_paddle.y + right_paddle.height * 4 / 8:
                self.y_vel = ball_velocity_y

            elif self.y < right_paddle.y + right_paddle.height * 5 / 8:
                self.y_vel = (3 / 10) * ball_velocity_x

            elif self.y < right_paddle.y + right_paddle.height * 6 / 8:
                self.y_vel = (3 / 5) * ball_velocity_x

            elif self.y > right_paddle.y + right_paddle.height * 7 / 8:
                self.y_vel = 1 * ball_velocity_x - velocity_inc_flat

            sfx.play(assets.PADDLE_HIT_SOUND)
            self.x_vel *= -1
            self.x_vel -= velocity_inc_flat
            self.x = right_paddle.x - self.radius - 1 * W_PERC

        if self.x >= screen.get_width():   #right_side
            LEFT_SCORE.inc(1 + left_score_increment)
            self.reset()
            self.moving = False
            self.x_vel = ball_velocity_x
            self.y_vel = ball_velocity_y
            sfx.play(assets.WIN_LOSE_ROUND_SOUND)


    def move_start_screen(self):
        self.x += self.x_vel
        self.y += self.y_vel

        if self.y + self.radius > W_HEIGHT:  # lower barrier
            self.y_vel *= -1
            self.y = W_HEIGHT - self.radius
            self.y_vel = self.y_vel - (velocity_inc_flat / 4)
            sfx.play(assets.MARGIN_HIT_SOUND_2)

        elif self.y - self.radius < 0: # upper barrier
            self.y_vel *= -1
            self.y = self.radius
            self.y_vel = self.y_vel - (velocity_inc_flat / 4)
            sfx.play(assets.MARGIN_HIT_SOUND_2)

        if self.x + ball.radius >= W_WIDTH: # right barrier
            self.x_vel *= -1
            self.x = W_WIDTH - self.radius
            sfx.play(assets.MARGIN_HIT_SOUND_2)

        if self.x - self.radius <= 0: # left barrier
            self.x_vel *= -1
            sfx.play(assets.MARGIN_HIT_SOUND_2)






    def draw(self, screen):
        pygame.draw.circle(screen, self.ball_color, (self.x, self.y), self.radius, width = 0)

ball = Ball(W_WIDTH // 2, W_HEIGHT // 2, ball_velocity_x, ball_velocity_y, BALL_RADIUS, Colors.BALL_COLOR)
ball_start_screen_red = Ball(int(W_WIDTH * random_value_red_x), int(W_WIDTH * random_value_red_y), ball_velocity_x * 0.60, ball_velocity_x * 0.85, BALL_RADIUS, Colors.RED_TINT_AUX)
ball_start_screen_blue = Ball(int(W_WIDTH * random_value_blue_x), int(W_WIDTH * random_value_blue_y), -ball_velocity_x * 0.85, ball_velocity_x * 0.60, BALL_RADIUS, Colors.BLUE_TINT_AUX)

#######################################################################################################################

class Score:
    def __init__(self, x, y):
        self.count = 0
        self.x = x
        self.y = y

    def get(self):
        return self.count

    def inc(self, amount):
        self.count += amount

    def dec(self, amount):
        self.count -= amount

    def draw(self):
        score_surface = score_font.render(str(self.get()), False, Colors.WHITE)
        screen.blit(score_surface, (self.x, self.y))


LEFT_SCORE = Score(W_WIDTH // 2 - TEXT_SPACING - 17 * W_PERC, TEXT_UP)
RIGHT_SCORE = Score(W_WIDTH // 2 + TEXT_SPACING, TEXT_UP)

#######################################################################################################################

# Variable initializing
midlines_draw = True
ball.moving = False
player_won = False
WAY_ARROW_SEM = 0
game_won_sound_sem = 0


right_score_powerup_usage = 0
left_score_powerup_usage = 0
right_paddle_enlarge_usage = 0
left_paddle_enlarge_usage = 0
right_paddle_speed_boost_usage = 0
left_paddle_speed_boost_usage = 0
right_paddle_sabotage_usage = 0
left_paddle_sabotage_usage = 0
right_paddle_reverse_controls_usage = 0
left_paddle_reverse_controls_usage = 0

right_score_mult_interdicted = False
left_score_mult_interdicted = False
right_enlarge_paddle_interdicted = False
left_enlarge_paddle_interdicted = False
right_paddle_speed_boost_interdicted = False
left_paddle_speed_boost_interdicted = False
right_paddle_sabotage_interdicted = False
left_paddle_sabotage_interdicted = False

right_paddle_reverse_controls = False
left_paddle_reverse_controls = False

right_score_start_time = None
left_score_start_time = None
enlarge_paddle_left_start_time = None
enlarge_paddle_right_start_time = None
left_speed_boost_start_time = None
right_speed_boost_start_time = None
ball_right_freeze_start_time = None
ball_left_freeze_start_time = None
right_paddle_sabotage_start_time = None
left_paddle_sabotage_start_time = None
right_paddle_reverse_controls_start_time = None
left_paddle_reverse_controls_start_time = None


SCORE_MULT_LIFESPAN = 42 * TPS
ENLARGE_PADDLE_LIFESPAN = 40 * TPS
SPEED_BOOST_LIFESPAN = 40 * TPS
BALL_FREEZE_LIFESPAN = FREEZE_BALL_TIME
SABOTAGE_LIFESPAN = SABOTAGE_TIME
REVERSE_CONTROLS_LIFESPAN = 30 * TPS

left_paddle_height_aux = left_paddle.height
right_paddle_height_aux = right_paddle.height
left_paddle_height_aux2 = left_paddle.height
right_paddle_height_aux2 = right_paddle.height
PADDLE_SPEED_AUX = PADDLE_SPEED

right_score_mult_active = False
left_score_mult_active = False
right_paddle_enlarge_active = False
left_paddle_enlarge_active = False
right_paddle_speed_boost_active = False
left_paddle_speed_boost_active = False
right_paddle_sabotage_active = False
left_paddle_sabotage_active = False
right_paddle_reverse_controls_active = False
left_paddle_reverse_controls_active = False

ball_velocity_x_aux = None
ball_velocity_y_aux = None

ball_right_freeze_active = False
ball_left_freeze_active = False
ball_right_freeze_usage = 0
ball_left_freeze_usage = 0
ball_right_unfreeze_usage = 0
ball_left_unfreeze_usage = 0



                                    ##################################################################
                                 #####################---- WHILE RUNNING ----######################
                             ##################################################################


start_screen = True
music_playing = False

if music_playing is False:
    channel.play(assets.MUSIC_3)
    music_playing = True


while running:

#----------------------------------------------------------------------------------------------------------------------
    ########### START SCREEN ###########

    if start_screen is True:
        screen.fill(Colors.SCREEN_FILL_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print_success("Closing the game...")
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print_success("Closing the game...")
                    pygame.quit()
                    exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start_screen = False
                    sfx.play(assets.ENTER_GAME_SOUND)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_m:
                    if music_playing:
                        channel.pause()
                        music_playing = False
                        break
                    if music_playing is not True:
                        channel.unpause()
                        music_playing = True
                        break

        ball_start_screen_red.draw(screen)
        ball_start_screen_red.move_start_screen()
        ball_start_screen_blue.draw(screen)
        ball_start_screen_blue.move_start_screen()


        start_screen_text1 = SuperDreamFont4.render("SUPER PONG", True, Colors.BLUE_TINT)
        screen.blit(start_screen_text1, (W_WIDTH // 2 - start_screen_text1.get_width() / 2 * W_PERC, W_HEIGHT / 2.45 * W_PERC))

        start_screen_text2 = SuperDreamFont5.render("~ PRESS SPACE TO BEGIN ~", True, Colors.GRAY3)
        screen.blit(start_screen_text2, (W_WIDTH // 2 - start_screen_text2.get_width() / 2 * W_PERC, W_HEIGHT / 1.8 * W_PERC))


        if screen_resolution_sem == 1: # FULL HD monitor
            start_screen_text3 = SuperDreamFont3.render("~ press M to toggle music ~", True, Colors.GRAY3)
            screen.blit(start_screen_text3, (W_WIDTH // 1.088 - start_screen_text3.get_width() / 2 * W_PERC, W_HEIGHT / 1.03 * W_PERC))


        elif screen_resolution_sem == 2: #2K monitor
            start_screen_text3 = SuperDreamFont3.render("~ press M to toggle music ~", True, Colors.GRAY3)
            screen.blit(start_screen_text3, (W_WIDTH // 1.075 - start_screen_text3.get_width() / 2 * W_PERC, W_HEIGHT / 1.03 * W_PERC))

        else:
            start_screen_text3 = SuperDreamFont3.render("~ press M to toggle music ~", True, Colors.GRAY3)
            screen.blit(start_screen_text3,(W_WIDTH // 1.075 - start_screen_text3.get_width() / 2 * W_PERC, W_HEIGHT / 1.03 * W_PERC))


        pygame.display.update()
        clock.tick(TPS)



#----------------------------------------------------------------------------------------------------------------------
    #####################################
    ############ MAIN GAME ##############
    #####################################

    elif start_screen is False:
        screen.fill(Colors.SCREEN_FILL_COLOR)
        current_frame = pygame.time.get_ticks()
        KEYS_PRESSED = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print_success("Closing the game...")
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print_success("Closing the game...")
                    pygame.quit()
                    exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ball.moving = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_m:
                    if music_playing:
                        channel.pause()
                        music_playing = False
                        break
                    if music_playing is not True:
                        channel.unpause()
                        music_playing = True
                        break

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #POWERUP - SCORE MULTIPLIER EVENT

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE and right_score_powerup_usage == 0 and right_score_mult_interdicted is False:  #start_time =~ 640
                    if ball.moving:
                        right_score_increment = 1
                        right_score_powerup_usage = 1
                    right_score_start_time = pygame.time.get_ticks()
                    sfx.play(assets.POWERUP_SOUND)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_5 and left_score_powerup_usage == 0 and left_score_mult_interdicted is False:
                    if ball.moving:
                        left_score_increment = 1
                        left_score_powerup_usage = 1
                    left_score_start_time = pygame.time.get_ticks()
                    sfx.play(assets.POWERUP_SOUND)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #POWERUP - PADDLE ENLARGE EVENT

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RSHIFT and right_paddle_enlarge_usage == 0 and right_enlarge_paddle_interdicted is False:
                    if ball.moving:
                        right_paddle.height += THE_PADDLE_HEIGHT_INCREASE
                        right_paddle.y -= (THE_PADDLE_HEIGHT_INCREASE / 2)
                        right_paddle_enlarge_usage = 1
                        enlarge_paddle_right_start_time = pygame.time.get_ticks()
                        right_paddle_enlarge_active = True
                        sfx.play(assets.POWERUP_SOUND2)
                paddle_height_increase = left_paddle.y


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_2 and left_paddle_enlarge_usage == 0 and left_enlarge_paddle_interdicted is False:
                    if ball.moving:
                        left_paddle.height += THE_PADDLE_HEIGHT_INCREASE
                        left_paddle.y -= (THE_PADDLE_HEIGHT_INCREASE / 2)
                        left_paddle_enlarge_usage = 1
                        enlarge_paddle_left_start_time = pygame.time.get_ticks()
                        left_paddle_enlarge_active = True
                        sfx.play(assets.POWERUP_SOUND2)
                paddle_height_increase = left_paddle.y

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # POWERUP - PADDLE SPEED BOOST EVENT

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and right_paddle_speed_boost_usage == 0 and right_paddle_speed_boost_interdicted is False:
                    if ball.moving:
                        right_paddle.speed += PADDLE_SPEED_INCREASE
                        right_paddle_speed_boost_usage = 1
                        right_paddle_speed_boost_active = True
                        right_speed_boost_start_time = pygame.time.get_ticks()
                        sfx.play(assets.POWERUP_SOUND3)


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_3 and left_paddle_speed_boost_usage == 0 and left_paddle_speed_boost_interdicted is False:
                    if ball.moving:
                        left_paddle.speed += PADDLE_SPEED_INCREASE
                        left_paddle_speed_boost_usage = 1
                        left_paddle_speed_boost_active = True
                        left_speed_boost_start_time = pygame.time.get_ticks()
                        sfx.play(assets.POWERUP_SOUND3)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # POWERUP - FREEZE BALL EVENT

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and ball_left_freeze_active is False:
                    if ball.moving and ball_right_freeze_usage == 0 and left_paddle.x + (1.5 * PADDLE_WIDTH) <= ball.x <= right_paddle.x - PADDLE_WIDTH:

                        ball_right_freeze_active = True
                        ball_right_freeze_usage = 1

                        ball_velocity_x_aux = ball.x_vel
                        ball_velocity_y_aux = ball.y_vel
                        ball.ball_color = Colors.DARKER_BLUE
                        ball_right_freeze_start_time = pygame.time.get_ticks()
                        sfx.play(assets.ICE_SOUND)

                        ball.x_vel = 0
                        ball.y_vel = 0


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and ball_right_freeze_active is False:
                    if ball.moving and ball_left_freeze_usage == 0 and left_paddle.x + (1.5 * PADDLE_WIDTH) <= ball.x <= right_paddle.x - PADDLE_WIDTH:

                        ball_left_freeze_active = True
                        ball_left_freeze_usage = 1

                        ball_velocity_x_aux = ball.x_vel
                        ball_velocity_y_aux = ball.y_vel
                        ball.ball_color = Colors.DARKER_BLUE
                        ball_left_freeze_start_time = pygame.time.get_ticks()
                        sfx.play(assets.ICE_SOUND)

                        ball.x_vel = 0
                        ball.y_vel = 0

    #------------------------------------------------------------------------------------------------------------------------------------------
        # POWERUP - SABOTAGE EVENT
        # The variables are named with the paddle that activates the powerup in mind, so right_paddle_sabotage means when the right paddle uses the sabotage powerup.

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSLASH and right_paddle_sabotage_interdicted is False:
                    if ball.moving and right_paddle_sabotage_usage == 0 and ball.x > left_paddle.x + left_paddle.width + SABOTAGE_SPACING_INCREASE:

                        right_paddle_sabotage_active = True
                        right_paddle_sabotage_usage = 1

                        right_paddle_sabotage_start_time = pygame.time.get_ticks()
                        sfx.play(assets.SABOTAGE_SOUND)

                        left_paddle.x += SABOTAGE_SPACING_INCREASE


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_4 and left_paddle_sabotage_interdicted is False:
                    if ball.moving and left_paddle_sabotage_usage == 0 and ball.x < right_paddle.x - SABOTAGE_SPACING_INCREASE:

                        left_paddle_sabotage_active = True
                        left_paddle_sabotage_usage = 1

                        left_paddle_sabotage_start_time = pygame.time.get_ticks()
                        sfx.play(assets.SABOTAGE_SOUND)

                        right_paddle.x -= SABOTAGE_SPACING_INCREASE

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # POWERUP - REVERSE CONTROLS EVENT
        """
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_6 and right_paddle_reverse_controls_usage == 0:
                    right_paddle_reverse_controls_active = True
                    right_paddle_reverse_controls_usage = 1
                    right_paddle_reverse_controls_start_time = pygame.time.get_ticks()
                    sfx.play(assets.POWERUP_SOUND)
    
    
    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y and left_paddle_reverse_controls_usage == 0:
                    left_paddle_reverse_controls_active = True
                    left_paddle_reverse_controls_usage = 1
                    left_paddle_reverse_controls_start_time = pygame.time.get_ticks()
                    sfx.play(assets.POWERUP_SOUND)
    
        if right_paddle_reverse_controls_start_time is not None and current_frame - right_paddle_reverse_controls_start_time >= (REVERSE_CONTROLS_LIFESPAN / 1.1) and right_paddle_reverse_controls_active is True:
            Colors.MEGA_LIGHT_BLUE = (0, 0, 120)
        elif right_paddle_reverse_controls_active is True:
            Colors.MEGA_LIGHT_BLUE = Colors.MEGA_LIGHT_BLUE_AUX
    
        if left_paddle_reverse_controls_start_time is not None and current_frame - left_paddle_reverse_controls_start_time >= (REVERSE_CONTROLS_LIFESPAN / 1.1) and left_paddle_reverse_controls_active is True:
            Colors.MEGA_LIGHT_RED = (120, 0, 0)
        elif left_paddle_reverse_controls_active is True:
            Colors.MEGA_LIGHT_RED = Colors.MEGA_LIGHT_RED_AUX
    
    
    
        if right_paddle_reverse_controls_start_time is not None and current_frame - right_paddle_reverse_controls_start_time >= REVERSE_CONTROLS_LIFESPAN:
            right_paddle_reverse_controls_active = False
            right_paddle_reverse_controls_start_time = None
    
    
        if left_paddle_reverse_controls_start_time is not None and current_frame - left_paddle_reverse_controls_start_time >= REVERSE_CONTROLS_LIFESPAN:
            left_paddle_reverse_controls_active = False
            left_paddle_reverse_controls_start_time = None
    
        """
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # POWERUP - FREEZE BALL

        if ball_right_freeze_start_time is not None and current_frame - ball_right_freeze_start_time >= BALL_FREEZE_LIFESPAN:
            ball.x_vel = ball_velocity_x_aux
            ball.y_vel = ball_velocity_y_aux
            ball.ball_color = Colors.BALL_COLOR_AUX
            sfx.play(assets.UNFREEZE_SOUND)
            ball_right_freeze_start_time = None
            ball_right_freeze_active = False


        if ball_left_freeze_start_time is not None and current_frame - ball_left_freeze_start_time >= BALL_FREEZE_LIFESPAN:
            ball.x_vel = ball_velocity_x_aux
            ball.y_vel = ball_velocity_y_aux
            ball.ball_color = Colors.BALL_COLOR_AUX
            sfx.play(assets.UNFREEZE_SOUND)
            ball_left_freeze_start_time = None
            ball_left_freeze_active = False



        if ball_right_freeze_active is True:

            right_freeze_powerup_text = SuperDreamFont.render("FREEZE ACTIVE", True, Colors.MEGA_LIGHT_BLUE_AUX)
            screen.blit(right_freeze_powerup_text, (W_WIDTH // 2 - right_freeze_powerup_text.get_width() // 2, W_HEIGHT - (W_HEIGHT - 165 * W_PERC)))
            Colors.SCREEN_FILL_COLOR = (0, 0, 9)

        if ball_left_freeze_active is True:
            left_freeze_powerup_text = SuperDreamFont.render("FREEZE ACTIVE", True, Colors.MEGA_LIGHT_RED_AUX)
            screen.blit(left_freeze_powerup_text, (W_WIDTH // 2 - left_freeze_powerup_text.get_width() // 2, W_HEIGHT - (W_HEIGHT - 165 * W_PERC)))
            Colors.SCREEN_FILL_COLOR = (0, 0, 9)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #POWERUP - SCORE MULTIPLIER

        if right_score_start_time is not None and current_frame - right_score_start_time >= SCORE_MULT_LIFESPAN:
            right_score_increment = 0
            right_score_start_time = None

        if left_score_start_time is not None and current_frame - left_score_start_time >= SCORE_MULT_LIFESPAN:
            left_score_increment = 0
            left_score_start_time = None

        if right_score_increment == 1:
            right_enlarge_paddle_interdicted = True
            right_paddle_speed_boost_interdicted = True
            right_paddle_sabotage_interdicted = True
            right_score_powerup_text = SuperDreamFont.render("SCORE MULTIPLIER ACTIVE", True, Colors.MEGA_LIGHT_BLUE_AUX)
            screen.blit(right_score_powerup_text, (W_WIDTH // 1.14 - right_score_powerup_text.get_width() // 2, W_HEIGHT - (W_HEIGHT - 12 * W_PERC)))
            Colors.SCREEN_FILL_COLOR = (0, 0, 9)

        elif right_score_increment == 0 and left_score_increment == 0:
            Colors.SCREEN_FILL_COLOR = Colors.SCREEN_FILL_COLOR_AUX
            right_enlarge_paddle_interdicted = False
            right_paddle_speed_boost_interdicted = False
            right_paddle_sabotage_interdicted = False

        if left_score_increment == 1:
            left_enlarge_paddle_interdicted = True
            left_paddle_speed_boost_interdicted = True
            left_paddle_sabotage_interdicted = True
            left_score_powerup_text = SuperDreamFont.render("SCORE MULTIPLIER ACTIVE", True, Colors.MEGA_LIGHT_RED_AUX)
            screen.blit(left_score_powerup_text, (W_WIDTH // 10 - left_score_powerup_text.get_width() // 2, W_HEIGHT - (W_HEIGHT - 12 * W_PERC)))
            Colors.SCREEN_FILL_COLOR = (9, 0, 0)

        elif left_score_increment == 0 and right_score_increment == 0:
            Colors.SCREEN_FILL_COLOR = Colors.SCREEN_FILL_COLOR_AUX
            left_enlarge_paddle_interdicted = False
            left_paddle_speed_boost_interdicted = False
            left_paddle_sabotage_interdicted = False

        if left_score_increment == 1 and right_score_increment == 1:
            Colors.SCREEN_FILL_COLOR = (10, 0, 14)

        if right_score_increment == 1:
            Colors.MEGA_LIGHT_BLUE = (0, 50, 245)
        elif right_score_increment == 0:
            Colors.MEGA_LIGHT_BLUE = Colors.MEGA_LIGHT_BLUE_AUX

        if left_score_increment == 1:
            Colors.MEGA_LIGHT_RED = (240, 100, 0)
        elif left_score_increment == 0:
            Colors.MEGA_LIGHT_RED = Colors.MEGA_LIGHT_RED_AUX

     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # POWERUP - ENLARGE PADDLE

        if enlarge_paddle_right_start_time is not None and current_frame - enlarge_paddle_right_start_time >= (ENLARGE_PADDLE_LIFESPAN / 1.1) and right_paddle_enlarge_active is True:
            Colors.MEGA_LIGHT_BLUE = (0, 0, 120)
        elif right_paddle_enlarge_active is True:
            Colors.MEGA_LIGHT_BLUE = Colors.MEGA_LIGHT_BLUE_AUX

        if enlarge_paddle_left_start_time is not None and current_frame - enlarge_paddle_left_start_time >= (ENLARGE_PADDLE_LIFESPAN / 1.1) and left_paddle_enlarge_active is True:
            Colors.MEGA_LIGHT_RED = (120, 0, 0)
        elif left_paddle_enlarge_active is True:
            Colors.MEGA_LIGHT_RED = Colors.MEGA_LIGHT_RED_AUX

        if enlarge_paddle_right_start_time is not None and current_frame - enlarge_paddle_right_start_time >= ENLARGE_PADDLE_LIFESPAN and right_paddle_enlarge_active is True:
            enlarge_paddle_right_start_time = None
            right_paddle_enlarge_usage += 1
            right_paddle.height = left_paddle_height_aux
            right_paddle.y += (THE_PADDLE_HEIGHT_INCREASE // 2)
            right_paddle_enlarge_active = False
            right_score_mult_interdicted = False
            right_paddle_speed_boost_interdicted = False
            right_paddle_sabotage_interdicted = False

        if enlarge_paddle_left_start_time is not None and current_frame - enlarge_paddle_left_start_time >= ENLARGE_PADDLE_LIFESPAN and left_paddle_enlarge_active is True:
            enlarge_paddle_left_start_time = None
            left_paddle_enlarge_usage += 1
            left_paddle.height = left_paddle_height_aux
            left_paddle.y += (THE_PADDLE_HEIGHT_INCREASE // 2)
            left_paddle_enlarge_active = False
            left_score_mult_interdicted = False
            left_paddle_speed_boost_interdicted = False
            left_paddle_sabotage_interdicted = False

        if right_paddle_enlarge_active == 1:
            right_enlarge_paddle_text = SuperDreamFont.render("ENLARGE PADDLE ACTIVE", True, Colors.MEGA_LIGHT_BLUE_AUX)
            screen.blit(right_enlarge_paddle_text, (W_WIDTH // 1.14 - right_enlarge_paddle_text.get_width() // 2, W_HEIGHT - (W_HEIGHT - 12 * W_PERC)))

        if left_paddle_enlarge_active == 1:
            left_enlarge_paddle_text = SuperDreamFont.render("ENLARGE PADDLE ACTIVE", True, Colors.MEGA_LIGHT_RED_AUX)
            screen.blit(left_enlarge_paddle_text, (W_WIDTH // 10 - left_enlarge_paddle_text.get_width() // 2, W_HEIGHT - (W_HEIGHT - 12 * W_PERC)))

        if left_paddle_enlarge_active:
            left_score_mult_interdicted = True
            left_paddle_speed_boost_interdicted = True
            left_paddle_sabotage_interdicted = True

        if right_paddle_enlarge_active:
            right_score_mult_interdicted = True
            right_paddle_speed_boost_interdicted = True
            right_paddle_sabotage_interdicted = True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # POWERUP - PADDLE SPEED BOOST

        if right_speed_boost_start_time is not None and current_frame - right_speed_boost_start_time >= (SPEED_BOOST_LIFESPAN / 1.1) and right_paddle_speed_boost_active is True:
            Colors.MEGA_LIGHT_BLUE = (0, 0, 120)
        elif right_paddle_speed_boost_active is True:
            Colors.MEGA_LIGHT_BLUE = Colors.MEGA_LIGHT_BLUE_AUX

        if left_speed_boost_start_time is not None and current_frame - left_speed_boost_start_time >= (SPEED_BOOST_LIFESPAN / 1.1) and left_paddle_speed_boost_active is True:
            Colors.MEGA_LIGHT_RED = (120, 0, 0)
        elif left_paddle_speed_boost_active is True:
            Colors.MEGA_LIGHT_RED = Colors.MEGA_LIGHT_RED_AUX


        if right_speed_boost_start_time is not None and current_frame - right_speed_boost_start_time >= SPEED_BOOST_LIFESPAN:
            right_speed_boost_start_time = None
            right_paddle_speed_boost_active = False
            right_paddle.speed = PADDLE_SPEED_AUX
            right_score_mult_interdicted = False
            right_enlarge_paddle_interdicted = False
            right_paddle_sabotage_interdicted = False

        if left_speed_boost_start_time is not None and current_frame - left_speed_boost_start_time >= SPEED_BOOST_LIFESPAN:
            left_speed_boost_start_time = None
            left_paddle_speed_boost_active = False
            left_paddle.speed = PADDLE_SPEED_AUX
            left_score_mult_interdicted = False
            left_enlarge_paddle_interdicted = False
            left_paddle_sabotage_interdicted = False

        if right_paddle_speed_boost_active == 1:
            right_speed_boost_text = SuperDreamFont.render("SPEED BOOST ACTIVE", True, Colors.MEGA_LIGHT_BLUE_AUX)
            screen.blit(right_speed_boost_text, (W_WIDTH // 1.14 - right_speed_boost_text.get_width() // 2, W_HEIGHT - (W_HEIGHT - 12 * W_PERC)))

        if left_paddle_speed_boost_active == 1:
            left_speed_boost_text = SuperDreamFont.render("SPEED BOOST ACTIVE", True, Colors.MEGA_LIGHT_RED_AUX)
            screen.blit(left_speed_boost_text, (W_WIDTH // 10 - left_speed_boost_text.get_width() // 2, W_HEIGHT - (W_HEIGHT - 12 * W_PERC)))


        if left_paddle_speed_boost_active:
            left_score_mult_interdicted = True
            left_enlarge_paddle_interdicted = True
            left_paddle_sabotage_interdicted = True

        if right_paddle_speed_boost_active:
            right_score_mult_interdicted = True
            right_enlarge_paddle_interdicted = True
            right_paddle_sabotage_interdicted = True

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # POWERUP - SABOTAGE

        if right_paddle_sabotage_start_time is not None and current_frame - right_paddle_sabotage_start_time >= (SABOTAGE_LIFESPAN / 1.1) and right_paddle_sabotage_active is True:
            Colors.MEGA_LIGHT_BLUE = (0, 0, 120)
        elif right_paddle_sabotage_active is True:
            Colors.MEGA_LIGHT_BLUE = Colors.MEGA_LIGHT_BLUE_AUX

        if left_paddle_sabotage_start_time is not None and current_frame - left_paddle_sabotage_start_time >= (SABOTAGE_LIFESPAN / 1.1) and left_paddle_sabotage_active is True:
            Colors.MEGA_LIGHT_RED = (120, 0, 0)
        elif left_paddle_sabotage_active is True:
            Colors.MEGA_LIGHT_RED = Colors.MEGA_LIGHT_RED_AUX

        if right_paddle_sabotage_start_time is not None and current_frame - right_paddle_sabotage_start_time >= SABOTAGE_LIFESPAN and right_paddle_sabotage_active is True:
            right_paddle_sabotage_start_time = None
            right_paddle_sabotage_active = False
            left_paddle.x -= SABOTAGE_SPACING_INCREASE
            right_score_mult_interdicted = False
            right_enlarge_paddle_interdicted = False
            right_speed_boost_interdicted = False


        if left_paddle_sabotage_start_time is not None and current_frame - left_paddle_sabotage_start_time >= SABOTAGE_LIFESPAN and left_paddle_sabotage_active is True:
            left_paddle_sabotage_start_time = None
            left_paddle_sabotage_active = False
            right_paddle.x += SABOTAGE_SPACING_INCREASE
            left_score_mult_interdicted = False
            left_enlarge_paddle_interdicted = False
            left_speed_boost_interdicted = False

        if right_paddle_sabotage_active == 1:
            right_paddle_sabotage_text = SuperDreamFont.render("SABOTAGE ACTIVE", True, Colors.MEGA_LIGHT_BLUE_AUX)
            screen.blit(right_paddle_sabotage_text, (W_WIDTH // 1.14 - right_paddle_sabotage_text.get_width() // 2, W_HEIGHT - (W_HEIGHT - 12 * W_PERC)))

        if left_paddle_sabotage_active == 1:
            left_paddle_sabotage_text = SuperDreamFont.render("SABOTAGE ACTIVE", True, Colors.MEGA_LIGHT_RED_AUX)
            screen.blit(left_paddle_sabotage_text, (W_WIDTH // 10 - left_paddle_sabotage_text.get_width() // 2, W_HEIGHT - (W_HEIGHT - 12 * W_PERC)))

        if left_paddle_sabotage_active == 1:
            left_score_mult_interdicted = True
            left_enlarge_paddle_interdicted = True
            left_paddle_speed_boost_interdicted = True

        if right_paddle_sabotage_active == 1:
            right_score_mult_interdicted = True
            right_enlarge_paddle_interdicted = True
            right_paddle_speed_boost_interdicted = True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
           ###### DRAWS #######

        if midlines_draw:
            for i in range(0, MID_LINES_COUNT):
                LINE_START = i * 2 * W_HEIGHT / (MID_LINES_COUNT * 2)
                LINE_END = (i * 2 + 1) * W_HEIGHT / (MID_LINES_COUNT * 2)
                pygame.draw.line(screen, Colors.WAY_TOO_DARK_GRAY, (W_WIDTH / 2, LINE_START), (W_WIDTH / 2, LINE_END),2)

        left_paddle.draw_left(screen)
        right_paddle.draw_right(screen)
        ball.draw(screen)
        LEFT_SCORE.draw()
        RIGHT_SCORE.draw()

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        Press_space_sem = True
        print_arrows = True

        #########   WINNING SITUATION   #########

        if LEFT_SCORE.get() >= WINNING_SCORE or RIGHT_SCORE.get() >= WINNING_SCORE:

            if game_won_sound_sem == 0:
                sfx.play(assets.GAME_WON_SOUND)
                game_won_sound_sem = 1


            right_score_increment = 0
            left_score_increment = 0
            left_score_powerup_usage = 0
            right_score_powerup_usage = 0
            right_paddle_enlarge_usage = 0
            left_paddle_enlarge_usage = 0
            right_paddle_speed_boost_usage = 0
            left_paddle_speed_boost_usage = 0
            ball_right_freeze_usage = 0
            ball_left_freeze_usage = 0

            left_paddle_sabotage_usage = 0
            right_paddle_sabotage_usage = 0
            right_paddle.height = left_paddle_height_aux2
            right_paddle_enlarge_active = False

            left_paddle.height = left_paddle_height_aux2
            left_paddle_enlarge_active = False

            if right_paddle_speed_boost_active:
                right_paddle.speed = PADDLE_SPEED_AUX
                right_paddle_speed_boost_active = False

            if left_paddle_speed_boost_active:
                left_paddle.speed = PADDLE_SPEED_AUX
                left_paddle_speed_boost_active = False

            if left_paddle_sabotage_active:
                right_paddle.x += SABOTAGE_SPACING_INCREASE
                left_paddle_sabotage_active = False

            if right_paddle_sabotage_active:
                left_paddle.x -= SABOTAGE_SPACING_INCREASE
                right_paddle_sabotage_active = False


            if LEFT_SCORE.get() >= WINNING_SCORE:
                Winning_font = pygame.font.Font(".\\resources\\SuperDream-ax3vE.ttf", 78)
                Left_won_text = Winning_font.render("RED SIDE WON !", True, Colors.RED)
                Left_won_text.set_alpha(255)
                screen.blit(Left_won_text, (W_WIDTH // 2 - Left_won_text.get_width() // 2, W_HEIGHT // 3))

            else:
                Winning_font = pygame.font.Font(".\\resources\\SuperDream-ax3vE.ttf", 78)
                Right_won_text = Winning_font.render("BLUE SIDE WON !", True, Colors.BLUE)
                Right_won_text.set_alpha(255)
                screen.blit(Right_won_text, (W_WIDTH // 2 - Right_won_text.get_width() // 2, W_HEIGHT // 3))

            Continue_font = pygame.font.Font(".\\resources\\SuperDream-ax3vE.ttf", 48)
            Continue_text = Continue_font.render("Press SPACE to Restart", True, Colors.GRAY)
            Continue_text.set_alpha(148)
            screen.blit(Continue_text, (W_WIDTH // 2 - Continue_text.get_width() // 2, W_HEIGHT // 2 + W_HEIGHT// 8 ))
            print_arrows = False

            player_won = True
            Press_space_sem = False

            if player_won and pygame.key.get_pressed()[pygame.K_SPACE]:
                game_won_sound_sem = 0
                LEFT_SCORE.count = 0
                RIGHT_SCORE.count = 0
                ball.reset()
                ball.moving = False
                player_won = False
                Press_space_sem = True
                print_arrows = False

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        #######  PRESS SPACE TO START SITUATION  #######

        if ball.moving:
            ball.move()
        else:

            Press_space_font = pygame.font.Font(".\\resources\\SuperDream-ax3vE.ttf", 48)
            Press_space_text = Press_space_font.render("PRESS SPACE TO START", True, Colors.GRAY)

            Way_line_right_font = pygame.font.Font(".\\resources\\SuperDream-ax3vE.ttf", 28)
            Way_line_right_text = Press_space_font.render(">>>", True, Colors.WAY_TOO_DARK_GRAY)

            Way_line_left_font = pygame.font.Font(".\\resources\\SuperDream-ax3vE.ttf", 28)
            Way_line_left_text = Press_space_font.render("<<<", True, Colors.WAY_TOO_DARK_GRAY)

            Press_space_text.set_alpha(236)

            if Press_space_sem:
                screen.blit(Press_space_text, (W_WIDTH // 2 - Press_space_text.get_width() // 2, W_HEIGHT // 5))
                right_score_increment = 0
                left_score_increment = 0
                right_score_mult_interdicted = False
                left_score_mult_interdicted = False
                right_paddle_speed_boost_interdicted = False
                left_paddle_speed_boost_interdicted = False

                left_paddle.height = left_paddle_height_aux2
                left_paddle_enlarge_active = False
                right_paddle.height = left_paddle_height_aux2
                right_paddle_enlarge_active = False


                if right_paddle_speed_boost_active:
                    right_paddle.speed = PADDLE_SPEED_AUX
                    right_paddle_speed_boost_active = False

                if left_paddle_speed_boost_active:
                    left_paddle.speed = PADDLE_SPEED_AUX
                    left_paddle_speed_boost_active = False

                if left_paddle_sabotage_active:
                    right_paddle.x += SABOTAGE_SPACING_INCREASE
                    left_paddle_sabotage_active = False
                    left_paddle_sabotage_start_time = None

                if right_paddle_sabotage_active:
                    left_paddle.x -= SABOTAGE_SPACING_INCREASE
                    right_paddle_sabotage_active = False
                    right_paddle_sabotage_start_time = None

            if ball.x_vel < 0:
                WAY_ARROW_SEM = False  # Ball is moving left
            else:
                WAY_ARROW_SEM = True

            if print_arrows:
                if WAY_ARROW_SEM:
                    screen.blit(Way_line_right_text, (W_WIDTH // 2 + 40 * W_PERC, W_HEIGHT // 2 - 30 * W_PERC))
                elif not WAY_ARROW_SEM:
                    screen.blit(Way_line_left_text, (W_WIDTH // 2 - 115 * W_PERC, W_HEIGHT // 2 - 30 * W_PERC))


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # EXPLAIN  THE CONTROLS

            if player_won is False:

                controls_right_text = SuperDreamFont3.render("HOLD   ENTER   TO SHOW CONTROLS:", True, Colors.BLUE_TINT)
                control_up_right_text = SuperDreamFont2.render("UP ARROW           -    MOVE UP", True, Colors.GRAY2)
                control_down_right_text = SuperDreamFont2.render("DOWN ARROW    -  MOVE DOWN", True, Colors.GRAY2)
                control_1_right_text = SuperDreamFont2.render("BACKSPACE     -  SCORE MULTIPLIER", True, Colors.GRAY2)
                control_2_right_text = SuperDreamFont2.render("BACKSLASH      -  SABOTAGE", True, Colors.GRAY2)
                control_3_right_text = SuperDreamFont2.render("ENTER     -  SPEED BOOST", True, Colors.GRAY2)
                control_4_right_text = SuperDreamFont2.render("R SHIFT     -  ENLARGE PADDLE", True, Colors.GRAY2)
                control_5_right_text = SuperDreamFont2.render("LEFT ARROW  -  FREEZE BALL", True, Colors.GRAY2)


                control_info_right_text = SuperDreamFont2.render("Note :  Power-ups can be used once per match", True, Colors.BLUE_TINT2)



                if screen_resolution_sem == 1:
                    screen.blit(controls_right_text, (W_WIDTH // 1.3 - 53 * W_PERC, W_HEIGHT / 12 - 50 * W_PERC))
                elif screen_resolution_sem == 2:
                    screen.blit(controls_right_text, (W_WIDTH // 1.3 + 23 * W_PERC, W_HEIGHT / 12 - 50 * W_PERC))
                else:
                    screen.blit(controls_right_text, (W_WIDTH // 1.3 + 23 * W_PERC, W_HEIGHT / 12 - 50 * W_PERC))


                if KEYS_PRESSED[pygame.K_RETURN]:
                    if screen_resolution_sem == 1:
                        screen.blit(control_up_right_text, (W_WIDTH // 1.3 + 7 * W_PERC, W_HEIGHT / 12 + 10 * W_PERC))
                        screen.blit(control_down_right_text, (W_WIDTH // 1.3 + 7 * W_PERC, W_HEIGHT / 12 + 60 * W_PERC))
                        screen.blit(control_1_right_text, (W_WIDTH // 1.3 + 7 * W_PERC, W_HEIGHT / 12 + 110 * W_PERC))
                        screen.blit(control_2_right_text, (W_WIDTH // 1.3 + 7 * W_PERC, W_HEIGHT / 12 + 160 * W_PERC))
                        screen.blit(control_3_right_text, (W_WIDTH // 1.3 + 7 * W_PERC, W_HEIGHT / 12 + 210 * W_PERC))
                        screen.blit(control_4_right_text, (W_WIDTH // 1.3 + 7 * W_PERC, W_HEIGHT / 12 + 260 * W_PERC))
                        screen.blit(control_5_right_text, (W_WIDTH // 1.3 + 7 * W_PERC, W_HEIGHT / 12 + 310 * W_PERC))
                        screen.blit(control_info_right_text, (W_WIDTH // 1.3 - 53 * W_PERC, W_HEIGHT / 12 + 360 * W_PERC))

                    elif screen_resolution_sem == 2:
                        screen.blit(control_up_right_text, (W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 10 * W_PERC))
                        screen.blit(control_down_right_text,(W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 60 * W_PERC))
                        screen.blit(control_1_right_text, (W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 110 * W_PERC))
                        screen.blit(control_2_right_text, (W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 160 * W_PERC))
                        screen.blit(control_3_right_text, (W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 210 * W_PERC))
                        screen.blit(control_4_right_text, (W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 260 * W_PERC))
                        screen.blit(control_5_right_text, (W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 310 * W_PERC))
                        screen.blit(control_info_right_text,(W_WIDTH // 1.3 + 23 * W_PERC, W_HEIGHT / 12 + 360 * W_PERC))

                    else:
                        screen.blit(control_up_right_text, (W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 10 * W_PERC))
                        screen.blit(control_down_right_text,(W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 60 * W_PERC))
                        screen.blit(control_1_right_text, (W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 110 * W_PERC))
                        screen.blit(control_2_right_text, (W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 160 * W_PERC))
                        screen.blit(control_3_right_text, (W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 210 * W_PERC))
                        screen.blit(control_4_right_text, (W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 260 * W_PERC))
                        screen.blit(control_5_right_text, (W_WIDTH // 1.3 + 77 * W_PERC, W_HEIGHT / 12 + 310 * W_PERC))
                        screen.blit(control_info_right_text,(W_WIDTH // 1.3 + 23 * W_PERC, W_HEIGHT / 12 + 360 * W_PERC))




                controls_left_text = SuperDreamFont3.render("HOLD   Q   TO SHOW CONTROLS:", True, Colors.RED_TINT)  # 1 - FREEZE
                control_up_left_text = SuperDreamFont2.render("W         -  MOVE UP", True, Colors.GRAY2)
                control_down_left_text = SuperDreamFont2.render("S         -  MOVE DOWN", True, Colors.GRAY2)
                control_1_left_text = SuperDreamFont2.render("1         -  FREEZE BALL", True, Colors.GRAY2)
                control_2_left_text = SuperDreamFont2.render("2         -  ENLARGE PADDLE", True, Colors.GRAY2)
                control_3_left_text = SuperDreamFont2.render("3         -  SPEED BOOST", True, Colors.GRAY2)
                control_4_left_text = SuperDreamFont2.render("4         -  SABOTAGE", True, Colors.GRAY2)
                control_5_left_text = SuperDreamFont2.render("5         -  SCORE MULTIPLIER", True, Colors.GRAY2)


                control_info_left_text = SuperDreamFont2.render("Note :  Power-ups can only be used once at a time (except freeze)", True, Colors.RED_TINT2)



                if screen_resolution_sem == 1:
                    screen.blit(controls_left_text, (W_WIDTH // 8 - 110 * W_PERC, W_HEIGHT / 12 - 50 * W_PERC))
                elif screen_resolution_sem == 2:
                    screen.blit(controls_left_text, (W_WIDTH // 8 - 170 * W_PERC, W_HEIGHT / 12 - 50 * W_PERC))
                else:
                    screen.blit(controls_left_text, (W_WIDTH // 8 - 170 * W_PERC, W_HEIGHT / 12 - 50 * W_PERC))

                if KEYS_PRESSED[pygame.K_q]:
                    if screen_resolution_sem == 1:
                        screen.blit(control_up_left_text, (W_WIDTH // 8 - 55 * W_PERC, W_HEIGHT / 12 + 10 * W_PERC))
                        screen.blit(control_down_left_text, (W_WIDTH // 8 - 55 * W_PERC, W_HEIGHT / 12 + 60 * W_PERC))
                        screen.blit(control_1_left_text, (W_WIDTH // 8 - 55 * W_PERC, W_HEIGHT / 12 + 110 * W_PERC))
                        screen.blit(control_2_left_text, (W_WIDTH // 8 - 55 * W_PERC, W_HEIGHT / 12 + 160 * W_PERC))
                        screen.blit(control_3_left_text, (W_WIDTH // 8 - 55 * W_PERC, W_HEIGHT / 12 + 210 * W_PERC))
                        screen.blit(control_4_left_text, (W_WIDTH // 8 - 55 * W_PERC, W_HEIGHT / 12 + 260 * W_PERC))
                        screen.blit(control_5_left_text, (W_WIDTH // 8 - 55 * W_PERC, W_HEIGHT / 12 + 310 * W_PERC))
                        screen.blit(control_info_left_text, (W_WIDTH // 8 - 110 * W_PERC, W_HEIGHT / 12 + 360 * W_PERC))

                    elif screen_resolution_sem == 2:
                        screen.blit(control_up_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 10 * W_PERC))
                        screen.blit(control_down_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 60 * W_PERC))
                        screen.blit(control_1_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 110 * W_PERC))
                        screen.blit(control_2_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 160 * W_PERC))
                        screen.blit(control_3_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 210 * W_PERC))
                        screen.blit(control_4_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 260 * W_PERC))
                        screen.blit(control_5_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 310 * W_PERC))
                        screen.blit(control_info_left_text, (W_WIDTH // 8 - 170 * W_PERC, W_HEIGHT / 12 + 360 * W_PERC))
                    else:
                        screen.blit(control_up_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 10 * W_PERC))
                        screen.blit(control_down_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 60 * W_PERC))
                        screen.blit(control_1_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 110 * W_PERC))
                        screen.blit(control_2_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 160 * W_PERC))
                        screen.blit(control_3_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 210 * W_PERC))
                        screen.blit(control_4_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 260 * W_PERC))
                        screen.blit(control_5_left_text, (W_WIDTH // 8 - 115 * W_PERC, W_HEIGHT / 12 + 310 * W_PERC))
                        screen.blit(control_info_left_text, (W_WIDTH // 8 - 170 * W_PERC, W_HEIGHT / 12 + 360 * W_PERC))



    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #########  Controls  #########

        if KEYS_PRESSED[pygame.K_UP]:
            if DEBUG_MODE: print_debug("Keydown: UP")
            if right_paddle_reverse_controls_active is False:
                if right_paddle.y > 0:
                    right_paddle.y -= right_paddle.speed * RIGHT_PADDLE_SPEED_MULT / TPS
            else:
                if right_paddle.y < W_HEIGHT - right_paddle.height:
                    right_paddle.y += right_paddle.speed * RIGHT_PADDLE_SPEED_MULT / TPS

        if KEYS_PRESSED[pygame.K_DOWN]:
            if DEBUG_MODE: print_debug("Keydown: DOWN")
            if right_paddle_reverse_controls_active is False:
                if right_paddle.y < W_HEIGHT - right_paddle.height:
                    right_paddle.y += right_paddle.speed * RIGHT_PADDLE_SPEED_MULT / TPS
            else:
                if right_paddle.y > 0:
                    right_paddle.y -= right_paddle.speed * RIGHT_PADDLE_SPEED_MULT / TPS

        if KEYS_PRESSED[pygame.K_w]:
            if DEBUG_MODE: print_debug("Keydown: W")
            if left_paddle_reverse_controls_active is False:
                if left_paddle.y > 0:
                    left_paddle.y -= left_paddle.speed * LEFT_PADDLE_SPEED_MULT / TPS
            else:
                if left_paddle.y < W_HEIGHT - left_paddle.height:
                    left_paddle.y += left_paddle.speed * LEFT_PADDLE_SPEED_MULT / TPS

        if KEYS_PRESSED[pygame.K_s]:
            if DEBUG_MODE: print_debug("Keydown: S")
            if left_paddle_reverse_controls_active is False:
                if left_paddle.y < W_HEIGHT - left_paddle.height:
                    left_paddle.y += left_paddle.speed * LEFT_PADDLE_SPEED_MULT / TPS
            else:
                if left_paddle.y > 0:
                    left_paddle.y -= left_paddle.speed * LEFT_PADDLE_SPEED_MULT / TPS

        ################################
        ######### Clip Bug Fix #########
        ################################

        if left_paddle.y > W_HEIGHT - left_paddle.height:
            left_paddle.y = W_HEIGHT - left_paddle.height
        if left_paddle.y < 0:
            left_paddle.y = 0
        if right_paddle.y > W_HEIGHT - right_paddle.height:
            right_paddle.y = W_HEIGHT - right_paddle.height
        if right_paddle.y < 0:
            right_paddle.y = 0

        if DEBUG_MODE:
            fps = clock.get_fps()
            font = pygame.font.Font(None, 24)
            fps_text = font.render(f"FPS: {fps:.2f}", True, (170, 170, 170))
            screen.blit(fps_text, (10, 10))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        pygame.display.update()
        clock.tick(TPS)