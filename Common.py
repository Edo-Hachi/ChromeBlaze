from enum import Enum

DEBUG = False

# Game States
class GameState(Enum):
    LOGO = "logo"
    TITLE = "title"
    GAME = "game"

# Game Constants
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 128
FPS = 60
SPRITE_SIZE = 8

# Colors
# COLOR_BLACK = 0
# COLOR_NAVY = 1
# COLOR_PURPLE = 2
# COLOR_GREEN = 3
# COLOR_BROWN = 4
# COLOR_DARK_BLUE = 5
# COLOR_LIGHT_BLUE = 6
# COLOR_WHITE = 7
# COLOR_RED = 8
# COLOR_ORANGE = 9
# COLOR_YELLOW = 10
# COLOR_LIME = 11
# COLOR_CYAN = 12
# COLOR_GRAY = 13
# COLOR_PINK = 14
# COLOR_PEACH = 15


def check_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    """AABB collision detection"""
    left1 = x1
    right1 = x1 + w1
    top1 = y1
    bottom1 = y1 + h1

    left2 = x2
    right2 = x2 + w2
    top2 = y2
    bottom2 = y2 + h2

    is_collision = (
        left1 < right2 and
        right1 > left2 and
        top1 < bottom2 and
        bottom1 > top2
    )

    return is_collision
