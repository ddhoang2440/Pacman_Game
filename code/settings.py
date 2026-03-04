import pygame

# code/settings.py
TILE_SIZE = 16
MAP_COLS = 29
MAP_ROWS = 31

# Tỷ lệ phóng to (Ví dụ: x2 cho dễ nhìn)
SCALE = 1.5

# Kích thước thực tế của game
INTERNAL_WIDTH = MAP_COLS * TILE_SIZE
INTERNAL_HEIGHT = MAP_ROWS * TILE_SIZE

# Kích thước cửa sổ hiển thị
SCREEN_WIDTH = INTERNAL_WIDTH * SCALE
SCREEN_HEIGHT = INTERNAL_HEIGHT * SCALE

MAP_PATH = '../data/maps/Map1.tmx'
PLAYER_PATH = '../images/player/walk.png'

BG_COLOR = '#060606'