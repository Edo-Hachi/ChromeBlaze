#!/usr/bin/env python3
"""
GameLogger - Unified Logging System for ChromeBlaze
統一ログシステム
"""

import datetime
import os
from Common import DEBUG

class GameLogger:
    """ゲーム全体の統一ログシステム"""
    
    _instance = None
    _log_file = "debug_log/debug.log"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._clear_log()
            self.log("=== ChromeBlaze Game Session Started ===")
    
    def _clear_log(self):
        """ログファイルをクリア"""
        try:
            # debug_log/ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(self._log_file), exist_ok=True)
            with open(self._log_file, 'w', encoding='utf-8') as f:
                f.write("")
        except Exception as e:
            if DEBUG:
                print(f"Failed to clear log file: {e}")
    
    def _get_timestamp(self):
        """現在時刻のタイムスタンプを取得"""
        return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    def log(self, message, category="INFO"):
        """統一ログ出力"""
        timestamp = self._get_timestamp()
        formatted_message = f"[{timestamp}] {category}: {message}"
        
        # コンソールにも出力（DEBUGフラグで制御）
        if DEBUG:
            print(formatted_message)
        
        # ファイルに出力（DEBUGフラグに関係なく常に出力）
        try:
            # debug_log/ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(self._log_file), exist_ok=True)
            with open(self._log_file, 'a', encoding='utf-8') as f:
                f.write(formatted_message + "\n")
                f.flush()  # 即座にファイルに書き込み
        except Exception as e:
            if DEBUG:
                print(f"Failed to write to log file: {e}")
    
    def debug(self, message):
        """デバッグレベルのログ"""
        self.log(message, "DEBUG")
    
    def info(self, message):
        """情報レベルのログ"""
        self.log(message, "INFO")
    
    def warning(self, message):
        """警告レベルのログ"""
        self.log(message, "WARNING")
    
    def error(self, message):
        """エラーレベルのログ"""
        self.log(message, "ERROR")
    
    def player_action(self, message):
        """プレイヤーアクション専用ログ"""
        self.log(message, "PLAYER")
    
    def laser_event(self, message):
        """レーザーイベント専用ログ"""
        self.log(message, "LASER")
    
    def state_change(self, message):
        """状態変化専用ログ"""
        self.log(message, "STATE")
    
    def section(self, title):
        """セクション区切り"""
        separator = "=" * 50
        self.log(separator, "SECTION")
        self.log(f" {title} ", "SECTION")
        self.log(separator, "SECTION")
    
    def separator(self):
        """簡単な区切り線"""
        self.log("-" * 30, "SEP")

# グローバルインスタンス
logger = GameLogger()