from enum import Enum

class LockOnState(Enum):
    """
    ロックオンシステムの状態を管理するEnum
    
    IDLE: アイドル状態 - 白カーソル、コリジョンチェックなし
    STANDBY: スタンバイ状態 - 緑カーソル、コリジョンチェックあり  
    COOLDOWN: クールダウン状態 - 黄カーソル、コリジョンチェックなし
    SHOOTING: 発射中状態 - グレーカーソル、コリジョンチェックなし
    """
    IDLE = "idle"
    STANDBY = "standby" 
    COOLDOWN = "cooldown"
    SHOOTING = "shooting"