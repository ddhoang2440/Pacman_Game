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