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
        
        # UI State
        self.font = pygame.font.Font(None, 50)
        self.score = 0
        self.paused = False
        self.nodes_expanded = 0
        self.path_cost = 0
        self.exec_time = 0.0
        self.frontier_size = 0
        self.selected_algo = 'BFS'
        self.algo_buttons = []
        self.current_node = (12, 8)
        self.goal_node = (3, 17)
        self.heuristic_val = 5
        self.search_status = "Searching..."
        
        self.blinky = None
        # Khởi tạo rect cho nút pause
        self.pause_rect = pygame.Rect(MAZE_VISIBLE_WIDTH + 40, 580, 220, 100)
        # Khởi tạo rect cho nút pause để tránh lỗi click trước khi vẽ
        self.pause_rect = pygame.Rect(MAZE_VISIBLE_WIDTH + 40, 580, 220, 100)

        # Nhóm quản lý Sprite
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.food_sprites = pygame.sprite.Group()
        
        self.setup()

    def setup(self):
        # 1. Duyệt các Layer gạch (Tile Layers)
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

        # 2. Nạp dữ liệu Cổng (Portals)
        portal_layer = self.tmx_data.get_layer_by_name('Portals')
        self.portals = {}
        for obj in portal_layer:
            self.portals[obj.name] = {'x': obj.x, 'y': obj.y}

        # 3. Nạp Vật phẩm lớn (BigItems)
        try:
            big_items_layer = self.tmx_data.get_layer_by_name('BigItems')
            for obj in big_items_layer:
                pos = (obj.x, obj.y)
                groups = [self.visible_sprites, self.food_sprites]
                Tile(pos, groups, obj.image, 'food')
        except ValueError:
            print("Cảnh báo: Không tìm thấy layer BigItems!")

        # 4. Khởi tạo Player
        player_layer = self.tmx_data.get_layer_by_name('Player')
        for obj in player_layer:
            self.player = Player(
                pos = (obj.x, obj.y), 
                groups = self.visible_sprites, 
                obstacle_sprites = self.obstacle_sprites,
                food_sprites = self.food_sprites,
                portals = self.portals,
                change_score = self.change_score                                          
            )

        # 5. Khởi tạo Ghost
        try:
            self.ghost_data = self.tmx_data.get_layer_by_name('Ghost')
            for obj in self.ghost_data:
                # Tìm đúng đối tượng tên 'Blinky' trong Tiled 
                if obj.properties.get('ghost_name') == 'Blinky':
                    self.blinky = Ghost(
                        pos = (obj.x, obj.y), 
                        groups = self.visible_sprites, 
                        obstacle_sprites = self.obstacle_sprites, 
                        player = self.player
                    )
        except ValueError:
            print("Cảnh báo: Không tìm thấy layer Ghost hoặc đối tượng Blinky!")
            
        # 5. Lưu dữ liệu Ghost để dùng sau này
        self.ghost_data = self.tmx_data.get_layer_by_name('Ghost')

    def change_score(self, amount):
        self.score += amount

    def draw_diagnostics(self, x_pos, y_pos):
        # 1. Khung nền cho bảng chẩn đoán
        diag_rect = pygame.Rect(x_pos, y_pos, 230, 220)
        pygame.draw.rect(self.display_surface, '#1e1e1e', diag_rect, border_radius=12)
        pygame.draw.rect(self.display_surface, '#333333', diag_rect, 2, border_radius=12) # Viền nhẹ

        # 2. Tiêu đề bảng
        header_font = pygame.font.Font(None, 30)
        title_surf = header_font.render("AI DIAGNOSTICS", True, '#00BFFF') # Màu xanh Neon
        self.display_surface.blit(title_surf, (x_pos + 15, y_pos + 15))
        
        # 3. Danh sách thông số (Dùng font nhỏ hơn, kiểu Monospace nhìn cho "tech")
        info_font = pygame.font.Font(None, 28)
        metrics = [
            f"Algo: {self.selected_algo}",
            f"Nodes: {self.nodes_expanded}",
            f"Path Cost: {self.path_cost}",
            f"Frontier: {self.frontier_size}",
            f"Time: {self.exec_time:.3f} ms"
        ]

        for i, text in enumerate(metrics):
            surf = info_font.render(text, True, 'white')
            self.display_surface.blit(surf, (x_pos + 20, y_pos + 55 + (i * 30)))
    def draw_controls(self, x_pos, y_pos):
        # Thêm hướng dẫn phím tắt ở dưới cùng để lấp khoảng trống cuối
        font_small = pygame.font.Font(None, 22)
        controls = [
            "[SPACE] Start/Pause",
            "[R] Reset Level",
            "[ESC] Quit Game"
        ]
        for i, text in enumerate(controls):
            surf = font_small.render(text, True, '#888888')
            self.display_surface.blit(surf, (x_pos, y_pos + (i * 20)))

    def draw_sidebar(self):
        # --- 1. THIẾT LẬP NỀN VÀ ĐƯỜNG CHIA ---
        sidebar_x = MAZE_VISIBLE_WIDTH
        sidebar_rect = pygame.Rect(sidebar_x, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        # Nền Sidebar màu xám cực đậm để làm nổi bật các Card
        pygame.draw.rect(self.display_surface, '#121212', sidebar_rect) 
        # Đường kẻ phân cách Maze và UI
        pygame.draw.line(self.display_surface, '#333333', (sidebar_x, 0), (sidebar_x, SCREEN_HEIGHT), 2)

        # --- 2. KHỐI ĐIỂM SỐ (TOTAL SCORE CARD) ---
        # Thiết kế dạng thẻ (Card) bo góc
        score_card = pygame.Rect(sidebar_x + 20, 30, SIDEBAR_WIDTH - 40, 110)
        pygame.draw.rect(self.display_surface, '#1e1e1e', score_card, border_radius=12)
        
        # Tiêu đề Score màu xám nhạt
        score_label = self.font.render('TOTAL SCORE', True, '#888888')
        self.display_surface.blit(score_label, (sidebar_x + 40, 45))
        
        # Số điểm định dạng 6 chữ số, màu vàng rực rỡ
        score_str = f"{self.score:06}"
        score_num = self.font.render(score_str, True, '#FFD700') 
        num_rect = score_num.get_rect(midleft=(sidebar_x + 40, 100))
        self.display_surface.blit(score_num, num_rect)

        # --- 3. KHỐI THUẬT TOÁN (ALGORITHMS GRID) ---
        algo_label = self.font.render('ALGORITHMS', True, '#00BFFF') # Màu xanh Neon chủ đạo
        self.display_surface.blit(algo_label, (sidebar_x + 30, 160))
        
        self.algo_buttons = [] # Lưu Rect để bắt sự kiện click trong hàm run()
        algos = ['BFS', 'DFS', 'UCS', 'A*', 'IDS', 'GBFS']
        
        for i, name in enumerate(algos):
            col = i % 2
            row = i // 2
            x = sidebar_x + 30 + (col * 105)
            y = 205 + (row * 65)
            
            btn_rect = pygame.Rect(x, y, 95, 50)
            self.algo_buttons.append((btn_rect, name))
            
            # Trạng thái Selected (Nền xanh) vs Unselected (Viền xám)
            if self.selected_algo == name:
                pygame.draw.rect(self.display_surface, '#00BFFF', btn_rect, border_radius=8)
                text_color = 'black'
            else:
                pygame.draw.rect(self.display_surface, '#333333', btn_rect, 2, border_radius=8)
                text_color = 'white'
            
            # Dùng font nhỏ hơn một chút cho các nút bấm
            btn_font = pygame.font.Font(None, 32)
            algo_text = btn_font.render(name, True, text_color)
            self.display_surface.blit(algo_text, algo_text.get_rect(center=btn_rect.center))

        # --- 4. KHỐI THÔNG SỐ AI (DIAGNOSTICS - LẤP ĐẦY PHẦN TRỐNG) ---
        # Khu vực này cực kỳ quan trọng để ghi điểm đồ án AI
        diag_card = pygame.Rect(sidebar_x + 20, 400, SIDEBAR_WIDTH - 40, 150)
        pygame.draw.rect(self.display_surface, '#1e1e1e', diag_card, border_radius=12)
        # Viền mỏng màu xanh bao quanh bảng thông số
        pygame.draw.rect(self.display_surface, '#00BFFF', diag_card, 1, border_radius=12)

        diag_label = pygame.font.Font(None, 28).render('AI DIAGNOSTICS', True, '#00BFFF')
        self.display_surface.blit(diag_label, (sidebar_x + 35, 415))

        # Các thông số kỹ thuật (Lấy từ biến hệ thống của bạn)
        # Nếu chưa có biến, mặc định sẽ hiện là 0
        metrics = [
            f"Nodes Expanded: {getattr(self, 'nodes_visited', 0)}",
            f"Path Cost: {getattr(self, 'path_len', 0)}",
            f"Runtime: {getattr(self, 'search_time', 0.0):.4f}s"
        ]

        for i, text in enumerate(metrics):
            metric_surf = pygame.font.Font(None, 24).render(text, True, '#AAAAAA')
            self.display_surface.blit(metric_surf, (sidebar_x + 35, 450 + (i * 28)))

        # --- 5. NÚT PAUSE (DƯỚI CÙNG) ---
        # Nền màu cam đậm (Orange Red) nổi bật cho nút điều khiển chính
        pause_btn_color = '#FF4500' if not self.paused else '#32CD32' 
        pygame.draw.rect(self.display_surface, pause_btn_color, self.pause_rect, border_radius=15)
        
        pause_text = 'PAUSE' if not self.paused else 'RESUME'
        pause_surf = self.font.render(pause_text, True, 'white')
        self.display_surface.blit(pause_surf, pause_surf.get_rect(center=self.pause_rect.center))

        # Gợi ý phím tắt dưới cùng để giao diện thêm đầy đặn
        hint_text = pygame.font.Font(None, 20).render('Press R to Reset Level', True, '#555555')
        self.display_surface.blit(hint_text, (sidebar_x + 65, 715))
    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Kiểm tra click nút Pause
                    if self.pause_rect.collidepoint(event.pos):
                        self.paused = not self.paused
                    
                    # --- THÊM: Kiểm tra click chọn thuật toán ---
                    for btn_rect, algo_name in self.algo_buttons:
                        if btn_rect.collidepoint(event.pos):
                            self.selected_algo = algo_name
                            print(f"Algorithm selected: {self.selected_algo}")

            # Logic Update
            if not self.paused:
                self.internal_surf.fill(BG_COLOR)
                self.visible_sprites.update(dt)
                # --- CẬP NHẬT THÔNG SỐ AI TỪ BLINKY ---
                # Gọi hàm tìm đường và lấy dữ liệu
                if self.blinky:
                        nodes, cost, time_val = self.blinky.calculate_path()
                        self.nodes_visited = nodes
                        self.path_len = cost
                        self.search_time = time_val / 1000 
                        self.current_node = (self.blinky.rect.x // TILE_SIZE, self.blinky.rect.y // TILE_SIZE)
                        self.goal_node = (self.player.rect.x // TILE_SIZE, self.player.rect.y // TILE_SIZE)
                        self.search_status = "Path Found!" if cost > 0 else "Searching..."
            # Rendering
            self.display_surface.fill('#1a1a1a') # Màu nền bao quanh

            # 1. Vẽ Maze lên mặt phẳng nội bộ
            self.visible_sprites.draw(self.internal_surf)

            # 2. Phóng to Maze dán sang bên trái
            scaled_maze = pygame.transform.scale(self.internal_surf, (MAZE_VISIBLE_WIDTH, SCREEN_HEIGHT))
            self.display_surface.blit(scaled_maze, (0, 0))

            # 3. Vẽ Sidebar thông tin bên phải
            self.draw_sidebar()

            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()