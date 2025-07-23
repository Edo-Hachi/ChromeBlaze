import pyxel
from Common import GameState, SCREEN_WIDTH, SCREEN_HEIGHT
from SpriteManager import sprite_manager
from Player import Player
from Enemy import EnemyManager
import math

class GamePlayState:
    def __init__(self):
        self.stage = 1
        self.frame_count = 0
        self.player = Player(SCREEN_WIDTH // 2 - 4, SCREEN_HEIGHT - 30)
        
        # エネミー管理システム
        self.enemy_manager = EnemyManager(8, SCREEN_WIDTH, SCREEN_HEIGHT)
        
    def update(self):
        self.frame_count += 1
        
        if pyxel.btnp(pyxel.KEY_Q):
            return GameState.TITLE
            
        # エネミー管理システムの更新
        delta_time = 1.0 / 60.0  # 60FPS想定
        self.enemy_manager.update(delta_time)
        
        # プレイヤーの更新（エネミー管理システムを渡す）
        self.player.update(self.enemy_manager)
        
        return GameState.GAME
    
    def draw(self):
        pyxel.cls(pyxel.COLOR_NAVY)
        
        # プレイヤーとエネミーの描画
        self.player.draw()
        self.player.draw_bullets(self.frame_count)
        self.player.draw_homing_lasers()
        self.enemy_manager.draw(sprite_manager)
        self.player.draw_hit_effects()
        
        # ロックオンカーソルの描画
        is_cursor_on_enemy = self.player.is_cursor_on_enemy(self.enemy_manager)
        self.player.draw_lock_cursor(is_cursor_on_enemy)
        
        # UI表示
        pyxel.text(10, 10, f"Stage: {self.stage}", pyxel.COLOR_WHITE)
        pyxel.text(10, 20, f"Power Level: {self.player.power_level}", pyxel.COLOR_WHITE)
        
        # エネミー数の表示
        active_count = len(self.enemy_manager.get_active_enemies())
        pyxel.text(10, 30, f"Enemies: {active_count}/5", pyxel.COLOR_RED)
        
        # ロックオンリスト状態表示
        lock_count = len(self.player.lock_enemy_list)
        if lock_count > 0:
            lock_color = pyxel.COLOR_YELLOW
            lock_text = f"Locked: {lock_count}/{self.player.max_lock_count} IDs:{self.player.lock_enemy_list}"
        else:
            lock_color = pyxel.COLOR_GRAY
            lock_text = f"Locked: {lock_count}/{self.player.max_lock_count}"
        pyxel.text(10, 40, lock_text, lock_color)
        
        # Phase 4: ロック数表示システム (n/10) - 改良版UI
        if lock_count > 0:
            # ロックオン中は大きく目立つ表示
            lock_display_color = pyxel.COLOR_CYAN
            lock_display_text = f"({lock_count}/10)"
            # 中央上部に配置
            display_x = SCREEN_WIDTH // 2 - 20
            display_y = 20
            pyxel.text(display_x, display_y, lock_display_text, lock_display_color)
        
        # Phase 4: ロックオン状態表示（デバッグ・ユーザーフィードバック用）
        state_text = f"Lock State: {self.player.lock_state.value.upper()}"
        state_color = self.player.cursor_colors.get(self.player.lock_state, pyxel.COLOR_WHITE)
        pyxel.text(10, 60, state_text, state_color)
        
        # クールダウンタイマー表示（COOLDOWN状態時のみ）
        if self.player.lock_state.value == "cooldown":
            cooldown_text = f"Cooldown: {self.player.cooldown_timer}/30"
            pyxel.text(10, 70, cooldown_text, pyxel.COLOR_YELLOW)
        
        # レーザー状態表示
        active_lasers = len([laser for laser in self.player.homing_lasers if laser.active])
        if active_lasers > 0:
            laser_color = pyxel.COLOR_GREEN
            laser_status = f"Lasers: {active_lasers}/{self.player.max_lasers}"
        else:
            laser_color = pyxel.COLOR_GRAY
            laser_status = f"Lasers: {active_lasers}/{self.player.max_lasers}"
        pyxel.text(10, 50, laser_status, laser_color)
        
        # 操作説明（Phase 5: 新インターフェイス対応）
        pyxel.text(10, 90, "Arrow Keys: Move", pyxel.COLOR_YELLOW)
        pyxel.text(10, 100, "Z: Shoot", pyxel.COLOR_YELLOW)
        pyxel.text(10, 110, "X: Power Up", pyxel.COLOR_YELLOW)
        pyxel.text(10, 120, "A Hold: Lock-on enemies", pyxel.COLOR_CYAN)
        pyxel.text(10, 130, "A Release: Fire homing", pyxel.COLOR_CYAN)
        pyxel.text(10, 140, "Q: Return to Title", pyxel.COLOR_YELLOW)
