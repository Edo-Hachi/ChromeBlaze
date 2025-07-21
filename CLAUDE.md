# ChromeBlaze Project

## Overview
Pyxelベースのゲームプロジェクト

## Project Structure
```
ChromeBlaze/
├── main.py                 # メインエントリーポイント
├── Common.py              # 共通機能
├── SpriteDefiner.py       # スプライト定義ツール
├── SpriteManager.py       # スプライト管理
├── State_StudioLogo.py    # スタジオロゴ状態
├── State_Title.py         # タイトル画面状態
├── State_Game.py          # ゲーム状態
└── my_resource.pyxres     # Pyxelリソースファイル
```

## Running the Project
```bash
python main.py
```

## Development Notes
- 状態管理パターンを使用してゲーム画面を管理
- Pyxelライブラリを使用した2Dゲーム開発
- スプライト定義・管理システムを独自実装

## Git Repository
- Repository: https://github.com/Edo-Hachi/ChromeBlaze.git
- Main branch: `main`

## VS Code Configuration
- デバッグ設定済み（.vscode/launch.json）
- main.pyをエントリーポイントとして設定

## RayForce-Style Multi-Lock Laser System (homing.py)

### Overview
完全なRayForce風マルチロックオンレーザーシステムを実装。ステップバイステップで開発し、最終的に完全に機能するシステムが完成した。

### Key Features
1. **Lock-on Cursor System**: プレイヤー位置から-60ピクセルオフセットに表示される照準カーソル
2. **Multi-Enemy Lock-on**: 複数の敵を同時にロックオン可能（同一敵への重複ロック可能）
3. **Mass Fire System**: Xキーで全ロックオン対象に同時レーザー発射
4. **Visual Scatter System**: 同一対象への複数レーザーも視覚的に区別可能
5. **Per-Laser Target Tracking**: 各レーザーが独自のターゲットを追尾

### Technical Implementation

#### Core Classes
- **Enemy**: エネミー管理（ID、ランダム移動、境界反射）
- **EnemyManager**: 5体のエネミー群管理
- **LaserType01**: ホーミングレーザー（線形補間＋角度制限）
- **HomingLaserTest**: メインゲームループ

#### Key Parameters
```python
# Visual Scatter Settings
scatter_range = 500  # ±500ピクセルの大幅なばらつき
start_scatter = 10   # 発射位置のばらつき±10ピクセル

# Laser Configuration
speed = 500.0                    # レーザー速度
turn_speed_slow = 8.0           # 初期旋回速度
turn_speed_fast = 20.0          # 近距離時旋回速度
transition_distance = 150.0     # 旋回速度切り替え距離
```

#### Controls
- **Arrow Keys**: プレイヤー移動
- **Z**: カーソルがエネミー上にある時にロックオン
- **X**: ロックオンした全ターゲットに一斉レーザー発射
- **Q/ESC**: 終了

### Development Process
1. **Step 1**: ロックオンカーソル表示（プレイヤー-30ピクセル位置）
2. **Step 2**: カーソルとエネミーのコリジョン検出
3. **Step 3**: Zキー押下時のエネミーIDロック機能
4. **Step 4**: 同一エネミーへの重複ロック許可
5. **Step 5**: Xキーでの一斉レーザー発射システム
6. **Step 6**: ターゲット追尾バグ修正（全レーザーが最初のエネミーを追尾する問題）
7. **Step 7**: ビジュアル散布システム追加（±500ピクセル散布）

### Major Bug Fixes
1. **Target Tracking Issue**: 全レーザーが`active_enemies[0]`を追尾していた問題を、各レーザーに`target_enemy_id`を付与して個別追尾に修正
2. **Visual Distinction**: 同一ターゲットへの複数レーザーが同じ軌道を描く問題を、大幅な散布範囲（±500px）で解決

### Debug System
- **debug.log**: 自動生成ログファイル
  - ロックイベント（敵ID、位置、ロックリスト）
  - 発射イベント（ロックリスト、発射数、ターゲット詳細）
  - ヒットイベント（終了理由、フレーム数）

### Files Involved
- **homing.py**: メイン実装ファイル
- **Common.py**: DEBUGフラグとcheck_collision関数
- **debug.log**: 自動生成デバッグログ
- **sprites.json**: スプライト定義（PLAYER、ENEMY01）

### Performance Notes
- 最大10レーザー同時発射
- 60FPS動作
- エネミー速度: 25ピクセル/秒（調整済み）
- 画面サイズ: 256x256

### Test Results
実際のテストで以下を確認:
- 複数エネミーロックオン動作
- 同一エネミーへの重複ロック
- 視覚的に区別可能なレーザー軌道
- 正確なターゲット追尾
- システム全体の安定性

