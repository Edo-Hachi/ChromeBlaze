import pyxel
from Common import GameState, SCREEN_WIDTH, SCREEN_HEIGHT
from SpriteManager import sprite_manager
import math

class Bullet:

    def _get_animation_speed(self):
        """JSONからアニメーション速度を取得する"""
        try:
            anim_spd = sprite_manager.get_sprite_metadata("PBULLET", "ANIM_SPD", "10")
            return int(anim_spd)
        except (ValueError, TypeError):
            return 10
    
    def _get_animation_frame(self, game_timer):
        """ゲームタイマーに基づいてアニメーションフレームを計算する（最適化済み）"""
        cycle_position = game_timer % self.animation_cycle  # 事前計算済み値を使用
        return 0 if cycle_position < self.animation_speed else 1

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8
        self.speed = 3
        self.active = True
        
        # アニメーション設定とスプライトキャッシュ
        self.animation_speed = self._get_animation_speed()
        self.animation_cycle = self.animation_speed * 2  # 事前計算でパフォーマンス最適化
        self.bullet_sprites = [
            sprite_manager.get_sprite_by_name_and_field("PBULLET", "FRAME_NUM", "0"),
            sprite_manager.get_sprite_by_name_and_field("PBULLET", "FRAME_NUM", "1")
        ]
        
    def update(self):
        self.y -= self.speed
        
        # 画面上部を超えたら削除
        if self.y < -8:
            self.active = False
    
    def draw(self, game_timer):
        try:
            # アニメーションフレーム計算（最適化済み）
            anim_frame = self._get_animation_frame(game_timer)
            bullet_sprite = self.bullet_sprites[anim_frame]
            
            pyxel.blt(self.x, self.y, 0, bullet_sprite.x, bullet_sprite.y,
                     self.width, self.height, pyxel.COLOR_BLACK)
        except Exception as e:
            # フォールバック: 白い矩形
            pyxel.rect(self.x, self.y, self.width, self.height, pyxel.COLOR_WHITE)
    

    

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8
        self.speed = 2

        self.DIAGONAL_NORMALIZE = 0.707  # 1/√2 の近似値
        
        
        # スプライト管理
        self.sprite_direction = "TOP"  # TOP/LEFT/RIGHT
        
        # スプライトキャッシュ（初期化時に一括取得）
        self.sprites = {
            "TOP": sprite_manager.get_sprite_by_name_and_field("PLAYER", "ACT_NAME", "TOP"),
            "LEFT": sprite_manager.get_sprite_by_name_and_field("PLAYER", "ACT_NAME", "LEFT"),
            "RIGHT": sprite_manager.get_sprite_by_name_and_field("PLAYER", "ACT_NAME", "RIGHT")
        }
        
        # エグゾーストスプライトキャッシュ
        self.exhaust_sprites = [
            sprite_manager.get_sprite_by_name_and_field("EXHST", "FRAME_NUM", "0"),
            sprite_manager.get_sprite_by_name_and_field("EXHST", "FRAME_NUM", "1"),
            sprite_manager.get_sprite_by_name_and_field("EXHST", "FRAME_NUM", "2"),
            sprite_manager.get_sprite_by_name_and_field("EXHST", "FRAME_NUM", "3")
        ]
        
        # エグゾーストアニメーション管理
        self.exhaust_index = 0
        self.exhaust_timer = 0
        self.exhaust_duration = self._get_exhaust_animation_duration()
        
        # ショット管理
        self.bullets = []
        self.shot_cooldown = 0  # ショットクールダウンタイマー
        self.shot_cooldown_duration = 10  # 10フレーム間隔（60FPS時0.167秒）
        
        # パワーレベルシステム
        self.power_level = 0  # 0: 1発, 1: 2発
        
    def update(self):
        # ショットクールダウン更新
        if self.shot_cooldown > 0:
            self.shot_cooldown -= 1
            
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
            dx *= self.DIAGONAL_NORMALIZE #=0.707
            dy *= self.DIAGONAL_NORMALIZE #=0.707
            
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # 画面境界制限
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
        
        # パワーレベル変更（テスト用）
        if pyxel.btnp(pyxel.KEY_X):
            self.power_level = (self.power_level + 1) % 2  # 0と1を切り替え
        
        # ショット処理（クールダウン制御）
        if pyxel.btn(pyxel.KEY_Z) and self.shot_cooldown == 0:
            self.shoot()
            self.shot_cooldown = self.shot_cooldown_duration  # クールダウン開始
        
        # 弾丸の更新
        for bullet in self.bullets:
            bullet.update()
        
        # 非アクティブな弾丸を削除
        self.bullets = [bullet for bullet in self.bullets if bullet.active]
        
    def draw(self):
        try:
            # プレイヤー機のスプライト描画（キャッシュから取得）
            player_sprite = self.sprites[self.sprite_direction]
            pyxel.blt(self.x, self.y, 0, player_sprite.x, player_sprite.y, 
                     self.width, self.height, pyxel.COLOR_BLACK)
            
            # エグゾーストアニメーション描画（キャッシュから取得）
            exhaust_sprite = self.exhaust_sprites[self.exhaust_index]
            pyxel.blt(self.x, self.y + 8, 0, exhaust_sprite.x, exhaust_sprite.y,
                     self.width, self.height, pyxel.COLOR_BLACK)
                     
        except Exception as e:
            # フォールバック: 矩形描画
            pyxel.rect(self.x, self.y, self.width, self.height, pyxel.COLOR_WHITE)
            pyxel.rect(self.x + 2, self.y + 2, 4, 4, pyxel.COLOR_CYAN)
    
    def draw_bullets(self, game_timer):
        """弾丸の描画"""
        for bullet in self.bullets:
            bullet.draw(game_timer)
    
    def shoot(self):
        """パワーレベルに応じて弾丸を発射する"""
        bullet_y = self.y - 4  # プレイヤーの少し上から発射
        
        if self.power_level == 0:
            # Power Level 0: 1発発射（中央）
            bullet_x = self.x
            self.bullets.append(Bullet(bullet_x, bullet_y))
        elif self.power_level == 1:
            # Power Level 1: 2発発射（左右）
            bullet_x1 = self.x - 4
            bullet_x2 = self.x + 4
            self.bullets.append(Bullet(bullet_x1, bullet_y))
            self.bullets.append(Bullet(bullet_x2, bullet_y))
    
    
    
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
        self.player.draw_bullets(self.frame_count)
        
        pyxel.text(10, 10, f"Stage: {self.stage}", pyxel.COLOR_WHITE)
        pyxel.text(10, 20, f"Power Level: {self.player.power_level}", pyxel.COLOR_WHITE)
        pyxel.text(10, 30, "Arrow Keys: Move", pyxel.COLOR_YELLOW)
        pyxel.text(10, 40, "Z: Shoot", pyxel.COLOR_YELLOW)
        pyxel.text(10, 50, "X: Power Up", pyxel.COLOR_YELLOW)
        pyxel.text(10, 60, "Q: Return to Title", pyxel.COLOR_YELLOW)
