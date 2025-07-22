#!/usr/bin/env python3
"""
LaserConfig - Laser System Configuration for ChromeBlaze
レーザーシステム設定管理 (dataclass版)
"""

from dataclasses import dataclass

@dataclass
class LaserConfig:
    """レーザーシステムの設定をdataclassで管理"""
    
    # === 物理演算設定 ===
    initial_speed: float = 500.0       # 初期速度（ピクセル/秒）
    min_speed: float = 300.0          # 最低速度（ピクセル/秒）
    speed_decay: float = 5.0          # フレームごとの減速量（ピクセル/秒）
    
    # === ホーミング設定 ===
    turn_speed_slow: float = 8.0      # 初期：ゆっくり旋回（ラジアン/秒）
    turn_speed_fast: float = 20.0     # 後半：急旋回（ラジアン/秒）
    transition_distance: float = 150.0 # 旋回速度切り替え距離（ピクセル）
    
    # === 判定設定 ===
    hit_threshold: float = 10.0       # ヒット判定距離（100%命中保証用）
    collision_threshold: float = 15.0 # コリジョン判定距離
    
    # === 表示設定 ===
    max_trail_length: int = 30        # 軌跡の最大長
    trail_color: int = 11            # 軌跡の色（pyxel.COLOR_CYAN）
    
    # === デバッグ設定 ===
    circling_detection_frames: int = 10    # 周回検出用フレーム数
    no_progress_threshold: float = -0.5    # 進歩なし判定閾値（ピクセル）
    circling_threshold: float = -0.1       # 周回判定閾値（平均距離変化）
    
    def get_physics_config(self) -> dict:
        """物理演算関連の設定を辞書で返す"""
        return {
            'initial_speed': self.initial_speed,
            'min_speed': self.min_speed,
            'speed_decay': self.speed_decay
        }
    
    def get_homing_config(self) -> dict:
        """ホーミング関連の設定を辞書で返す"""
        return {
            'turn_speed_slow': self.turn_speed_slow,
            'turn_speed_fast': self.turn_speed_fast,
            'transition_distance': self.transition_distance
        }
    
    def get_collision_config(self) -> dict:
        """判定関連の設定を辞書で返す"""
        return {
            'hit_threshold': self.hit_threshold,
            'collision_threshold': self.collision_threshold
        }
    
    def get_visual_config(self) -> dict:
        """表示関連の設定を辞書で返す"""
        return {
            'max_trail_length': self.max_trail_length,
            'trail_color': self.trail_color
        }
    
    def get_debug_config(self) -> dict:
        """デバッグ関連の設定を辞書で返す"""
        return {
            'circling_detection_frames': self.circling_detection_frames,
            'no_progress_threshold': self.no_progress_threshold,
            'circling_threshold': self.circling_threshold
        }

# === 設定プロファイル ===
class LaserProfiles:
    """異なる難易度やバランス用の設定プロファイル"""
    
    @staticmethod
    def easy_mode() -> LaserConfig:
        """簡単モード: より確実にヒットする設定"""
        return LaserConfig(
            hit_threshold=15.0,
            collision_threshold=20.0,
            turn_speed_fast=25.0
        )
    
    @staticmethod
    def normal_mode() -> LaserConfig:
        """通常モード: デフォルト設定"""
        return LaserConfig()  # デフォルト値を使用
    
    @staticmethod
    def hard_mode() -> LaserConfig:
        """難しいモード: より精密な操作が必要"""
        return LaserConfig(
            hit_threshold=8.0,
            collision_threshold=12.0,
            turn_speed_fast=15.0
        )
    
    @staticmethod
    def debug_mode() -> LaserConfig:
        """デバッグモード: 調整用の極端な設定"""
        return LaserConfig(
            hit_threshold=5.0,
            speed_decay=10.0,
            turn_speed_fast=30.0
        )

# グローバル設定インスタンス
default_laser_config = LaserConfig()