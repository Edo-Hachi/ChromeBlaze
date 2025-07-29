#!/usr/bin/env python3
"""
LaserType01 - Homing Laser System for ChromeBlaze
ホーミングレーザーシステム
"""

import pyxel
import math
from Common import SCREEN_WIDTH
from LaserConfig import LaserConfig, default_laser_config
from LaserTelemetry import LaserTelemetry
from Vector2D import Vector2D, angle_difference

class LaserType01:
    """方法1: 線形補間 + 角度制限（最軽量）"""
    
    # クラス定数
    OUT_OF_BOUNDS_THRESHOLD = 30  # 画面外判定の閾値
    MIN_TRAIL_LENGTH = 2          # 軌跡描画の最小長さ
    
    def __init__(self, start_x, start_y, target_x, target_y, target_enemy_id=None, config: LaserConfig = None):
        # 設定の取得（カスタム設定がない場合はデフォルトを使用）
        if config is None:
            config = default_laser_config
        
        # 設定をインスタンス変数として保持
        self.config = config
        
        # 現在の速度（設定から初期化、フレーム毎に更新）
        self.speed = config.initial_speed
        
        # 位置と方向（Vector2D使用）
        self.position = Vector2D(start_x, start_y)
        self.target_position = Vector2D(target_x, target_y)
        
        # ターゲット情報
        self.target_enemy_id = target_enemy_id
        self.initial_target_position = Vector2D(target_x, target_y)
        
        # 初期方向設定
        self.direction = self._initialize_direction(start_x)
        
        # 軌跡
        self.trail = [self.position.to_tuple()]
        
        # アクティブ状態
        self.active = True
        
        # テレメトリーシステム
        self.telemetry = LaserTelemetry()
        self.frame_count = 0
    
    def _initialize_direction(self, start_x):
        """初期方向をプレイヤー位置に基づいて設定"""
        screen_center_x = SCREEN_WIDTH // 2
        if start_x > screen_center_x:
            # 右側にいる場合：右向きで発射
            return Vector2D(1.0, 0.0)
        elif start_x < screen_center_x:
            # 左側にいる場合：左向きで発射
            return Vector2D(-1.0, 0.0)
        else:
            # 中央にいる場合：上向きで発射
            return Vector2D(0.0, -1.0)
    
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
        self.target_position = Vector2D(target_x, target_y)
    
    def _calculate_homing_direction(self, delta_time):
        """ホーミング方向計算（Vector2D使用）"""
        # ターゲットへのベクトルと距離を計算
        to_target = self.target_position - self.position
        distance = to_target.magnitude()
        current_turn_speed = 0.0
        
        if distance > 0:
            # ターゲット方向の正規化ベクトル
            target_direction = to_target.normalize()
            
            # 現在の方向とターゲット方向の角度差を計算
            current_angle = self.direction.angle()
            target_angle = target_direction.angle()
            angle_diff = angle_difference(current_angle, target_angle)
            
            # 距離に基づいて旋回速度を調整
            current_turn_speed = self.config.turn_speed_slow
            if distance < self.config.transition_distance:
                # 近づくほど急旋回に切り替え
                ratio = 1.0 - (distance / self.config.transition_distance)
                current_turn_speed = self.config.turn_speed_slow + (self.config.turn_speed_fast - self.config.turn_speed_slow) * ratio
            
            # 角度制限を適用
            max_turn = current_turn_speed * delta_time
            if abs(angle_diff) > max_turn:
                angle_diff = math.copysign(max_turn, angle_diff)
            
            # 新しい方向を設定
            new_angle = current_angle + angle_diff
            self.direction = Vector2D.from_angle(new_angle)
        
        return distance, current_turn_speed
    
    def _apply_speed_decay(self):
        """速度減速処理"""
        if self.speed > self.config.min_speed:
            self.speed -= self.config.speed_decay
            if self.speed < self.config.min_speed:
                self.speed = self.config.min_speed
    
    def _update_position(self, delta_time):
        """位置更新"""
        velocity = self.direction * self.speed * delta_time
        self.position += velocity
    
    def _update_debug_and_trail(self, distance, current_turn_speed):
        """デバッグ情報と軌跡の更新"""
        # 簡略化されたテレメトリーデータ（位置・距離・状態のみ）
        simple_data = {
            'laser_pos': (round(self.position.x, 1), round(self.position.y, 1)),
            'distance': round(distance, 1),
            'current_speed': self.speed
        }
        self.telemetry.record_frame(self.frame_count, simple_data)
        
        self.frame_count += 1
        
        # 軌跡の更新
        self.trail.append(self.position.to_tuple())
        if len(self.trail) > self.config.max_trail_length:
            self.trail.pop(0)
    
    def _check_hit_and_boundaries(self, distance):
        """ヒット判定と境界チェック"""
        # ターゲットに近づいたらヒット（100%命中保証）
        if distance < self.config.hit_threshold:
            self.active = False
            details = f"Update distance hit - Distance: {distance:.2f} < threshold: {self.config.hit_threshold}"
            self.telemetry.export_homing_analysis("Homing.log", self.target_enemy_id, "DISTANCE_HIT", details)
            self.telemetry.export_debug_summary("debug.log", "HIT")
            return True  # ヒットを示すフラグ
        
        # 画面外チェック
        if (self.position.x < -self.OUT_OF_BOUNDS_THRESHOLD or self.position.x > SCREEN_WIDTH + self.OUT_OF_BOUNDS_THRESHOLD or 
            self.position.y < -self.OUT_OF_BOUNDS_THRESHOLD or self.position.y > SCREEN_WIDTH + self.OUT_OF_BOUNDS_THRESHOLD):
            if self.active:  # まだアクティブな場合のみログ出力
                self.active = False
                details = f"Final pos: {self.position}"
                self.telemetry.export_homing_analysis("Homing.log", self.target_enemy_id, "OUT_OF_BOUNDS", details)
                self.telemetry.export_debug_summary("debug.log", "OUT_OF_BOUNDS")
        
        return False
    
    def draw(self):
        """レーザーの描画"""
        if not self.active or len(self.trail) < self.MIN_TRAIL_LENGTH:
            return
        
        # 軌跡を線で描画
        for i in range(len(self.trail) - 1):
            start_x, start_y = self.trail[i]
            end_x, end_y = self.trail[i + 1]
            pyxel.line(int(start_x), int(start_y), int(end_x), int(end_y), pyxel.COLOR_CYAN)
    
    def check_collision(self, enemy):
        """エネミーとの距離判定（100%命中保証）"""
        if not self.active or not enemy.active:
            return False
        
        # エネミー中心位置をVector2Dで計算
        enemy_center = Vector2D(enemy.x + enemy.sprite_size / 2, enemy.y + enemy.sprite_size / 2)
        center_distance = self.position.distance_to(enemy_center)
        
        # 距離判定のみ（ホーミングレーザーは100%命中システム）
        hit_distance_threshold = self.config.collision_threshold
        
        if center_distance <= hit_distance_threshold:
            self.active = False
            details = (f"Distance hit - Distance: {center_distance:.2f}, Threshold: {hit_distance_threshold:.2f}, " +
                      f"Laser: {self.position}, Enemy: {enemy_center}")
            self.telemetry.export_homing_analysis("Homing.log", self.target_enemy_id, "COLLISION_HIT", details)
            return True
        
        return False
    

    

    