import pygame
import sys
import os
from map_class import Map # Assuming map_class.py is in the same directory

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
# TILE_SIZE is now primarily for reference or if game logic needs a fixed tile dimension.
# The actual tile dimensions are loaded from map_meta.json by the Map class.
# Ensure this matches the size used in convert_map_to_tiles.py (e.g., 64).
REFERENCE_TILE_SIZE = 64
ZOOM_SPEED_MULTIPLIER = 1.1 # Factor for zooming in/out

# --- Colors ---
WHITE = (255, 255, 255)
BLUE = (0, 0, 255) # Player color

# --- Player Class (Manages world position) ---
class Player(pygame.sprite.Sprite):
    def __init__(self, initial_world_x, initial_world_y):
        super().__init__()
        self.image = pygame.Surface([20, 20]) # Visual size of player
        self.image.fill(BLUE)
        self.image.set_colorkey((0,0,0)) # Optional: if you want a black background to be transparent
        # self.image = pygame.transform.scale(pygame.image.load("player_sprite.png").convert_alpha(), (20,20)) # Example with sprite

        # The rect is for drawing the player AT THE SCREEN CENTER
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Player's precise position in the game world (in pixels, not tiles)
        self.world_x = float(initial_world_x)
        self.world_y = float(initial_world_y)
        
        self.speed = 200 # World pixels per second
        self.direction = pygame.math.Vector2(0, 0)

    # Inside Player class in main.py
    def update(self, dt, game_map_instance): # dt is delta time
        if self.direction.length_squared() == 0:
            return # No movement requested

        normalized_direction = self.direction.normalize()

        # --- Proposed new position ---
        # Calculate how much the player *wants* to move
        move_x_amount = normalized_direction.x * self.speed * dt
        move_y_amount = normalized_direction.y * self.speed * dt

        new_world_x = self.world_x + move_x_amount
        new_world_y = self.world_y # Check X movement first

        # --- Collision Detection for X-axis ---
        # Determine the tile the player would be moving into
        # Consider player's bounding box for more accuracy, for now, center point is simpler
        # For better collision, you might want to check multiple points on the player's bounding box

        # Get current tile of player
        current_tile_x_idx = int(self.world_x / game_map_instance.tile_pixel_width)
        current_tile_y_idx = int(self.world_y / game_map_instance.tile_pixel_height)

        # Get target tile based on new_world_x
        target_tile_for_x_move_idx = int(new_world_x / game_map_instance.tile_pixel_width)

        if game_map_instance.is_tile_walkable(target_tile_for_x_move_idx, current_tile_y_idx):
            self.world_x = new_world_x # Allow X movement
        else:
            # If moving into a wall on X, snap to edge of current tile or wall tile
            # This prevents slight overlap.
            if move_x_amount > 0: # Moving right
                self.world_x = (target_tile_for_x_move_idx * game_map_instance.tile_pixel_width) - (self.rect.width / 2) - 0.1 # Epsilon
            elif move_x_amount < 0: # Moving left
                self.world_x = ((current_tile_x_idx) * game_map_instance.tile_pixel_width) + (self.rect.width / 2) + 0.1 # Epsilon


        # --- Collision Detection for Y-axis ---
        new_world_y = self.world_y + move_y_amount # Reset for Y check based on potentially updated self.world_x
        current_tile_x_idx = int(self.world_x / game_map_instance.tile_pixel_width) # Re-evaluate current X tile
        target_tile_for_y_move_idx = int(new_world_y / game_map_instance.tile_pixel_height)

        if game_map_instance.is_tile_walkable(current_tile_x_idx, target_tile_for_y_move_idx):
            self.world_y = new_world_y # Allow Y movement
        else:
            # If moving into a wall on Y, snap to edge
            if move_y_amount > 0: # Moving down
                self.world_y = (target_tile_for_y_move_idx * game_map_instance.tile_pixel_height) - (self.rect.height / 2) - 0.1
            elif move_y_amount < 0: # Moving up
                self.world_y = ((current_tile_y_idx) * game_map_instance.tile_pixel_height) + (self.rect.height / 2) + 0.1

        # Optional: Clamp player to map boundaries (already present, keep it)
        if game_map_instance and game_map_instance.full_map_pixel_width > 0:
            player_half_width = self.rect.width / 2
            player_half_height = self.rect.height / 2
            self.world_x = max(player_half_width, min(self.world_x, game_map_instance.full_map_pixel_width - player_half_width))
            self.world_y = max(player_half_height, min(self.world_y, game_map_instance.full_map_pixel_height - player_half_height))

        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def set_movement_direction(self, input_direction_vector):
        self.direction = input_direction_vector


