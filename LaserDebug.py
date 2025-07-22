#!/usr/bin/env python3
"""
LaserDebug - Laser System Debug and Logging for ChromeBlaze
レーザーシステムのデバッグ・ログ機能を分離

旧システムの検証用に残しています
"""

import datetime
import math
from Common import DEBUG

class LaserDebug:
    """レーザーシステムのデバッグ機能を管理"""
    
    def __init__(self, laser_id: str = "unknown"):
        self.laser_id = laser_id
        self.frame_count = 0
        
        # デバッグ情報（DEBUGフラグで制御）
        if DEBUG:
            self.debug_log = []
            self.homing_debug_log = []
        else:
            self.debug_log = None
            self.homing_debug_log = []  # ホーミングログは常に有効
        
        # 追跡情報
        self.min_distance_achieved = float('inf')
        self.circling_detection = []
        self.last_distance = float('inf')
        self.distance_not_decreasing_count = 0
    
    def record_frame_debug(self, laser_x: float, laser_y: float, direction_x: float, 
                          direction_y: float, distance: float, turn_speed: float, 
                          transition_distance: float):
        """フレームごとのデバッグ情報を記録（DEBUGフラグで制御）"""
        if not DEBUG or self.debug_log is None:
            return
            
        current_angle = math.atan2(direction_y, direction_x)
        turn_mode = "slow" if distance >= transition_distance else "fast"
        
        self.debug_log.append({
            'frame': self.frame_count,
            'x': round(laser_x, 2),
            'y': round(laser_y, 2),
            'angle_rad': round(current_angle, 4),
            'angle_deg': round(math.degrees(current_angle), 2),
            'distance_to_target': round(distance, 2),
            'turn_mode': turn_mode,
            'turn_speed': round(turn_speed, 4)
        })
        
        self.frame_count += 1
    
    def record_homing_debug(self, laser_x: float, laser_y: float, target_x: float, 
                           target_y: float, distance: float, target_dir_x: float, 
                           target_dir_y: float, direction_x: float, direction_y: float,
                           turn_speed: float, current_speed: float, config):
        """ホーミング動作のデバッグ情報を記録"""
        # 最小接近距離を更新
        if distance < self.min_distance_achieved:
            self.min_distance_achieved = distance
        
        # 距離の変化を記録して周回検出
        if len(self.circling_detection) > 0:
            distance_change = distance - self.last_distance
            self.circling_detection.append(distance_change)
            
            # 距離が縮まらない状況をカウント
            if distance_change >= config.no_progress_threshold:
                self.distance_not_decreasing_count += 1
            else:
                self.distance_not_decreasing_count = 0
        else:
            self.circling_detection.append(0)
        
        # 直近の設定フレーム数の情報だけ保持
        if len(self.circling_detection) > config.circling_detection_frames:
            self.circling_detection.pop(0)
        
        # デバッグログに記録
        self.homing_debug_log.append({
            'frame': self.frame_count,
            'laser_pos': (round(laser_x, 2), round(laser_y, 2)),
            'target_pos': (round(target_x, 2), round(target_y, 2)),
            'distance': round(distance, 2),
            'target_direction': (round(target_dir_x, 3), round(target_dir_y, 3)),
            'laser_direction': (round(direction_x, 3), round(direction_y, 3)),
            'turn_speed': round(turn_speed, 3),
            'current_speed': round(current_speed, 1),
            'min_distance': round(self.min_distance_achieved, 2),
            'distance_change': round(distance - self.last_distance, 2) if self.last_distance != float('inf') else 0,
            'no_progress_count': self.distance_not_decreasing_count
        })
        
        self.last_distance = distance
    
    def write_debug_log(self, end_reason: str):
        """デバッグログをファイルに書き出し（DEBUGフラグで制御）"""
        if not DEBUG or self.debug_log is None:
            return
            
        try:
            with open("debug.log", "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime('%H:%M:%S')
                f.write(f"\n## Laser Hit Event - {timestamp}\n")
                f.write(f"- Laser ID: {self.laser_id}\n")
                f.write(f"- End Reason: {end_reason}\n")
                f.write(f"- Total Frames: {len(self.debug_log)}\n")
                
        except Exception as e:
            print(f"Debug log write error: {e}")
    
    def write_homing_log(self, end_reason: str, details: str, target_enemy_id: str,
                        hit_threshold: float, collision_threshold: float, config):
        """Homing.logにデバッグ情報を出力"""
        try:
            with open("Homing.log", "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                
                f.write(f"\n=== LASER ANALYSIS [{timestamp}] ===\n")
                f.write(f"Laser ID: {self.laser_id}\n")
                f.write(f"Target Enemy ID: {target_enemy_id}\n")
                f.write(f"End Reason: {end_reason}\n")
                f.write(f"Details: {details}\n")
                f.write(f"Total Frames: {len(self.homing_debug_log)}\n")
                f.write(f"Minimum Distance Achieved: {self.min_distance_achieved:.2f}px\n")
                f.write(f"Hit Threshold: {hit_threshold}px\n")
                f.write(f"Collision Threshold: {collision_threshold}px\n")
                
                # 周回検出分析
                if len(self.circling_detection) >= 5:
                    avg_distance_change = sum(self.circling_detection[-5:]) / 5
                    f.write(f"Average Distance Change (last 5 frames): {avg_distance_change:.3f}px\n")
                    
                    if avg_distance_change > config.circling_threshold:
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
                if end_reason not in ["HIT", "COLLISION_HIT", "DISTANCE_HIT"]:
                    f.write("\n*** ANALYSIS ***\n")
                    
                    if self.min_distance_achieved < hit_threshold * 1.5:
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
                for data in self.homing_debug_log[:5]:
                    f.write(f"{data['frame']:5d} | {str(data['laser_pos']):14s} | {str(data['target_pos']):14s} | {data['distance']:5.1f} | {data['turn_speed']:6.3f} | {data['distance_change']:+7.2f}\n")
                
                if len(self.homing_debug_log) > 10:
                    f.write("  ... (middle frames omitted) ...\n")
                
                # 最後の5フレーム
                for data in self.homing_debug_log[-5:]:
                    f.write(f"{data['frame']:5d} | {str(data['laser_pos']):14s} | {str(data['target_pos']):14s} | {data['distance']:5.1f} | {data['turn_speed']:6.3f} | {data['distance_change']:+7.2f}\n")
                
                f.write("\n")
                
        except Exception as e:
            print(f"Homing log write error: {e}")
    
    def is_debug_enabled(self) -> bool:
        """デバッグが有効かどうかを返す"""
        return DEBUG and self.debug_log is not None