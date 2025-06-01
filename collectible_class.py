# collectible_class.py
import pygame

DEFAULT_COLLECTIBLE_COLOR = (255, 215, 0)  # Gold

class Collectible(pygame.sprite.Sprite):
    def __init__(self, id, name, world_x, world_y, image_path, info_text, points_value, 
                 riddle_text, riddle_options, correct_option_index, default_size=(24, 24)): # Added riddle params
        super().__init__()
        self.id = id
        self.name = name
        self.world_x = float(world_x)
        self.world_y = float(world_y)
        self.image_path = image_path
        self.info_text = info_text
        self.points_value = int(points_value)
        self.collected = False
        self.default_size = default_size

        # --- Riddle Data ---
        self.riddle_text = riddle_text
        self.riddle_options = riddle_options # List of 4 strings
        self.correct_option_index = int(correct_option_index) # 0, 1, 2, or 3
        # --- ---

        try:
            self.original_image = pygame.image.load(self.image_path).convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, self.default_size)
        except pygame.error as e:
            print(f"Warning: Could not load collectible image '{self.image_path}': {e}. Using default color.")
            self.original_image = pygame.Surface(self.default_size, pygame.SRCALPHA)
            self.original_image.fill((0,0,0,0))
            pygame.draw.circle(self.original_image, DEFAULT_COLLECTIBLE_COLOR, (default_size[0]//2, default_size[1]//2), default_size[0]//2)

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(self.world_x, self.world_y))

    def update_screen_position(self, game_map):
        if self.collected: return
        screen_x_of_center = game_map.offset_x + (self.world_x * game_map.zoom_level)
        screen_y_of_center = game_map.offset_y + (self.world_y * game_map.zoom_level)
        self.rect.center = (screen_x_of_center, screen_y_of_center)

    def mark_collected(self): # This is called AFTER successfully answering the riddle
        self.collected = True
        print(f"Collectible '{self.name}' successfully collected! Points: {self.points_value}")
        self.kill()