
システムを回収するプラン（検討中です。

#まだ実装しませんよ


==== Laser System Refactoring Plan ====

[日本語版]

■ 現状の課題
<!-- 完了//1. ベクトル演算が複数箇所に散在 -->
2. Playerクラスでレーザーを直接生成（責務が重い）
3. レーザーの大量生成・破棄によるパフォーマンス低下

■ 改善提案
<!-- //1. Vector2Dクラスの導入（角度計算・正規化・回転を統一） -->
2. Factoryパターンでレーザー生成を集中管理
3. オブジェクトプーリングでGC負荷を軽減(10発くらいしかレーザー打ってないし、長さも短くしたから効果は不明)

■ 実装例
<!-- 完了！ -->
<!-- ### 1. Vector2D -->
<!-- class Vector2D:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y

    def angle(self):
        return math.atan2(self.y, self.x)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        mag = self.magnitude()
        return Vector2D(self.x / mag, self.y / mag) if mag > 0 else Vector2D(0, 0) -->

### 2. LaserFactory
class LaserFactory:
    @staticmethod
    def create_homing_laser(start_pos, target_pos, enemy_id, config=None):
        return LaserType01(start_pos.x, start_pos.y, target_pos.x, target_pos.y, enemy_id, config)

### 3. LaserPool
class LaserPool:
    def __init__(self, pool_size=50):
        self._available = []
        self._active = []
        self._create_pool(pool_size)

    def acquire_laser(self, start_x, start_y, target_x, target_y, enemy_id):
        if self._available:
            laser = self._available.pop()
            laser.reset(start_x, start_y, target_x, target_y, enemy_id)
        else:
            laser = LaserType01(start_x, start_y, target_x, target_y, enemy_id)
        self._active.append(laser)
        return laser

    def release_laser(self, laser):
        self._active.remove(laser)
        self._available.append(laser)


[English Version]

■ Current Issues
1. Vector math operations scattered across code
2. Player class directly creates LaserType01 (tight coupling)
3. Frequent creation/destruction of lasers causes performance issues

■ Suggested Improvements
1. Introduce Vector2D utility class for angle/normalization/rotation
2. Implement Factory Pattern for centralized laser creation
3. Add Object Pooling to reduce GC overhead

■ Code Examples
(See Japanese section for Python code snippets)
