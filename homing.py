#!/usr/bin/env python3
"""
Homing Laser Test Project - Pyxel Implementation
ホーミングレーザーテスト用のモックアッププロジェクト
"""

import pyxel
import math
from SpriteManager import SpriteManager
from Common import DEBUG

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
            with open("debug.md", "w", encoding="utf-8") as f:
                f.write("# Laser Debug Log\n\n")
                f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"End Reason: {end_reason}\n")
                f.write(f"Total Frames: {len(self.debug_log)}\n\n")
                
                f.write("## Laser Movement Data\n\n")
                f.write("| Frame | X | Y | Angle(rad) | Angle(deg) | Distance | Turn Mode | Turn Speed |\n")
                f.write("|-------|---|---|------------|------------|----------|-----------|------------|\n")
                
                for entry in self.debug_log:
                    f.write(f"| {entry['frame']:3d} | {entry['x']:6.2f} | {entry['y']:6.2f} | {entry['angle_rad']:7.4f} | {entry['angle_deg']:7.2f} | {entry['distance_to_target']:6.2f} | {entry['turn_mode']:4s} | {entry['turn_speed']:7.4f} |\n")
                
                f.write(f"\n## Analysis\n\n")
                f.write(f"- Start Position: ({self.debug_log[0]['x']}, {self.debug_log[0]['y']})\n")
                f.write(f"- End Position: ({self.debug_log[-1]['x']}, {self.debug_log[-1]['y']})\n")
                f.write(f"- Final Distance to Target: {self.debug_log[-1]['distance_to_target']:.2f}px\n")
                
                slow_frames = sum(1 for entry in self.debug_log if entry['turn_mode'] == 'slow')
                fast_frames = len(self.debug_log) - slow_frames
                f.write(f"- Slow Turn Frames: {slow_frames}\n")
                f.write(f"- Fast Turn Frames: {fast_frames}\n")
                
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
        
        # エネミー設定
        self.enemy_x = self.WIDTH // 2 - self.SPRITE_SIZE // 2
        self.enemy_y = 50
        
        # ホーミングレーザー設定
        self.laser = None  # レーザーインスタンス
        
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
        
        # 1キーでLaserType01発射
        if pyxel.btnp(pyxel.KEY_1):
            if self.laser is None or not self.laser.active:
                start_x = self.player_x + self.SPRITE_SIZE // 2
                start_y = self.player_y
                target_x = self.enemy_x + self.SPRITE_SIZE // 2
                target_y = self.enemy_y + self.SPRITE_SIZE // 2
                self.laser = LaserType01(start_x, start_y, target_x, target_y)
        
        # レーザーの更新
        if self.laser and self.laser.active:
            delta_time = 1.0 / 60.0  # 60FPS想定
            target_x = self.enemy_x + self.SPRITE_SIZE // 2
            target_y = self.enemy_y + self.SPRITE_SIZE // 2
            self.laser.update(delta_time, target_x, target_y)
    
    def draw(self):
        """描画処理"""
        # 背景をクリア（黒）
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # PLAYERスプライト（TOP固定）を表示
        player_sprite = self.sprite_manager.get_sprite_by_name_and_field("PLAYER", "ACT_NAME", "TOP")
        if player_sprite:
            pyxel.blt(self.player_x, self.player_y, 0, player_sprite.x, player_sprite.y, 
                     self.SPRITE_SIZE, self.SPRITE_SIZE, pyxel.COLOR_BLACK)
        
        # ENEMY01スプライト（フレーム0）を表示
        enemy_sprite = self.sprite_manager.get_sprite_by_name_and_field("ENEMY01", "FRAME_NUM", "0")
        if enemy_sprite:
            pyxel.blt(self.enemy_x, self.enemy_y, 0, enemy_sprite.x, enemy_sprite.y, 
                     self.SPRITE_SIZE, self.SPRITE_SIZE, pyxel.COLOR_BLACK)
        
        # ホーミングレーザーの描画
        if self.laser and self.laser.active:
            self.laser.draw()
        
        # テストメッセージを上部に表示
        text_x = (self.WIDTH - len(self.message) * 4) // 2
        pyxel.text(text_x, 10, self.message, pyxel.COLOR_WHITE)
        
        # プレイヤー位置を表示
        position_info = f"Player: ({self.player_x}, {self.player_y})"
        info_x = (self.WIDTH - len(position_info) * 4) // 2
        pyxel.text(info_x, 25, position_info, pyxel.COLOR_CYAN)
        
        # エネミー位置を表示
        enemy_info = f"Enemy: ({self.enemy_x}, {self.enemy_y})"
        enemy_info_x = (self.WIDTH - len(enemy_info) * 4) // 2
        pyxel.text(enemy_info_x, 35, enemy_info, pyxel.COLOR_RED)
        
        # テストステータスを表示
        status_x = (self.WIDTH - len(self.test_status) * 4) // 2
        pyxel.text(status_x, 40, self.test_status, pyxel.COLOR_GREEN)
        
        # 操作説明
        controls = [
            "Arrow Keys: Move player",
            "1: Fire LaserType01",
            "Q/ESC: Quit"
        ]
        for i, control in enumerate(controls):
            control_x = (self.WIDTH - len(control) * 4) // 2
            control_y = self.HEIGHT - 40 + i * 10
            pyxel.text(control_x, control_y, control, pyxel.COLOR_GRAY)
        
        # レーザー状態表示
        if self.laser:
            laser_status = "Active" if self.laser.active else "Inactive"
            laser_color = pyxel.COLOR_GREEN if self.laser.active else pyxel.COLOR_RED
        else:
            laser_status = "None"
            laser_color = pyxel.COLOR_GRAY
        
        status_text = f"Laser: {laser_status}"
        pyxel.text(10, self.HEIGHT - 15, status_text, laser_color)

if __name__ == "__main__":
    HomingLaserTest()