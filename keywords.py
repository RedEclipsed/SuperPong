from colored import Fore, Style

#Console Colors
c_red = Fore.red
c_blue = Fore.blue
c_green = Fore.green
c_white = Fore.white
c_yellow = Fore.yellow
c_rst = Style.reset

#Colors
class Colors:

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (210, 120, 120)
    GREEN = (0, 255, 0)
    BLUE = (120, 120, 210)
    DARKER_BLUE = (100, 100, 220)
    GRAY = (190, 190, 190)
    GRAY2 = (150, 150, 150)
    GRAY3 = (110, 110, 110)
    LIGHT_GRAY = (215, 215, 215)
    LIGHTER_GRAY = (245, 245, 245)
    DARK_GRAY = (100, 100, 110)
    VERY_DARK_GRAY = (50, 50, 50)
    WAY_TOO_DARK_GRAY = (38, 38, 38)

    MEGA_LIGHT_BLUE = (180, 180, 255)
    MEGA_LIGHT_RED = (255, 180, 180)
    BLUE_TINT = (190, 190, 220)
    RED_TINT = (220, 190, 190)
    BLUE_TINT_AUX = BLUE_TINT
    RED_TINT_AUX = RED_TINT

    BLUE_TINT2 = (170, 170, 190)
    RED_TINT2 = (190, 170, 170)

    MEGA_LIGHT_BLUE_AUX = MEGA_LIGHT_BLUE
    MEGA_LIGHT_BLUE_AUX2 = MEGA_LIGHT_BLUE

    MEGA_LIGHT_RED_AUX = MEGA_LIGHT_RED
    MEGA_LIGHT_RED_AUX2 = MEGA_LIGHT_RED

    SCREEN_FILL_COLOR = (10, 10, 15)
    SCREEN_FILL_COLOR_AUX = (10, 10, 15)

    BALL_COLOR = LIGHT_GRAY
    BALL_COLOR_AUX = LIGHT_GRAY

#Console Debugs
def print_warning(*txt):
    string = ""
    for substr in txt:
        string += str(substr) + " "
    print(f"{c_white}[{c_rst}{c_yellow}warning{c_rst}{c_white}]{c_rst} " + string)

def print_error(*txt):
    string = ""
    for substr in txt:
        string += str(substr) + " "
    print(f"{c_white}[{c_rst}{c_red}error{c_rst}{c_white}]{c_rst} " + string)

def print_debug(*txt):
    string = ""
    for substr in txt:
        string += str(substr) + " "
    print(f"{c_white}[{c_rst}{c_blue}debug{c_rst}{c_white}]{c_rst} " + string)

def print_success(*txt):
    string = ""
    for substr in txt:
        string += str(substr) + " "
    print(f"{c_white}[{c_rst}{c_green}success{c_rst}{c_white}]{c_rst} " + string)
