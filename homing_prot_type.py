#!/usr/bin/env python3
"""
Homing Laser Test Project - Pyxel Implementation
ホーミングレーザーテスト用のモックアッププロジェクト
"""

import pyxel
import math
import random
from SpriteManager import SpriteManager
from Common import DEBUG, check_collision

class Enemy:
    """エネミー管理クラス"""
    def __init__(self, enemy_id, x, y, sprite_size, screen_width, screen_height):
        self.enemy_id = enemy_id
        self.x = float(x)
        self.y = float(y)
        self.active = True
        self.sprite_size = sprite_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 移動設定
        self.speed = 25  # ピクセル/秒（さらに減速）
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # ランダム移動制御
        self.move_timer = 0.0
        self.direction_duration = 3.0  # 3秒間同じ方向
        
        # 初期方向設定
        self._generate_random_direction()
    
    def _generate_random_direction(self):
        """3秒間持続するランダムな移動方向を生成"""
        import random
        # ランダムな角度（0-360度）
        angle = random.uniform(0, 2 * math.pi)
        
        # 速度ベクトルを計算
        self.velocity_x = math.cos(angle) * self.speed
        self.velocity_y = math.sin(angle) * self.speed
    
    def update(self, delta_time):
        """エネミーの更新"""
        if not self.active:
            return
        
        # ランダム移動タイマー更新
        self.move_timer += delta_time
        
        # 3秒ごとに新しいランダム方向を生成
        if self.move_timer >= self.direction_duration:
            self.move_timer = 0.0
            self._generate_random_direction()
        
        # 位置更新
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        
        # 画面端での境界チェック（反射）
        if self.x <= 0:
            self.x = 0
            self.velocity_x = abs(self.velocity_x)  # 右向きに反転
        elif self.x >= self.screen_width - self.sprite_size:
            self.x = self.screen_width - self.sprite_size
            self.velocity_x = -abs(self.velocity_x)  # 左向きに反転
            
        if self.y <= 0:
            self.y = 0
            self.velocity_y = abs(self.velocity_y)  # 下向きに反転
        elif self.y >= self.screen_height // 2:  # 画面上半分に制限
            self.y = self.screen_height // 2
            self.velocity_y = -abs(self.velocity_y)  # 上向きに反転
    
    def draw(self, sprite_manager, sprite_size):
        """エネミーの描画"""
        if not self.active:
            return
        
        # ENEMY01スプライト（フレーム0）を表示
        enemy_sprite = sprite_manager.get_sprite_by_name_and_field("ENEMY01", "FRAME_NUM", "0")
        if enemy_sprite:
            pyxel.blt(int(self.x), int(self.y), 0, enemy_sprite.x, enemy_sprite.y, 
                     sprite_size, sprite_size, pyxel.COLOR_BLACK)

class EnemyManager:
    """エネミー群管理クラス"""
    def __init__(self, sprite_size, screen_width, screen_height):
        self.enemies = []
        self.sprite_size = sprite_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 5体のエネミーを生成
        self._spawn_enemies()
    
    def _spawn_enemies(self):
        """5体のエネミーを異なる位置に配置"""
        import random
        
        positions = [
            (50, 30),   # 左上
            (150, 40),  # 右上
            (100, 60),  # 中央上
            (80, 80),   # 左中
            (180, 70)   # 右中
        ]
        
        for i, (x, y) in enumerate(positions):
            enemy = Enemy(i, x, y, self.sprite_size, self.screen_width, self.screen_height)
            self.enemies.append(enemy)
    
    def update(self, delta_time):
        """全エネミーの更新"""
        for enemy in self.enemies:
            enemy.update(delta_time)
    
    def draw(self, sprite_manager):
        """全エネミーの描画"""
        for enemy in self.enemies:
            enemy.draw(sprite_manager, self.sprite_size)
    
    def get_active_enemies(self):
        """アクティブなエネミーのリストを取得"""
        return [enemy for enemy in self.enemies if enemy.active]
    
    def get_enemy_by_id(self, enemy_id):
        """IDでエネミーを取得"""
        for enemy in self.enemies:
            if enemy.enemy_id == enemy_id:
                return enemy
        return None

