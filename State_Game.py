import pyxel
from Common import GameState, SCREEN_WIDTH, SCREEN_HEIGHT

class GamePlayState:
    def __init__(self):
        self.frame_count = 0
        
    def update(self):
        self.frame_count += 1
        
        if pyxel.btnp(pyxel.KEY_Q):
            return GameState.TITLE
        
        return GameState.GAME
    
    def draw(self):
        pyxel.cls(2)
        pyxel.text(10, 10, "Game Screen (Q to return)", 7)