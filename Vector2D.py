#!/usr/bin/env python3
"""
Vector2D - 2D Vector Utility Class for ChromeBlaze
2Dベクター計算ユーティリティクラス
"""

import math
from typing import Tuple, Union

class Vector2D:
    """2Dベクトルクラス - 角度計算・正規化・回転を統一管理"""
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        """
        2Dベクトルの初期化
        
        Args:
            x: X成分
            y: Y成分
        """
        self.x = float(x)
        self.y = float(y)
    
    @classmethod
    def from_tuple(cls, pos: Tuple[float, float]) -> 'Vector2D':
        """タプルからVector2Dを作成"""
        return cls(pos[0], pos[1])
    
    @classmethod
    def from_angle(cls, angle: float, magnitude: float = 1.0) -> 'Vector2D':
        """角度と大きさからVector2Dを作成"""
        return cls(math.cos(angle) * magnitude, math.sin(angle) * magnitude)
    
    def to_tuple(self) -> Tuple[float, float]:
        """タプル形式で返す"""
        return (self.x, self.y)
    
    def magnitude(self) -> float:
        """ベクトルの大きさ（長さ）を計算"""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def magnitude_squared(self) -> float:
        """ベクトルの大きさの二乗（sqrt計算を避けて高速化）"""
        return self.x * self.x + self.y * self.y
    
    def angle(self) -> float:
        """ベクトルの角度をラジアンで返す"""
        return math.atan2(self.y, self.x)
    
    def angle_degrees(self) -> float:
        """ベクトルの角度を度数法で返す"""
        return math.degrees(self.angle())
    
    def normalize(self) -> 'Vector2D':
        """正規化されたベクトルを返す（元のベクトルは変更しない）"""
        mag = self.magnitude()
        if mag > 0:
            return Vector2D(self.x / mag, self.y / mag)
        return Vector2D(0, 0)
    
    def normalize_self(self) -> 'Vector2D':
        """自身を正規化（元のベクトルを変更）"""
        mag = self.magnitude()
        if mag > 0:
            self.x /= mag
            self.y /= mag
        else:
            self.x = self.y = 0
        return self
    
    def distance_to(self, other: 'Vector2D') -> float:
        """他のベクトルとの距離を計算"""
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx * dx + dy * dy)
    
    def distance_squared_to(self, other: 'Vector2D') -> float:
        """他のベクトルとの距離の二乗（高速版）"""
        dx = other.x - self.x
        dy = other.y - self.y
        return dx * dx + dy * dy
    
    def direction_to(self, other: 'Vector2D') -> 'Vector2D':
        """他のベクトルへの方向ベクトル（正規化済み）を返す"""
        return (other - self).normalize()
    
    def angle_to(self, other: 'Vector2D') -> float:
        """他のベクトルへの角度を計算"""
        return (other - self).angle()
    
    def rotate(self, angle: float) -> 'Vector2D':
        """指定角度回転したベクトルを返す（元のベクトルは変更しない）"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2D(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )
    
    def rotate_self(self, angle: float) -> 'Vector2D':
        """自身を指定角度回転（元のベクトルを変更）"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        new_x = self.x * cos_a - self.y * sin_a
        new_y = self.x * sin_a + self.y * cos_a
        self.x = new_x
        self.y = new_y
        return self
    
    def lerp(self, other: 'Vector2D', t: float) -> 'Vector2D':
        """線形補間（t=0で自身、t=1で相手）"""
        return Vector2D(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t
        )
    
    def dot(self, other: 'Vector2D') -> float:
        """内積を計算"""
        return self.x * other.x + self.y * other.y
    
    def cross(self, other: 'Vector2D') -> float:
        """外積のZ成分を計算（2Dでは スカラー値）"""
        return self.x * other.y - self.y * other.x
    
    def copy(self) -> 'Vector2D':
        """コピーを作成"""
        return Vector2D(self.x, self.y)
    
    # 演算子オーバーロード
    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        """ベクトル加算"""
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        """ベクトル減算"""
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: Union[float, int]) -> 'Vector2D':
        """スカラー倍"""
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar: Union[float, int]) -> 'Vector2D':
        """スカラー倍（逆順）"""
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar: Union[float, int]) -> 'Vector2D':
        """スカラー除算"""
        return Vector2D(self.x / scalar, self.y / scalar)
    
    def __neg__(self) -> 'Vector2D':
        """符号反転"""
        return Vector2D(-self.x, -self.y)
    
    def __eq__(self, other: 'Vector2D') -> bool:
        """等価判定"""
        return abs(self.x - other.x) < 1e-10 and abs(self.y - other.y) < 1e-10
    
    def __repr__(self) -> str:
        """文字列表現"""
        return f"Vector2D({self.x:.3f}, {self.y:.3f})"
    
    def __str__(self) -> str:
        """文字列表現（簡略版）"""
        return f"({self.x:.2f}, {self.y:.2f})"

# ユーティリティ関数
def angle_difference(angle1: float, angle2: float) -> float:
    """2つの角度の差を-π～πの範囲で計算"""
    diff = angle2 - angle1
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff

def clamp_angle(angle: float) -> float:
    """角度を-π～πの範囲にクランプ"""
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle

# 定数
ZERO = Vector2D(0, 0)
ONE = Vector2D(1, 1)
UP = Vector2D(0, -1)
DOWN = Vector2D(0, 1)
LEFT = Vector2D(-1, 0)
RIGHT = Vector2D(1, 0)