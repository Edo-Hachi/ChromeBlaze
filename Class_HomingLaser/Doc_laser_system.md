# ChromeBlaze ホーミングレーザーシステム技術仕様書

## 概要

ChromeBlazeのホーミングレーザーシステムは、RayForce風の高精度ホーミング機能を実現するために設計された統合システムです。段階的減速アルゴリズムと100%命中保証システムにより、滑らかで確実な追尾動作を提供します。

## システム構成

### 核心クラス構造

```
ホーミングレーザーシステム
├── LaserType01 (メインレーザークラス)
├── LaserConfig (設定管理)
├── Vector2D (数学計算)
├── LaserTelemetry (デバッグ・分析)
└── Player (統合制御)
```

## 主要クラス詳細

### 1. LaserType01 (コアレーザーシステム)

**ファイル**: `LaserType01.py`

#### 責任範囲
- ホーミング軌道計算
- 段階的減速制御
- 100%命中判定
- 軌跡描画
- テレメトリーデータ収集

#### 核心メソッド

```python
def __init__(start_x, start_y, target_x, target_y, target_enemy_id, config)
    # 初期化（設定・位置・方向・テレメトリー）

def update(delta_time, target_x, target_y) -> bool
    # フレーム毎更新（6段階処理）
    
def _calculate_homing_direction(delta_time) -> (distance, turn_speed)
    # Vector2D使用のホーミング計算
    
def _apply_speed_decay()
    # 段階的減速アルゴリズム
    
def check_collision(enemy) -> bool
    # 100%命中保証システム
```

#### アルゴリズム特徴

**段階的減速システム**:
```python
# グルグル現象を解決する核心技術
initial_speed: 500.0    # 高速接近
min_speed: 300.0        # 精密追尾
speed_decay: 5.0        # フレーム毎減速
```

**適応旋回制御**:
```python
# 距離に応じた旋回速度調整
if distance < transition_distance:  # 150.0px
    turn_speed = slow + (fast - slow) * ratio
```

### 2. LaserConfig (設定管理システム)

**ファイル**: `LaserConfig.py`

#### 設定カテゴリ

##### 物理演算設定
```python
initial_speed: 500.0      # 初期速度（px/s）
min_speed: 300.0          # 最低速度（px/s）
speed_decay: 5.0          # 減速量（px/s/frame）
```

##### ホーミング設定
```python
turn_speed_slow: 8.0      # 初期旋回速度（rad/s）
turn_speed_fast: 20.0     # 近距離旋回速度（rad/s）
transition_distance: 150.0 # 切り替え距離（px）
```

##### 判定設定
```python
hit_threshold: 10.0       # ヒット判定距離（px）
collision_threshold: 15.0 # コリジョン判定距離（px）
```

##### 表示設定
```python
max_trail_length: 10      # 軌跡長
trail_color: 11          # 軌跡色（CYAN）
```

#### 設定プロファイル機能

```python
LaserProfiles.easy_mode()    # 簡単（hit_threshold: 15.0）
LaserProfiles.normal_mode()  # 通常（デフォルト）
LaserProfiles.hard_mode()    # 難しい（hit_threshold: 8.0）
LaserProfiles.debug_mode()   # デバッグ用
```

### 3. Vector2D (数学計算エンジン)

**ファイル**: `Vector2D.py`

#### 核心機能

**基本演算**:
```python
Vector2D(x, y)              # 基本コンストラクタ
Vector2D.from_angle(angle)  # 角度からベクター生成
magnitude()                 # ベクター長計算
normalize()                 # 正規化
```

**ホーミング用計算**:
```python
distance_to(other)          # 距離計算
direction_to(other)         # 方向ベクター
angle_difference(a1, a2)    # 角度差計算（-π〜π）
```

**最適化機能**:
```python
magnitude_squared()         # sqrt回避高速計算
distance_squared_to()       # 距離二乗計算
```

### 4. LaserTelemetry (分析システム)

**ファイル**: `LaserTelemetry.py`

