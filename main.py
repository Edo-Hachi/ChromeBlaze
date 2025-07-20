import pyxel
from Common import GameState, SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from SpriteManager import sprite_manager
from State_StudioLogo import StudioLogoState
from State_Title import TitleState
from State_Game import GamePlayState

class Game:
    def __init__(self):
        self.state = GameState.LOGO
        self.studio_logo_state = StudioLogoState()
        self.title_state = TitleState()
        self.game_state = GamePlayState()
        
    def update(self):
        if self.state == GameState.LOGO:
            new_state = self.studio_logo_state.update()
            if new_state != self.state:
                self.state = new_state
        elif self.state == GameState.TITLE:
            new_state = self.title_state.update()
            if new_state != self.state:
                self.state = new_state
        elif self.state == GameState.GAME:
            new_state = self.game_state.update()
            if new_state != self.state:
                self.state = new_state
    
    def draw(self):
        if self.state == GameState.LOGO:
            self.studio_logo_state.draw()
        elif self.state == GameState.TITLE:
            self.title_state.draw()
        elif self.state == GameState.GAME:
            self.game_state.draw()

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Chrome Blaze", fps=FPS, display_scale=3)
        pyxel.load("my_resource.pyxres")
        self.game = Game()
        pyxel.run(self.update, self.draw)

    def update(self):
        self.game.update()

    def draw(self):
        self.game.draw()

App()