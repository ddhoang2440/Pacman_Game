import pygame, sys
from pytmx.util_pygame import load_pygame
from settings import *
from sprites import Tile, Ghost
from player import Player

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.internal_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        self.clock = pygame.time.Clock()
        self.tmx_data = load_pygame(MAP_PATH)
        
        # --- TỐI ƯU 1: CACHE FONTS (Tránh lag do nạp font liên tục) ---
        self.font_large = pygame.font.Font(None, 45)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_diag = pygame.font.Font(None, 24)
        self.font_button = pygame.font.Font(None, 28)

        # UI State & AI Metrics (Đã đồng bộ tên biến)
        self.score = 0
        self.paused = False
        self.selected_algo = 'BFS'
        self.nodes_expanded = 0
        self.path_cost = 0
        self.exec_time = 0.0
        self.heuristic_val = 0
        self.current_node = (0, 0)
        self.goal_node = (0, 0)
        self.search_status = "Waiting..."
        
        self.monitored_ghost = None
        self.algo_buttons = []
        
        # Khởi tạo rect cho nút pause (Đã xóa dòng trùng lặp)
        self.pause_rect = pygame.Rect(MAZE_VISIBLE_WIDTH + 40, 620, 240, 85)

        # Nhóm quản lý Sprite
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.food_sprites = pygame.sprite.Group()
        self.ghost_group = pygame.sprite.Group()
        
        self.setup()

    def setup(self):
        # 1. Duyệt các Layer gạch
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'): 
                for x, y, surf in layer.tiles():
                    pos = (x * TILE_SIZE, y * TILE_SIZE)
                    groups = [self.visible_sprites]
                    if layer.name == 'Walls':
                        groups.append(self.obstacle_sprites)
                        Tile(pos, groups, surf, 'wall')
                    elif layer.name == 'Door':
                        groups.append(self.obstacle_sprites) 
                        Tile(pos, groups, surf, 'door')
                    elif layer.name == 'Power':
                        groups.append(self.food_sprites)
                        Tile(pos, groups, surf, 'power')
                    elif layer.name == 'Background':
                        Tile(pos, groups, surf, 'bg')

        # 2. Portals
        self.portals = {obj.name: {'x': obj.x, 'y': obj.y} for obj in self.tmx_data.get_layer_by_name('Portals')}

        # 3. Khởi tạo Player
        player_layer = self.tmx_data.get_layer_by_name('Player')
        for obj in player_layer:
            self.player = Player((obj.x, obj.y), self.visible_sprites, self.obstacle_sprites, self.food_sprites, self.portals, self.change_score)

        # 4. Khởi tạo 4 Ghost theo yêu cầu nhân vật mới
        configs = [
            {'name': 'EggGirl',    'path': '../images/enemies/EggGirl',    'algo': 'BFS'},
            {'name': 'Eskimo',     'path': '../images/enemies/Eskimo',     'algo': 'Alpha-Beta'},
            {'name': 'GoldStatue', 'path': '../images/enemies/GoldStatue', 'algo': 'A*'},
            {'name': 'Cavegirl',   'path': '../images/enemies/Cavegirl',   'algo': 'Minimax'}
        ]
        
        ghost_layer = self.tmx_data.get_layer_by_name('Ghost')
        spawn_points = [(obj.x, obj.y) for obj in ghost_layer]

        self.ghost_list = []
        for i, cfg in enumerate(configs):
            if i < len(spawn_points):
                ghost = Ghost(spawn_points[i], [self.visible_sprites, self.ghost_group], 
                             self.obstacle_sprites, self.player, cfg['name'], cfg['path'], cfg['algo'])
                self.ghost_list.append(ghost)
            
        if self.ghost_list:
            self.monitored_ghost = self.ghost_list[0]

    def change_score(self, amount):
        self.score += amount

    def draw_sidebar(self):
        sidebar_x = MAZE_VISIBLE_WIDTH
        # Nền Sidebar
        pygame.draw.rect(self.display_surface, '#121212', (sidebar_x, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(self.display_surface, '#333333', (sidebar_x, 0), (sidebar_x, SCREEN_HEIGHT), 2)

        # --- CARD 1: TOTAL SCORE (Y=20) ---
        score_card = pygame.Rect(sidebar_x + 20, 20, SIDEBAR_WIDTH - 40, 100)
        pygame.draw.rect(self.display_surface, '#1e1e1e', score_card, border_radius=12)
        self.display_surface.blit(self.font_medium.render('TOTAL SCORE', True, '#888888'), (sidebar_x + 40, 35))
        score_num = self.font_large.render(f"{self.score:06}", True, '#FFD700') 
        self.display_surface.blit(score_num, (sidebar_x + 40, 70))

        # --- CARD 2: ALGORITHMS (Y=140) ---
        self.display_surface.blit(self.font_medium.render('ALGORITHMS', True, '#00BFFF'), (sidebar_x + 30, 140))
        self.algo_buttons = []
        algos = ['BFS', 'Alpha-Beta', 'A*', 'Minimax']
        for i, name in enumerate(algos):
            col, row = i % 2, i // 2
            btn_rect = pygame.Rect(sidebar_x + 30 + (col * 130), 185 + (row * 75), 120, 60)
            self.algo_buttons.append((btn_rect, name))
            
            color = '#00BFFF' if self.selected_algo == name else '#333333'
            text_color = 'black' if self.selected_algo == name else 'white'
            pygame.draw.rect(self.display_surface, color, btn_rect, border_radius=8)
            txt_surf = self.font_button.render(name, True, text_color)
            self.display_surface.blit(txt_surf, txt_surf.get_rect(center=btn_rect.center))

        # --- CARD 3: AI DIAGNOSTICS (Y=380) ---
        diag_card = pygame.Rect(sidebar_x + 20, 380, SIDEBAR_WIDTH - 40, 220)
        pygame.draw.rect(self.display_surface, '#1e1e1e', diag_card, border_radius=12)
        pygame.draw.rect(self.display_surface, '#00BFFF', diag_card, 1, border_radius=12)
        self.display_surface.blit(self.font_medium.render('AI DIAGNOSTICS', True, '#00BFFF'), (sidebar_x + 35, 395))

        metrics = [
            f"Algorithm: {self.selected_algo}",
            f"Nodes Expanded: {self.nodes_expanded}",
            f"Path Cost: {self.path_cost}",
            f"Runtime: {self.exec_time:.4f}s",
            f"Heuristic: {self.heuristic_val}",
            f"Current: {self.current_node} | Goal: {self.goal_node}",
            f"Status: {self.search_status}"
        ]
        for i, text in enumerate(metrics):
            color = 'white' if "Status" not in text else '#00FF00'
            self.display_surface.blit(self.font_diag.render(text, True, color), (sidebar_x + 35, 435 + i * 22))

        # --- CARD 4: CONTROLS (Y=620) ---
        btn_color = '#FF4500' if not self.paused else '#32CD32'
        pygame.draw.rect(self.display_surface, btn_color, self.pause_rect, border_radius=15)
        txt = 'PAUSE' if not self.paused else 'RESUME'
        pause_surf = self.font_medium.render(txt, True, 'white')
        self.display_surface.blit(pause_surf, pause_surf.get_rect(center=self.pause_rect.center))

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.pause_rect.collidepoint(event.pos):
                        self.paused = not self.paused
                    
                    for btn_rect, algo_name in self.algo_buttons:
                        if btn_rect.collidepoint(event.pos):
                            self.selected_algo = algo_name
                            # Chuyển monitored_ghost sang con ma dùng thuật toán tương ứng
                            for g in self.ghost_list:
                                if g.algo_type == algo_name:
                                    self.monitored_ghost = g

            if not self.paused:
                self.internal_surf.fill(BG_COLOR)
                self.visible_sprites.update(dt) 
                
                if self.monitored_ghost:
                    # TỐI ƯU 2: Lấy dữ liệu trực tiếp từ monitored_ghost
                    path_data = self.monitored_ghost.calculate_path()
                    if path_data and len(path_data) == 3:
                        nodes, cost, time_val = path_data
                        self.nodes_expanded = nodes
                        self.path_cost = cost
                        self.exec_time = time_val / 1000 
                        
                        # Thêm thông số tọa độ thực tế
                        self.current_node = (int(self.monitored_ghost.pos.x // TILE_SIZE), int(self.monitored_ghost.pos.y // TILE_SIZE))
                        self.goal_node = (self.player.rect.x // TILE_SIZE, self.player.rect.y // TILE_SIZE)
                        self.search_status = "In Pursuit!" if cost > 0 else "Path Blocked"
                        
                        # Gán heuristic (ví dụ Manhattan cho A*)
                        if self.selected_algo == 'A*':
                            self.heuristic_val = abs(self.current_node[0]-self.goal_node[0]) + abs(self.current_node[1]-self.goal_node[1])
                        else:
                            self.heuristic_val = 0

            # Rendering
            self.display_surface.fill('#1a1a1a')
            self.visible_sprites.draw(self.internal_surf)
            scaled_maze = pygame.transform.scale(self.internal_surf, (MAZE_VISIBLE_WIDTH, SCREEN_HEIGHT))
            self.display_surface.blit(scaled_maze, (0, 0))
            self.draw_sidebar()
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()