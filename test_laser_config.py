#!/usr/bin/env python3
"""
LaserConfig動作確認テスト
設定変更が正しく適用されるかテスト
"""

import sys
sys.path.append('.')

from LaserConfig import LaserConfig, LaserProfiles
from LaserType01 import LaserType01

def test_default_config():
    """デフォルト設定のテスト"""
    print("=== デフォルト設定テスト ===")
    
    # レーザー作成
    laser = LaserType01(100, 100, 150, 150, target_enemy_id=1)
    
    # 設定値の確認
    print(f"Initial Speed: {laser.initial_speed} (expected: {LaserConfig.INITIAL_SPEED})")
    print(f"Min Speed: {laser.min_speed} (expected: {LaserConfig.MIN_SPEED})")
    print(f"Hit Threshold: {laser.hit_threshold} (expected: {LaserConfig.HIT_THRESHOLD})")
    print(f"Turn Speed Fast: {laser.turn_speed_fast} (expected: {LaserConfig.TURN_SPEED_FAST})")
    print(f"Max Trail Length: {laser.max_trail_length} (expected: {LaserConfig.MAX_TRAIL_LENGTH})")
    
    # 検証
    assert laser.initial_speed == LaserConfig.INITIAL_SPEED
    assert laser.min_speed == LaserConfig.MIN_SPEED
    assert laser.hit_threshold == LaserConfig.HIT_THRESHOLD
    print("✅ デフォルト設定テスト成功\n")

def test_easy_mode():
    """簡単モードのテスト"""
    print("=== 簡単モード設定テスト ===")
    
    # 簡単モード適用
    LaserProfiles.easy_mode()
    
    # レーザー作成（新しい設定が適用される）
    laser = LaserType01(100, 100, 150, 150, target_enemy_id=2)
    
    print(f"Hit Threshold: {laser.hit_threshold} (expected: 15.0)")
    print(f"Collision Threshold: {laser.collision_threshold} (expected: 20.0)")
    print(f"Turn Speed Fast: {laser.turn_speed_fast} (expected: 25.0)")
    
    # 検証
    assert laser.hit_threshold == 15.0
    assert laser.collision_threshold == 20.0
    assert laser.turn_speed_fast == 25.0
    print("✅ 簡単モード設定テスト成功\n")

def test_hard_mode():
    """難しいモードのテスト"""
    print("=== 難しいモード設定テスト ===")
    
    # 難しいモード適用
    LaserProfiles.hard_mode()
    
    # レーザー作成
    laser = LaserType01(100, 100, 150, 150, target_enemy_id=3)
    
    print(f"Hit Threshold: {laser.hit_threshold} (expected: 8.0)")
    print(f"Collision Threshold: {laser.collision_threshold} (expected: 12.0)")
    print(f"Turn Speed Fast: {laser.turn_speed_fast} (expected: 15.0)")
    
    # 検証
    assert laser.hit_threshold == 8.0
    assert laser.collision_threshold == 12.0
    assert laser.turn_speed_fast == 15.0
    print("✅ 難しいモード設定テスト成功\n")

def test_config_methods():
    """設定取得メソッドのテスト"""
    print("=== 設定取得メソッドテスト ===")
    
    # 通常モードに戻す
    LaserProfiles.normal_mode()
    
    physics = LaserConfig.get_physics_config()
    homing = LaserConfig.get_homing_config()
    collision = LaserConfig.get_collision_config()
    visual = LaserConfig.get_visual_config()
    debug = LaserConfig.get_debug_config()
    
    print(f"Physics Config: {physics}")
    print(f"Homing Config: {homing}")
    print(f"Collision Config: {collision}")
    print(f"Visual Config: {visual}")
    print(f"Debug Config: {debug}")
    
    # 検証
    assert 'initial_speed' in physics
    assert 'turn_speed_slow' in homing
    assert 'hit_threshold' in collision
    assert 'max_trail_length' in visual
    assert 'circling_detection_frames' in debug
    print("✅ 設定取得メソッドテスト成功\n")

def test_runtime_config_change():
    """実行時設定変更のテスト"""
    print("=== 実行時設定変更テスト ===")
    
    # 元の設定を保存
    original_speed = LaserConfig.INITIAL_SPEED
    original_threshold = LaserConfig.HIT_THRESHOLD
    
    # 設定変更
    LaserConfig.INITIAL_SPEED = 999.0
    LaserConfig.HIT_THRESHOLD = 5.0
    
    # 新しいレーザーに反映されるか確認
    laser = LaserType01(100, 100, 150, 150, target_enemy_id=4)
    
    print(f"Changed Initial Speed: {laser.initial_speed} (expected: 999.0)")
    print(f"Changed Hit Threshold: {laser.hit_threshold} (expected: 5.0)")
    
    assert laser.initial_speed == 999.0
    assert laser.hit_threshold == 5.0
    
    # 設定を元に戻す
    LaserConfig.INITIAL_SPEED = original_speed
    LaserConfig.HIT_THRESHOLD = original_threshold
    print("✅ 実行時設定変更テスト成功\n")

if __name__ == "__main__":
    print("LaserConfig動作確認テスト開始\n")
    
    try:
        test_default_config()
        test_easy_mode()
        test_hard_mode()
        test_config_methods()
        test_runtime_config_change()
        
        print("🎉 全てのテストが成功しました！")
        print("\n📝 設定外部化の利点:")
        print("- マジックナンバーの排除")
        print("- 設定の一元管理")
        print("- プロファイル切り替え機能")
        print("- 実行時設定変更の容易さ")
        print("- テストとデバッグの改善")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        sys.exit(1)