import pygame
import json
import requests
from keywords import *
from screeninfo import get_monitors
pygame.init()

try:
    open("config.json")
except FileNotFoundError:
    print_error("Config file not found.")
    print_debug("Downloading config file from 'https://raw.githubusercontent.com/BlueStallion6/SuperPong/main/config.json'...")
    url = "https://raw.githubusercontent.com/BlueStallion6/SuperPong/main/config.json"
    config_file = requests.get(url)
    open("config.json", "wb").write(config_file.content)
    print_success("'config.json' has been created")

with open("config.json", "r") as file:
    CONFIG = json.load(file)
    file.close()

if CONFIG["settings"]["window_perc"] is None:
    W_PERC = 0.5
else:
    W_PERC = CONFIG["settings"]["window_perc"] / 100

MONITORS = get_monitors()
primary_monitor = MONITORS[0]

DEBUG_MODE = CONFIG["settings"]["debug_mode"]
W_WIDTH = primary_monitor.width * W_PERC
W_HEIGHT = primary_monitor.height * W_PERC
PADDLE_WIDTH, PADDLE_HEIGHT = CONFIG["play_configs"]["paddle_width"] * W_PERC, CONFIG["play_configs"]["paddle_height"] * W_PERC
TPS = CONFIG["settings"]["tps"]
PADDLE_SPEED = CONFIG["play_configs"]["paddle_speed"] * W_PERC
SCORE_MULT = CONFIG["powerups"]["score_mult"]
TEXT_UP = CONFIG["play_configs"]["text_up"] * W_PERC
TEXT_SPACING = CONFIG["play_configs"]["text_spacing"] * W_PERC
THE_PADDLE_HEIGHT_INCREASE = CONFIG["powerups"]["enlarge"] * W_PERC
PADDLE_WIDTH_INCREASE = 70 * W_PERC
PADDLE_SPEED_INCREASE = CONFIG["powerups"]["paddle_speed_increase"] * W_PERC
MID_LINES_COUNT = CONFIG["play_configs"]["mid_lines_count"]

PADDLE_SPACING = CONFIG["play_configs"]["paddle_spacing"] * W_PERC
RIGHT_PADDLE_SPACING = PADDLE_SPACING
LEFT_PADDLE_SPACING = PADDLE_SPACING

BALL_RADIUS = CONFIG["play_configs"]["ball_radius"] * W_PERC
SFX_VOLUME = CONFIG["settings"]["sfx_volume"]
WINNING_SCORE = CONFIG["play_configs"]["winning_score"]
RIGHT_SCORE_INCREASE_MULT = CONFIG["powerups"]["score_mult"]
LEFT_SCORE_INCREASE_MULT = CONFIG["powerups"]["score_mult"]

FREEZE_BALL_TIME = CONFIG["powerups"]["freeze_ball_time"] * TPS
SABOTAGE_TIME = CONFIG["powerups"]["sabotage_time"] * TPS

LEFT_PADDLE_SPEED_MULT = 1
RIGHT_PADDLE_SPEED_MULT = 1

LEFT_PADDLE_HEIGHT_MULT = 1
RIGHT_PADDLE_HEIGHT_MULT = 1

STARTSCREEN_BALL_Y_VEL_RANDOM_START = CONFIG["play_configs"]["startscreen_ball_y_vel_random_start"]
STARTSCREEN_BALL_Y_VEL_RANDOM_END = CONFIG["play_configs"]["startscreen_ball_y_vel_random_end"]


SABOTAGE_SPACING_INCREASE = CONFIG["powerups"]["sabotage_spacing_increase"] * W_PERC

SuperDreamFont = pygame.font.Font(".\\resources\\SuperDream-ax3vE.ttf", 22)
SuperDreamFont2 = pygame.font.Font(".\\resources\\SuperDream-ax3vE.ttf", 18)
SuperDreamFont3 = pygame.font.Font(".\\resources\\SuperDream-ax3vE.ttf", 24)
SuperDreamFont4 = pygame.font.Font(".\\resources\\SuperDream-ax3vE.ttf", 106)
SuperDreamFont5 = pygame.font.Font(".\\resources\\SuperDream-ax3vE.ttf", 40)

Press_space_sem = True
ball_going_right = True

FLAGS = pygame.HWSURFACE | pygame.DOUBLEBUF