# --- Main Function ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Campus Navigator")
    clock = pygame.time.Clock()

    # --- Create Map ---
    # "tiles" is the directory where map_meta.json and tile images are expected.
    game_map = Map(screen, "tiles")
    
    if not game_map.tile_filenames_grid: # Check if map metadata loaded successfully
        print("Map data failed to load properly. Exiting.")
        pygame.quit()
        sys.exit()

    # --- Create Player ---
    # Start player in the center of the map (world coordinates)
    initial_player_world_x = game_map.full_map_pixel_width / 2
    initial_player_world_y = game_map.full_map_pixel_height / 2
    player = Player(initial_player_world_x, initial_player_world_y)
    
    all_sprites = pygame.sprite.Group(player) # Group for easy drawing/updating

    # --- Game Loop ---
    running = True
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN]) # Optimize event handling

    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds (for frame-rate independence)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Zooming with + and - keys (or = for +)
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                     # Zoom in, focused on player's screen position (center)
                    game_map.zoom(ZOOM_SPEED_MULTIPLIER, player.rect.centerx, player.rect.centery)
                elif event.key == pygame.K_MINUS:
                     # Zoom out, focused on player's screen position (center)
                    game_map.zoom(1 / ZOOM_SPEED_MULTIPLIER, player.rect.centerx, player.rect.centery)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Mouse wheel zoom
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 4:  # Scroll up (zoom in)
                    game_map.zoom(ZOOM_SPEED_MULTIPLIER, mouse_pos[0], mouse_pos[1])
                elif event.button == 5:  # Scroll down (zoom out)
                    game_map.zoom(1 / ZOOM_SPEED_MULTIPLIER, mouse_pos[0], mouse_pos[1])
        
        # Handle continuous key presses for movement
        keys = pygame.key.get_pressed()
        current_direction = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            current_direction.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            current_direction.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            current_direction.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            current_direction.y += 1
        player.set_movement_direction(current_direction)

        # --- Game Logic Update ---
        player.update(dt, game_map) # Player moves in the world

        # --- Update Map Offset to Center Player on Screen ---
        # The map's top-left corner (offset_x, offset_y) needs to be positioned such that
        # the player's world coordinates (player.world_x, player.world_y)
        # end up at the player's screen rect center (SCREEN_WIDTH/2, SCREEN_HEIGHT/2).
        #
        # ScreenX = WorldX * Zoom + OffsetX
        # PlayerScreenX = PlayerWorldX * Zoom + OffsetX
        # OffsetX = PlayerScreenX - (PlayerWorldX * Zoom)
        
        game_map.offset_x = player.rect.centerx - (player.world_x * game_map.zoom_level)
        game_map.offset_y = player.rect.centery - (player.world_y * game_map.zoom_level)

        # --- Drawing ---
        screen.fill(WHITE)    # Clear screen
        game_map.draw()       # Draw the map with current offset and zoom
        all_sprites.draw(screen) # Draw player (and any other sprites)
        
        pygame.display.flip() # Update the full display

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Crucial Check: Ensure tiles and metadata exist before starting the game.
    tiles_dir = "tiles"
    meta_file = os.path.join(tiles_dir, "map_meta.json")

    if not os.path.exists(meta_file):
        print(f"Error: Metadata file '{meta_file}' not found.")
        print(f"Please run 'python convert_map_to_tiles.py' first.")
        print(f"Ensure 'campus_map.jpg' (or your map image) and 'convert_map_to_tiles.py' are configured correctly.")
        
        # Optional: Attempt to generate tiles if the map image exists
        # This part is a convenience and might need adjustment based on your project structure
        map_image_for_conversion = "campus_map.jpg" # Must match the one in convert_map_to_tiles.py
        tile_size_for_conversion = REFERENCE_TILE_SIZE # Must match
        if os.path.exists(map_image_for_conversion):
            print(f"\nFound '{map_image_for_conversion}'. Attempting to generate tiles now...")
            try:
                # Directly call the function from the other script
                # This requires convert_map_to_tiles.py to be importable
                from convert_map_to_tiles import convert_map_to_tiles as tile_converter_func
                tile_converter_func(
                    map_image_for_conversion,
                    tile_size_for_conversion,
                    tile_size_for_conversion, # Assuming square tiles
                    tiles_dir
                )
                if os.path.exists(meta_file):
                     print("\nTile generation successful. Please try running main.py again.")
                else:
                    print("\nTile generation might have failed. Check output from convert_map_to_tiles.")
            except ImportError:
                print("Could not import 'convert_map_to_tiles'. Please run it manually.")
            except Exception as e:
                print(f"An error occurred during automatic tile generation: {e}")
        sys.exit()
    else:
        main()