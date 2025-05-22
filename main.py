# main.py
import pygame
import sys
import os
import random # Needed for random objective selection

from map_class import Map
from destination_class import Destination # Import the Destination class

# --- IMPORT YOUR DESTINATIONS DATA ---
try:
    from destinations_data import destinations_data
except ImportError:
    print("CRITICAL ERROR: destinations_data.py not found or destinations_data list is missing!")
    print("Please create it with your destination information using the template provided.")
    destinations_data = [] # Fallback

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
# This REFERENCE_TILE_SIZE should match the tile size used in Tiled and
# in convert_map_to_tiles.py if that script defines tile size.
REFERENCE_TILE_SIZE = 32
ZOOM_SPEED_MULTIPLIER = 1.1

# --- Colors ---
WHITE = (255, 255, 255)
BLUE = (0, 0, 255) 
BLACK = (0, 0, 0) # Used for player colorkey and some text
RED = (255,0,0) # For debug drawing

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, initial_world_x, initial_world_y, width=20, height=20):
        super().__init__()
        self.width = width
        self.height = height
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(BLUE)
        self.image.set_colorkey(BLACK) 

        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.world_x = float(initial_world_x)
        self.world_y = float(initial_world_y)
        self.speed = 150 
        self.direction = pygame.math.Vector2(0, 0)

    def update(self, dt, game_map):
        if self.direction.length_squared() == 0:
            return

        try:
            normalized_direction = self.direction.normalize()
        except ValueError:
            normalized_direction = pygame.math.Vector2(0, 0)

        delta_x = normalized_direction.x * self.speed * dt
        delta_y = normalized_direction.y * self.speed * dt

        # --- X-axis movement and collision ---
        new_world_x_center = self.world_x + delta_x
        potential_player_rect_x = pygame.Rect(
            new_world_x_center - self.width / 2, 
            self.world_y - self.height / 2, 
            self.width, 
            self.height
        )
        
        if delta_x != 0:
            collided_x = False
            corners_to_check_x = []
            if delta_x > 0: corners_to_check_x = [potential_player_rect_x.topright, potential_player_rect_x.bottomright]
            elif delta_x < 0: corners_to_check_x = [potential_player_rect_x.topleft, potential_player_rect_x.bottomleft]

            for corner_x_coord, corner_y_coord in corners_to_check_x:
                tile_cx = int(corner_x_coord / game_map.tile_pixel_width)
                tile_cy = int(corner_y_coord / game_map.tile_pixel_height)
                
                if not game_map.is_tile_walkable(tile_cx, tile_cy):
                    collided_x = True
                    if delta_x > 0: new_world_x_center = (tile_cx * game_map.tile_pixel_width) - (self.width / 2) - 0.01 
                    elif delta_x < 0: new_world_x_center = ((tile_cx + 1) * game_map.tile_pixel_width) + (self.width / 2) + 0.01
                    break 
            self.world_x = new_world_x_center
        else:
            self.world_x = new_world_x_center

        # --- Y-axis movement and collision ---
        new_world_y_center = self.world_y + delta_y
        potential_player_rect_y = pygame.Rect(
            self.world_x - self.width / 2, 
            new_world_y_center - self.height / 2,
            self.width,
            self.height
        )

        if delta_y != 0:
            collided_y = False
            corners_to_check_y = []
            if delta_y > 0: corners_to_check_y = [potential_player_rect_y.bottomleft, potential_player_rect_y.bottomright]
            elif delta_y < 0: corners_to_check_y = [potential_player_rect_y.topleft, potential_player_rect_y.topright]

            for corner_x_coord, corner_y_coord in corners_to_check_y:
                tile_cx = int(corner_x_coord / game_map.tile_pixel_width)
                tile_cy = int(corner_y_coord / game_map.tile_pixel_height)

                if not game_map.is_tile_walkable(tile_cx, tile_cy):
                    collided_y = True
                    if delta_y > 0: new_world_y_center = (tile_cy * game_map.tile_pixel_height) - (self.height / 2) - 0.01
                    elif delta_y < 0: new_world_y_center = ((tile_cy + 1) * game_map.tile_pixel_height) + (self.height / 2) + 0.01
                    break
            self.world_y = new_world_y_center
        else:
            self.world_y = new_world_y_center
        
        half_w, half_h = self.width / 2, self.height / 2
        self.world_x = max(half_w, min(self.world_x, game_map.full_map_pixel_width - half_w))
        self.world_y = max(half_h, min(self.world_y, game_map.full_map_pixel_height - half_h))
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def set_movement_direction(self, input_direction_vector):
        self.direction = input_direction_vector

