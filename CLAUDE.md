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
- **debug.md**: 自動生成ログファイル
  - ロックイベント（敵ID、位置、ロックリスト）
  - 発射イベント（ロックリスト、発射数、ターゲット詳細）
  - ヒットイベント（終了理由、フレーム数）

### Files Involved
- **homing.py**: メイン実装ファイル
- **Common.py**: DEBUGフラグとcheck_collision関数
- **debug.md**: 自動生成デバッグログ
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

## TODO
- [ ] プロジェクトの詳細な説明を追加
- [ ] 依存関係の明記
- [ ] テスト方法の記載
- [ ] ビルド手順の追加（必要に応じて）