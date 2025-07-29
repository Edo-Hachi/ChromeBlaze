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
from GameLogger import logger

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
        
        # カーソル色管理システム（Phase 2追加）
        self.cursor_colors = {
            LockOnState.IDLE: pyxel.COLOR_WHITE,     # アイドル状態: 白色
            LockOnState.STANDBY: pyxel.COLOR_GREEN,  # スタンバイ状態: 緑色
            LockOnState.COOLDOWN: pyxel.COLOR_YELLOW, # クールダウン状態: 黄色
            LockOnState.SHOOTING: pyxel.COLOR_GRAY   # 発射中状態: グレー
        }
        
        # クールダウンシステム（Phase 3追加）
        self.COOLDOWN_FRAMES = 30  # 30フレーム = 0.5秒（60FPS想定）
        
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
        
        # Phase 5: Sキー発射機能を削除（A離しシステムに置換）
        # 旧Sキー発射システムは完全に削除
        
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
        
        # Phase 6: 状態整合性チェック（デバッグ時のみ）
        # 本番では無効化可能
        # self._check_state_consistency()
        
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
        """ロックオンカーソルの描画（Phase 2: 状態依存色管理）"""
        cursor_x = self.x
        cursor_y = self.y + self.cursor_offset_y
        
        # 状態に応じたカーソル色を取得
        cursor_color = self.cursor_colors.get(self.lock_state, pyxel.COLOR_WHITE)
        
        # エネミー上にいる場合は色を強調（赤色）
        if is_cursor_on_enemy and self.lock_state == LockOnState.STANDBY:
            cursor_color = pyxel.COLOR_RED
        
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
                    logger.player_action(f"Legacy: Locked Enemy ID: {enemy.enemy_id} (Total: {len(self.lock_enemy_list)})")
                else:
                    logger.warning(f"Legacy: Lock list is full! ({self.max_lock_count} enemies)")
                break
    
    def get_cursor_position(self):
        """カーソル位置を取得"""
        return self.x, self.y + self.cursor_offset_y
    
    def is_cursor_on_enemy(self, enemy_manager):
        """カーソルがエネミー上にあるかチェック（Phase 2: 状態依存制御）"""
        # STANDBY状態でのみコリジョンチェックを実行
        if self.lock_state != LockOnState.STANDBY:
            return False
        
        from Common import check_collision
        
        cursor_x, cursor_y = self.get_cursor_position()
        
        for enemy in enemy_manager.get_active_enemies():
            if check_collision(cursor_x, cursor_y, self.cursor_size, self.cursor_size,
                             enemy.x, enemy.y, 8, 8):
                return True
        return False
    
    def _fire_homing_lasers(self, enemy_manager):
        """
        DEPRECATED: Phase 5で削除 - A離しシステム(_fire_homing_lasers_on_release)に置換
        """
        """ロックオンしたエネミーにホーミングレーザーを発射"""
        if not self.lock_enemy_list:
            logger.warning("Legacy: No locked targets!")
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
                logger.warning(f"Max laser limit reached! Fired {fired_count} of {len(self.lock_enemy_list)} locked targets")
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
                
                logger.laser_event(f"Legacy: Created laser for Enemy ID {enemy_id} at ({target_x:.1f}, {target_y:.1f}) (scatter: {scatter_x:+.1f}, {scatter_y:+.1f})")
        
        # 全レーザーを一括でメインリストに追加
        self.homing_lasers.extend(new_lasers)
        
        logger.laser_event(f"Legacy: Multi-lock fired! {fired_count} lasers to targets: {self.lock_enemy_list}")
        
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
                        logger.laser_event(f"Enemy {laser.target_enemy_id} hit by laser!")
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
        ロックオン状態遷移管理（Phase 3: クールダウン付き版）
        """
        # 現在のAキー押下状態を取得
        a_pressed = pyxel.btn(pyxel.KEY_A)
        a_just_pressed = a_pressed and not self.was_a_pressed    # 押した瞬間
        a_just_released = not a_pressed and self.was_a_pressed  # 離した瞬間
        
        if a_just_pressed or a_just_released:
            logger.separator()
            logger.player_action(f"A input - pressed: {a_just_pressed}, released: {a_just_released}, state: {self.lock_state.value}")
        
        # 状態遷移処理
        if self.lock_state == LockOnState.IDLE:
            if a_just_pressed:
                # IDLE → STANDBY 遷移（A押下開始）
                self.lock_state = LockOnState.STANDBY
                logger.state_change("IDLE → STANDBY (A pressed)")
        
        elif self.lock_state == LockOnState.STANDBY:
            # STANDBYでのロックオン処理
            if enemy_manager:
                self._try_lock_enemy(enemy_manager)
            
            if a_just_released:
                # Phase 5: A離し時の発射システム
                logger.player_action(f"A released in STANDBY state. Lock list: {self.lock_enemy_list}")
                if len(self.lock_enemy_list) > 0:
                    # ロック中のエネミーがある場合: STANDBY → SHOOTING 遷移
                    target_count = len(self.lock_enemy_list)  # 発射前にカウント保存
                    self.lock_state = LockOnState.SHOOTING
                    logger.section("HOMING LASER FIRE")
                    logger.laser_event(f"About to fire {target_count} homing lasers")
                    logger.state_change(f"STANDBY → SHOOTING (A released, {target_count} targets)")
                    self._fire_homing_lasers_on_release(enemy_manager)
                else:
                    # ロック中のエネミーがない場合: STANDBY → IDLE 遷移
                    self.lock_state = LockOnState.IDLE
                    logger.state_change("STANDBY → IDLE (A released, no targets)")
        
        elif self.lock_state == LockOnState.COOLDOWN:
            # クールダウンタイマー更新
            self.cooldown_timer -= 1
            if self.cooldown_timer <= 0:
                # COOLDOWN → STANDBY 遷移（時間経過）
                self.lock_state = LockOnState.STANDBY
                logger.state_change("COOLDOWN → STANDBY (timer expired)")
            
            # クールダウン中でもA離しは有効
            if a_just_released:
                self.cooldown_timer = 0  # タイマーリセット
                
                # ロックがある場合はレーザー発射してからSHOOTING状態へ
                if len(self.lock_enemy_list) > 0:
                    target_count = len(self.lock_enemy_list)
                    self.lock_state = LockOnState.SHOOTING
                    logger.section("HOMING LASER FIRE")
                    logger.laser_event(f"About to fire {target_count} homing lasers (from COOLDOWN)")
                    logger.state_change(f"COOLDOWN → SHOOTING (A released, {target_count} targets)")
                    self._fire_homing_lasers_on_release(enemy_manager)
                else:
                    # ロックがない場合は直接IDLE
                    self.lock_state = LockOnState.IDLE
                    logger.state_change("COOLDOWN → IDLE (A released, no targets)")
        
        elif self.lock_state == LockOnState.SHOOTING:
            # Phase 5: SHOOTING状態の処理
            # すべてのホーミングレーザーがアクティブでなくなったらIDLE復帰
            active_lasers = [laser for laser in self.homing_lasers if laser.active]
            if len(active_lasers) == 0:
                self.lock_state = LockOnState.IDLE
                logger.state_change("SHOOTING → IDLE (all lasers finished)")
            
            # Phase 6: エッジケース処理 - SHOOTING中の入力制御
            # SHOOTING中はA押下/離しは無効（既に発射済みのため）
            if a_just_pressed:
                logger.debug("A press ignored during SHOOTING state")
            if a_just_released:
                logger.debug("A release ignored during SHOOTING state")
        
        # 前フレームのAキー状態を記録
        self.was_a_pressed = a_pressed
    
    def _try_lock_enemy(self, enemy_manager):
        """
        エネミーのロックオン試行（Phase 3: クールダウン付き）
        """
        from Common import check_collision
        
        cursor_x, cursor_y = self.get_cursor_position()
        
        for enemy in enemy_manager.get_active_enemies():
            if check_collision(cursor_x, cursor_y, self.cursor_size, self.cursor_size,
                             enemy.x, enemy.y, 8, 8):
                if len(self.lock_enemy_list) < self.max_lock_count:
                    # ロック成功
                    self.lock_enemy_list.append(enemy.enemy_id)
                    logger.player_action(f"Locked Enemy ID: {enemy.enemy_id} (Total: {len(self.lock_enemy_list)})")
                    
                    # STANDBY → COOLDOWN 遷移
                    self.lock_state = LockOnState.COOLDOWN
                    self.cooldown_timer = self.COOLDOWN_FRAMES
                    logger.state_change("STANDBY → COOLDOWN (enemy locked)")
                else:
                    logger.warning(f"Lock list is full! ({self.max_lock_count} enemies)")
                break
    
    def _fire_homing_lasers_on_release(self, enemy_manager):
        """
        Phase 5: A離し時のホーミングレーザー発射（新システム）
        """
        if not self.lock_enemy_list:
            logger.warning("No locked targets for A-release firing!")
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
                logger.warning(f"Max laser limit reached! Fired {fired_count} of {len(self.lock_enemy_list)} locked targets")
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
                
                logger.laser_event(f"A-release laser for Enemy ID {enemy_id} at ({target_x:.1f}, {target_y:.1f}) (scatter: {scatter_x:+.1f}, {scatter_y:+.1f})")
        
        # 全レーザーを一括でメインリストに追加
        self.homing_lasers.extend(new_lasers)
        
        logger.laser_event(f"A-release multi-lock fired! {fired_count} lasers to targets: {self.lock_enemy_list}")
        
        # 発射後にロックリストをクリア
        self.lock_enemy_list = []
    
    def _check_state_consistency(self):
        """
        Phase 6: 状態整合性チェック機能
        デバッグ時の状態不整合を検出
        """
        issues = []
        
        # ロック数とレーザー数の論理チェック
        if self.lock_state == LockOnState.SHOOTING and len(self.lock_enemy_list) > 0:
            issues.append("SHOOTING state with non-empty lock list")
        
        # クールダウンタイマーの範囲チェック
        if self.lock_state == LockOnState.COOLDOWN and self.cooldown_timer <= 0:
            issues.append("COOLDOWN state with invalid timer")
        elif self.lock_state != LockOnState.COOLDOWN and self.cooldown_timer > 0:
            issues.append("Non-COOLDOWN state with active timer")
        
        # レーザー状態のチェック
        active_laser_count = len([laser for laser in self.homing_lasers if laser.active])
        if self.lock_state == LockOnState.SHOOTING and active_laser_count == 0:
            issues.append("SHOOTING state with no active lasers")
        
        # 問題があればログ出力
        if issues:
            logger.warning(f"CONSISTENCY WARNING: {', '.join(issues)}")
            logger.debug(f"  State: {self.lock_state.value}, Locks: {len(self.lock_enemy_list)}, Timer: {self.cooldown_timer}, Lasers: {active_laser_count}")
        
        return len(issues) == 0