# --- Objective Manager (MODIFIED for Random Objectives) ---
class ObjectiveManager:
    NUM_OBJECTIVES_TO_COMPLETE = 5 # How many random destinations to visit

    def __init__(self, all_destination_objects_list):
        # Filter out destinations with missing coordinates from the main pool
        self.full_destination_pool = [
            d for d in all_destination_objects_list 
            if d.world_x is not None and d.world_y is not None
        ]
        
        self.game_objectives = [] # The N destinations chosen for this game session
        self.current_objective_idx_in_game_list = -1 # Tracks progress through self.game_objectives
        self.current_target_destination = None
        
        self._select_random_objectives()
        self.set_next_objective() # Set the first objective

    def _select_random_objectives(self):
        if not self.full_destination_pool:
            print("Warning: No valid destinations available to select for objectives.")
            self.game_objectives = []
            return

        available_to_pick = list(self.full_destination_pool)
        random.shuffle(available_to_pick)
        
        num_to_select = min(len(available_to_pick), self.NUM_OBJECTIVES_TO_COMPLETE)
        self.game_objectives = available_to_pick[:num_to_select]
        
        for dest in self.game_objectives:
            dest.visited = False 
            dest.set_active_target(False)

        if self.game_objectives:
            print(f"Selected {len(self.game_objectives)} objectives for this session:")
            for i, dest in enumerate(self.game_objectives):
                print(f"  {i+1}. {dest.name}")
        else:
            print("Warning: Could not select any objectives for this session.")

    def set_next_objective(self):
        if self.current_target_destination:
            self.current_target_destination.set_active_target(False)

        # Iterate through the *selected* game_objectives list
        self.current_objective_idx_in_game_list +=1
        if self.current_objective_idx_in_game_list < len(self.game_objectives):
            self.current_target_destination = self.game_objectives[self.current_objective_idx_in_game_list]
            if not self.current_target_destination.visited: # Should always be true if logic is correct
                 self.current_target_destination.set_active_target(True)
                 print(f"New Objective: Go to {self.current_target_destination.name}")
                 return True
            else: # Should ideally not happen if mark_visited and set_next_objective are paired
                print(f"Debug: Objective {self.current_target_destination.name} was already visited, skipping.")
                return self.set_next_objective() # Try to find the next *actual* unvisited one
        else:
            self.current_target_destination = None
            print("All selected session objectives visited! Congratulations!")
            return False

    def get_current_objective_text(self):
        if self.current_target_destination:
            # Display progress based on the game_objectives list
            # The current_objective_idx_in_game_list is 0-based for the selected list
            return f"Find ({self.current_objective_idx_in_game_list + 1}/{len(self.game_objectives)}): {self.current_target_destination.name}"
        elif self.all_session_objectives_visited():
            return "Session Complete! All objectives met!"
        elif not self.game_objectives:
            return "No objectives available for this session."
        return "Welcome! Starting campus tour..."
        
    def all_session_objectives_visited(self):
        if not self.game_objectives: 
            return True # No objectives means session is "over" or wasn't set up
        for dest in self.game_objectives:
            if not dest.visited:
                return False
        return True

