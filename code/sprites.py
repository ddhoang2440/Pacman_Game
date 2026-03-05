# code/sprites.py
import pygame
from settings import *
from algo import get_path_bfs

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, surface, sprite_type):
        super().__init__(groups)
        self.sprite_type = sprite_type # 'wall', 'food', 'power'
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)

class Ghost(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, player):
        super().__init__(groups)
        # Sử dụng hình ảnh màu đỏ cho Blinky
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill('red')
        self.rect = self.image.get_rect(topleft = pos)
        
        self.player = player
        self.obstacle_sprites = obstacle_sprites
        # Chuyển đổi tọa độ tường thành tập hợp các ô Grid để BFS xử lý nhanh
        self.walls = {(s.rect.x // TILE_SIZE, s.rect.y // TILE_SIZE) for s in obstacle_sprites}
        
        self.path = []
        self.timer = 0
        self.step_delay = 0.3 # Thời gian chờ giữa mỗi bước (giây)

    def calculate_path(self):
        # Tọa độ ô hiện tại của Ma và Player
        start = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)
        target = (self.player.rect.x // TILE_SIZE, self.player.rect.y // TILE_SIZE)
        
        # Thực hiện thuật toán BFS
        self.path, nodes_expanded, exec_time = get_path_bfs(start, target, self.walls)
        
        return nodes_expanded, len(self.path), exec_time

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.step_delay:
            # Tự động cập nhật đường đi mỗi khi đến lượt di chuyển
            self.calculate_path()
            if len(self.path) > 1:
                # Di chuyển đến ô kế tiếp trong danh sách Path
                next_tile = self.path[1]
                self.rect.x = next_tile[0] * TILE_SIZE
                self.rect.y = next_tile[1] * TILE_SIZE
            self.timer = 0