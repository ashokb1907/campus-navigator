# player_class.py
import pygame
import os
from settings import (SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, BLUE, 
                      PLAYER_DEFAULT_WIDTH, PLAYER_DEFAULT_HEIGHT, PLAYER_SPEED) # Import from settings

class Player(pygame.sprite.Sprite):
    def __init__(self, initial_world_x, initial_world_y, sprite_image_path):
        super().__init__()
        self.width = PLAYER_DEFAULT_WIDTH
        self.height = PLAYER_DEFAULT_HEIGHT
        self.sprite_image_path = sprite_image_path 

        try:
            if self.sprite_image_path and os.path.exists(self.sprite_image_path):
                self.original_image = pygame.image.load(self.sprite_image_path).convert_alpha()
            else:
                # This case should ideally be handled by get_player_sprite_paths in settings.py
                # providing a valid default path or None. If None, this error will trigger.
                raise pygame.error(f"Player sprite path invalid or None: {self.sprite_image_path}")
            self.original_image = pygame.transform.scale(self.original_image, (self.width, self.height))
        except pygame.error as e:
            print(f"Error loading player sprite '{self.sprite_image_path}': {e}. Using default blue square.")
            self.original_image = pygame.Surface([self.width, self.height])
            self.original_image.fill(BLUE)
        
        self.image = self.original_image.copy()
        # Attempt to set colorkey if image doesn't have per-pixel alpha
        # This helps if your sprites are not PNGs with good transparency
        if self.image.get_flags() & pygame.SRCALPHA == 0: # Check if not SRCALPHA
             if self.image.get_alpha() is None: # Further check if no global alpha is set
                self.image.set_colorkey(BLACK) # Common default for non-alpha images
        
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.world_x = float(initial_world_x)
        self.world_y = float(initial_world_y)
        self.speed = PLAYER_SPEED
        self.direction = pygame.math.Vector2(0, 0)

    def update(self, dt, game_map):
        if self.direction.length_squared() == 0: return
        try: normalized_direction = self.direction.normalize()
        except ValueError: normalized_direction = pygame.math.Vector2(0,0)
        
        delta_x = normalized_direction.x * self.speed * dt
        delta_y = normalized_direction.y * self.speed * dt
        
        new_world_x_center = self.world_x + delta_x
        potential_player_rect_x = pygame.Rect(new_world_x_center - self.width/2, self.world_y - self.height/2, self.width, self.height)
        if delta_x != 0:
            corners_to_check_x = [potential_player_rect_x.topright, potential_player_rect_x.bottomright] if delta_x > 0 else [potential_player_rect_x.topleft, potential_player_rect_x.bottomleft]
            for corner_x_coord, corner_y_coord in corners_to_check_x:
                if game_map.tile_pixel_width == 0: continue 
                tile_cx = int(corner_x_coord / game_map.tile_pixel_width); tile_cy = int(corner_y_coord / game_map.tile_pixel_height)
                if not game_map.is_tile_walkable(tile_cx, tile_cy):
                    if delta_x > 0: new_world_x_center = (tile_cx * game_map.tile_pixel_width) - (self.width / 2) - 0.01 
                    elif delta_x < 0: new_world_x_center = ((tile_cx + 1) * game_map.tile_pixel_width) + (self.width / 2) + 0.01
                    break 
            self.world_x = new_world_x_center
        # No else needed, self.world_x is already new_world_x_center if no collision

        new_world_y_center = self.world_y + delta_y
        # Update rect for Y check using the potentially modified self.world_x
        potential_player_rect_y = pygame.Rect(self.world_x - self.width/2, new_world_y_center - self.height/2, self.width, self.height)
        if delta_y != 0:
            corners_to_check_y = [potential_player_rect_y.bottomleft, potential_player_rect_y.bottomright] if delta_y > 0 else [potential_player_rect_y.topleft, potential_player_rect_y.topright]
            for corner_x_coord, corner_y_coord in corners_to_check_y:
                if game_map.tile_pixel_height == 0: continue 
                # Use current self.world_x (after X collision) to determine current X tile for Y check
                current_x_tile_for_y_check = int((self.world_x + (self.width/2 * (1 if delta_x == 0 else delta_x/abs(delta_x)) if delta_x != 0 else 0) ) / game_map.tile_pixel_width) # A bit complex, simpler to use center for Y check
                tile_cx_for_y_check = int(corner_x_coord / game_map.tile_pixel_width) # Use corner's X for more accuracy
                tile_cy = int(corner_y_coord / game_map.tile_pixel_height)
                if not game_map.is_tile_walkable(tile_cx_for_y_check, tile_cy): # Check using corner's X
                    if delta_y > 0: new_world_y_center = (tile_cy * game_map.tile_pixel_height) - (self.height / 2) - 0.01
                    elif delta_y < 0: new_world_y_center = ((tile_cy + 1) * game_map.tile_pixel_height) + (self.height / 2) + 0.01
                    break
            self.world_y = new_world_y_center
        # No else needed

        half_w, half_h = self.width/2, self.height/2
        if game_map.full_map_pixel_width > 0: self.world_x = max(half_w, min(self.world_x, game_map.full_map_pixel_width - half_w))
        if game_map.full_map_pixel_height > 0: self.world_y = max(half_h, min(self.world_y, game_map.full_map_pixel_height - half_h))
        self.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

    def set_movement_direction(self, input_direction_vector): 
        self.direction = input_direction_vector