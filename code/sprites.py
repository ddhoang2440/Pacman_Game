import pygame
from settings import *
from algo import *
from support import import_sprite_sheet

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, surface, sprite_type, gid=None):
        super().__init__(groups)
        self.sprite_type = sprite_type 
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)
        self.gid = gid

class Ghost(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, player, name, folder_path, algo_type):
        super().__init__(groups)
        self.name = name
        self.folder_path = folder_path
        self.algo_type = algo_type
        
        # ANIMATION SETUP
        self.import_assets()
        self.status = 'walk'
        self.facing = 'down' # Hướng mặc định
        self.frame_index = 0
        self.animation_speed = 6
        
        self.image = self.animations[self.status][self.facing][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        
        # SMOOTH MOVEMENT
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2()
        self.speed = 70
        
        self.player = player
        self.obstacle_sprites = obstacle_sprites
        self.walls = { (s.rect.x // TILE_SIZE, s.rect.y // TILE_SIZE) for s in obstacle_sprites 
                      if getattr(s, 'sprite_type', 'wall') == 'wall' }
        
        self.path = []
        self.timer = 0
        self.recalc_delay = 0.4

    def import_assets(self):
        self.animations = {'walk': {}, 'attack': {}, 'dead': {}}
        
        # 1. Walk animation
        walk_frames = import_sprite_sheet(f'{self.folder_path}/Walk.png', 4, 4)
        self.animations['walk'] = {
            'down':  [walk_frames[i] for i in [0, 4, 8, 12]],
            'up':    [walk_frames[i] for i in [1, 5, 9, 13]],
            'left':  [walk_frames[i] for i in [2, 6, 10, 14]],
            'right': [walk_frames[i] for i in [3, 7, 11, 15]]
        }

        # 2. Attack animation
        a_f = import_sprite_sheet(f'{self.folder_path}/Attack.png', 1, 4)
        self.animations['attack'] = {
            'down': [a_f[0]], 'up': [a_f[1]], 'left': [a_f[2]], 'right': [a_f[3]]
        }

        # 3. Dead animation
        try:
            dead_frames = import_sprite_sheet(f'{self.folder_path}/Dead.png', 1, 4)
            self.animations['dead'] = {'down': [dead_frames[0]], 'up': [dead_frames[1]], 
                                     'left': [dead_frames[2]], 'right': [dead_frames[3]]}
        except:
            self.animations['dead'] = self.animations['walk']

    def calculate_path(self):
        curr_grid = (round(self.pos.x / TILE_SIZE), round(self.pos.y / TILE_SIZE))
        player_grid = (self.player.rect.x // TILE_SIZE, self.player.rect.y // TILE_SIZE)
        
        in_house = (11 <= curr_grid[0] <= 17) and (12 <= curr_grid[1] <= 16)
        target = (14, 11) if in_house else player_grid

        if target in self.walls: 
            self.path = []
            return 0, 0, 0 

        # Algorithm selection
        res = None
        if in_house: res = get_path_bfs(curr_grid, target, self.walls)
        else:
            if self.algo_type == 'BFS': res = get_path_bfs(curr_grid, target, self.walls)
            elif self.algo_type == 'Alpha-Beta': res = get_path_alpha_beta(curr_grid, target, self.walls)
            elif self.algo_type == 'A*': res = get_path_astar(curr_grid, target, self.walls)
            else: res = get_path_minimax(curr_grid, target, self.walls)
        
        if res:
            self.path, nodes, time_ms = res
            return nodes, len(self.path), time_ms
        return 0, 0, 0

    def move(self, dt):
        if len(self.path) > 1:
            target_pos = pygame.math.Vector2(self.path[1][0] * TILE_SIZE, self.path[1][1] * TILE_SIZE)
            
            # Caculate direction towards the next tile in the path
            if (target_pos - self.pos).magnitude() > 2:
                self.direction = (target_pos - self.pos).normalize()
            else:
                self.pos = target_pos
                self.direction = pygame.math.Vector2()
        else:
            self.direction = pygame.math.Vector2()

        # Update position based on direction and speed
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # Update facing direction for animation
        if self.direction.magnitude() > 0:
            if abs(self.direction.x) > abs(self.direction.y):
                self.facing = 'right' if self.direction.x > 0 else 'left'
            else:
                self.facing = 'down' if self.direction.y > 0 else 'up'

    def animate(self, dt):
        current_animation = self.animations[self.status][self.facing]
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
        self.image = current_animation[int(self.frame_index)]

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.recalc_delay:
            self.calculate_path()
            self.timer = 0
        
        # Update attack/walk status based on distance to player
        dist = (pygame.math.Vector2(self.player.rect.center) - pygame.math.Vector2(self.rect.center)).magnitude()
        self.status = 'attack' if dist < 40 else 'walk'
            
        self.move(dt)
        self.animate(dt)