import pygame
from settings import *
from algo import *
from support import import_sprite_sheet
import math

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
        
        self.scared = False
        self.scared_timer = 0
        self.normal_speed = 75 # Lưu lại tốc độ gốc

        self.player = player
        self.obstacle_sprites = obstacle_sprites
        self.walls = { (s.rect.x // TILE_SIZE, s.rect.y // TILE_SIZE) for s in obstacle_sprites 
                      if getattr(s, 'sprite_type', 'wall') == 'wall' }
        
        self.path = []
        self.timer = 0
        self.recalc_delay = 0.4
        self.spawn_pos = pos
        
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
            # Nạp tấm hình Dead.png (định dạng 1 hàng 1 cột vì chỉ có 1 hình)
            dead_f = import_sprite_sheet(f'{self.folder_path}/Dead.png', 1, 1)
            
            # Lấy tấm hình duy nhất đó bỏ vào list [dead_f[0]]
            # Gán tấm hình này cho cả 4 hướng để dù đi hướng nào khi chết cũng hiện hình này
            single_image_list = [dead_f[0]]
            
            self.animations['dead'] = {
                'down':  single_image_list,
                'up':    single_image_list,
                'left':  single_image_list,
                'right': single_image_list
            }
        except:
            # Nếu không tìm thấy file Dead.png thì dùng tạm ảnh walk để không bị crash
            self.animations['dead'] = self.animations['walk']

    def calculate_path(self):
        curr_grid = (round(self.pos.x / TILE_SIZE), round(self.pos.y / TILE_SIZE))
        player_grid = (self.player.rect.x // TILE_SIZE, self.player.rect.y // TILE_SIZE)
        
        in_house = (11 <= curr_grid[0] <= 17) and (12 <= curr_grid[1] <= 16)
        if in_house:
            target = (14, 11)
        else:
            target = player_grid

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
        # Lấy ảnh gốc từ danh sách
        self.image = current_animation[int(self.frame_index)]

        # --- THÊM HIỆU ỨNG NHẤP NHÁY TẠI ĐÂY ---
        if self.scared:
            # math.sin tạo ra giá trị từ -1 đến 1. 
            # Chúng ta biến nó thành giá trị từ 100 (mờ) đến 255 (đặc)
            # 0.01 là tốc độ nháy, bạn có thể tăng lên 0.02 nếu muốn nháy nhanh hơn
            alpha = 150 + (math.sin(pygame.time.get_ticks() * 0.01) * 105)
            
            # Tạo một bản sao của ảnh để không làm hỏng ảnh gốc trong bộ nhớ
            self.image = self.image.copy()
            self.image.set_alpha(int(alpha))
        else:
            # Nếu không sợ thì hiện rõ 100%
            self.image.set_alpha(255)
    def reset_to_house(self):
        # Đưa tọa độ vector và rect về lại tâm nhà ma (vị trí 14, 14 trên grid)
        # Bạn có thể dùng tọa độ cụ thể tùy theo map của bạn
        self.pos = pygame.math.Vector2(14 * TILE_SIZE, 14 * TILE_SIZE)
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        
        # Sau khi về nhà thì cho ma trở lại bình thường (hết sợ)
        self.recover()
    
    def reset(self):
        # Đưa ma về vị trí xuất phát của nó trên bản đồ
        self.pos = pygame.math.Vector2(self.spawn_pos)
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        
        # Đưa ma về trạng thái bình thường
        self.scared = False
        self.status = 'walk'
        self.direction = pygame.math.Vector2(0, 0)
        self.path = [] # Xóa đường đi cũ

    def recover(self):
        self.scared = False
        self.speed = self.normal_speed

    def update(self, dt):
        if self.scared:
            if pygame.time.get_ticks() - self.scared_timer >= POWER_UP_DURATION:
                self.scared = False
                self.status = 'walk' # Trở lại bình thường

        self.timer += dt
        if self.timer >= self.recalc_delay:
            self.calculate_path()
            self.timer = 0
        


        if self.scared: self.status = 'dead'
        else:
            dist = (pygame.math.Vector2(self.player.rect.center) - pygame.math.Vector2(self.rect.center)).magnitude()
            self.status = 'attack' if dist < 40 else 'walk'
            
        self.move(dt)
        self.animate(dt)