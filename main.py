# ChromeBlaze ゲームのメインエントリーポイント
# このファイルがゲーム全体の司令塔として動作します


# *** Special Prompt ***
# name: game-developer
# description: Build games with Pyxel, Godot, Unity, Unreal Engine, or web technologies. Implements game mechanics, physics, AI, and optimization. Use PROACTIVELY for game development, engine integration, or gameplay programming.
# ---

# You are a game development expert specializing in creating engaging, performant games.

# ## Focus Areas
# - Game engine expertise (Unity, Unreal, Godot)
# - Gameplay mechanics and systems design
# - Physics simulation and collision detection
# - AI behavior trees and pathfinding
# - Performance optimization for 60+ FPS
# - Multiplayer networking and synchronization

# ## Approach
# 1. Prototype gameplay mechanics quickly
# 2. Use component-based architecture (ECS)
# 3. Optimize draw calls and batch rendering
# 4. Implement object pooling for performance
# 5. Design for multiple input methods
# 6. Profile early and optimize bottlenecks

# ## Technical Skills
# - Shader programming (HLSL/GLSL)
# - Animation systems and state machines
# - Procedural generation algorithms
# - Audio integration and 3D sound
# - Save system and progression tracking
# - Platform-specific optimizations

# ## Output
# - Clean, modular game code
# - Performance profiling results
# - Input handling for multiple devices
# - Networking code for multiplayer
# - Level design tools and editors
# - Documentation for game systems

# Balance fun gameplay with technical performance.


import pyxel          # Pyxelゲームエンジンをインポート（ゲーム画面や音声を管理）
import logging        # Pythonの標準ログ機能（コンソールにメッセージを出力）
import sys            # システム関連の機能（プログラム終了など）
from Common import GameState, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DISPLAY_SCALE  # ゲームの基本設定
from SpriteManager import sprite_manager      # スプライト（キャラクターの画像）を管理
from State_StudioLogo import StudioLogoState  # スタジオロゴ画面の処理
from State_Title import TitleState            # タイトル画面の処理  
from State_Game import GamePlayState          # 実際のゲーム画面の処理
from GameLogger import logger                 # ChromeBlaze専用のログシステム

# Pythonの標準ログ設定（時刻とメッセージレベルを表示）
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Game:
    """
    ゲーム全体の状態を管理するクラス
    ゲームには3つの画面があります：ロゴ→タイトル→ゲーム本編
    """
    def __init__(self):
        """ゲームの初期化（最初に1回だけ実行される）"""
        logging.info("Initializing Game")
        logger.info("Game initialization started")
        try:
            # 最初はロゴ画面から開始
            self.state = GameState.LOGO
            
            # 各画面の処理を担当するオブジェクトを作成
            self.studio_logo_state = StudioLogoState()  # ロゴ画面
            self.title_state = TitleState()              # タイトル画面
            self.game_state = GamePlayState()            # ゲーム本編画面
            
            logging.info("Game initialization completed")
            logger.info("All game states initialized successfully")
        except Exception as e:
            # もし初期化でエラーが発生したらログに記録してプログラム終了
            logging.error(f"Failed to initialize game: {e}")
            logger.error(f"Game initialization failed: {e}")
            raise  # エラーを上位に伝える
        
    def update(self):
        """
        毎フレーム（1/60秒ごと）呼ばれる更新処理
        現在どの画面にいるかによって処理を切り替える
        """
        try:
            # 現在の画面状態に応じて処理を分ける
            if self.state == GameState.LOGO:
                # ロゴ画面の処理を実行
                new_state = self.studio_logo_state.update()
                # もし画面遷移が発生したら（ロゴ→タイトルなど）
                if new_state != self.state:
                    logging.info(f"State transition: {self.state.value} -> {new_state.value}")
                    logger.state_change(f"Game state: {self.state.value} -> {new_state.value}")
                    self.state = new_state  # 新しい画面に切り替え
                    
            elif self.state == GameState.TITLE:
                # タイトル画面の処理を実行
                new_state = self.title_state.update()
                # 画面遷移チェック（タイトル→ゲーム本編など）
                if new_state != self.state:
                    logging.info(f"State transition: {self.state.value} -> {new_state.value}")
                    logger.state_change(f"Game state: {self.state.value} -> {new_state.value}")
                    self.state = new_state
                    
            elif self.state == GameState.GAME:
                # ゲーム本編の処理を実行
                new_state = self.game_state.update()
                # 画面遷移チェック（ゲーム→タイトルなど）
                if new_state != self.state:
                    logging.info(f"State transition: {self.state.value} -> {new_state.value}")
                    logger.state_change(f"Game state: {self.state.value} -> {new_state.value}")
                    self.state = new_state
                    
        except Exception as e:
            # エラーが発生してもゲームを止めずにログに記録
            logging.error(f"Error in game update: {e}")
    
    def draw(self):
        """
        毎フレーム（1/60秒ごと）呼ばれる描画処理
        現在の画面状態に応じて適切な画面を描画する
        """
        try:
            # 画面を黒色でクリア（古い描画内容を消去）
            pyxel.cls(pyxel.COLOR_BLACK)
            
            # 現在の画面状態に応じて描画処理を分ける
            if self.state == GameState.LOGO:
                # ロゴ画面を描画
                self.studio_logo_state.draw()
            elif self.state == GameState.TITLE:
                # タイトル画面を描画
                self.title_state.draw() 
            elif self.state == GameState.GAME:
                # ゲーム本編画面を描画
                self.game_state.draw()
                
        except Exception as e:
            # 描画でエラーが発生した場合の緊急処理
            logging.error(f"Error in game draw: {e}")
            # エラーメッセージを画面に表示（プレイヤーに状況を知らせる）
            pyxel.text(10, 10, f"Draw Error: {str(e)[:30]}", pyxel.COLOR_RED)