class LaserType01:
    """方法1: 線形補間 + 角度制限（最軽量）"""
    
    def __init__(self, start_x, start_y, target_x, target_y):
        # レーザー設定
        self.speed = 500.0  # ピクセル/秒（50%スピードアップ）
        self.turn_speed_slow = 8.0  # 初期：ゆっくり旋回（ラジアン/秒）
        self.turn_speed_fast = 20.0  # 後半：急旋回（ラジアン/秒）
        self.transition_distance = 150.0  # 切り替え距離（ピクセル）
        self.max_trail_length = 30  # 軌跡の最大長
        
        # 位置と方向
        self.x = float(start_x)
        self.y = float(start_y)
        self.target_x = target_x
        self.target_y = target_y
        
        # 初期方向をプレイヤー位置に基づいて設定
        screen_center_x = 128  # 256 / 2
        if start_x > screen_center_x:
            # 右側にいる場合：右向きで発射
            self.direction_x = 1.0
            self.direction_y = 0.0
        elif start_x < screen_center_x:
            # 左側にいる場合：左向きで発射
            self.direction_x = -1.0
            self.direction_y = 0.0
        else:
            # 中央にいる場合：上向きで発射
            self.direction_x = 0.0
            self.direction_y = -1.0
        
        # 軌跡
        self.trail = [(self.x, self.y)]
        
        # アクティブ状態
        self.active = True
        
        # デバッグ情報（DEBUGフラグで制御）
        if DEBUG:
            self.debug_log = []
            self.frame_count = 0
        else:
            self.debug_log = None
            self.frame_count = 0
    
    def update(self, delta_time, target_x, target_y):
        """レーザーの更新"""
        if not self.active:
            return
        
        # ターゲット位置を更新
        self.target_x = target_x
        self.target_y = target_y
        
        # ターゲットへの方向を計算
        to_target_x = self.target_x - self.x
        to_target_y = self.target_y - self.y
        distance = math.sqrt(to_target_x * to_target_x + to_target_y * to_target_y)
        
        if distance > 0:
            # 正規化
            to_target_x /= distance
            to_target_y /= distance
            
            # 現在の方向からターゲット方向への角度差を計算
            current_angle = math.atan2(self.direction_y, self.direction_x)
            target_angle = math.atan2(to_target_y, to_target_x)
            
            # 角度差を -π から π の範囲に正規化
            angle_diff = target_angle - current_angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # 距離に基づいて旋回速度を調整
            current_turn_speed = self.turn_speed_slow
            if distance < self.transition_distance:
                # 近づくほど急旋回に切り替え
                ratio = 1.0 - (distance / self.transition_distance)
                current_turn_speed = self.turn_speed_slow + (self.turn_speed_fast - self.turn_speed_slow) * ratio
            
            # 角度制限を適用
            max_turn = current_turn_speed * delta_time
            if abs(angle_diff) > max_turn:
                angle_diff = math.copysign(max_turn, angle_diff)
            
            # 新しい方向を計算
            new_angle = current_angle + angle_diff
            self.direction_x = math.cos(new_angle)
            self.direction_y = math.sin(new_angle)
        
        # 位置を更新
        self.x += self.direction_x * self.speed * delta_time
        self.y += self.direction_y * self.speed * delta_time
        
        # デバッグ情報を記録（DEBUGフラグで制御）
        if DEBUG and self.debug_log is not None:
            current_angle = math.atan2(self.direction_y, self.direction_x)
            turn_mode = "slow" if distance >= self.transition_distance else "fast"
            self.debug_log.append({
                'frame': self.frame_count,
                'x': round(self.x, 2),
                'y': round(self.y, 2),
                'angle_rad': round(current_angle, 4),
                'angle_deg': round(math.degrees(current_angle), 2),
                'distance_to_target': round(distance, 2),
                'turn_mode': turn_mode,
                'turn_speed': round(current_turn_speed, 4)
            })
        self.frame_count += 1
        
        # 軌跡に追加
        self.trail.append((self.x, self.y))
        
        # 軌跡の長さ制限
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
        
        # ターゲットに近づいたらヒット
        if distance < 12:
            self.active = False
            if DEBUG:
                self._write_debug_log("HIT")
        
        # 画面外チェックでもログ出力
        if (self.x < -10 or self.x > 266 or 
            self.y < -10 or self.y > 266):
            if self.active:  # まだアクティブな場合のみログ出力
                if DEBUG:
                    self._write_debug_log("OUT_OF_BOUNDS")
    
    def draw(self):
        """レーザーの描画"""
        if not self.active or len(self.trail) < 2:
            return
        
        # 軌跡を線で描画
        for i in range(len(self.trail) - 1):
            start_x, start_y = self.trail[i]
            end_x, end_y = self.trail[i + 1]
            
            # 透明度効果（古い軌跡ほど薄く）
            alpha_ratio = i / len(self.trail)
            if alpha_ratio > 0.3:  # 薄すぎる部分はスキップ
                pyxel.line(int(start_x), int(start_y), int(end_x), int(end_y), pyxel.COLOR_CYAN)
        
        # レーザーヘッド（8x8の矩形）
        head_x = int(self.x) - 4
        head_y = int(self.y) - 4
        pyxel.rect(head_x, head_y, 8, 8, pyxel.COLOR_YELLOW)
    
    def _write_debug_log(self, end_reason):
        """デバッグログをファイルに書き出し（DEBUGフラグで制御）"""
        if not DEBUG or self.debug_log is None:
            return
            
        import datetime
        
        try:
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"\n## Laser Hit Event - {datetime.datetime.now().strftime('%H:%M:%S')}\n")
                f.write(f"- End Reason: {end_reason}\n")
                f.write(f"- Total Frames: {len(self.debug_log)}\n")
                
                # f.write("## Laser Movement Data\n\n")
                # f.write("| Frame | X | Y | Angle(rad) | Angle(deg) | Distance | Turn Mode | Turn Speed |\n")
                # f.write("|-------|---|---|------------|------------|----------|-----------|------------|\n")
                
                # for entry in self.debug_log:
                #     f.write(f"| {entry['frame']:3d} | {entry['x']:6.2f} | {entry['y']:6.2f} | {entry['angle_rad']:7.4f} | {entry['angle_deg']:7.2f} | {entry['distance_to_target']:6.2f} | {entry['turn_mode']:4s} | {entry['turn_speed']:7.4f} |\n")
                
                # f.write(f"\n## Analysis\n\n")
                # f.write(f"- Start Position: ({self.debug_log[0]['x']}, {self.debug_log[0]['y']})\n")
                # f.write(f"- End Position: ({self.debug_log[-1]['x']}, {self.debug_log[-1]['y']})\n")
                # f.write(f"- Final Distance to Target: {self.debug_log[-1]['distance_to_target']:.2f}px\n")
                
                # slow_frames = sum(1 for entry in self.debug_log if entry['turn_mode'] == 'slow')
                # fast_frames = len(self.debug_log) - slow_frames
                # f.write(f"- Slow Turn Frames: {slow_frames}\n")
                # f.write(f"- Fast Turn Frames: {fast_frames}\n")
                
        except Exception as e:
            print(f"Debug log write error: {e}")

