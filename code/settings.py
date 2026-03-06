import pygame

import pygame

# =========================================================
# DISPLAY & WINDOW SETTINGS
# =========================================================
TILE_SIZE = 16
MAP_COLS = 29
MAP_ROWS = 31
SCALE = 1.5

# Internal resolution (pixel art gốc)
INTERNAL_WIDTH = MAP_COLS * TILE_SIZE
INTERNAL_HEIGHT = MAP_ROWS * TILE_SIZE

# Sidebar
SIDEBAR_WIDTH = 520
MAZE_VISIBLE_WIDTH = INTERNAL_WIDTH * SCALE

# Final window size
SCREEN_WIDTH = MAZE_VISIBLE_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = INTERNAL_HEIGHT * SCALE


# =========================================================
# MAP SETTINGS
# =========================================================
MAP_PATH = '../data/maps/Map1.tmx'


# =========================================================
# COLORS & UI THEME
# =========================================================
BG_COLOR = '#0f0f0f'        # Deep Dark
SIDEBAR_BG = '#121212'      # Slightly lighter than bg
CARD_BG = '#1b1b1b'         # Card surface
ACCENT = '#1EA7E1'          # Professional Cyan
GOLD = '#FFD700'            # Score & Highlights
TEXT_MAIN = '#ffffff'
TEXT_DIM = '#aaaaaa'        # Secondary labels
PAUSE_COLOR = '#ff4d00'     # Action Orange
SUCCESS = '#00FF00'
VALUE_COLOR = '#00FFFF'
# --- UI CONSTANTS ---
CARD_RADIUS = 12
CARD_PADDING = 20
# =========================================================
# ALGORITHMS
# =========================================================
ALGO_LIST = ['BFS', 'DFS', 'UCS', 'A*', 'IDS', 'GBFS']


# =========================================================
# PLAYER SETTINGS
# =========================================================
PLAYER_SPEED = 110
PLAYER_ANIM_SPEED = 6
PLAYER_PATH = '../images/player/Walk.png'

MAX_LIVES = 3
INVINCIBILITY_DURATION = 2000  # ms


# =========================================================
# POWER UP
# =========================================================
POWER_UP_DURATION = 7000  # ms


# =========================================================
# GHOST SETTINGS
# =========================================================
GHOST_SPEED = 75
SCARED_SPEED = 40
GHOST_HOUSE_POS = (14, 14)

ANIMATION_SPEED = 8


# Ghost configs
GHOST_CONFIGS = [
    {'name': 'EggGirl',    'path': '../images/enemies/EggGirl',    'algo': 'BFS'},
    {'name': 'Eskimo',     'path': '../images/enemies/Eskimo',     'algo': 'Alpha-Beta'},
    {'name': 'GoldStatue', 'path': '../images/enemies/GoldStatue', 'algo': 'A*'},
    {'name': 'Cavegirl',   'path': '../images/enemies/Cavegirl',   'algo': 'Minimax'}
]


# =========================================================
# AI SETTINGS
# =========================================================
THINK_DELAY = 0.4  # seconds