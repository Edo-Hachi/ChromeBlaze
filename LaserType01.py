#!/usr/bin/env python3
"""
LaserType01 - Homing Laser System for ChromeBlaze
ホーミングレーザーシステム
"""

import pyxel
import math
import random
from Common import SCREEN_WIDTH
from LaserConfig import LaserConfig, default_laser_config
from LaserTelemetry import LaserTelemetry

class LaserType01:
    """方法1: 線形補間 + 角度制限（最軽量）"""
    
    def __init__(self, start_x, start_y, target_x, target_y, target_enemy_id=None, config: LaserConfig = None):
        # 設定の取得（カスタム設定がない場合はデフォルトを使用）
        if config is None:
            config = default_laser_config
        
        # 設定をインスタンス変数として保持
        self.config = config
        
        # レーザー設定（dataclassから取得）
        # === 物理演算パラメータ ===
        self.initial_speed = config.initial_speed      # 発射時の初期速度（ピクセル/秒）
        self.min_speed = config.min_speed              # 減速時の最低速度（ピクセル/秒）
        self.speed = self.initial_speed                # 現在の速度（フレーム毎に更新）
        self.speed_decay = config.speed_decay          # フレーム毎の減速量（ピクセル/秒）
        
        # === ホーミング制御パラメータ ===
        self.turn_speed_slow = config.turn_speed_slow  # 遠距離時の旋回速度（ラジアン/秒）
        self.turn_speed_fast = config.turn_speed_fast  # 近距離時の旋回速度（ラジアン/秒）
        self.transition_distance = config.transition_distance  # 旋回速度切り替え距離（ピクセル）
        
        # === 表示・軌跡パラメータ ===
        self.max_trail_length = config.max_trail_length  # 軌跡の最大表示点数
        
        # === 判定パラメータ ===
        self.hit_threshold = config.hit_threshold        # ヒット判定距離（100%命中保証用）
        self.collision_threshold = config.collision_threshold  # コリジョン判定距離
        
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
        
        # テレメトリーシステム
        self.telemetry = LaserTelemetry()
        self.frame_count = 0
    
    def update(self, delta_time, target_x, target_y):
        """レーザーの更新（分解版）"""
        if not self.active:
            return False
        
        # ターゲット位置を更新
        self._update_target_position(target_x, target_y)
        
        # ホーミング計算
        distance, current_turn_speed = self._calculate_homing_direction(delta_time)
        
        # 物理演算
        self._apply_speed_decay()
        self._update_position(delta_time)
        
        # デバッグ・軌跡更新
        self._update_debug_and_trail(distance, current_turn_speed)
        
        # 判定処理
        return self._check_hit_and_boundaries(distance)
    
    def _update_target_position(self, target_x, target_y):
        """ターゲット位置の更新"""
        self.target_x = target_x
        self.target_y = target_y
    
    def _calculate_homing_direction(self, delta_time):
        """ホーミング方向計算"""
        # ターゲットへの方向を計算
        to_target_x = self.target_x - self.x
        to_target_y = self.target_y - self.y
        distance = math.sqrt(to_target_x * to_target_x + to_target_y * to_target_y)
        current_turn_speed = 0.0
        
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
        
        return distance, current_turn_speed
    
    def _apply_speed_decay(self):
        """速度減速処理"""
        if self.speed > self.min_speed:
            self.speed -= self.speed_decay
            if self.speed < self.min_speed:
                self.speed = self.min_speed
    
    def _update_position(self, delta_time):
        """位置更新"""
        self.x += self.direction_x * self.speed * delta_time
        self.y += self.direction_y * self.speed * delta_time
    
    def _update_debug_and_trail(self, distance, current_turn_speed):
        """デバッグ情報と軌跡の更新"""
        # テレメトリーデータを記録
        to_target_x = (self.target_x - self.x) / distance if distance > 0 else 0
        to_target_y = (self.target_y - self.y) / distance if distance > 0 else 0
        
        laser_data = {
            'laser_pos': (round(self.x, 2), round(self.y, 2)),
            'target_pos': (round(self.target_x, 2), round(self.target_y, 2)),
            'distance': distance,
            'target_direction': (round(to_target_x, 3), round(to_target_y, 3)),
            'laser_direction': (round(self.direction_x, 3), round(self.direction_y, 3)),
            'turn_speed': current_turn_speed,
            'current_speed': self.speed
        }
        
        self.telemetry.record_frame(self.frame_count, laser_data)
        
        # デバッグイベントを記録（Telemetryシステム内でDEBUG判定）
        current_angle = math.atan2(self.direction_y, self.direction_x)
        turn_mode = "slow" if distance >= self.transition_distance else "fast"
        
        self.telemetry.record_debug_event(self.frame_count, "frame_update", {
            'x': round(self.x, 2),
            'y': round(self.y, 2),
            'angle_rad': round(current_angle, 4),
            'angle_deg': round(math.degrees(current_angle), 2),
            'distance_to_target': round(distance, 2),
            'turn_mode': turn_mode,
            'turn_speed': round(current_turn_speed, 4)
        })
        
        self.frame_count += 1
        
        # 軌跡の更新
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
    
    def _check_hit_and_boundaries(self, distance):
        """ヒット判定と境界チェック"""
        # ターゲットに近づいたらヒット（100%命中保証）
        if distance < self.hit_threshold:
            self.active = False
            details = f"Update distance hit - Distance: {distance:.2f} < threshold: {self.hit_threshold}"
            self.telemetry.export_homing_analysis("Homing.log", self.target_enemy_id, "DISTANCE_HIT", details)
            self.telemetry.export_debug_summary("debug.log", "HIT")
            return True  # ヒットを示すフラグ
        
        # 画面外チェック
        OUT_THRESHOLD = 30  # 画面外判定の閾値
        if (self.x < -OUT_THRESHOLD or self.x > SCREEN_WIDTH + OUT_THRESHOLD or 
            self.y < -OUT_THRESHOLD or self.y > SCREEN_WIDTH + OUT_THRESHOLD):
            if self.active:  # まだアクティブな場合のみログ出力
                self.active = False
                details = f"Final pos: ({self.x:.2f}, {self.y:.2f})"
                self.telemetry.export_homing_analysis("Homing.log", self.target_enemy_id, "OUT_OF_BOUNDS", details)
                self.telemetry.export_debug_summary("debug.log", "OUT_OF_BOUNDS")
        
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
            #alpha_ratio = i / len(self.trail)
            #if alpha_ratio > 0.3:  # 薄すぎる部分はスキップ
            #pyxel.line(int(start_x), int(start_y), int(end_x), int(end_y), self.config.trail_color)
            pyxel.line(int(start_x), int(start_y), int(end_x), int(end_y), pyxel.COLOR_CYAN)
        
        # レーザーヘッド（8x8の矩形）
        #head_x = int(self.x) - 1
        #head_y = int(self.y) - 1
        #pyxel.rect(head_x, head_y, 2, 2, pyxel.COLOR_RED)
    
    def check_collision(self, enemy):
        """エネミーとの距離判定（100%命中保証）"""
        if not self.active or not enemy.active:
            return False
        
        # エネミー中心との距離計算
        enemy_center_x = enemy.x + enemy.sprite_size / 2
        enemy_center_y = enemy.y + enemy.sprite_size / 2
        center_distance = math.sqrt((self.x - enemy_center_x)**2 + (self.y - enemy_center_y)**2)
        
        # 距離判定のみ（ホーミングレーザーは100%命中システム）
        hit_distance_threshold = self.collision_threshold
        
        if center_distance <= hit_distance_threshold:
            self.active = False
            details = (f"Distance hit - Distance: {center_distance:.2f}, Threshold: {hit_distance_threshold:.2f}, " +
                      f"Laser: ({self.x:.2f},{self.y:.2f}), Enemy: ({enemy_center_x:.2f},{enemy_center_y:.2f})")
            self.telemetry.export_homing_analysis("Homing.log", self.target_enemy_id, "COLLISION_HIT", details)
            return True
        
        return False
    

    

    