class HomingLaserTest:
    def __init__(self):
        # ウィンドウ設定
        self.WIDTH = 256
        self.HEIGHT = 256
        
        # リソース設定
        self.RESOURCE_FILE = "./my_resource.pyxres"
        self.SPRITE_SIZE = 8
        
        # スプライトマネージャー初期化
        self.sprite_manager = SpriteManager()
        
        # Pyxelを初期化
        pyxel.init(self.WIDTH, self.HEIGHT, title="Homing Laser Test", fps=60)
        pyxel.load(self.RESOURCE_FILE)
        
        # プレイヤー設定
        self.player_x = self.WIDTH // 2 - self.SPRITE_SIZE // 2
        self.player_y = 196 #self.HEIGHT // 2 - self.SPRITE_SIZE // 2
        
        # エネミー管理システム
        self.enemy_manager = EnemyManager(self.SPRITE_SIZE, self.WIDTH, self.HEIGHT)
        
        # ホーミングレーザー設定（連射対応）
        self.lasers = []  # レーザーリスト
        self.max_lasers = 10  # 最大レーザー数
        
        # ロックオンカーソル設定
        self.cursor_offset_y = -60  # プレイヤーからのY座標オフセット
        self.cursor_size = 8  # カーソルのサイズ
        self.is_cursor_on_enemy = False  # カーソルがエネミー上にあるかどうか
        
        # ロックオンエネミーリスト
        self.lock_enemy_list = []  # ロックオンしたエネミーIDのリスト
        self.max_lock_count = self.max_lasers  # 最大ロック数はレーザー最大数と同じ
        
        
        # テスト用メッセージ
        self.message = "PLAYER vs ENEMY01 Test"
        self.test_status = f"Loaded {len(self.sprite_manager.json_sprites)} sprites"
        
        pyxel.run(self.update, self.draw)
    
    def update(self):
        """ゲームロジックの更新"""
        # ESCキーで終了
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        
        # カーソルキーでプレイヤー移動
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x = max(0, self.player_x - 2)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x = min(self.WIDTH - self.SPRITE_SIZE, self.player_x + 2)
        if pyxel.btn(pyxel.KEY_UP):
            self.player_y = max(0, self.player_y - 2)
        if pyxel.btn(pyxel.KEY_DOWN):
            self.player_y = min(self.HEIGHT - self.SPRITE_SIZE, self.player_y + 2)
        
        # スペースキーでホーミングレーザー発射（連射対応）
        # if pyxel.btnp(pyxel.KEY_SPACE):
        #     # 非アクティブなレーザーを削除
        #     self.lasers = [laser for laser in self.lasers if laser.active]
        #     
        #     # 最大レーザー数に達していなければ発射（最初のアクティブなエネミーを狙う）
        #     if len(self.lasers) < self.max_lasers:
        #         active_enemies = self.enemy_manager.get_active_enemies()
        #         if active_enemies:
        #             target_enemy = active_enemies[0]  # とりあえず最初のエネミーを狙う
        #             start_x = self.player_x + self.SPRITE_SIZE // 2
        #             start_y = self.player_y
        #             target_x = target_enemy.x + self.SPRITE_SIZE // 2
        #             target_y = target_enemy.y + self.SPRITE_SIZE // 2
        #             
        #             new_laser = LaserType01(start_x, start_y, target_x, target_y)
        #             self.lasers.append(new_laser)
        
        # Xキーでロックオンしたエネミーに一斉レーザー発射
        if pyxel.btnp(pyxel.KEY_X):
            if self.lock_enemy_list:
                # 非アクティブなレーザーを削除
                self.lasers = [laser for laser in self.lasers if laser.active]
                
                base_start_x = self.player_x + self.SPRITE_SIZE // 2
                base_start_y = self.player_y
                
                # 発射するレーザーのリストを一時保存
                new_lasers = []
                fired_count = 0
                
                for enemy_id in self.lock_enemy_list:
                    # レーザー数制限チェック
                    if len(self.lasers) + len(new_lasers) >= self.max_lasers:
                        print(f"Max laser limit reached! Fired {fired_count} of {len(self.lock_enemy_list)} locked targets")
                        break
                    
                    # エネミーIDからエネミーオブジェクトを取得
                    target_enemy = self.enemy_manager.get_enemy_by_id(enemy_id)
                    if target_enemy and target_enemy.active:
                        # ベース座標にランダムなばらつきを追加
                        base_x = target_enemy.x + self.SPRITE_SIZE // 2
                        base_y = target_enemy.y + self.SPRITE_SIZE // 2
                        
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
                        
                        new_laser = LaserType01(start_x, start_y, target_x, target_y)
                        # デバッグ用：レーザーにターゲットIDを記録
                        new_laser.target_enemy_id = enemy_id
                        new_laser.initial_target_x = target_x
                        new_laser.initial_target_y = target_y
                        
                        new_lasers.append(new_laser)
                        fired_count += 1
                        
                        print(f"DEBUG: Created laser for Enemy ID {enemy_id} at ({target_x:.1f}, {target_y:.1f}) (scatter: {scatter_x:+.1f}, {scatter_y:+.1f})")
                
                # 全レーザーを一括でメインリストに追加
                self.lasers.extend(new_lasers)
                
                print(f"Multi-lock fired! {fired_count} lasers to targets: {self.lock_enemy_list}")
                
                # 発射時のデバッグ情報を記録
                print(f"DEBUG: Calling _write_fire_debug with {len(self.lock_enemy_list)} targets")
                self._write_fire_debug(self.lock_enemy_list, fired_count, new_lasers)
                
                # 発射後にロックリストをクリア
                self.lock_enemy_list = []
            else:
                print("No locked targets!")
        
        # エネミー管理システムの更新
        delta_time = 1.0 / 60.0  # 60FPS想定
        self.enemy_manager.update(delta_time)
        
        # ロックオンカーソルとエネミーのコリジョン判定（全エネミーをチェック）
        cursor_x = self.player_x
        cursor_y = self.player_y + self.cursor_offset_y
        
        self.is_cursor_on_enemy = False
        locked_enemy = None
        
        for enemy in self.enemy_manager.get_active_enemies():
            if check_collision(cursor_x, cursor_y, self.cursor_size, self.cursor_size,
                             enemy.x, enemy.y, self.SPRITE_SIZE, self.SPRITE_SIZE):
                self.is_cursor_on_enemy = True
                locked_enemy = enemy
                # print(f"Lock! Enemy ID: {enemy.enemy_id}")  # コメントアウト
                
                # Zキーが押されていたらロックオンリストに追加
                if pyxel.btnp(pyxel.KEY_Z):
                    if len(self.lock_enemy_list) < self.max_lock_count:
                        self.lock_enemy_list.append(enemy.enemy_id)
                        print(f"Locked Enemy ID: {enemy.enemy_id} (Total: {len(self.lock_enemy_list)})")
                        
                        # ロック時のデバッグ情報を記録
                        print(f"DEBUG: Calling _write_lock_debug for Enemy {enemy.enemy_id}")
                        self._write_lock_debug(enemy.enemy_id, enemy.x, enemy.y)
                    else:
                        print(f"Lock list is full! ({self.max_lock_count} enemies)")
                break
        
        # 全レーザーの更新（各レーザーが専用ターゲットを追尾）
        for laser in self.lasers:
            if laser.active and hasattr(laser, 'target_enemy_id'):
                # 各レーザーが自分専用のエネミーを追尾
                target_enemy = self.enemy_manager.get_enemy_by_id(laser.target_enemy_id)
                if target_enemy and target_enemy.active:
                    target_x = target_enemy.x + self.SPRITE_SIZE // 2
                    target_y = target_enemy.y + self.SPRITE_SIZE // 2
                    laser.update(delta_time, target_x, target_y)
                else:
                    # ターゲットが非アクティブになった場合は直進
                    laser.update(delta_time, laser.target_x, laser.target_y)
            elif laser.active:
                # 古いレーザー（ターゲットIDなし）は最初のエネミーを追尾
                active_enemies = self.enemy_manager.get_active_enemies()
                if active_enemies:
                    target_enemy = active_enemies[0]
                    target_x = target_enemy.x + self.SPRITE_SIZE // 2
                    target_y = target_enemy.y + self.SPRITE_SIZE // 2
                    laser.update(delta_time, target_x, target_y)
        
        # 非アクティブなレーザーを定期的に削除
        self.lasers = [laser for laser in self.lasers if laser.active]
    
    def draw(self):
        """描画処理"""
        # 背景をクリア（黒）
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # PLAYERスプライト（TOP固定）を表示
        player_sprite = self.sprite_manager.get_sprite_by_name_and_field("PLAYER", "ACT_NAME", "TOP")
        if player_sprite:
            pyxel.blt(self.player_x, self.player_y, 0, player_sprite.x, player_sprite.y, 
                     self.SPRITE_SIZE, self.SPRITE_SIZE, pyxel.COLOR_BLACK)
        
        # 全エネミーの描画
        self.enemy_manager.draw(self.sprite_manager)
        
        # 全ホーミングレーザーの描画
        for laser in self.lasers:
            if laser.active:
                laser.draw()
        
        # ロックオンカーソルの描画（プレイヤーと同期）
        cursor_x = self.player_x
        cursor_y = self.player_y + self.cursor_offset_y
        cursor_color = pyxel.COLOR_RED if self.is_cursor_on_enemy else pyxel.COLOR_GREEN
        pyxel.rectb(cursor_x, cursor_y, self.cursor_size, self.cursor_size, cursor_color)
        
        # テストメッセージを上部に表示
        text_x = (self.WIDTH - len(self.message) * 4) // 2
        pyxel.text(text_x, 10, self.message, pyxel.COLOR_WHITE)
        
        # プレイヤー位置を表示
        position_info = f"Player: ({self.player_x}, {self.player_y})"
        info_x = (self.WIDTH - len(position_info) * 4) // 2
        pyxel.text(info_x, 25, position_info, pyxel.COLOR_CYAN)
        
        # エネミー数の表示
        active_count = len(self.enemy_manager.get_active_enemies())
        enemy_info = f"Enemies: {active_count}/5"
        enemy_info_x = (self.WIDTH - len(enemy_info) * 4) // 2
        pyxel.text(enemy_info_x, 35, enemy_info, pyxel.COLOR_RED)
        
        # テストステータスを表示
        status_x = (self.WIDTH - len(self.test_status) * 4) // 2
        pyxel.text(status_x, 40, self.test_status, pyxel.COLOR_GREEN)
        
        # 操作説明
        controls = [
            "Arrow Keys: Move player",
            "Z: Lock-on enemy (when cursor on enemy)",
            "X: Fire multi-lock lasers",
            "Q/ESC: Quit"
        ]
        for i, control in enumerate(controls):
            control_x = (self.WIDTH - len(control) * 4) // 2
            control_y = self.HEIGHT - 40 + i * 10
            pyxel.text(control_x, control_y, control, pyxel.COLOR_GRAY)
        
        # レーザー状態表示
        active_lasers = len([laser for laser in self.lasers if laser.active])
        total_lasers = len(self.lasers)
        
        if active_lasers > 0:
            laser_color = pyxel.COLOR_GREEN
            status_text = f"Lasers: {active_lasers}/{self.max_lasers}"
        else:
            laser_color = pyxel.COLOR_GRAY
            status_text = f"Lasers: {active_lasers}/{self.max_lasers}"
        
        pyxel.text(10, self.HEIGHT - 15, status_text, laser_color)
        
        # ロックオンリスト状態表示
        lock_count = len(self.lock_enemy_list)
        if lock_count > 0:
            lock_color = pyxel.COLOR_YELLOW
            lock_text = f"Locked: {lock_count}/{self.max_lock_count} IDs:{self.lock_enemy_list}"
        else:
            lock_color = pyxel.COLOR_GRAY
            lock_text = f"Locked: {lock_count}/{self.max_lock_count}"
        
        pyxel.text(10, self.HEIGHT - 5, lock_text, lock_color)
    
    def _write_lock_debug(self, enemy_id, enemy_x, enemy_y):
        """ロック時のデバッグ情報をdebug.logに追記"""
        print(f"DEBUG: _write_lock_debug called, DEBUG={DEBUG}")
        if not DEBUG:
            print(f"DEBUG: Skipping because DEBUG is False")
            return
            
        import datetime
        
        try:
            print(f"DEBUG: Opening debug.log for append")
            with open("debug.log", "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                f.write(f"\n## Lock Event - {timestamp}\n")
                f.write(f"- Enemy ID: {enemy_id}\n")
                f.write(f"- Enemy Position: ({enemy_x:.2f}, {enemy_y:.2f})\n")
                f.write(f"- Lock List: {self.lock_enemy_list}\n")
                print(f"DEBUG: Lock debug written successfully")
                
        except Exception as e:
            print(f"Lock debug write error: {e}")
    
    def _write_fire_debug(self, lock_list, fired_count, fired_lasers):
        """発射時のデバッグ情報をdebug.logに追記"""
        print(f"DEBUG: _write_fire_debug called, DEBUG={DEBUG}")
        if not DEBUG:
            print(f"DEBUG: Skipping fire debug because DEBUG is False")
            return
            
        import datetime
        
        try:
            print(f"DEBUG: Opening debug.log for fire debug append")
            with open("debug.log", "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                f.write(f"\n## Fire Event - {timestamp}\n")
                f.write(f"- Lock List: {lock_list}\n")
                f.write(f"- Fired Count: {fired_count}\n")
                f.write(f"- Target Details:\n")
                
                for i, (enemy_id, laser) in enumerate(zip(lock_list, fired_lasers)):
                    # 実際に発射されたレーザーの座標を使用
                    target_x = laser.initial_target_x
                    target_y = laser.initial_target_y
                    f.write(f"  - Laser {i+1}: Enemy ID {enemy_id} at ({target_x:.2f}, {target_y:.2f})\n")
                        
                print(f"DEBUG: Fire debug written successfully")
                
        except Exception as e:
            print(f"Fire debug write error: {e}")

if __name__ == "__main__":
    HomingLaserTest()