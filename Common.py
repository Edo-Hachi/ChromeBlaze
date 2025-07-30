from enum import Enum

DEBUG = False

#Pyxel Color Pallet
#   0: pyxel.COLOR_BLACK     # 黒
#   1: pyxel.COLOR_NAVY      # 濃い青
#   2: pyxel.COLOR_PURPLE    # 紫
#   3: pyxel.COLOR_GREEN     # 緑
#   4: pyxel.COLOR_BROWN     # 茶色
#   5: pyxel.COLOR_DARK_BLUE # 暗い青
#   6: pyxel.COLOR_LIGHT_BLUE# 水色
#   7: pyxel.COLOR_WHITE     # 白
#   8: pyxel.COLOR_RED       # 赤
#   9: pyxel.COLOR_ORANGE    # オレンジ
#   10: pyxel.COLOR_YELLOW   # 黄色
#   11: pyxel.COLOR_LIME     # ライムグリーン
#   12: pyxel.COLOR_CYAN     # シアン
#   13: pyxel.COLOR_GRAY     # グレー
#   14: pyxel.COLOR_PINK     # ピンク
#   15: pyxel.COLOR_PEACH    # ピーチ




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
DISPLAY_SCALE = 5


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