システムとして完成度が高く、RayForce風のゲームプレイを実現した。

## Refactoring Analysis for homing.py

### Overview
homing.pyの構造分析により、シンプル化とメンテナンス性向上のためのリファクタリング箇所を特定。ゲーム本体構築時の参考情報として記録。

### Major Refactoring Opportunities

#### 1. Code Cleanup (即効性: 高)
```python
# 削除対象
- LaserType01._write_debug_log() 304-320行: 大量のコメントアウトコード
- HomingLaserTest.update() 384-401行: 未使用のスペースキー処理
- 重複import random (38行, 102行)
```

#### 2. Large Method Decomposition (効果: 大)
```python
# 分割対象
- HomingLaserTest.update() (368-520行, 152行) 
  → update_input(), update_game_logic(), update_lasers()
- HomingLaserTest.draw() (521-600行, 79行)
  → draw_game_objects(), draw_ui(), draw_debug_info()
- LaserType01.update() (183-270行, 87行)
  → update_movement(), update_targeting(), update_trail()
```

#### 3. Magic Numbers Consolidation
```python
# 推奨: 設定クラス
class GameConfig:
    # Screen Settings
    SCREEN_SIZE = 256
    SPRITE_SIZE = 8
    
    # Laser Settings
    LASER_SPEED = 500.0
    LASER_TURN_SPEED_SLOW = 8.0
    LASER_TURN_SPEED_FAST = 20.0
    LASER_TRANSITION_DISTANCE = 150.0
    MAX_LASERS = 10
    MAX_TRAIL_LENGTH = 30
    
    # Lock-on Settings
    CURSOR_OFFSET_Y = -60
    MAX_LOCK_COUNT = 10
    
    # Visual Effects
    SCATTER_RANGE = 500
    START_SCATTER = 10
```

#### 4. Class Responsibility Separation
```python
# 推奨アーキテクチャ
class InputHandler:
    """入力処理専用"""
    def handle_player_movement()
    def handle_lock_on()
    def handle_fire()

class GameState:
    """ゲーム状態管理"""
    def update_entities()
    def check_collisions()
    def manage_locks()

class Renderer:
    """描画専用"""
    def draw_entities()
    def draw_ui()
    def draw_debug_info()

class LaserSystem:
    """レーザー管理システム"""
    def create_laser()
    def update_lasers()
    def cleanup_inactive_lasers()
```

### Implementation Priority

#### Phase 1: Quick Wins (削減効果: 200+ 行)
1. コメントアウトコード削除
2. 重複import整理
3. 未使用メソッド削除

#### Phase 2: Structure Improvement
1. 長大メソッドの分割
2. GameConfig導入
3. 基本的な責任分離

#### Phase 3: Architecture Refinement
1. 完全なクラス分離
2. デザインパターン適用
3. テスタビリティ向上

### Benefits for Main Game Development
- **保守性**: モジュール化により個別修正が容易
- **拡張性**: 新機能追加時の影響範囲限定
- **可読性**: 責任分離による理解の容易さ
- **テスト**: ユニットテスト導入の土台
- **再利用**: コンポーネントの他部分での活用

この分析結果を基に、メインゲーム開発時はクリーンなアーキテクチャを最初から構築することを推奨。

## High-Performance Sprite Management System

### Overview
ChromeBlazeプロジェクトで確立された高性能スプライト管理システム。PyxelShmupプロジェクトの知見を活用し、JSON駆動のスプライト管理と初期化時キャッシュによる最適化を実現。

### Core Architecture

#### JSON-Driven Sprite System
```json
{
  "sprites": {
    "40_0": {
      "x": 40, "y": 0,
      "NAME": "PBULLET",
      "FRAME_NUM": "0",
      "ANIM_SPD": "10"
    }
  }
}
```

#### Sprite Caching Pattern
**Key Principle**: 初期化時一括読み込み、実行時高速アクセス