#### 機能概要
- フレーム毎データ記録
- グルグル現象検出
- 構造化ログ出力
- パフォーマンス分析

#### 出力ファイル

**Homing.log**: 詳細挙動分析
```
=== LASER ANALYSIS [timestamp] ===
Target Enemy ID: 3
End Reason: DISTANCE_HIT
Total Frames: 15
Minimum Distance: 8.45px
```

**debug.log**: 簡易サマリー
```
[timestamp] HIT: Frames=15, MinDist=8.45
```

## クラス依存関係図

```
Player.py
    ├── LaserType01.py (レーザー生成・管理)
    │   ├── LaserConfig.py (設定取得)
    │   ├── Vector2D.py (数学計算)
    │   └── LaserTelemetry.py (デバッグ)
    ├── Enemy.py (ターゲット管理)
    └── HitEffect.py (エフェクト表示)

LaserType01.py → LaserConfig.py
LaserType01.py → Vector2D.py
LaserType01.py → LaserTelemetry.py
LaserTelemetry.py → Common.py (DEBUGフラグ)
```

## パラメーター調整指針

### 基本バランス調整

#### 命中精度向上
```python
# より確実に命中させたい場合
hit_threshold: 15.0      # デフォルト: 10.0
collision_threshold: 20.0 # デフォルト: 15.0
```

#### 追尾性能調整
```python
# より鋭い追尾
turn_speed_fast: 25.0    # デフォルト: 20.0
transition_distance: 100.0 # デフォルト: 150.0

# より滑らかな追尾
turn_speed_slow: 6.0     # デフォルト: 8.0
speed_decay: 3.0         # デフォルト: 5.0
```

### パフォーマンス調整

#### 高フレームレート対応
```python
# delta_time使用により自動対応
# 60FPS/120FPS環境で同一挙動保証
```

#### メモリ使用量調整
```python
max_trail_length: 5      # 軌跡短縮（デフォルト: 10）
```

## デバッグ機能

### 問題診断システム

**グルグル現象検出**:
- 38フレーム超過の自動検出
- 距離縮小失敗パターン認識
- 根本原因分析レポート

**パフォーマンス監視**:
- フレーム毎の詳細状態記録
- 最小接近距離追跡
- 速度変化分析

### ログ分析ワークフロー

1. **問題発生**: ゲーム実行中の異常動作
2. **ログ確認**: `Homing.log`で詳細分析
3. **パターン特定**: AI支援による根本原因特定
4. **パラメーター調整**: 設定変更で解決
5. **効果確認**: 再テストで改善確認

## 運用時の注意点

### メモリ管理
- レーザーオブジェクトの適切な破棄
- 軌跡データの自動制限
- テレメトリーデータのサイズ管理

### パフォーマンス
- Vector2D使用による計算効率化
- DEBUGフラグによるテレメトリー制御
- magnitude_squared()使用での最適化

### エラーハンドリング
- ゼロ除算対策（Vector2D.normalize）
- 画面外レーザーの自動削除
- 無効ターゲットの安全処理

## 今後の拡張可能性

### 新機能追加
- 複数ターゲット同時追尾
- 障害物回避機能
- 弾道予測システム
- エフェクト強化

### システム統合
- 他武器システムとの連携
- AIエネミーとの相互作用
- 物理エンジン統合
- ネットワーク対応

## 技術的成果

### 解決した課題
- **グルグル現象**: 段階的減速により完全解決
- **命中精度**: 100%命中保証システム確立
- **デバッグ効率**: AI協働分析による高速問題解決
- **コード品質**: モジュール化による保守性向上

### 確立した技術
- **Vector2D統一**: 数学計算の標準化
- **設定外部化**: dataclass型安全管理
- **テレメトリー分離**: デバッグシステム独立化
- **段階的リファクタリング**: 安全な改善手法

この技術仕様書は、ChromeBlazeホーミングレーザーシステムの完全な理解と効果的な運用・拡張のための包括的ガイドです。