import pyxel
from Common import GameState, SCREEN_WIDTH, SCREEN_HEIGHT
from SpriteManager import sprite_manager

class StudioLogoState:
    def __init__(self):
        self.frame_count = 0
        
    def update(self):
        self.frame_count += 1
        
        if pyxel.btnp(pyxel.KEY_SPACE):
            return GameState.TITLE
        
        return GameState.LOGO
    
    def draw(self):
        pyxel.cls(pyxel.COLOR_NAVY)
        
        # Nekoya Studio logo
        logo_text = "Nekoya Studio"
        logo_width = len(logo_text) * 4
        logo_x = (SCREEN_WIDTH - logo_width) // 2
        pyxel.text(logo_x, 100, logo_text, pyxel.COLOR_WHITE)
        
        # スプライトテスト: プレイヤー機を画面中央に表示
        try:
            player_sprite = sprite_manager.get_sprite_by_name_and_field("PLAYER", "ACT_NAME", "TOP")
            player_x = (SCREEN_WIDTH - 8) // 2
            player_y = 80
            pyxel.blt(player_x, player_y, 0, player_sprite.x, player_sprite.y, 8, 8, pyxel.COLOR_BLACK)
            
            # スプライト情報表示
            sprite_info = f"Sprite: {player_sprite.x},{player_sprite.y}"
            pyxel.text(10, 10, sprite_info, pyxel.COLOR_WHITE)
        except Exception as e:
            # エラー時はフォールバック描画
            player_x = (SCREEN_WIDTH - 8) // 2
            player_y = 80
            pyxel.rect(player_x, player_y, 8, 8, pyxel.COLOR_WHITE)
            pyxel.text(10, 10, f"Sprite Error: {str(e)[:20]}", pyxel.COLOR_RED)
        
        # Push Space Key (blinking)
        if (self.frame_count // 30) % 2 == 0:
            prompt_text = "Push Space Key"
            prompt_width = len(prompt_text) * 4
            prompt_x = (SCREEN_WIDTH - prompt_width) // 2
            pyxel.text(prompt_x, 150, prompt_text, pyxel.rndi(0, 15))
