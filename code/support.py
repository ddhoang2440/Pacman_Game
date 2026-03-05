import pygame

def import_sprite_sheet(path, rows, cols):
    full_sheet = pygame.image.load(path).convert_alpha()
    sheet_width, sheet_height = full_sheet.get_size()
    sprite_width = sheet_width // cols
    sprite_height = sheet_height // rows
    
    frames = []
    for row in range(rows):
        for col in range(cols):
            x = col * sprite_width
            y = row * sprite_height
            # Cut the sprite and create a new surface for it
            temp_surface = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
            temp_surface.blit(full_sheet, (0, 0), pygame.Rect(x, y, sprite_width, sprite_height))
            frames.append(temp_surface)
    return frames