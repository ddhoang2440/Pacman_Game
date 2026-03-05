# code/sprites.py
import pygame
from settings import *
from algo import *
class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, surface, sprite_type, gid=None):
        super().__init__(groups)
        self.sprite_type = sprite_type 
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)
        self.gid = gid # Lưu gid để Ghost nhận diện cửa

# code/sprites.py

class Ghost(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, player, name, color, algo_type):
        super().__init__(groups)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color) # Mỗi con 1 màu
        self.rect = self.image.get_rect(topleft = pos)
        
        self.player = player
        self.name = name
        self.obstacle_sprites = obstacle_sprites
        self.algo_type = algo_type # BFS, DFS, A* hoặc Minimax
        
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
        
        if target in self.walls: return 0, 0, 0 

        # --- CHỌN THUẬT TOÁN ---
        if self.algo_type == 'BFS':
            self.path, nodes, time_ms = get_path_bfs(curr_grid, target, self.walls)
        elif self.algo_type == 'DFS':
            self.path, nodes, time_ms = get_path_dfs(curr_grid, target, self.walls)
        elif self.algo_type == 'A*':
            self.path, nodes, time_ms = get_path_astar(curr_grid, target, self.walls)
        else: # Minimax
            self.path, nodes, time_ms = get_path_minimax(curr_grid, target, self.walls)
            
        return nodes, len(self.path), time_ms

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.step_delay:
            self.calculate_path()
            if len(self.path) > 1:
                next_tile = self.path[1]
                self.rect.x = next_tile[0] * TILE_SIZE
                self.rect.y = next_tile[1] * TILE_SIZE
            self.timer = 0