class App:
    """
    ChromeBlazeアプリケーション全体を管理するクラス
    Pyxelエンジンの初期化からゲーム開始まで全て担当
    """
    def __init__(self):
        """アプリケーションの初期化（プログラム開始時に1回だけ実行）"""
        logging.info("Starting Chrome Blaze")
        logger.info("=== ChromeBlaze Application Starting ===")
        try:
            # Pyxelゲームエンジンを初期化
            # 画面サイズ、タイトル、フレームレート、表示倍率を設定
            pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Chrome Blaze", fps=FPS, display_scale=DISPLAY_SCALE)
            logging.info(f"Pyxel initialized: {SCREEN_WIDTH}x{SCREEN_HEIGHT}, FPS={FPS}")
            logger.info(f"Pyxel window: {SCREEN_WIDTH}x{SCREEN_HEIGHT}, {FPS}FPS, scale={DISPLAY_SCALE}")
            
            # ゲームで使用する画像・音声データを読み込み
            pyxel.load("my_resource.pyxres")
            logging.info("Pyxel resources loaded successfully")
            
            # スプライト管理システムの初期化状況を確認
            try:
                sprite_count = len(sprite_manager.json_sprites)
                if sprite_count > 0:
                    logging.info(f"Sprite manager loaded {sprite_count} sprites from JSON")
                    # プレイヤーキャラクターのスプライトが正しく読み込まれているかチェック
                    player_sprites = [key for key, sprite in sprite_manager.json_sprites.items() 
                                    if sprite.get("NAME") == "PLAYER"]
                    logging.info(f"Found {len(player_sprites)} player sprites: {player_sprites}")
                else:
                    logging.warning("No sprites loaded - sprite rendering may fail")
            except Exception as e:
                logging.error(f"Sprite manager initialization error: {e}")
            
            # ゲーム本体を作成
            self.game = Game()
            logging.info("Game instance created, starting main loop")
            
            # Pyxelのメインループを開始（ここから60FPS でupdate/drawが呼ばれ続ける）
            pyxel.run(self.update, self.draw)
            
        except FileNotFoundError as e:
            # 必要なファイル（my_resource.pyxresなど）が見つからない場合
            logging.error(f"Resource file not found: {e}")
            sys.exit(1)  # プログラム終了
        except Exception as e:
            # その他の予期しないエラーが発生した場合
            logging.error(f"Failed to initialize app: {e}")
            sys.exit(1)  # プログラム終了

    def update(self):
        """
        毎フレーム呼ばれる更新処理（Pyxelから自動で呼び出される）
        ESCキーでの終了処理とゲーム本体の更新を行う
        """
        try:
            # ESCキーが押されたらゲーム終了
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                logging.info("User requested exit via ESC key")
                logger.info("ESC pressed - Application exit requested")
                pyxel.quit()  # Pyxelを終了してプログラムも終了
                
            # ゲーム本体の更新処理を実行
            self.game.update()
            
        except Exception as e:
            # 致命的なエラーが発生した場合はゲームを終了
            logging.error(f"Critical error in update loop: {e}")
            pyxel.quit()

    def draw(self):
        """
        毎フレーム呼ばれる描画処理（Pyxelから自動で呼び出される）
        ゲーム本体の描画を行う
        """
        try:
            # ゲーム本体の描画処理を実行
            self.game.draw()
            
        except Exception as e:
            # 致命的な描画エラーが発生した場合の緊急処理
            logging.error(f"Critical error in draw loop: {e}")
            pyxel.cls(pyxel.COLOR_BLACK)  # 画面をクリア
            # エラーメッセージを画面に表示
            pyxel.text(10, 10, "CRITICAL ERROR", pyxel.COLOR_RED)

def main():
    """
    プログラムのメイン関数
    python main.py で実行されたときに最初に呼ばれる
    """
    try:
        # ChromeBlazeアプリケーションを開始
        App()
        
    except KeyboardInterrupt:
        # Ctrl+C でプログラムが中断された場合
        logging.info("Game interrupted by user")
        
    except Exception as e:
        # 予期しないエラーが発生した場合
        logging.error(f"Unhandled exception: {e}")
        sys.exit(1)  # エラーコード1でプログラム終了

# このファイルが直接実行された場合（python main.py）にmain関数を呼び出す
# 他のファイルからimportされた場合は実行されない
if __name__ == "__main__":
    main()