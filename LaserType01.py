#!/usr/bin/env python3
"""
LaserType01 - Homing Laser System for ChromeBlaze
ホーミングレーザーシステム
"""

import pyxel
import math
import random
from Common import DEBUG, SCREEN_WIDTH

class LaserType01:
    """方法1: 線形補間 + 角度制限（最軽量）"""
    
    def __init__(self, start_x, start_y, target_x, target_y, target_enemy_id=None):
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
        
        # ターゲット情報
        self.target_enemy_id = target_enemy_id
        self.initial_target_x = target_x
        self.initial_target_y = target_y
        
        # 初期方向をプレイヤー位置に基づいて設定
        screen_center_x = SCREEN_WIDTH // 2
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
            return True  # ヒットを示すフラグ
        
        # 画面外チェック
        if (self.x < -10 or self.x > SCREEN_WIDTH + 10 or 
            self.y < -10 or self.y > SCREEN_WIDTH + 10):
            if self.active:  # まだアクティブな場合のみログ出力
                self.active = False
                if DEBUG:
                    self._write_debug_log("OUT_OF_BOUNDS")
        
        return False
    
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
        head_x = int(self.x) - 2
        head_y = int(self.y) - 2
        pyxel.rect(head_x, head_y, 4, 4, pyxel.COLOR_YELLOW)
    
    def check_collision(self, enemy):
        """エネミーとのコリジョンチェック"""
        if not self.active or not enemy.active:
            return False
        
        # レーザーヘッドとエネミーの当たり判定
        laser_left = self.x - 2
        laser_right = self.x + 2
        laser_top = self.y - 2
        laser_bottom = self.y + 2
        
        enemy_left = enemy.x
        enemy_right = enemy.x + enemy.sprite_size
        enemy_top = enemy.y
        enemy_bottom = enemy.y + enemy.sprite_size
        
        # 矩形同士の衝突判定
        if (laser_right >= enemy_left and laser_left <= enemy_right and
            laser_bottom >= enemy_top and laser_top <= enemy_bottom):
            self.active = False
            return True
        
        return False
    
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
                
        except Exception as e:
            print(f"Debug log write error: {e}")