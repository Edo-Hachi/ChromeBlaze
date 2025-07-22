#!/usr/bin/env python3
"""
Hit Effect System for ChromeBlaze
ヒットエフェクトシステム
"""

import pyxel

class HitEffect:
    """ヒットエフェクトクラス"""
    def __init__(self, x, y, effect_type="circle"):
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.duration = 10  # 10フレーム表示
        self.timer = 0
        self.active = True
        
        # エフェクトの設定
        self.color = pyxel.COLOR_RED
        self.radius = 6  # 円の半径
        
    def update(self):
        """エフェクトの更新"""
        if not self.active:
            return
            
        self.timer += 1
        
        # 10フレーム経過後に非アクティブ化
        if self.timer >= self.duration:
            self.active = False
    
    def draw(self):
        """エフェクトの描画"""
        if not self.active:
            return
            
        if self.effect_type == "circle":
            # 赤い丸を描画
            pyxel.circ(int(self.x), int(self.y), self.radius, self.color)

class HitEffectManager:
    """ヒットエフェクト管理クラス"""
    def __init__(self):
        self.effects = []
    
    def add_effect(self, x, y, effect_type="circle"):
        """エフェクトを追加"""
        effect = HitEffect(x, y, effect_type)
        self.effects.append(effect)
    
    def update(self):
        """全エフェクトの更新"""
        for effect in self.effects:
            effect.update()
        
        # 非アクティブなエフェクトを削除
        self.effects = [effect for effect in self.effects if effect.active]
    
    def draw(self):
        """全エフェクトの描画"""
        for effect in self.effects:
            effect.draw()