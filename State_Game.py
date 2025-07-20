import pyxel
from Common import GameState, SCREEN_WIDTH, SCREEN_HEIGHT
from SpriteManager import sprite_manager
import math

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8
        self.speed = 2
        
        # スプライト管理
        self.sprite_direction = "TOP"  # TOP/LEFT/RIGHT
        
        # エグゾーストアニメーション管理
        self.exhaust_index = 0
        self.exhaust_timer = 0
        self.exhaust_duration = self._get_exhaust_animation_duration()
        
    def update(self):
        # エグゾーストアニメーション更新
        self.exhaust_timer += 1
        if self.exhaust_timer >= self.exhaust_duration:
            self.exhaust_timer = 0
            self.exhaust_index += 1
            if self.exhaust_index >= 4:  # EXHST has 4 frames (0-3)
                self.exhaust_index = 0
        
        # 移動処理
        self.sprite_direction = "TOP"  # デフォルト
        dx = 0
        dy = 0
        
        if pyxel.btn(pyxel.KEY_LEFT):
            dx -= 1
            self.sprite_direction = "LEFT"
        if pyxel.btn(pyxel.KEY_RIGHT):
            dx += 1
            self.sprite_direction = "RIGHT"
        if pyxel.btn(pyxel.KEY_UP):
            dy -= 1
        if pyxel.btn(pyxel.KEY_DOWN):
            dy += 1
            
        # 斜め移動時の速度正規化
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
            
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # 画面境界制限
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
        
    def draw(self):
        try:
            # プレイヤー機のスプライト描画
            player_sprite = self._get_player_sprite()
            pyxel.blt(self.x, self.y, 0, player_sprite.x, player_sprite.y, 
                     self.width, self.height, pyxel.COLOR_BLACK)
            
            # エグゾーストアニメーション描画
            exhaust_sprite = self._get_exhaust_sprite()
            pyxel.blt(self.x, self.y + 8, 0, exhaust_sprite.x, exhaust_sprite.y,
                     self.width, self.height, pyxel.COLOR_BLACK)
                     
        except Exception as e:
            # フォールバック: 矩形描画
            pyxel.rect(self.x, self.y, self.width, self.height, pyxel.COLOR_WHITE)
            pyxel.rect(self.x + 2, self.y + 2, 4, 4, pyxel.COLOR_CYAN)
    
    def _get_player_sprite(self):
        """プレイヤーの現在のスプライトを取得する"""
        return sprite_manager.get_sprite_by_name_and_field("PLAYER", "ACT_NAME", self.sprite_direction)
    
    def _get_exhaust_sprite(self):
        """エグゾーストの現在のスプライトを取得する"""
        return sprite_manager.get_sprite_by_name_and_field("EXHST", "FRAME_NUM", str(self.exhaust_index))
    
    def _get_exhaust_animation_duration(self):
        """エグゾーストアニメーションの持続時間を取得する"""
        try:
            anim_spd = sprite_manager.get_sprite_metadata("EXHST", "ANIM_SPD", "10")
            return int(anim_spd)
        except (ValueError, TypeError):
            return 10  # デフォルト値

class GamePlayState:
    def __init__(self):
        self.stage = 1
        self.frame_count = 0
        self.player = Player(SCREEN_WIDTH // 2 - 4, SCREEN_HEIGHT - 30)
        
    def update(self):
        self.frame_count += 1
        
        if pyxel.btnp(pyxel.KEY_Q):
            return GameState.TITLE
            
        self.player.update()
        
        return GameState.GAME
    
    def draw(self):
        pyxel.cls(pyxel.COLOR_NAVY)
        
        self.player.draw()
        
        pyxel.text(10, 10, f"Stage: {self.stage}", pyxel.COLOR_WHITE)
        pyxel.text(10, 20, "Arrow Keys: Move", pyxel.COLOR_YELLOW)
        pyxel.text(10, 30, "Q: Return to Title", pyxel.COLOR_YELLOW)
