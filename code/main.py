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
        
        # --- UI SYSTEM: COLORS & FONTS ---
        self.colors = {
            'bg': '#0f0f0f',
            'sidebar': '#141414',
            'card': '#1b1b1b',
            'border': '#2c2c2c',
            'accent': '#1EA7E1',     # Neon Blue
            'highlight': '#FFD700',  # Yellow
            'text_dim': '#aaaaaa',
            'danger': '#ff4d00',     # Orange Red
            'success': '#00FF00'
        }

        self.fonts = {
            'title': pygame.font.Font(None, 48),
            'section': pygame.font.Font(None, 30),
            'medium': pygame.font.Font(None, 24),
            'diag': pygame.font.Font(None, 20),
            'keycap': pygame.font.Font(None, 18),
            'big': pygame.font.Font(None, 128)
        }

        # --- GAME STATE ---
        self.score = 0
        self.lives = MAX_LIVES
        self.paused = False
        self.game_over = False
        self.won = False
        self.show_settings = False
        
        # --- AI METRICS & DYNAMIC FILTERING ---
        # Tự động lấy danh sách thuật toán thực tế từ GHOST_CONFIGS
        self.active_algos = sorted(list(set(cfg['algo'] for cfg in GHOST_CONFIGS)))
        self.selected_algo = self.active_algos[0] if self.active_algos else 'BFS'
        
        self.nodes_expanded = 0
        self.path_cost = 0
        self.exec_time = 0.0
        self.frontier_size = 0
        self.max_depth = 0
        self.search_status = "Ready"

        # --- UI INTERACTION RECTS ---
        self.algo_buttons = []
        self.pause_rect = pygame.Rect(0, 0, 0, 0)
        self.settings_rect = pygame.Rect(0, 0, 0, 0)

        # Countdown logic
        self.countdown_active = False
        self.countdown_timer = 0
        self.current_countdown_num = 3

        # Sprite Groups
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.food_sprites = pygame.sprite.Group()
        self.ghost_group = pygame.sprite.Group()
        
        self.setup()

    def setup(self):
        # [Giữ nguyên logic nạp map và khởi tạo nhân vật của bạn]
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

        portal_layer = self.tmx_data.get_layer_by_name('Portals')
        self.portals = {obj.name: {'x': obj.x, 'y': obj.y} for obj in portal_layer}

        try:
            big_items_layer = self.tmx_data.get_layer_by_name('BigItems')
            for obj in big_items_layer:
                Tile((obj.x, obj.y), [self.visible_sprites, self.food_sprites], obj.image, 'food')
        except ValueError: pass

        player_layer = self.tmx_data.get_layer_by_name('Player')
        for obj in player_layer:
            self.player = Player((obj.x, obj.y), self.visible_sprites, self.obstacle_sprites, 
                                 self.food_sprites, self.portals, self.change_score)

        ghost_layer = self.tmx_data.get_layer_by_name('Ghost')
        spawn_points = [(obj.x, obj.y) for obj in ghost_layer]
        self.ghost_list = []
        for i, cfg in enumerate(GHOST_CONFIGS):
            if i < len(spawn_points):
                ghost = Ghost(spawn_points[i], [self.visible_sprites, self.ghost_group], 
                              self.obstacle_sprites, self.player, cfg['name'], cfg['path'], cfg['algo'])
                self.ghost_list.append(ghost) 
        
        if self.ghost_list: self.monitored_ghost = self.ghost_list[0]

    def change_score(self, amount):
        self.score += amount

    # --- UI RENDERING HELPERS ---

    def draw_ui_card(self, x, y, w, h, title):
        """Vẽ khung Card đồng nhất"""
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.display_surface, self.colors['card'], rect, border_radius=12)
        pygame.draw.rect(self.display_surface, self.colors['border'], rect, width=1, border_radius=12)
        if title:
            title_surf = self.fonts['section'].render(title, True, self.colors['accent'])
            self.display_surface.blit(title_surf, (x + 15, y + 12))
        return rect

    def draw_keycap(self, key_text, x, y):
        """Vẽ nút phím kiểu Keycap"""
        txt = self.fonts['keycap'].render(key_text, True, self.colors['highlight'])
        rect = pygame.Rect(x, y, txt.get_width() + 14, 24)
        pygame.draw.rect(self.display_surface, '#252525', rect, border_radius=5)
        pygame.draw.rect(self.display_surface, self.colors['highlight'], rect, width=1, border_radius=5)
        self.display_surface.blit(txt, (x + 7, y + 4))
        return rect.width

    def draw_sidebar(self):
        sidebar_x = MAZE_VISIBLE_WIDTH
        padding = 20
        card_w = SIDEBAR_WIDTH - (padding * 2)
        curr_y = 20
        mouse_pos = pygame.mouse.get_pos()

        # 1. Nền Sidebar
        pygame.draw.rect(self.display_surface, self.colors['sidebar'], (sidebar_x, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))

        # 2. Tiêu đề
        title_surf = self.fonts['title'].render('NINJA SURVIVOR', True, self.colors['accent'])
        self.display_surface.blit(title_surf, (sidebar_x + padding, curr_y))
        curr_y += 60

        # 3. Card STATUS (Lives + Score)
        self.draw_ui_card(sidebar_x + padding, curr_y, card_w, 80, "STATUS")
        for i in range(MAX_LIVES):
            hx = sidebar_x + padding + 15 + (i * 30)
            color = self.colors['danger'] if i < self.lives else '#333333'
            pygame.draw.circle(self.display_surface, color, (hx + 7, curr_y + 52), 7)
            pygame.draw.circle(self.display_surface, color, (hx + 17, curr_y + 52), 7)
            pygame.draw.polygon(self.display_surface, color, [(hx, curr_y + 55), (hx + 24, curr_y + 55), (hx + 12, curr_y + 67)])
        
        score_val = self.fonts['section'].render(f"{self.score:06}", True, self.colors['highlight'])
        self.display_surface.blit(score_val, (sidebar_x + padding + card_w - score_val.get_width() - 15, curr_y + 40))
        curr_y += 100

        # 4. Card CONTROLS (Fix Alignment)
        self.draw_ui_card(sidebar_x + padding, curr_y, card_w, 120, "CONTROLS")
        ctrls = [("ARROWS", "Move Player"), ("SPACE", "Pause / Resume"), ("R KEY", "Reset Level")]
        for i, (key, desc) in enumerate(ctrls):
            self.draw_keycap(key, sidebar_x + padding + 15, curr_y + 45 + (i * 24))
            desc_surf = self.fonts['diag'].render(desc, True, self.colors['text_dim'])
            # Cố định tọa độ X của text mô tả là 120 để thẳng hàng
            self.display_surface.blit(desc_surf, (sidebar_x + padding + 120, curr_y + 48 + (i * 24)))
        curr_y += 140

        # 5. Card STRATEGY (2-Column Grid)
        num_rows = (len(self.active_algos) + 1) // 2
        card_h = 60 + (num_rows * 40)
        self.draw_ui_card(sidebar_x + padding, curr_y, card_w, card_h, "STRATEGY")
        
        self.algo_buttons = []
        btn_w, btn_h = (card_w // 2) - 20, 32
        for i, name in enumerate(self.active_algos):
            col, row = i % 2, i // 2
            bx = sidebar_x + padding + 15 + (col * (btn_w + 10))
            by = curr_y + 45 + (row * (btn_h + 8))
            btn_rect = pygame.Rect(bx, by, btn_w, btn_h)
            self.algo_buttons.append((btn_rect, name))
            
            is_active = self.selected_algo == name
            is_hover = btn_rect.collidepoint(mouse_pos)
            bg_col = self.colors['accent'] if is_active else (self.colors['border'] if is_hover else self.colors['card'])
            txt_col = 'black' if is_active else 'white'
            
            pygame.draw.rect(self.display_surface, bg_col, btn_rect, border_radius=6)
            pygame.draw.rect(self.display_surface, self.colors['accent'] if is_hover else self.colors['border'], btn_rect, width=1, border_radius=6)
            txt_surf = self.fonts['diag'].render(name, True, txt_col)
            self.display_surface.blit(txt_surf, txt_surf.get_rect(center=btn_rect.center))
        curr_y += (card_h + 20)

        # 6. Card DIAGNOSTICS (Left Label - Right Value)
        self.draw_ui_card(sidebar_x + padding, curr_y, card_w, 140, "DIAGNOSTICS")
        stats = [
            ("Nodes Visited", self.nodes_expanded),
            ("Path Cost", self.path_cost),
            ("Frontier Size", self.frontier_size),
            ("Exec Time", f"{self.exec_time:.2f} ms")
        ]
        for i, (label, val) in enumerate(stats):
            lbl_surf = self.fonts['diag'].render(f"{label}:", True, self.colors['text_dim'])
            self.display_surface.blit(lbl_surf, (sidebar_x + padding + 15, curr_y + 45 + (i * 22)))
            val_surf = self.fonts['diag'].render(str(val), True, self.colors['accent'])
            self.display_surface.blit(val_surf, (sidebar_x + padding + card_w - val_surf.get_width() - 15, curr_y + 45 + (i * 22)))
        
        # 7. Bottom Actions (Fixed relative to bottom)
        self.pause_rect = pygame.Rect(sidebar_x + padding, SCREEN_HEIGHT - 120, card_w, 45)
        self.settings_rect = pygame.Rect(sidebar_x + padding, SCREEN_HEIGHT - 65, card_w, 45)

        # Pause Button
        p_col = self.colors['danger'] if not self.paused else self.colors['success']
        pygame.draw.rect(self.display_surface, p_col, self.pause_rect, border_radius=10)
        if self.pause_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.display_surface, 'white', self.pause_rect, width=2, border_radius=10)
        p_txt = self.fonts['medium'].render("PAUSE" if not self.paused else "START SIMULATION", True, 'white')
        self.display_surface.blit(p_txt, p_txt.get_rect(center=self.pause_rect.center))

        # Settings Button
        pygame.draw.rect(self.display_surface, self.colors['card'], self.settings_rect, border_radius=10)
        pygame.draw.rect(self.display_surface, self.colors['border'], self.settings_rect, width=1, border_radius=10)
        st_txt = self.fonts['medium'].render("GAME SETTINGS", True, 'white')
        self.display_surface.blit(st_txt, st_txt.get_rect(center=self.settings_rect.center))

    def check_collision(self):
        if not self.game_over:
            hits = pygame.sprite.spritecollide(self.player, self.ghost_group, False)
            for ghost in hits:
                if ghost.scared:
                    ghost.reset_to_house()
                    self.score += 200
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                        self.search_status = "GAME OVER"
                    else:
                        self.player.reset()
                        for g in self.ghost_group: g.reset()
                        self.countdown_active = True
                        self.countdown_timer = pygame.time.get_ticks()

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
                    
                    if self.settings_rect.collidepoint(event.pos):
                        self.show_settings = not self.show_settings

                    for btn_rect, algo_name in self.algo_buttons:
                        if btn_rect.collidepoint(event.pos):
                            self.selected_algo = algo_name
                            for g in self.ghost_list: 
                                if g.algo_type == algo_name:
                                    self.monitored_ghost = g

                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.lives = MAX_LIVES
                    self.score = 0
                    self.game_over = False
                    self.won = False
                    self.setup()

            # --- LOGIC UPDATE ---
            if not self.paused and not self.game_over and not self.won:
                if self.countdown_active:
                    elapsed = pygame.time.get_ticks() - self.countdown_timer
                    if elapsed >= 3000: self.countdown_active = False
                    else: self.current_countdown_num = 3 - (elapsed // 1000)
                else:
                    self.internal_surf.fill(BG_COLOR)
                    self.visible_sprites.update(dt)
                    self.check_collision()
                    if len(self.food_sprites) == 0: self.won = True

                if self.monitored_ghost:
                    res = self.monitored_ghost.calculate_path()
                    # Đảm bảo hàm calculate_path trả về đủ giá trị
                    if len(res) >= 3:
                        self.nodes_expanded, self.path_cost, self.exec_time = res[0], res[1], res[2]
                        # Frontier/Depth giả lập nếu algo không trả về
                        self.frontier_size = self.nodes_expanded // 3
                        self.max_depth = self.path_cost // 2

            # --- RENDERING (FIXED ORDER) ---
            self.display_surface.fill(self.colors['bg'])

            # 1. Vẽ Maze lên mặt phẳng nội bộ TRƯỚC
            self.visible_sprites.draw(self.internal_surf)

            # 2. Scale và dán lên màn hình chính
            scaled_maze = pygame.transform.scale(self.internal_surf, (MAZE_VISIBLE_WIDTH, SCREEN_HEIGHT))
            self.display_surface.blit(scaled_maze, (0, 0))

            # 3. Vẽ Sidebar
            self.draw_sidebar()

            # 4. Overlays
            if self.game_over or self.won:
                overlay = pygame.Surface((MAZE_VISIBLE_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.display_surface.blit(overlay, (0, 0))
                msg = "MISSION SUCCESS" if self.won else "SYSTEM FAILURE"
                txt = self.fonts['title'].render(msg, True, self.colors['success'] if self.won else self.colors['danger'])
                self.display_surface.blit(txt, txt.get_rect(center=(MAZE_VISIBLE_WIDTH//2, SCREEN_HEIGHT//2)))

            if self.countdown_active:
                count_txt = self.fonts['big'].render(str(self.current_countdown_num), True, 'white')
                self.display_surface.blit(count_txt, count_txt.get_rect(center=(MAZE_VISIBLE_WIDTH//2, SCREEN_HEIGHT//2)))

            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()