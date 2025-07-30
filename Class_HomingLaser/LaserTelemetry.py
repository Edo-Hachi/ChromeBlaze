#!/usr/bin/env python3
"""
LaserTelemetry - Debug and Telemetry System for ChromeBlaze
レーザーテレメトリーシステム
"""

import datetime
from typing import Dict, List, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Common import DEBUG


class LaserTelemetry:
    """レーザーのデバッグ・テレメトリー管理クラス"""
    
    def __init__(self, enabled: bool = None):
        """
        テレメトリーシステムの初期化
        
        Args:
            enabled: テレメトリーの有効/無効（Noneの場合はDEBUGフラグを使用）
        """
        self.enabled = enabled if enabled is not None else DEBUG
        self.frame_data: List[Dict[str, Any]] = []
        self.debug_log: List[Dict[str, Any]] = [] if self.enabled else None
        
        # 分析用データ
        self.min_distance_achieved = float('inf')
        self.circling_detection: List[float] = []
        self.last_distance = float('inf')
        self.distance_not_decreasing_count = 0
        
        # 設定
        self.max_circling_frames = 10
        self.no_progress_threshold = -0.5
        self.circling_threshold = -0.1
    
    def record_frame(self, frame_count: int, laser_data: Dict[str, Any]):
        """フレームデータを記録"""
        if not self.enabled:
            return
        
        distance = laser_data.get('distance', 0)
        
        # 最小接近距離を更新
        if distance < self.min_distance_achieved:
            self.min_distance_achieved = distance
        
        # 距離変化の分析
        self._analyze_distance_change(distance)
        
        # フレームデータを記録
        frame_data = {
            'frame': frame_count,
            'laser_pos': laser_data.get('laser_pos', (0, 0)),
            'target_pos': laser_data.get('target_pos', (0, 0)),
            'distance': round(distance, 2),
            'target_direction': laser_data.get('target_direction', (0, 0)),
            'laser_direction': laser_data.get('laser_direction', (0, 0)),
            'turn_speed': laser_data.get('turn_speed', 0),
            'current_speed': laser_data.get('current_speed', 0),
            'min_distance': round(self.min_distance_achieved, 2),
            'distance_change': round(distance - self.last_distance, 2) if self.last_distance != float('inf') else 0,
            'no_progress_count': self.distance_not_decreasing_count
        }
        
        self.frame_data.append(frame_data)
        self.last_distance = distance
    
    def record_debug_event(self, frame_count: int, event_type: str, data: Dict[str, Any]):
        """デバッグイベントを記録"""
        if not self.enabled or self.debug_log is None:
            return
        
        self.debug_log.append({
            'frame': frame_count,
            'event_type': event_type,
            'timestamp': datetime.datetime.now(),
            **data
        })
    
    def _analyze_distance_change(self, distance: float):
        """距離変化を分析して周回検出"""
        if len(self.circling_detection) > 0:
            distance_change = distance - self.last_distance
            self.circling_detection.append(distance_change)
            
            # 距離が縮まらない状況をカウント
            if distance_change >= self.no_progress_threshold:
                self.distance_not_decreasing_count += 1
            else:
                self.distance_not_decreasing_count = 0
        else:
            self.circling_detection.append(0)
        
        # 直近のフレーム数の情報だけ保持
        if len(self.circling_detection) > self.max_circling_frames:
            self.circling_detection.pop(0)
    
    def is_circling(self) -> bool:
        """周回状態かどうかを判定"""
        if len(self.circling_detection) < 5:
            return False
        
        avg_distance_change = sum(self.circling_detection[-5:]) / 5
        return avg_distance_change > self.circling_threshold
    
    def export_homing_analysis(self, filename: str, laser_id: Optional[str], end_reason: str, details: str = ""):
        """ホーミング分析レポートをエクスポート"""
        if not self.enabled or not self.frame_data:
            return
        
        # debug_log/ディレクトリ配下に出力するパスを構築
        import os
        debug_dir = "debug_log"
        os.makedirs(debug_dir, exist_ok=True)
        filepath = os.path.join(debug_dir, filename)
        
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                
                f.write(f"\n=== LASER ANALYSIS [{timestamp}] ===\n")
                f.write(f"Target Enemy ID: {laser_id}\n")
                f.write(f"End Reason: {end_reason}\n")
                f.write(f"Details: {details}\n")
                f.write(f"Total Frames: {len(self.frame_data)}\n")
                f.write(f"Minimum Distance Achieved: {self.min_distance_achieved:.2f}px\n")
                
                # 周回検出分析
                if len(self.circling_detection) >= 5:
                    avg_distance_change = sum(self.circling_detection[-5:]) / 5
                    f.write(f"Average Distance Change (last 5 frames): {avg_distance_change:.3f}px\n")
                    
                    if self.is_circling():
                        f.write("*** POTENTIAL CIRCLING DETECTED ***\n")
                
                f.write(f"Frames with No Progress: {self.distance_not_decreasing_count}\n")
                
                # 開始・終了位置
                if len(self.frame_data) > 0:
                    start_data = self.frame_data[0]
                    end_data = self.frame_data[-1]
                    
                    f.write(f"Start Position: {start_data['laser_pos']}\n")
                    f.write(f"End Position: {end_data['laser_pos']}\n")
                    f.write(f"Start Target: {start_data['target_pos']}\n")
                    f.write(f"End Target: {end_data['target_pos']}\n")
                    f.write(f"Start Distance: {start_data['distance']:.2f}px\n")
                    f.write(f"End Distance: {end_data['distance']:.2f}px\n")
                
                # 問題判定
                self._write_analysis_summary(f, end_reason)
                
                # 詳細なフレームデータ
                self._write_detailed_frame_data(f)
                
                f.write("\n")
                
        except Exception as e:
            print(f"Homing log write error: {e}")
    
    def _write_analysis_summary(self, file, end_reason: str):
        """分析サマリーを書き出し"""
        if end_reason in ["HIT", "COLLISION_HIT"]:
            return
        
        file.write("\n*** ANALYSIS ***\n")
        
        # 設定値は外部から注入される想定
        hit_threshold = 10.0  # デフォルト値
        
        if self.min_distance_achieved < hit_threshold * 1.5:
            file.write(f"- Got close ({self.min_distance_achieved:.2f}px) but failed to hit\n")
            file.write(f"- Possible threshold issue or collision detection problem\n")
        
        if self.distance_not_decreasing_count > 30:
            file.write(f"- Spent {self.distance_not_decreasing_count} frames not getting closer\n")
            file.write(f"- Likely circling or overshooting target\n")
        
        if end_reason == "OUT_OF_BOUNDS":
            file.write(f"- Laser went out of bounds - possible overshoot or lost target\n")
    
    def _write_detailed_frame_data(self, file):
        """詳細なフレームデータを書き出し"""
        file.write(f"\n--- DETAILED FRAME DATA ---\n")
        file.write(f"Frame | Laser Pos      | Target Pos     | Dist  | Dir Change | Progress\n")
        file.write(f"------|----------------|----------------|-------|------------|----------\n")
        
        # 最初の5フレーム
        for data in self.frame_data[:5]:
            file.write(f"{data['frame']:5d} | {str(data['laser_pos']):14s} | {str(data['target_pos']):14s} | {data['distance']:5.1f} | {data['turn_speed']:6.3f} | {data['distance_change']:+7.2f}\n")
        
        if len(self.frame_data) > 10:
            file.write("  ... (middle frames omitted) ...\n")
        
        # 最後の5フレーム
        for data in self.frame_data[-5:]:
            file.write(f"{data['frame']:5d} | {str(data['laser_pos']):14s} | {str(data['target_pos']):14s} | {data['distance']:5.1f} | {data['turn_speed']:6.3f} | {data['distance_change']:+7.2f}\n")
    
    def export_debug_summary(self, filename: str, end_reason: str):
        """デバッグサマリーをエクスポート"""
        if not self.enabled or self.debug_log is None:
            return
        
        # debug_log/ディレクトリ配下に出力するパスを構築
        import os
        debug_dir = "debug_log"
        os.makedirs(debug_dir, exist_ok=True)
        filepath = os.path.join(debug_dir, filename)
        
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(f"\n## Laser Hit Event - {datetime.datetime.now().strftime('%H:%M:%S')}\n")
                f.write(f"- End Reason: {end_reason}\n")
                f.write(f"- Total Frames: {len(self.debug_log)}\n")
                
        except Exception as e:
            print(f"Debug log write error: {e}")
    
    def clear(self):
        """データをクリア"""
        self.frame_data.clear()
        if self.debug_log is not None:
            self.debug_log.clear()
        self.min_distance_achieved = float('inf')
        self.circling_detection.clear()
        self.last_distance = float('inf')
        self.distance_not_decreasing_count = 0


class LaserTelemetryManager:
    """複数のレーザーテレメトリーを管理するクラス"""
    
    def __init__(self, enabled: bool = None):
        self.enabled = enabled if enabled is not None else DEBUG
        self.telemetries: Dict[str, LaserTelemetry] = {}
    
    def create_telemetry(self, laser_id: str) -> LaserTelemetry:
        """新しいテレメトリーインスタンスを作成"""
        telemetry = LaserTelemetry(self.enabled)
        self.telemetries[laser_id] = telemetry
        return telemetry
    
    def get_telemetry(self, laser_id: str) -> Optional[LaserTelemetry]:
        """テレメトリーインスタンスを取得"""
        return self.telemetries.get(laser_id)
    
    def remove_telemetry(self, laser_id: str):
        """テレメトリーインスタンスを削除"""
        if laser_id in self.telemetries:
            del self.telemetries[laser_id]
    
    def export_all_reports(self, base_filename: str):
        """全てのテレメトリーレポートをエクスポート"""
        for laser_id, telemetry in self.telemetries.items():
            filename = f"{base_filename}_{laser_id}.log"
            telemetry.export_homing_analysis(filename, laser_id, "BATCH_EXPORT")
