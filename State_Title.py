import pyxel
from Common import GameState, SCREEN_WIDTH, SCREEN_HEIGHT

class TitleState:
    def __init__(self):
        self.frame_count = 0
        
    def update(self):
        self.frame_count += 1
        
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_SPACE):
            return GameState.GAME
        
        return GameState.TITLE
    
    def draw(self):
        pyxel.cls(pyxel.COLOR_NAVY)
        
        # Chrome Blaze title
        title_text = "Chrome Blaze"
        title_width = len(title_text) * 4
        title_x = (SCREEN_WIDTH - title_width) // 2
        pyxel.text(title_x, 80, title_text, pyxel.COLOR_WHITE)
        
        # Menu options
        pyxel.text(100, 120, "Space: Start Game", pyxel.COLOR_YELLOW)
        pyxel.text(100, 140, "Q: Quit", pyxel.COLOR_RED)