import pygame
import sys
import os
from map_class import Map # Assuming map_class.py is in the same directory

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
REFERENCE_TILE_SIZE = 32 # Ensure this matches the size used in convert_map_to_tiles.py
ZOOM_SPEED_MULTIPLIER = 1.1

# --- Colors ---
WHITE = (255, 255, 255)
BLUE = (0, 0, 255) # Player color

# --- Player Class (Manages world position) ---
class Player(pygame.sprite.Sprite):
    def __init__(self, initial_world_x, initial_world_y):
        super().__init__()
        self.image = pygame.Surface([20, 20]) # Visual size of player
        self.image.fill(BLUE)
        self.image.set_colorkey((0,0,0)) 

        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.world_x = float(initial_world_x)
        self.world_y = float(initial_world_y)
        self.speed = 200
        self.direction = pygame.math.Vector2(0, 0)

    def update(self, dt, game_map_instance):
        if self.direction.length_squared() == 0:
            return

        try:
            normalized_direction = self.direction.normalize()
        except ValueError:
            normalized_direction = pygame.math.Vector2(0, 0)

        move_x_amount = normalized_direction.x * self.speed * dt
        move_y_amount = normalized_direction.y * self.speed * dt
        
        potential_world_x = self.world_x + move_x_amount
        if move_x_amount > 0:
            leading_edge_check_x = self.world_x + (self.rect.width / 2) + move_x_amount
        elif move_x_amount < 0:
            leading_edge_check_x = self.world_x - (self.rect.width / 2) + move_x_amount
        else:
            leading_edge_check_x = self.world_x
        
        target_tile_x_idx = int(leading_edge_check_x / game_map_instance.tile_pixel_width)
        current_center_tile_y_idx = int(self.world_y / game_map_instance.tile_pixel_height)

        if game_map_instance.is_tile_walkable(target_tile_x_idx, current_center_tile_y_idx):
            self.world_x = potential_world_x
        else:
            if move_x_amount > 0:
                self.world_x = (target_tile_x_idx * game_map_instance.tile_pixel_width) - (self.rect.width / 2) - 0.01
            elif move_x_amount < 0:
                self.world_x = ((target_tile_x_idx + 1) * game_map_instance.tile_pixel_width) + (self.rect.width / 2) + 0.01
        
        potential_world_y = self.world_y + move_y_amount
        if move_y_amount > 0:
            leading_edge_check_y = self.world_y + (self.rect.height / 2) + move_y_amount
        elif move_y_amount < 0:
            leading_edge_check_y = self.world_y - (self.rect.height / 2) + move_y_amount
        else:
            leading_edge_check_y = self.world_y
            
        current_center_tile_x_idx = int(self.world_x / game_map_instance.tile_pixel_width)
        target_tile_y_idx = int(leading_edge_check_y / game_map_instance.tile_pixel_height)

        if game_map_instance.is_tile_walkable(current_center_tile_x_idx, target_tile_y_idx):
            self.world_y = potential_world_y
        else:
            if move_y_amount > 0:
                self.world_y = (target_tile_y_idx * game_map_instance.tile_pixel_height) - (self.rect.height / 2) - 0.01
            elif move_y_amount < 0:
                self.world_y = ((target_tile_y_idx + 1) * game_map_instance.tile_pixel_height) + (self.rect.height / 2) + 0.01

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
    game_map = Map(screen, "tiles")
    
    if not game_map.tile_filenames_grid or not game_map.collision_grid:
        print("Map data or collision grid failed to load properly. Exiting.")
        if game_map.collision_grid is None:
            print("Collision grid specifically is None.")
        elif not game_map.collision_grid:
             print("Collision grid specifically is empty.")
        pygame.quit()
        sys.exit()

    # --- Determine Player Starting Position ---
    initial_player_world_x = game_map.full_map_pixel_width / 2  # Default
    initial_player_world_y = game_map.full_map_pixel_height / 2 # Default

    # Preferred starting tile (e.g., top-right corner of the tile grid)
    # Ensure map dimensions are valid before calculating preferred start
    if game_map.grid_width_in_tiles > 0 and game_map.grid_height_in_tiles > 0:
        preferred_start_tile_x = game_map.grid_width_in_tiles - 1
        preferred_start_tile_y = 0
        
        found_start_tile_coords = None
        max_search_radius = max(game_map.grid_width_in_tiles, game_map.grid_height_in_tiles)

        for r in range(max_search_radius): # r is the radius of the square spiral layer
            # Check preferred point itself at radius 0
            if r == 0:
                cx, cy = preferred_start_tile_x, preferred_start_tile_y
                if 0 <= cx < game_map.grid_width_in_tiles and \
                   0 <= cy < game_map.grid_height_in_tiles and \
                   game_map.is_tile_walkable(cx, cy):
                    found_start_tile_coords = (cx, cy)
                    break
                continue # Skip to next radius if r=0 and preferred is not walkable

            # Search points in a square layer around preferred_start_tile_x, preferred_start_tile_y
            # Top row of the layer: (preferred_start_tile_y - r)
            # Bottom row: (preferred_start_tile_y + r)
            # Left col: (preferred_start_tile_x - r)
            # Right col: (preferred_start_tile_x + r)
            
            # Iterate over the perimeter of the square layer
            # (min_x, max_x), (min_y, max_y) define the current search square
            min_x = preferred_start_tile_x - r
            max_x = preferred_start_tile_x + r
            min_y = preferred_start_tile_y - r
            max_y = preferred_start_tile_y + r

            # Check top & bottom rows
            for cur_x in range(min_x, max_x + 1):
                # Top row
                if 0 <= cur_x < game_map.grid_width_in_tiles and \
                   0 <= min_y < game_map.grid_height_in_tiles and \
                   game_map.is_tile_walkable(cur_x, min_y):
                    found_start_tile_coords = (cur_x, min_y)
                    break
                # Bottom row
                if 0 <= cur_x < game_map.grid_width_in_tiles and \
                   0 <= max_y < game_map.grid_height_in_tiles and \
                   game_map.is_tile_walkable(cur_x, max_y):
                    found_start_tile_coords = (cur_x, max_y)
                    break
            if found_start_tile_coords: break
            
            # Check left & right columns (excluding corners already checked by top/bottom rows)
            for cur_y in range(min_y + 1, max_y): # +1 and exclusive max_y to avoid corners
                # Left col
                if 0 <= min_x < game_map.grid_width_in_tiles and \
                   0 <= cur_y < game_map.grid_height_in_tiles and \
                   game_map.is_tile_walkable(min_x, cur_y):
                    found_start_tile_coords = (min_x, cur_y)
                    break
                # Right col
                if 0 <= max_x < game_map.grid_width_in_tiles and \
                   0 <= cur_y < game_map.grid_height_in_tiles and \
                   game_map.is_tile_walkable(max_x, cur_y):
                    found_start_tile_coords = (max_x, cur_y)
                    break
            if found_start_tile_coords: break

        if found_start_tile_coords:
            start_tile_x, start_tile_y = found_start_tile_coords
            initial_player_world_x = (start_tile_x * game_map.tile_pixel_width) + (game_map.tile_pixel_width / 2)
            initial_player_world_y = (start_tile_y * game_map.tile_pixel_height) + (game_map.tile_pixel_height / 2)
            print(f"Player starting on walkable tile: ({start_tile_x}, {start_tile_y}) at world coordinates: ({initial_player_world_x:.1f}, {initial_player_world_y:.1f})")
        else:
            print(f"Warning: No walkable starting tile found near preferred top-right ({preferred_start_tile_x}, {preferred_start_tile_y}). Using default map center.")
            # Defaulting to map center if no suitable spot is found (already set above)
    else:
        print("Warning: Map grid dimensions are not valid. Player starting at default screen center.")
        # Defaulting to map center if map dimensions are not valid (already set above)


    player = Player(initial_player_world_x, initial_player_world_y)
    all_sprites = pygame.sprite.Group(player) 

    running = True
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN])

    while running:
        dt = clock.tick(60) / 1000.0 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    game_map.zoom(ZOOM_SPEED_MULTIPLIER, player.rect.centerx, player.rect.centery)
                elif event.key == pygame.K_MINUS:
                    game_map.zoom(1 / ZOOM_SPEED_MULTIPLIER, player.rect.centerx, player.rect.centery)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 4: 
                    game_map.zoom(ZOOM_SPEED_MULTIPLIER, mouse_pos[0], mouse_pos[1])
                elif event.button == 5: 
                    game_map.zoom(1 / ZOOM_SPEED_MULTIPLIER, mouse_pos[0], mouse_pos[1])
        
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

        player.update(dt, game_map) 
        
        game_map.offset_x = player.rect.centerx - (player.world_x * game_map.zoom_level)
        game_map.offset_y = player.rect.centery - (player.world_y * game_map.zoom_level)

        screen.fill(WHITE) 
        game_map.draw() 
        all_sprites.draw(screen) 
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    tiles_dir = "tiles"
    meta_file = os.path.join(tiles_dir, "map_meta.json")

    if not os.path.exists(meta_file):
        print(f"Error: Metadata file '{meta_file}' not found.")
        print(f"Please run 'python convert_map_to_tiles.py' first.")
        print(f"Ensure 'campus_map.png' (or your map image) and 'convert_map_to_tiles.py' are configured correctly.")
        
        map_image_for_conversion = "campus_map.png" # Assuming this is the name of your map image
        tile_size_for_conversion = REFERENCE_TILE_SIZE 
        if os.path.exists(map_image_for_conversion):
            print(f"\nFound '{map_image_for_conversion}'. Attempting to generate tiles now...")
            try:
                from convert_map_to_tiles import convert_map_to_tiles as tile_converter_func
                tile_converter_func(
                    map_image_for_conversion,
                    tile_size_for_conversion,
                    tile_size_for_conversion, 
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