# destination_class.py
import pygame

# Define some colors for destinations or load images later
DESTINATION_COLOR_PENDING = (255, 165, 0, 180)  # Orange, semi-transparent for pending
DESTINATION_COLOR_VISITED = (0, 255, 0, 100)    # Green, semi-transparent for visited
DESTINATION_OUTLINE_COLOR = (255, 255, 255)     # White outline

class Destination(pygame.sprite.Sprite):
    def __init__(self, id, name, world_x, world_y, radius, info_text, image_path=None):
        super().__init__()
        self.id = id
        self.name = name
        self.world_x = float(world_x)  # Center X in world coordinates
        self.world_y = float(world_y)  # Center Y in world coordinates
        self.radius = int(radius)
        self.info_text = info_text
        self.visited = False
        self.is_active_target = False # To highlight the current objective

        # Visual representation
        self.image_path = image_path
        if self.image_path:
            try:
                # Placeholder: Load and scale an actual icon if you have one
                # self.original_image = pygame.image.load(image_path).convert_alpha()
                # self.original_image = pygame.transform.scale(self.original_image, (self.radius * 2, self.radius * 2))
                pass # Replace with actual image loading
            except pygame.error as e:
                print(f"Warning: Could not load destination image {image_path}: {e}")
                self.image_path = None # Fallback to drawing a circle

        # Create a surface for drawing. Size is radius * 2 for diameter.
        # We'll draw a circle on this surface.
        # The actual self.image will be created/updated in the update_visuals method
        self.current_diameter = self.radius * 2
        self.image = pygame.Surface([self.current_diameter, self.current_diameter], pygame.SRCALPHA)
        self.rect = self.image.get_rect() # This rect's position will be updated for screen drawing

        self.update_visuals() # Initial visual setup

    def update_visuals(self):
        """Updates the destination's appearance based on its state (visited, active)."""
        self.image.fill((0,0,0,0)) # Clear with transparent
        
        color_to_use = DESTINATION_COLOR_PENDING
        if self.visited:
            color_to_use = DESTINATION_COLOR_VISITED
        
        # Draw the main circle
        pygame.draw.circle(self.image, color_to_use, (self.radius, self.radius), self.radius)
        
        # Add an outline or highlight if it's the active target
        if self.is_active_target and not self.visited:
            pygame.draw.circle(self.image, DESTINATION_OUTLINE_COLOR, (self.radius, self.radius), self.radius, 3) # 3px outline
            # You could also make it pulse or have a different animation

    def mark_visited(self):
        self.visited = True
        self.is_active_target = False # No longer the active target once visited
        self.update_visuals()
        print(f"Destination '{self.name}' visited!")

    def set_active_target(self, is_active):
        if self.is_active_target != is_active:
            self.is_active_target = is_active
            self.update_visuals()

    def update_screen_position(self, game_map):
        """
        Updates the destination's on-screen rect position based on map offset and zoom.
        This is called before drawing if it's not part of a sprite group that handles this.
        If it IS part of a Pygame sprite group that gets drawn, this logic would be
        implicitly handled if the rect's world coordinates were directly used/converted by a camera.
        However, since our map moves and player is screen-center, we calculate screen pos.
        """
        # Calculate the destination's top-left position on the screen
        # based on its world center, the map's current offset, and zoom.
        screen_x_of_center = game_map.offset_x + (self.world_x * game_map.zoom_level)
        screen_y_of_center = game_map.offset_y + (self.world_y * game_map.zoom_level)
        
        # The self.rect is for the sprite's image. Set its center.
        self.rect.center = (screen_x_of_center, screen_y_of_center)

        # Optional: Rescale the image if zoom changes significantly and you want destinations to scale
        # For simplicity, we'll keep destination visual size constant on screen for now,
        # but you could add logic here to change self.current_diameter and redraw self.image
        # if self.radius * game_map.zoom_level is different from self.current_diameter.