```python
# ✅ High-Performance Pattern
class Player:
    def __init__(self, x, y):
        # 初期化時に全スプライトをキャッシュ
        self.sprites = {
            "TOP": sprite_manager.get_sprite_by_name_and_field("PLAYER", "ACT_NAME", "TOP"),
            "LEFT": sprite_manager.get_sprite_by_name_and_field("PLAYER", "ACT_NAME", "LEFT"),
            "RIGHT": sprite_manager.get_sprite_by_name_and_field("PLAYER", "ACT_NAME", "RIGHT")
        }
        self.exhaust_sprites = [
            sprite_manager.get_sprite_by_name_and_field("EXHST", "FRAME_NUM", "0"),
            sprite_manager.get_sprite_by_name_and_field("EXHST", "FRAME_NUM", "1"),
            sprite_manager.get_sprite_by_name_and_field("EXHST", "FRAME_NUM", "2"),
            sprite_manager.get_sprite_by_name_and_field("EXHST", "FRAME_NUM", "3")
        ]

    def draw(self):
        # 実行時は配列/辞書アクセスのみ
        player_sprite = self.sprites[self.sprite_direction]      # O(1)
        exhaust_sprite = self.exhaust_sprites[self.exhaust_index] # O(1)
```

### Performance Optimization Results

#### Before Optimization (Non-optimal)
```python
# ❌ 毎フレームJSON検索パターン
def draw(self):
    player_sprite = sprite_manager.get_sprite_by_name_and_field(...)  # 60FPS × JSON検索
    exhaust_sprite = sprite_manager.get_sprite_by_name_and_field(...) # 60FPS × JSON検索
```

#### After Optimization (High-performance)
```python
# ✅ キャッシュアクセスパターン  
def draw(self):
    player_sprite = self.sprites[self.sprite_direction]     # 60FPS × 辞書アクセス
    exhaust_sprite = self.exhaust_sprites[self.exhaust_index] # 60FPS × 配列アクセス
```

### Performance Metrics

#### Entity-Level Optimization
- **Player**: 7スプライト（Player×3 + Exhaust×4）を初期化時キャッシュ
- **Bullet**: 2スプライト（FRAME_NUM 0,1）を初期化時キャッシュ
- **JSON検索**: 初期化時のみ実行、実行時はメモリアクセス

#### System-Level Impact
- **画面解像度**: 128×128（最適化効果が顕著）
- **ターゲットFPS**: 60FPS安定動作
- **弾丸負荷**: 10発同時 × 60FPS = 600回/秒のスプライト描画を最適化

### Implementation Guidelines

#### 1. Sprite Caching Strategy
```python
# 固定パターンスプライト → 辞書キャッシュ
self.sprites = {"TOP": sprite, "LEFT": sprite, "RIGHT": sprite}

# アニメーションスプライト → 配列キャッシュ  
self.anim_sprites = [frame0, frame1, frame2, frame3]

# 実行時アクセス
sprite = self.sprites[direction]        # 方向指定
sprite = self.anim_sprites[frame_index] # フレーム指定
```

#### 2. Error Handling with Fallback
```python
def draw(self):
    try:
        # 高速スプライト描画
        sprite = self.sprites[self.direction]
        pyxel.blt(self.x, self.y, 0, sprite.x, sprite.y, 8, 8, 0)
    except Exception as e:
        # フォールバック: 矩形描画（開発時安全性）
        pyxel.rect(self.x, self.y, 8, 8, pyxel.COLOR_WHITE)
```

#### 3. Animation Management
```python
# JSON駆動アニメーション速度
self.animation_speed = sprite_manager.get_sprite_metadata("ENTITY", "ANIM_SPD", "10")

# フレーム計算
def _get_animation_frame(self, game_timer):
    cycle_position = game_timer % (self.animation_speed * 2)
    return 0 if cycle_position < self.animation_speed else 1
```

### Technical Benefits

#### Performance
- **60FPS安定**: 128×128解像度での滑らかな動作
- **メモリ効率**: 必要最小限のスプライトキャッシュ
- **CPU負荷軽減**: JSON検索からメモリアクセスへの最適化

#### Maintainability  
- **JSON外部化**: スプライト設定の柔軟な変更
- **キャッシュ統一**: 全エンティティで一貫したパターン
- **エラー安全**: フォールバック機構による堅牢性

#### Scalability
- **新エンティティ**: 同パターンで容易に追加可能
- **アニメーション拡張**: フレーム数増加に柔軟対応
- **画面解像度**: より高解像度での性能余裕

### Best Practices for Future Development

1. **初期化時キャッシュ**: 全スプライトを__init__で一括取得
2. **実行時最適化**: 辞書/配列アクセスのみ使用
3. **JSON駆動**: アニメーション速度等の外部設定化
4. **エラーハンドリング**: try-except + fallback描画
5. **統一パターン**: 全エンティティでキャッシュ方式統一

この最適化手法は、今後実装する敵機、エフェクト、UI要素等、全てのスプライト処理で標準として適用する。

## TODO
- [ ] プロジェクトの詳細な説明を追加
- [ ] 依存関係の明記
- [ ] テスト方法の記載
- [ ] ビルド手順の追加（必要に応じて）