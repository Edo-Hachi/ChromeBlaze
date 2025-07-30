#!/usr/bin/env python3
"""
LaserConfig dataclass版使用例
"""

from Class_HomingLaser import LaserConfig, LaserProfiles, default_laser_config, LaserType01

def example_usage():
    """dataclass版LaserConfigの使用例"""
    
    print("=== Dataclass版LaserConfig使用例 ===\n")
    
    # 1. デフォルト設定でレーザー作成
    print("1. デフォルト設定:")
    laser1 = LaserType01(100, 100, 150, 150)
    print(f"   Hit Threshold: {laser1.hit_threshold}")
    print(f"   Turn Speed Fast: {laser1.turn_speed_fast}")
    
    # 2. 簡単モード設定でレーザー作成  
    print("\n2. 簡単モード設定:")
    easy_config = LaserProfiles.easy_mode()
    laser2 = LaserType01(100, 100, 150, 150, config=easy_config)
    print(f"   Hit Threshold: {laser2.hit_threshold}")
    print(f"   Turn Speed Fast: {laser2.turn_speed_fast}")
    
    # 3. カスタム設定でレーザー作成
    print("\n3. カスタム設定:")
    custom_config = LaserConfig(
        initial_speed=800.0,
        hit_threshold=20.0,
        turn_speed_fast=30.0,
        trail_color=7  # pyxel.COLOR_WHITE
    )
    laser3 = LaserType01(100, 100, 150, 150, config=custom_config)
    print(f"   Initial Speed: {laser3.initial_speed}")
    print(f"   Hit Threshold: {laser3.hit_threshold}")
    print(f"   Turn Speed Fast: {laser3.turn_speed_fast}")
    
    # 4. 設定の部分的変更
    print("\n4. 部分的変更設定:")
    partial_config = LaserConfig(hit_threshold=5.0)  # 他はデフォルト値
    laser4 = LaserType01(100, 100, 150, 150, config=partial_config)
    print(f"   Hit Threshold: {laser4.hit_threshold} (変更)")
    print(f"   Initial Speed: {laser4.initial_speed} (デフォルト)")
    
    # 5. 設定情報の取得
    print("\n5. 設定情報取得:")
    physics = custom_config.get_physics_config()
    print(f"   Physics Config: {physics}")
    
    print("\n✅ dataclass版LaserConfigの利点:")
    print("   - 型安全性（型ヒント付き）")
    print("   - 部分的設定変更が簡単")
    print("   - インスタンスベースで柔軟")
    print("   - IDEの補完サポート")

if __name__ == "__main__":
    example_usage()