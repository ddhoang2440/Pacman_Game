import pygame

# code/settings.py
TILE_SIZE = 16
MAP_COLS = 29
MAP_ROWS = 31
SCALE = 1.5

# Kích thước nội bộ (Pixel Art gốc)
INTERNAL_WIDTH = MAP_COLS * TILE_SIZE  # 720
INTERNAL_HEIGHT = MAP_ROWS * TILE_SIZE # 496

# KÍCH THƯỚC CỬA SỔ HIỂN THỊ
SIDEBAR_WIDTH = 300 # Độ rộng vùng thông tin bên phải
MAZE_VISIBLE_WIDTH = INTERNAL_WIDTH * SCALE # 1080

SCREEN_WIDTH = MAZE_VISIBLE_WIDTH + SIDEBAR_WIDTH # Tổng: 1380
SCREEN_HEIGHT = INTERNAL_HEIGHT * SCALE # 744

MAP_PATH = '../data/maps/Map1.tmx'
BG_COLOR = '#060606'
UI_COLOR = '#121212' # Màu nền Sidebar (xám đậm hơn nền game)

ALGO_LIST = ['BFS', 'DFS', 'UCS', 'A*', 'IDS', 'GBFS']
# Màu sắc bổ sung
ALGO_BOX_COLOR = '#252525' 
SELECTED_COLOR = 'yellow'
ACCENT = '#00BFFF'
SIDEBAR_BG = '#0f0f0f'
CARD_BG = '#1c1c1c'
CARD_BORDER = '#2e2e2e'
TEXT_DIM = '#aaaaaa'
ACCENT = '#00BFFF'

# --- UI & Colors ---
SIDEBAR_BG = '#121212'
CARD_BG = '#1e1e1e'
UI_BORDER = '#333333'
NEON_BLUE = '#00BFFF'
GOLD = '#FFD700'

# --- Ghost Configs ---
# Gom folder path và thuật toán vào một chỗ
GHOST_CONFIGS = [
    {'name': 'EggGirl',    'path': '../images/enemies/EggGirl',    'algo': 'BFS'},
    {'name': 'Eskimo',     'path': '../images/enemies/Eskimo',     'algo': 'Alpha-Beta'},
    {'name': 'GoldStatue', 'path': '../images/enemies/GoldStatue', 'algo': 'A*'},
    {'name': 'Cavegirl',   'path': '../images/enemies/Cavegirl',   'algo': 'Minimax'}
]

# --- AI & Animation Settings ---
THINK_DELAY = 0.4      # Thời gian Ma suy nghĩ (giây)
ANIMATION_SPEED = 8    # Tốc độ khung hình
GHOST_SPEED = 75       # Tốc độ Ma di chuyển

POWER_UP_DURATION = 7000 # 7 giây hiệu lực
SCARED_SPEED = 40        # Ma đi chậm lại khi bị sợ
POWER_UP_DURATION = 7000  # 7 giây
GHOST_HOUSE_POS = (14, 14) # Vị trí hồi sinh của Ma


# code/settings.py
PLAYER_SPEED = 110
PLAYER_ANIM_SPEED = 6
PLAYER_PATH = '../images/player/Walk.png'
TILE_SIZE = 16 # Đảm bảo hằng số này có trong settings