#!/usr/bin/env python3
"""
Enemy Management System for ChromeBlaze
エネミー管理システム
"""

import pyxel
import math
import random

class Enemy:
    """エネミー管理クラス"""
    def __init__(self, enemy_id, x, y, sprite_size, screen_width, screen_height):
        self.enemy_id = enemy_id
        self.x = float(x)
        self.y = float(y)
        self.active = True
        self.sprite_size = sprite_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 移動設定
        self.speed = 25  # ピクセル/秒
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # ランダム移動制御
        self.move_timer = 0.0
        self.direction_duration = 3.0  # 3秒間同じ方向
        
        # 初期方向設定
        self._generate_random_direction()
    
    def _generate_random_direction(self):
        """3秒間持続するランダムな移動方向を生成"""
        # ランダムな角度（0-360度）
        angle = random.uniform(0, 2 * math.pi)
        
        # 速度ベクトルを計算
        self.velocity_x = math.cos(angle) * self.speed
        self.velocity_y = math.sin(angle) * self.speed
    
    def update(self, delta_time):
        """エネミーの更新"""
        if not self.active:
            return
        
        # ランダム移動タイマー更新
        self.move_timer += delta_time
        
        # 3秒ごとに新しいランダム方向を生成
        if self.move_timer >= self.direction_duration:
            self.move_timer = 0.0
            self._generate_random_direction()
        
        # 位置更新
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        
        # 画面端での境界チェック（反射）
        if self.x <= 0:
            self.x = 0
            self.velocity_x = abs(self.velocity_x)  # 右向きに反転
        elif self.x >= self.screen_width - self.sprite_size:
            self.x = self.screen_width - self.sprite_size
            self.velocity_x = -abs(self.velocity_x)  # 左向きに反転
            
        if self.y <= 0:
            self.y = 0
            self.velocity_y = abs(self.velocity_y)  # 下向きに反転
        elif self.y >= self.screen_height // 2:  # 画面上半分に制限
            self.y = self.screen_height // 2
            self.velocity_y = -abs(self.velocity_y)  # 上向きに反転
    
    def draw(self, sprite_manager, sprite_size):
        """エネミーの描画"""
        if not self.active:
            return
        
        # ENEMY01スプライト（フレーム0）を表示
        enemy_sprite = sprite_manager.get_sprite_by_name_and_field("ENEMY01", "FRAME_NUM", "0")
        if enemy_sprite:
            pyxel.blt(int(self.x), int(self.y), 0, enemy_sprite.x, enemy_sprite.y, 
                     sprite_size, sprite_size, pyxel.COLOR_BLACK)

class EnemyManager:
    """エネミー群管理クラス"""
    def __init__(self, sprite_size, screen_width, screen_height):
        self.enemies = []
        self.sprite_size = sprite_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 5体のエネミーを生成
        self._spawn_enemies()
    
    def _spawn_enemies(self):
        """5体のエネミーを異なる位置に配置"""
        positions = [
            (50, 30),   # 左上
            (150, 40),  # 右上
            (100, 60),  # 中央上
            (80, 80),   # 左中
            (180, 70)   # 右中
        ]
        
        for i, (x, y) in enumerate(positions):
            enemy = Enemy(i, x, y, self.sprite_size, self.screen_width, self.screen_height)
            self.enemies.append(enemy)
    
    def update(self, delta_time):
        """全エネミーの更新"""
        for enemy in self.enemies:
            enemy.update(delta_time)
    
    def draw(self, sprite_manager):
        """全エネミーの描画"""
        for enemy in self.enemies:
            enemy.draw(sprite_manager, self.sprite_size)
    
    def get_active_enemies(self):
        """アクティブなエネミーのリストを取得"""
        return [enemy for enemy in self.enemies if enemy.active]
    
    def get_enemy_by_id(self, enemy_id):
        """IDでエネミーを取得"""
        for enemy in self.enemies:
            if enemy.enemy_id == enemy_id:
                return enemy
        return None
    
    def remove_enemy(self, enemy_id):
        """エネミーをactiveをFalseにして削除"""
        enemy = self.get_enemy_by_id(enemy_id)
        if enemy:
            enemy.active = False
            return True
        return False