# --- Main Function ---
def main():
    pygame.init()
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    if joysticks:
        # joysticks[0].init() # Pygame usually auto-inits
        print(f"Controller found: {joysticks[0].get_name()}")
    else:
        print("No controller found. Using keyboard.")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Campus Navigator")
    clock = pygame.time.Clock()
    
    try:
        ui_font = pygame.font.Font(None, 36)
        info_font = pygame.font.Font(None, 28)
    except pygame.error:
        print("Warning: Default font not found, using system Arial.")
        ui_font = pygame.font.SysFont("arial", 30)
        info_font = pygame.font.SysFont("arial", 24)

    game_map = Map(screen, "tiles")
    
    if not game_map.is_loaded_successfully():
        print("CRITICAL ERROR: Map data failed to load. Check 'tiles/map_meta.json' and tile image paths.")
        pygame.quit()
        sys.exit()
    print(f"Debug: Map loaded. Grid: {game_map.grid_width_in_tiles}x{game_map.grid_height_in_tiles}.")
    if game_map.collision_grid and len(game_map.collision_grid) > 0 :
        print(f"Collision grid rows: {len(game_map.collision_grid)}, cols: {len(game_map.collision_grid[0])}")
    else:
        print("CRITICAL WARNING: Collision grid is empty or not loaded in game_map!")

    # --- Player Starting Position Search ---
    initial_player_world_x = game_map.full_map_pixel_width / 2
    initial_player_world_y = game_map.full_map_pixel_height / 2

    if game_map.grid_width_in_tiles > 0 and game_map.grid_height_in_tiles > 0 and \
       game_map.collision_grid and len(game_map.collision_grid) > 0:
        preferred_start_tile_x = game_map.grid_width_in_tiles - 1
        preferred_start_tile_y = 0 
        print(f"Debug: Preferred start tile index for search: ({preferred_start_tile_x}, {preferred_start_tile_y})")

        found_tile_coords = None
        max_search_radius = max(game_map.grid_width_in_tiles, game_map.grid_height_in_tiles) 

        if game_map.is_tile_walkable(preferred_start_tile_x, preferred_start_tile_y):
            found_tile_coords = (preferred_start_tile_x, preferred_start_tile_y)
        else:
            for r_search in range(1, max_search_radius):
                # Top edge
                check_y = preferred_start_tile_y - r_search
                for x_offset in range(-r_search, r_search + 1):
                    check_x = preferred_start_tile_x + x_offset
                    if game_map.is_tile_walkable(check_x, check_y): found_tile_coords = (check_x, check_y); break
                if found_tile_coords: break
                # Bottom edge
                check_y = preferred_start_tile_y + r_search
                for x_offset in range(-r_search, r_search + 1):
                    check_x = preferred_start_tile_x + x_offset
                    if game_map.is_tile_walkable(check_x, check_y): found_tile_coords = (check_x, check_y); break
                if found_tile_coords: break
                # Left edge
                check_x = preferred_start_tile_x - r_search
                for y_offset in range(-r_search + 1, r_search):
                    check_y = preferred_start_tile_y + y_offset
                    if game_map.is_tile_walkable(check_x, check_y): found_tile_coords = (check_x, check_y); break
                if found_tile_coords: break
                # Right edge
                check_x = preferred_start_tile_x + r_search
                for y_offset in range(-r_search + 1, r_search):
                    check_y = preferred_start_tile_y + y_offset
                    if game_map.is_tile_walkable(check_x, check_y): found_tile_coords = (check_x, check_y); break
                if found_tile_coords: break 
            
        if found_tile_coords:
            start_tile_x, start_tile_y = found_tile_coords
            initial_player_world_x = (start_tile_x * game_map.tile_pixel_width) + (game_map.tile_pixel_width / 2)
            initial_player_world_y = (start_tile_y * game_map.tile_pixel_height) + (game_map.tile_pixel_height / 2)
            print(f"Player starting on walkable tile: ({start_tile_x}, {start_tile_y}) at world: ({initial_player_world_x:.1f}, {initial_player_world_y:.1f})")
        else:
            print(f"Warning: No walkable starting tile found near preferred. Using default map center.")
    else:
        print("Warning: Map grid invalid or collision grid missing. Player starting at default map center.")
    # --- End Player Starting Position Search ---

    player = Player(initial_player_world_x, initial_player_world_y)
    all_sprites_group = pygame.sprite.Group(player)

    destination_objects_list = []
    if not destinations_data:
        print("Warning: No destination data loaded. Game will have no interactive destinations.")
    for data in destinations_data:
        if data.get("world_x") is not None and data.get("world_y") is not None:
            dest = Destination(
                id=data["id"], name=data["name"],
                world_x=data["world_x"], world_y=data["world_y"],
                radius=data.get("radius", 30), # Defaulting to 30 if not specified
                info_text=data.get("info_text", "No information available.")
            )
            destination_objects_list.append(dest)
        else:
            print(f"Warning: Destination '{data.get('name', 'Unknown')}' in destinations_data.py skipped due to missing coordinates.")
    destinations_sprite_group = pygame.sprite.Group(destination_objects_list)
    
    objective_manager = ObjectiveManager(destination_objects_list)
    
    current_info_message = None
    info_message_timer = 0
    INFO_MESSAGE_DURATION = 5000 

    debug_draw_collision = False

    running = True
    while running:
        dt = clock.tick(60) / 1000.0 
        
        joystick_direction_input = pygame.math.Vector2(0, 0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS: game_map.zoom(ZOOM_SPEED_MULTIPLIER, player.rect.centerx, player.rect.centery)
                elif event.key == pygame.K_MINUS: game_map.zoom(1 / ZOOM_SPEED_MULTIPLIER, player.rect.centerx, player.rect.centery)
                elif event.key == pygame.K_c: debug_draw_collision = not debug_draw_collision
                elif event.key == pygame.K_n: 
                    if objective_manager.current_target_destination and not objective_manager.current_target_destination.visited:
                         objective_manager.current_target_destination.mark_visited()
                    objective_manager.set_next_objective()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 4: game_map.zoom(ZOOM_SPEED_MULTIPLIER, mouse_pos[0], mouse_pos[1])
                elif event.button == 5: game_map.zoom(1 / ZOOM_SPEED_MULTIPLIER, mouse_pos[0], mouse_pos[1])
            
            if event.type == pygame.JOYAXISMOTION:
                 if joysticks:
                    joy = joysticks[0]
                    dead_zone = 0.25
                    if event.axis == 0: # Horizontal
                        if abs(event.value) > dead_zone: joystick_direction_input.x = event.value
                        else: joystick_direction_input.x = 0 # Reset if in deadzone
                    elif event.axis == 1: # Vertical
                        if abs(event.value) > dead_zone: joystick_direction_input.y = event.value
                        else: joystick_direction_input.y = 0 # Reset if in deadzone
            # Add JOYHATMOTION for D-Pads if needed
            # elif event.type == pygame.JOYHATMOTION:
            #     if joysticks:
            #         joystick_direction_input.x, joystick_direction_input.y = event.value


        keys = pygame.key.get_pressed()
        keyboard_direction = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: keyboard_direction.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: keyboard_direction.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: keyboard_direction.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: keyboard_direction.y += 1
        
        if joystick_direction_input.length_squared() > 0:
            player.set_movement_direction(joystick_direction_input)
        else:
            player.set_movement_direction(keyboard_direction)

        player.update(dt, game_map) 
        
        for dest_sprite in destinations_sprite_group:
            dest_sprite.update_screen_position(game_map)

        target_dest = objective_manager.current_target_destination
        if target_dest and not target_dest.visited:
            dx = player.world_x - target_dest.world_x
            dy = player.world_y - target_dest.world_y
            player_effective_radius = player.width / 2 
            if (dx*dx + dy*dy) < (target_dest.radius + player_effective_radius)**2:
                target_dest.mark_visited()
                current_info_message = f"{target_dest.name}: {target_dest.info_text}"
                info_message_timer = pygame.time.get_ticks()
                objective_manager.set_next_objective()

        if current_info_message:
            if pygame.time.get_ticks() - info_message_timer > INFO_MESSAGE_DURATION:
                current_info_message = None
        
        game_map.offset_x = player.rect.centerx - (player.world_x * game_map.zoom_level)
        game_map.offset_y = player.rect.centery - (player.world_y * game_map.zoom_level)

        screen.fill(WHITE) 
        game_map.draw(debug_draw_collision) 
        destinations_sprite_group.draw(screen)
        all_sprites_group.draw(screen)
        
        obj_text_surface = ui_font.render(objective_manager.get_current_objective_text(), True, BLACK)
        screen.blit(obj_text_surface, (20, 20))

        if current_info_message:
            max_width = SCREEN_WIDTH - 40
            words = current_info_message.split(' ')
            lines = []
            current_line_text = ""
            for word in words:
                test_line_text = current_line_text + word + " "
                if info_font.size(test_line_text)[0] <= max_width:
                    current_line_text = test_line_text
                else:
                    lines.append(current_line_text)
                    current_line_text = word + " "
            lines.append(current_line_text)

            num_lines = len(lines)
            line_height = info_font.get_linesize()
            total_text_height = num_lines * line_height
            
            padding = 10
            info_bg_height = total_text_height + (2 * padding)
            info_bg_width = max_width + (2 * padding) if lines else 2 * padding # Ensure some width even if no text
            if lines: # Get width of longest line for better fitting background
                actual_text_max_width = 0
                for line_surf_text in lines:
                    line_width = info_font.size(line_surf_text.strip())[0]
                    if line_width > actual_text_max_width:
                        actual_text_max_width = line_width
                info_bg_width = actual_text_max_width + (2*padding)


            info_bg_rect = pygame.Rect(0,0, info_bg_width, info_bg_height)
            info_bg_rect.centerx = SCREEN_WIDTH / 2
            info_bg_rect.bottom = SCREEN_HEIGHT - 10
            
            pygame.draw.rect(screen, (230, 230, 230, 200), info_bg_rect) # Semi-transparent Light grey background
            pygame.draw.rect(screen, BLACK, info_bg_rect, 1) 

            for i, line_text in enumerate(lines):
                info_surface = info_font.render(line_text.strip(), True, BLACK)
                # Center each line of text within the background box
                info_text_render_rect = info_surface.get_rect(centerx=info_bg_rect.centerx, 
                                                              top=info_bg_rect.top + padding + i * line_height)
                screen.blit(info_surface, info_text_render_rect)
        
        pygame.display.flip()

    pygame.quit()
    if joysticks:
        pygame.joystick.quit()
    sys.exit()

if __name__ == "__main__":
    tiles_dir = "tiles"
    meta_file = os.path.join(tiles_dir, "map_meta.json")
    if not os.path.exists(meta_file):
        print(f"Error: Metadata file '{meta_file}' not found.")
        print(f"Please ensure your map data generation workflow is complete:")
        print(f"1. 'campus_map.png' is in the project directory.")
        print(f"2. Run 'python convert_map_to_tiles.py' (for visual tiles & basic meta).")
        print(f"3. Use Tiled to create collision layer & export e.g. 'tiled_campus_map.json'.")
        print(f"4. Run 'python tiled_importer.py' (updates meta with Tiled collision data).")
        sys.exit()
    else:
        try:
            with open(meta_file, 'r') as f:
                temp_meta = json.load(f) # Need import json here if this check is to work fully
                if not temp_meta.get("collision_grid_data") or \
                   (isinstance(temp_meta.get("collision_grid_data"), list) and not temp_meta.get("collision_grid_data")) or \
                   (isinstance(temp_meta.get("collision_grid_data"), list) and len(temp_meta.get("collision_grid_data")) > 0 and not temp_meta.get("collision_grid_data")[0]):
                    print(f"CRITICAL WARNING: 'collision_grid_data' in {meta_file} appears empty or improperly formatted.")
                    print(f"Ensure 'tiled_importer.py' ran successfully after Tiled setup.")
        except NameError: # Catches 'json' not defined if import json is missing at top of file
             print(f"Warning: Could not perform quick check of metadata file {meta_file} (json module not imported at top level).")
        except Exception as e:
            print(f"Warning: Could not quickly check metadata file {meta_file}: {e}")
        main()