#!/usr/bin/env python3
"""
Player Management System for ChromeBlaze
プレイヤー管理システム
"""

import pyxel
import math
import random
from Common import SCREEN_WIDTH, SCREEN_HEIGHT
from SpriteManager import sprite_manager
from LaserType01 import LaserType01
from HitEffect import HitEffectManager
from LockOnState import LockOnState

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
        
        # ロックオンシステム
        self.lock_enemy_list = []  # ロックオンしたエネミーIDのリスト
        self.max_lock_count = 10  # 最大ロック数
        self.cursor_offset_y = -60  # プレイヤーからのY座標オフセット
        self.cursor_size = 8  # カーソルのサイズ
        
        # ホーミングレーザーシステム
        self.homing_lasers = []  # ホーミングレーザーリスト
        self.max_lasers = 10  # 最大レーザー数
        
        # ヒットエフェクトシステム
        self.hit_effect_manager = HitEffectManager()
        
        # ロックオン状態管理システム（Phase 1追加）
        self.lock_state = LockOnState.IDLE  # 初期状態はIDLE
        self.was_a_pressed = False  # 前フレームのAキー押下状態
        self.cooldown_timer = 0  # クールダウンタイマー（フレーム数）
        
    def update(self, enemy_manager=None):
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
        
        # 通常ショット処理（クールダウン制御）
        if pyxel.btn(pyxel.KEY_Z) and self.shot_cooldown == 0:
            self.shoot()
            self.shot_cooldown = self.shot_cooldown_duration  # クールダウン開始
        
        # ロックオン状態管理システム（Phase 1: 基本遷移）
        self._handle_lock_on_state_transitions(enemy_manager)
        
        # ホーミングレーザー発射処理（Sキー）
        if pyxel.btnp(pyxel.KEY_S) and enemy_manager:
            self._fire_homing_lasers(enemy_manager)
        
        # 弾丸の更新
        for bullet in self.bullets:
            bullet.update()
        
        # 非アクティブな弾丸を削除
        self.bullets = [bullet for bullet in self.bullets if bullet.active]
        
        # ホーミングレーザーの更新
        if enemy_manager:
            self._update_homing_lasers(enemy_manager)
        
        # ヒットエフェクトの更新
        self.hit_effect_manager.update()
        
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
    
    def draw_homing_lasers(self):
        """ホーミングレーザーの描画"""
        for laser in self.homing_lasers:
            if laser.active:
                laser.draw()
    
    def draw_hit_effects(self):
        """ヒットエフェクトの描画"""
        self.hit_effect_manager.draw()
    
    def draw_lock_cursor(self, is_cursor_on_enemy):
        """ロックオンカーソルの描画"""
        cursor_x = self.x
        cursor_y = self.y + self.cursor_offset_y
        cursor_color = pyxel.COLOR_RED if is_cursor_on_enemy else pyxel.COLOR_GREEN
        pyxel.rectb(cursor_x, cursor_y, self.cursor_size, self.cursor_size, cursor_color)
    
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
    
    def _handle_lock_on(self, enemy_manager):
        """ロックオン処理"""
        from Common import check_collision
        
        cursor_x = self.x
        cursor_y = self.y + self.cursor_offset_y
        
        for enemy in enemy_manager.get_active_enemies():
            if check_collision(cursor_x, cursor_y, self.cursor_size, self.cursor_size,
                             enemy.x, enemy.y, 8, 8):
                if len(self.lock_enemy_list) < self.max_lock_count:
                    self.lock_enemy_list.append(enemy.enemy_id)
                    print(f"Locked Enemy ID: {enemy.enemy_id} (Total: {len(self.lock_enemy_list)})")
                else:
                    print(f"Lock list is full! ({self.max_lock_count} enemies)")
                break
    
    def get_cursor_position(self):
        """カーソル位置を取得"""
        return self.x, self.y + self.cursor_offset_y
    
    def is_cursor_on_enemy(self, enemy_manager):
        """カーソルがエネミー上にあるかチェック"""
        from Common import check_collision
        
        cursor_x, cursor_y = self.get_cursor_position()
        
        for enemy in enemy_manager.get_active_enemies():
            if check_collision(cursor_x, cursor_y, self.cursor_size, self.cursor_size,
                             enemy.x, enemy.y, 8, 8):
                return True
        return False
    
    def _fire_homing_lasers(self, enemy_manager):
        """ロックオンしたエネミーにホーミングレーザーを発射"""
        if not self.lock_enemy_list:
            print("No locked targets!")
            return
        
        # 非アクティブなレーザーを削除
        self.homing_lasers = [laser for laser in self.homing_lasers if laser.active]
        
        base_start_x = self.x + self.width // 2
        base_start_y = self.y
        
        # 発射するレーザーのリストを一時保存
        new_lasers = []
        fired_count = 0
        
        for enemy_id in self.lock_enemy_list:
            # レーザー数制限チェック
            if len(self.homing_lasers) + len(new_lasers) >= self.max_lasers:
                print(f"Max laser limit reached! Fired {fired_count} of {len(self.lock_enemy_list)} locked targets")
                break
            
            # エネミーIDからエネミーオブジェクトを取得
            target_enemy = enemy_manager.get_enemy_by_id(enemy_id)
            if target_enemy and target_enemy.active:
                # ベース座標にランダムなばらつきを追加
                base_x = target_enemy.x + target_enemy.sprite_size // 2
                base_y = target_enemy.y + target_enemy.sprite_size // 2
                
                # ±500ピクセルの大幅なばらつき（画面外も含む）
                scatter_range = 500
                # 各レーザーで異なるランダム値を確実に生成
                scatter_x = random.uniform(-scatter_range, scatter_range)
                scatter_y = random.uniform(-scatter_range, scatter_range)
                target_x = base_x + scatter_x
                target_y = base_y + scatter_y
                
                # 発射位置も少しばらつかせる（±10ピクセル）
                start_scatter = 10
                start_x = base_start_x + random.uniform(-start_scatter, start_scatter)
                start_y = base_start_y + random.uniform(-start_scatter, start_scatter)
                
                new_laser = LaserType01(start_x, start_y, target_x, target_y, enemy_id)
                new_lasers.append(new_laser)
                fired_count += 1
                
                print(f"DEBUG: Created laser for Enemy ID {enemy_id} at ({target_x:.1f}, {target_y:.1f}) (scatter: {scatter_x:+.1f}, {scatter_y:+.1f})")
        
        # 全レーザーを一括でメインリストに追加
        self.homing_lasers.extend(new_lasers)
        
        print(f"Multi-lock fired! {fired_count} lasers to targets: {self.lock_enemy_list}")
        
        # 発射後にロックリストをクリア
        self.lock_enemy_list = []
    
    def _update_homing_lasers(self, enemy_manager):
        """ホーミングレーザーの更新"""
        delta_time = 1.0 / 60.0  # 60FPS想定
        
        for laser in self.homing_lasers:
            if laser.active and hasattr(laser, 'target_enemy_id'):
                # 各レーザーが自分専用のエネミーを追尾
                target_enemy = enemy_manager.get_enemy_by_id(laser.target_enemy_id)
                if target_enemy and target_enemy.active:
                    target_x = target_enemy.x + target_enemy.sprite_size // 2
                    target_y = target_enemy.y + target_enemy.sprite_size // 2
                    hit = laser.update(delta_time, target_x, target_y)
                    
                    # コリジョンチェック
                    if laser.check_collision(target_enemy):
                        # ヒットエフェクトを追加
                        effect_x = target_enemy.x + target_enemy.sprite_size // 2
                        effect_y = target_enemy.y + target_enemy.sprite_size // 2
                        self.hit_effect_manager.add_effect(effect_x, effect_y)
                        
                        enemy_manager.remove_enemy(laser.target_enemy_id)
                        print(f"Enemy {laser.target_enemy_id} hit by laser!")
                else:
                    # ターゲットが非アクティブになった場合は直進
                    laser.update(delta_time, laser.target_position.x, laser.target_position.y)
            elif laser.active:
                # 古いレーザー（ターゲットIDなし）は最初のエネミーを追尾
                active_enemies = enemy_manager.get_active_enemies()
                if active_enemies:
                    target_enemy = active_enemies[0]
                    target_x = target_enemy.x + target_enemy.sprite_size // 2
                    target_y = target_enemy.y + target_enemy.sprite_size // 2
                    laser.update(delta_time, target_x, target_y)
        
        # 非アクティブになったレーザーのログ出力（テレメトリーシステムで処理済み）
    # テレメトリーシステムに移行したため、ここでのログ処理は不要
        
        # 非アクティブなレーザーを定期的に削除
        self.homing_lasers = [laser for laser in self.homing_lasers if laser.active]
    
    def _get_exhaust_animation_duration(self):
        """エグゾーストアニメーションの持続時間を取得する"""
        try:
            anim_spd = sprite_manager.get_sprite_metadata("EXHST", "ANIM_SPD", "10")
            return int(anim_spd)
        except (ValueError, TypeError):
            return 10  # デフォルト値
    
    def _handle_lock_on_state_transitions(self, enemy_manager):
        """
        ロックオン状態遷移管理（Phase 1: 基本IDLE↔STANDBY遷移）
        """
        # 現在のAキー押下状態を取得
        a_pressed = pyxel.btn(pyxel.KEY_A)
        
        # 状態遷移処理
        if self.lock_state == LockOnState.IDLE:
            if a_pressed:
                # IDLE → STANDBY 遷移
                self.lock_state = LockOnState.STANDBY
                print(f"State transition: IDLE → STANDBY")
        
        elif self.lock_state == LockOnState.STANDBY:
            if not a_pressed and self.was_a_pressed:
                # STANDBY → IDLE 遷移（A離し）
                self.lock_state = LockOnState.IDLE
                print(f"State transition: STANDBY → IDLE")
        
        # 前フレームのAキー状態を記録
        self.was_a_pressed = a_pressed