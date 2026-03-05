# code/sprites.py
import pygame
from settings import *
from algo import get_path_bfs

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, surface, sprite_type, gid=None):
        super().__init__(groups)
        self.sprite_type = sprite_type 
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)
        self.gid = gid # Lưu gid để Ghost nhận diện cửa

# code/sprites.py

class Ghost(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, player):
        super().__init__(groups)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill('red')
        self.rect = self.image.get_rect(topleft = pos)
        
        self.player = player
        self.obstacle_sprites = obstacle_sprites
        
        # LOGIC QUAN TRỌNG: Loại bỏ các ô 'door' khỏi danh sách tường của Ma 
        self.walls = set()
        for s in obstacle_sprites:
            if getattr(s, 'sprite_type', 'wall') == 'wall':
                self.walls.add((s.rect.x // TILE_SIZE, s.rect.y // TILE_SIZE))
        
        self.path = []
        self.timer = 0
        self.step_delay = 0.3

    def calculate_path(self):
        curr_grid = (self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE)
        player_grid = (self.player.rect.x // TILE_SIZE, self.player.rect.y // TILE_SIZE)
        
        in_house = (11 <= curr_grid[0] <= 17) and (12 <= curr_grid[1] <= 16)
        target = (14, 11) if in_house else player_grid
        
        # KIỂM TRA QUAN TRỌNG: Nếu đích đến là tường, không chạy BFS để tránh treo máy
        if target in self.walls:
            self.path = []
            return 0, 0, 0 

        # Chỉ chạy BFS nếu đích đến hợp lệ
        self.path, nodes_expanded, exec_time = get_path_bfs(curr_grid, target, self.walls)
        return nodes_expanded, len(self.path), exec_time

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.step_delay:
            self.calculate_path()
            if len(self.path) > 1:
                # Di chuyển Ma tới ô kế tiếp
                next_tile = self.path[1]
                self.rect.x = next_tile[0] * TILE_SIZE
                self.rect.y = next_tile[1] * TILE_SIZE
            self.timer = 0