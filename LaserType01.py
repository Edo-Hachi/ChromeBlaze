#!/usr/bin/env python3
"""
LaserType01 - Homing Laser System for ChromeBlaze
ホーミングレーザーシステム
"""

import pyxel
import math
import random
from Common import DEBUG, SCREEN_WIDTH
from LaserConfig import LaserConfig

class LaserType01:
    """方法1: 線形補間 + 角度制限（最軽量）"""
    
    def __init__(self, start_x, start_y, target_x, target_y, target_enemy_id=None):
        # レーザー設定（LaserConfigから取得）
        self.initial_speed = LaserConfig.INITIAL_SPEED
        self.min_speed = LaserConfig.MIN_SPEED
        self.speed = self.initial_speed  # 現在の速度
        self.speed_decay = LaserConfig.SPEED_DECAY
        self.turn_speed_slow = LaserConfig.TURN_SPEED_SLOW
        self.turn_speed_fast = LaserConfig.TURN_SPEED_FAST
        self.transition_distance = LaserConfig.TRANSITION_DISTANCE
        self.max_trail_length = LaserConfig.MAX_TRAIL_LENGTH
        self.hit_threshold = LaserConfig.HIT_THRESHOLD
        self.collision_threshold = LaserConfig.COLLISION_THRESHOLD
        
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
        
        # ホーミングデバッグ情報
        self.homing_debug_log = []
        self.frame_count = 0
        self.min_distance_achieved = float('inf')  # 最小接近距離
        self.circling_detection = []  # 周回検出用
        self.last_distance = float('inf')
        self.distance_not_decreasing_count = 0  # 距離が縮まらないフレーム数
        
        # デバッグ情報（DEBUGフラグで制御）
        if DEBUG:
            self.debug_log = []
        else:
            self.debug_log = None
    
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
        
        # 速度減速処理（フレームごとに減速）
        if self.speed > self.min_speed:
            self.speed -= self.speed_decay
            if self.speed < self.min_speed:
                self.speed = self.min_speed
        
        # 位置を更新
        self.x += self.direction_x * self.speed * delta_time
        self.y += self.direction_y * self.speed * delta_time
        
        # ホーミングデバッグ情報を記録
        self._record_homing_debug(distance, to_target_x if distance > 0 else 0, 
                                 to_target_y if distance > 0 else 0, 
                                 current_turn_speed if distance > 0 else 0)
        
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
        
        # ターゲットに近づいたらヒット（100%命中保証）
        if distance < self.hit_threshold:
            self.active = False
            self._write_homing_log("DISTANCE_HIT", f"Update distance hit - Distance: {distance:.2f} < threshold: {self.hit_threshold}")
            if DEBUG:
                self._write_debug_log("HIT")
            return True  # ヒットを示すフラグ
        
        # 画面外チェック
        if (self.x < -10 or self.x > SCREEN_WIDTH + 10 or 
            self.y < -10 or self.y > SCREEN_WIDTH + 10):
            if self.active:  # まだアクティブな場合のみログ出力
                self.active = False
                self._write_homing_log("OUT_OF_BOUNDS", f"Final pos: ({self.x:.2f}, {self.y:.2f})")
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
            #alpha_ratio = i / len(self.trail)
            #if alpha_ratio > 0.3:  # 薄すぎる部分はスキップ
            pyxel.line(int(start_x), int(start_y), int(end_x), int(end_y), LaserConfig.TRAIL_COLOR)
        
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
        hit_distance_threshold = LaserConfig.COLLISION_THRESHOLD
        
        if center_distance <= hit_distance_threshold:
            self.active = False
            self._write_homing_log("DISTANCE_HIT", 
                f"Distance hit - Distance: {center_distance:.2f}, Threshold: {hit_distance_threshold:.2f}, " +
                f"Laser: ({self.x:.2f},{self.y:.2f}), Enemy: ({enemy_center_x:.2f},{enemy_center_y:.2f})")
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
    
    def _record_homing_debug(self, distance, target_dir_x, target_dir_y, turn_speed):
        """ホーミング動作のデバッグ情報を記録"""
        # 最小接近距離を更新
        if distance < self.min_distance_achieved:
            self.min_distance_achieved = distance
        
        # 距離の変化を記録して周回検出
        if len(self.circling_detection) > 0:
            distance_change = distance - self.last_distance
            self.circling_detection.append(distance_change)
            
            # 距離が縮まらない状況をカウント
            if distance_change >= LaserConfig.NO_PROGRESS_THRESHOLD:
                self.distance_not_decreasing_count += 1
            else:
                self.distance_not_decreasing_count = 0
        else:
            self.circling_detection.append(0)
        
        # 直近の設定フレーム数の情報だけ保持
        if len(self.circling_detection) > LaserConfig.CIRCLING_DETECTION_FRAMES:
            self.circling_detection.pop(0)
        
        # デバッグログに記録
        self.homing_debug_log.append({
            'frame': self.frame_count,
            'laser_pos': (round(self.x, 2), round(self.y, 2)),
            'target_pos': (round(self.target_x, 2), round(self.target_y, 2)),
            'distance': round(distance, 2),
            'target_direction': (round(target_dir_x, 3), round(target_dir_y, 3)),
            'laser_direction': (round(self.direction_x, 3), round(self.direction_y, 3)),
            'turn_speed': round(turn_speed, 3),
            'current_speed': round(self.speed, 1),  # 現在の速度を追加
            'min_distance': round(self.min_distance_achieved, 2),
            'distance_change': round(distance - self.last_distance, 2) if self.last_distance != float('inf') else 0,
            'no_progress_count': self.distance_not_decreasing_count
        })
        
        self.last_distance = distance
    
    def _write_homing_log(self, end_reason, details=""):
        """Homing.logにデバッグ情報を出力"""
        import datetime
        
        try:
            with open("Homing.log", "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                
                f.write(f"\n=== LASER ANALYSIS [{timestamp}] ===\n")
                f.write(f"Target Enemy ID: {self.target_enemy_id}\n")
                f.write(f"End Reason: {end_reason}\n")
                f.write(f"Details: {details}\n")
                f.write(f"Total Frames: {len(self.homing_debug_log)}\n")
                f.write(f"Minimum Distance Achieved: {self.min_distance_achieved:.2f}px\n")
                f.write(f"Hit Threshold: {self.hit_threshold}px\n")
                f.write(f"Collision Threshold: {self.collision_threshold}px\n")
                
                # 周回検出分析
                if len(self.circling_detection) >= 5:
                    avg_distance_change = sum(self.circling_detection[-5:]) / 5
                    f.write(f"Average Distance Change (last 5 frames): {avg_distance_change:.3f}px\n")
                    
                    if avg_distance_change > LaserConfig.CIRCLING_THRESHOLD:
                        f.write("*** POTENTIAL CIRCLING DETECTED ***\n")
                
                f.write(f"Frames with No Progress: {self.distance_not_decreasing_count}\n")
                
                # 開始・終了位置
                if len(self.homing_debug_log) > 0:
                    start_data = self.homing_debug_log[0]
                    end_data = self.homing_debug_log[-1]
                    
                    f.write(f"Start Position: {start_data['laser_pos']}\n")
                    f.write(f"End Position: {end_data['laser_pos']}\n")
                    f.write(f"Start Target: {start_data['target_pos']}\n")
                    f.write(f"End Target: {end_data['target_pos']}\n")
                    f.write(f"Start Distance: {start_data['distance']:.2f}px\n")
                    f.write(f"End Distance: {end_data['distance']:.2f}px\n")
                
                # 問題判定
                if end_reason != "HIT" and end_reason != "COLLISION_HIT":
                    f.write("\n*** ANALYSIS ***\n")
                    
                    if self.min_distance_achieved < self.hit_threshold * 1.5:
                        f.write(f"- Got close ({self.min_distance_achieved:.2f}px) but failed to hit\n")
                        f.write(f"- Possible threshold issue or collision detection problem\n")
                    
                    if self.distance_not_decreasing_count > 30:
                        f.write(f"- Spent {self.distance_not_decreasing_count} frames not getting closer\n")
                        f.write(f"- Likely circling or overshooting target\n")
                    
                    if end_reason == "OUT_OF_BOUNDS":
                        f.write(f"- Laser went out of bounds - possible overshoot or lost target\n")
                
                # 詳細なフレームデータ（最初と最後の5フレームのみ）
                f.write(f"\n--- DETAILED FRAME DATA ---\n")
                f.write(f"Frame | Laser Pos      | Target Pos     | Dist  | Dir Change | Progress\n")
                f.write(f"------|----------------|----------------|-------|------------|----------\n")
                
                # 最初の5フレーム
                for i, data in enumerate(self.homing_debug_log[:5]):
                    f.write(f"{data['frame']:5d} | {str(data['laser_pos']):14s} | {str(data['target_pos']):14s} | {data['distance']:5.1f} | {data['turn_speed']:6.3f} | {data['distance_change']:+7.2f}\n")
                
                if len(self.homing_debug_log) > 10:
                    f.write("  ... (middle frames omitted) ...\n")
                
                # 最後の5フレーム
                for i, data in enumerate(self.homing_debug_log[-5:]):
                    f.write(f"{data['frame']:5d} | {str(data['laser_pos']):14s} | {str(data['target_pos']):14s} | {data['distance']:5.1f} | {data['turn_speed']:6.3f} | {data['distance_change']:+7.2f}\n")
                
                f.write("\n")
                
        except Exception as e:
            print(f"Homing log write error: {e}")