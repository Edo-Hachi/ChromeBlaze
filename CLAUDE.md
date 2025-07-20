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

## TODO
- [ ] プロジェクトの詳細な説明を追加
- [ ] 依存関係の明記
- [ ] テスト方法の記載
- [ ] ビルド手順の追加（必要に応じて）