# main.py
import pygame, sys
from pytmx.util_pygame import load_pygame
from settings import *
from sprites import Tile
from player import Player

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.internal_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        self.clock = pygame.time.Clock()
        self.tmx_data = load_pygame(MAP_PATH) # Nạp Map
        
        # Nhóm quản lý Sprite
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.food_sprites = pygame.sprite.Group()
        self.setup()

    def setup(self):
        # Duyệt qua từng Layer trong file Tiled 
        for layer in self.tmx_data.visible_layers:
            # Chỉ xử lý các lớp gạch (Tile Layers)
            if hasattr(layer, 'data'): 
                for x, y, surf in layer.tiles():
                    pos = (x * TILE_SIZE, y * TILE_SIZE)
                    
                    # Mặc định gạch nào cũng phải được nhìn thấy 
                    groups = [self.visible_sprites]
                    
                    # Phân loại logic cho từng Layer 
                    if layer.name == 'Walls':
                        groups.append(self.obstacle_sprites) # Tường thì thêm vào để chặn đường
                        Tile(pos, groups, surf, 'wall')
                    elif layer.name == 'Foods':
                        Tile(pos, groups, surf, 'food') # Layer thức ăn
                    elif layer.name == 'Power':
                        Tile(pos, groups, surf, 'power') # Layer hạt năng lượng
                    else:
                        # Các layer khác như Background 
                        Tile(pos, groups, surf, 'bg')

        # Khởi tạo Player (Giữ nguyên phần này nhưng nhớ check tên object trong Tiled) 
        player_layer = self.tmx_data.get_layer_by_name('Player')
        for obj in player_layer:
            self.player = Player(
                            pos = (obj.x, obj.y), 
                            groups = self.visible_sprites, 
                            obstacle_sprites = self.obstacle_sprites,
                            food_sprites = self.food_sprites
                        )

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # 1. Vẽ mọi thứ lên mặt phẳng nội bộ trước
            self.internal_surf.fill(BG_COLOR)
            self.visible_sprites.update(dt)
            self.visible_sprites.draw(self.internal_surf)

            # 2. Phóng to mặt phẳng nội bộ và dán lên cửa sổ hiển thị
            scaled_surf = pygame.transform.scale(self.internal_surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.display_surface.blit(scaled_surf, (0, 0))
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()