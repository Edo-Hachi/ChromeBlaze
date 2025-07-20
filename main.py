import pyxel
import logging
import sys
from Common import GameState, SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from SpriteManager import sprite_manager
from State_StudioLogo import StudioLogoState
from State_Title import TitleState
from State_Game import GamePlayState

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Game:
    def __init__(self):
        logging.info("Initializing Game")
        try:
            self.state = GameState.LOGO
            self.studio_logo_state = StudioLogoState()
            self.title_state = TitleState()
            self.game_state = GamePlayState()
            logging.info("Game initialization completed")
        except Exception as e:
            logging.error(f"Failed to initialize game: {e}")
            raise
        
    def update(self):
        try:
            if self.state == GameState.LOGO:
                new_state = self.studio_logo_state.update()
                if new_state != self.state:
                    logging.info(f"State transition: {self.state.value} -> {new_state.value}")
                    self.state = new_state
            elif self.state == GameState.TITLE:
                new_state = self.title_state.update()
                if new_state != self.state:
                    logging.info(f"State transition: {self.state.value} -> {new_state.value}")
                    self.state = new_state
            elif self.state == GameState.GAME:
                new_state = self.game_state.update()
                if new_state != self.state:
                    logging.info(f"State transition: {self.state.value} -> {new_state.value}")
                    self.state = new_state
        except Exception as e:
            logging.error(f"Error in game update: {e}")
    
    def draw(self):
        try:
            pyxel.cls(0)
            if self.state == GameState.LOGO:
                self.studio_logo_state.draw()
            elif self.state == GameState.TITLE:
                self.title_state.draw()
            elif self.state == GameState.GAME:
                self.game_state.draw()
        except Exception as e:
            logging.error(f"Error in game draw: {e}")
            pyxel.text(10, 10, f"Draw Error: {str(e)[:30]}", 8)

class App:
    def __init__(self):
        logging.info("Starting Chrome Blaze")
        try:
            pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Chrome Blaze", fps=FPS, display_scale=3)
            logging.info(f"Pyxel initialized: {SCREEN_WIDTH}x{SCREEN_HEIGHT}, FPS={FPS}")
            
            pyxel.load("my_resource.pyxres")
            logging.info("Pyxel resources loaded successfully")
            
            # スプライト管理システムの初期化確認
            try:
                sprite_count = len(sprite_manager.json_sprites)
                if sprite_count > 0:
                    logging.info(f"Sprite manager loaded {sprite_count} sprites from JSON")
                    # プレイヤースプライトの確認
                    player_sprites = [key for key, sprite in sprite_manager.json_sprites.items() 
                                    if sprite.get("NAME") == "PLAYER"]
                    logging.info(f"Found {len(player_sprites)} player sprites: {player_sprites}")
                else:
                    logging.warning("No sprites loaded - sprite rendering may fail")
            except Exception as e:
                logging.error(f"Sprite manager initialization error: {e}")
            
            self.game = Game()
            logging.info("Game instance created, starting main loop")
            pyxel.run(self.update, self.draw)
        except FileNotFoundError as e:
            logging.error(f"Resource file not found: {e}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Failed to initialize app: {e}")
            sys.exit(1)

    def update(self):
        try:
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                logging.info("User requested exit via ESC key")
                pyxel.quit()
            self.game.update()
        except Exception as e:
            logging.error(f"Critical error in update loop: {e}")
            pyxel.quit()

    def draw(self):
        try:
            self.game.draw()
        except Exception as e:
            logging.error(f"Critical error in draw loop: {e}")
            pyxel.cls(0)
            pyxel.text(10, 10, "CRITICAL ERROR", 8)

def main():
    try:
        App()
    except KeyboardInterrupt:
        logging.info("Game interrupted by user")
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()