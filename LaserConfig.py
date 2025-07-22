#!/usr/bin/env python3
"""
LaserConfig - Laser System Configuration for ChromeBlaze
レーザーシステム設定管理
"""

class LaserConfig:
    """レーザーシステムの設定定数を管理するクラス"""
    
    # === 物理演算設定 ===
    INITIAL_SPEED = 500.0       # 初期速度（ピクセル/秒）
    MIN_SPEED = 300.0          # 最低速度（ピクセル/秒）
    SPEED_DECAY = 5.0          # フレームごとの減速量（ピクセル/秒）
    
    # === ホーミング設定 ===
    TURN_SPEED_SLOW = 8.0      # 初期：ゆっくり旋回（ラジアン/秒）
    TURN_SPEED_FAST = 20.0     # 後半：急旋回（ラジアン/秒）
    TRANSITION_DISTANCE = 150.0 # 旋回速度切り替え距離（ピクセル）
    
    # === 判定設定 ===
    HIT_THRESHOLD = 10.0       # ヒット判定距離（100%命中保証用）
    COLLISION_THRESHOLD = 15.0 # コリジョン判定距離
    
    # === 表示設定 ===
    MAX_TRAIL_LENGTH = 30      # 軌跡の最大長
    TRAIL_COLOR = 11          # 軌跡の色（pyxel.COLOR_CYAN）
    
    # === デバッグ設定 ===
    CIRCLING_DETECTION_FRAMES = 10    # 周回検出用フレーム数
    NO_PROGRESS_THRESHOLD = -0.5      # 進歩なし判定閾値（ピクセル）
    CIRCLING_THRESHOLD = -0.1         # 周回判定閾値（平均距離変化）
    
    @classmethod
    def get_physics_config(cls):
        """物理演算関連の設定を辞書で返す"""
        return {
            'initial_speed': cls.INITIAL_SPEED,
            'min_speed': cls.MIN_SPEED,
            'speed_decay': cls.SPEED_DECAY
        }
    
    @classmethod
    def get_homing_config(cls):
        """ホーミング関連の設定を辞書で返す"""
        return {
            'turn_speed_slow': cls.TURN_SPEED_SLOW,
            'turn_speed_fast': cls.TURN_SPEED_FAST,
            'transition_distance': cls.TRANSITION_DISTANCE
        }
    
    @classmethod
    def get_collision_config(cls):
        """判定関連の設定を辞書で返す"""
        return {
            'hit_threshold': cls.HIT_THRESHOLD,
            'collision_threshold': cls.COLLISION_THRESHOLD
        }
    
    @classmethod
    def get_visual_config(cls):
        """表示関連の設定を辞書で返す"""
        return {
            'max_trail_length': cls.MAX_TRAIL_LENGTH,
            'trail_color': cls.TRAIL_COLOR
        }
    
    @classmethod
    def get_debug_config(cls):
        """デバッグ関連の設定を辞書で返す"""
        return {
            'circling_detection_frames': cls.CIRCLING_DETECTION_FRAMES,
            'no_progress_threshold': cls.NO_PROGRESS_THRESHOLD,
            'circling_threshold': cls.CIRCLING_THRESHOLD
        }

# === 設定プロファイル ===
class LaserProfiles:
    """異なる難易度やバランス用の設定プロファイル"""
    
    @staticmethod
    def easy_mode():
        """簡単モード: より確実にヒットする設定"""
        LaserConfig.HIT_THRESHOLD = 15.0
        LaserConfig.COLLISION_THRESHOLD = 20.0
        LaserConfig.TURN_SPEED_FAST = 25.0
    
    @staticmethod
    def normal_mode():
        """通常モード: デフォルト設定"""
        LaserConfig.HIT_THRESHOLD = 10.0
        LaserConfig.COLLISION_THRESHOLD = 15.0
        LaserConfig.TURN_SPEED_FAST = 20.0
    
    @staticmethod
    def hard_mode():
        """難しいモード: より精密な操作が必要"""
        LaserConfig.HIT_THRESHOLD = 8.0
        LaserConfig.COLLISION_THRESHOLD = 12.0
        LaserConfig.TURN_SPEED_FAST = 15.0
    
    @staticmethod
    def debug_mode():
        """デバッグモード: 調整用の極端な設定"""
        LaserConfig.HIT_THRESHOLD = 5.0
        LaserConfig.SPEED_DECAY = 10.0
        LaserConfig.TURN_SPEED_FAST = 30.0