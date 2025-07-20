import pyxel
from Common import GameState, SCREEN_WIDTH, SCREEN_HEIGHT

class StudioLogoState:
    def __init__(self):
        self.frame_count = 0
        
    def update(self):
        self.frame_count += 1
        
        if pyxel.btnp(pyxel.KEY_SPACE):
            return GameState.TITLE
        
        return GameState.LOGO
    
    def draw(self):
        pyxel.cls(0)
        
        # Nekoya Studio logo
        logo_text = "Nekoya Studio"
        logo_width = len(logo_text) * 4
        logo_x = (SCREEN_WIDTH - logo_width) // 2
        pyxel.text(logo_x, 100, logo_text, 7)
        
        # Push Space Key (blinking)
        if (self.frame_count // 30) % 2 == 0:
            prompt_text = "Push Space Key"
            prompt_width = len(prompt_text) * 4
            prompt_x = (SCREEN_WIDTH - prompt_width) // 2
            pyxel.text(prompt_x, 150, prompt_text, 10)