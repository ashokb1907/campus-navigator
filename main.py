# main.py
import pygame
import sys
import os
import random
import json # For the metadata check in __main__

from map_class import Map
from destination_class import Destination 
from collectible_class import Collectible # Ensure this class handles riddle data

# --- IMPORT YOUR DATA FILES ---
try:
    from destinations_data import destinations_data
except ImportError:
    print("CRITICAL ERROR: destinations_data.py not found!")
    destinations_data = [] 
try:
    from collectibles_data import collectibles_data 
except ImportError:
    print("WARNING: collectibles_data.py not found! No collectibles will be loaded.")
    collectibles_data = []

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
REFERENCE_TILE_SIZE = 32 
ZOOM_SPEED_MULTIPLIER = 1.1
NUM_COLLECTIBLES_PER_SESSION = 3 
GAME_DURATION_SECONDS = 300 # 5 minutes, adjust as needed

# --- Colors ---
WHITE = (255, 255, 255)
BLUE = (0, 0, 255) 
BLACK = (0, 0, 0) 
RED = (255,0,0) 
GREEN = (0, 255, 0)
GREY = (200, 200, 200)
DARK_GREY = (100, 100, 100)
UI_TEXT_COLOR = (10, 10, 10)
UI_BG_COLOR = (230, 230, 230, 220) # RGBA for semi-transparency
RIDDLE_OPTION_COLOR = (70, 70, 170) 
RIDDLE_OPTION_HOVER_COLOR = (120, 120, 220) 

# --- Game States ---
GAME_STATE_MENU = "menu"
GAME_STATE_CONTROLS_DISPLAY = "controls_display"
GAME_STATE_PLAYING = "playing"
GAME_STATE_RIDDLE = "riddle"
GAME_STATE_INFO_DISPLAY = "info_display"
GAME_STATE_SESSION_COMPLETE = "session_complete" 
GAME_STATE_TIME_UP = "time_up"                 

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, initial_world_x, initial_world_y, width=20, height=20):
        super().__init__()
        self.width = width; self.height = height
        self.image = pygame.Surface([self.width, self.height]); self.image.fill(BLUE); self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.world_x = float(initial_world_x); self.world_y = float(initial_world_y)
        self.speed = 150; self.direction = pygame.math.Vector2(0, 0)
    def update(self, dt, game_map):
        if self.direction.length_squared() == 0: return
        try: normalized_direction = self.direction.normalize()
        except ValueError: normalized_direction = pygame.math.Vector2(0,0)
        delta_x = normalized_direction.x * self.speed * dt; delta_y = normalized_direction.y * self.speed * dt
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
        else: self.world_x = new_world_x_center
        new_world_y_center = self.world_y + delta_y
        potential_player_rect_y = pygame.Rect(self.world_x - self.width/2, new_world_y_center - self.height/2, self.width, self.height)
        if delta_y != 0:
            corners_to_check_y = [potential_player_rect_y.bottomleft, potential_player_rect_y.bottomright] if delta_y > 0 else [potential_player_rect_y.topleft, potential_player_rect_y.topright]
            for corner_x_coord, corner_y_coord in corners_to_check_y:
                if game_map.tile_pixel_height == 0: continue 
                tile_cx = int(corner_x_coord / game_map.tile_pixel_width); tile_cy = int(corner_y_coord / game_map.tile_pixel_height)
                if not game_map.is_tile_walkable(tile_cx, tile_cy):
                    if delta_y > 0: new_world_y_center = (tile_cy * game_map.tile_pixel_height) - (self.height / 2) - 0.01
                    elif delta_y < 0: new_world_y_center = ((tile_cy + 1) * game_map.tile_pixel_height) + (self.height / 2) + 0.01
                    break
            self.world_y = new_world_y_center
        else: self.world_y = new_world_y_center
        half_w, half_h = self.width/2, self.height/2
        if game_map.full_map_pixel_width > 0: self.world_x = max(half_w, min(self.world_x, game_map.full_map_pixel_width - half_w))
        if game_map.full_map_pixel_height > 0: self.world_y = max(half_h, min(self.world_y, game_map.full_map_pixel_height - half_h))
        self.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    def set_movement_direction(self, input_direction_vector): self.direction = input_direction_vector

# --- Objective Manager ---
class ObjectiveManager:
    NUM_OBJECTIVES_TO_COMPLETE = 5
    def __init__(self, all_destination_objects_list):
        self.full_destination_pool = [d for d in all_destination_objects_list if d.world_x is not None and d.world_y is not None]
        self.game_objectives = []; self.current_objective_idx_in_game_list = -1; self.current_target_destination = None
        self.reset() 

    def reset(self): 
        for dest in self.full_destination_pool: 
            dest.visited = False
            dest.set_active_target(False)
        self.current_objective_idx_in_game_list = -1
        self.current_target_destination = None
        self._select_random_objectives()
        self.set_next_objective()

    def _select_random_objectives(self):
        if not self.full_destination_pool: self.game_objectives = []; return
        available_to_pick = list(self.full_destination_pool); random.shuffle(available_to_pick)
        num_to_select = min(len(available_to_pick), self.NUM_OBJECTIVES_TO_COMPLETE)
        self.game_objectives = available_to_pick[:num_to_select]
        if self.game_objectives: print(f"Selected {len(self.game_objectives)} main objectives:"); [print(f"  {i+1}. {d.name}") for i,d in enumerate(self.game_objectives)]
        else: print("Warning: Could not select main objectives.")

    def set_next_objective(self):
        if self.current_target_destination: self.current_target_destination.set_active_target(False)
        self.current_objective_idx_in_game_list +=1
        if self.current_objective_idx_in_game_list < len(self.game_objectives):
            self.current_target_destination = self.game_objectives[self.current_objective_idx_in_game_list]
            if not self.current_target_destination.visited: 
                 self.current_target_destination.set_active_target(True); print(f"New Main Objective: Go to {self.current_target_destination.name}"); return True
            else: return self.set_next_objective()
        else: self.current_target_destination = None; print("All main session objectives visited!"); return False
    def get_current_objective_text(self):
        if self.current_target_destination: return f"Find ({self.current_objective_idx_in_game_list + 1}/{len(self.game_objectives)}): {self.current_target_destination.name}"
        elif self.all_session_objectives_visited(): return "Main Objectives Complete!"
        elif not self.game_objectives: return "No main objectives set."
        return "Welcome! Starting campus tour..."
    def all_session_objectives_visited(self):
        if not self.game_objectives: return True 
        return all(d.visited for d in self.game_objectives)

# --- Main Function ---
def main():
    # --- Variables local to main() that will be modified by the nested function ---
    game_map_obj = None 
    player_obj = None
    all_sprites = None # Group for player
    dest_obj_list = [] # List of Destination objects
    dest_sprites = None # Sprite group for destinations
    obj_manager = None # ObjectiveManager instance
    
    full_collectible_pool_list = [] # Master list of all Collectible objects
    active_collectible_list_session = [] 
    collectible_sprites = None # Sprite group for active collectibles

    score = 0
    time_left = GAME_DURATION_SECONDS # This is initialized here for the first time
    
    active_info_msg = None
    active_info_msg_timer = 0 # Initialized here
    INFO_MESSAGE_DURATION = 3500 # Defined here as per previous fix
    
    current_riddle_item = None 
    current_riddle_opt_rects = [] 

    current_menu_opt_rects = []
    current_selected_menu_opt = 0
    
    game_flow_state = GAME_STATE_MENU 

    # --- Pygame and Display Setup ---
    pygame.init()
    pygame.joystick.init()
    active_joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
    if active_joystick: print(f"Controller: {active_joystick.get_name()}")
    else: print("No controller. Using keyboard.")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Aston Campus Navigator")
    clock = pygame.time.Clock()
    
    try:
        ui_font = pygame.font.Font(None, 36)
        menu_title_font = pygame.font.Font(None, 48)
        riddle_font = pygame.font.Font(None, 30)
        option_font = pygame.font.Font(None, 28)
        info_font = pygame.font.Font(None, 28)
    except pygame.error: 
        ui_font = pygame.font.SysFont("arial", 30); menu_title_font = pygame.font.SysFont("arial", 40)
        riddle_font = pygame.font.SysFont("arial", 28); option_font = pygame.font.SysFont("arial", 26)
        info_font = pygame.font.SysFont("arial", 24)

    menu_options_texts = ["Start New Game", "Controls", "Quit"] 
    controls_display_texts = [
        "Campus Navigator Controls:", "", "Move: Arrow Keys / WASD / Joystick Left Stick",
        "Zoom: +/- Keys / Mouse Wheel", "Answer Riddle (Keyboard): 1, 2, 3, 4",
        "Answer Riddle (Mouse): Click Option", "Debug Skip Objective: N", 
        "Debug Toggle Collision: C", "Dismiss Info / To Menu: Mouse Click or ESC"
    ]
    debug_draw_collision_flag = False # Initialized here

    def initialize_new_game_session():
        nonlocal game_map_obj, player_obj, all_sprites, dest_obj_list, dest_sprites
        nonlocal obj_manager, active_collectible_list_session, collectible_sprites
        nonlocal score, time_left, active_info_msg, active_info_msg_timer, current_riddle_item
        nonlocal game_flow_state, full_collectible_pool_list # Ensure full_collectible_pool_list is nonlocal
        nonlocal debug_draw_collision_flag # if it needs to be reset by this function

        print("\n--- Initializing New Game Session ---")
        debug_draw_collision_flag = False # Default debug view for new game
        game_map_obj = Map(screen, "tiles")
        if not game_map_obj.is_loaded_successfully(): pygame.quit(); sys.exit()

        temp_initial_player_world_x = game_map_obj.full_map_pixel_width / 2
        temp_initial_player_world_y = game_map_obj.full_map_pixel_height / 2
        if game_map_obj.grid_width_in_tiles > 0 and game_map_obj.grid_height_in_tiles > 0 and \
           game_map_obj.collision_grid and len(game_map_obj.collision_grid) > 0:
            preferred_start_tile_x = game_map_obj.grid_width_in_tiles - 1 
            preferred_start_tile_y = 0 
            found_tile_coords = None
            max_search_radius = max(game_map_obj.grid_width_in_tiles, game_map_obj.grid_height_in_tiles) 
            if game_map_obj.is_tile_walkable(preferred_start_tile_x, preferred_start_tile_y):
                found_tile_coords = (preferred_start_tile_x, preferred_start_tile_y)
            else:
                for r_search in range(1, max_search_radius):
                    for i in range(-r_search, r_search + 1): 
                        if game_map_obj.is_tile_walkable(preferred_start_tile_x + i, preferred_start_tile_y - r_search): found_tile_coords = (preferred_start_tile_x + i, preferred_start_tile_y - r_search); break
                        if game_map_obj.is_tile_walkable(preferred_start_tile_x + i, preferred_start_tile_y + r_search): found_tile_coords = (preferred_start_tile_x + i, preferred_start_tile_y + r_search); break
                    if found_tile_coords: break
                    for i in range(-r_search + 1, r_search):
                        if game_map_obj.is_tile_walkable(preferred_start_tile_x - r_search, preferred_start_tile_y + i): found_tile_coords = (preferred_start_tile_x - r_search, preferred_start_tile_y + i); break
                        if game_map_obj.is_tile_walkable(preferred_start_tile_x + r_search, preferred_start_tile_y + i): found_tile_coords = (preferred_start_tile_x + r_search, preferred_start_tile_y + i); break
                    if found_tile_coords: break 
            if found_tile_coords:
                start_tile_x, start_tile_y = found_tile_coords
                temp_initial_player_world_x = (start_tile_x * game_map_obj.tile_pixel_width) + (game_map_obj.tile_pixel_width / 2)
                temp_initial_player_world_y = (start_tile_y * game_map_obj.tile_pixel_height) + (game_map_obj.tile_pixel_height / 2)
        
        player_obj = Player(temp_initial_player_world_x, temp_initial_player_world_y)
        all_sprites = pygame.sprite.Group(player_obj)

        dest_obj_list.clear() 
        for data in destinations_data:
            if data.get("world_x") is not None and data.get("world_y") is not None:
                dest = Destination(id=data["id"], name=data["name"], world_x=data["world_x"], world_y=data["world_y"],
                                   radius=data.get("radius", 30), info_text=data.get("info_text", ""))
                dest_obj_list.append(dest)
        dest_sprites = pygame.sprite.Group(dest_obj_list)
        
        obj_manager = ObjectiveManager(dest_obj_list) # This will call its own reset and _select_random_objectives
        
        if not full_collectible_pool_list: 
            for data in collectibles_data: 
                if data.get("world_x") is not None and data.get("world_y") is not None:
                    item = Collectible(
                        id=data.get("id"), name=data.get("name"), world_x=data["world_x"], world_y=data["world_y"],
                        image_path=data.get("image_path"), info_text=data.get("info_text"), 
                        points_value=data.get("points_value"),
                        riddle_text=data.get("riddle_text", "Riddle?"), 
                        riddle_options=data.get("riddle_options", ["A","B","C","D"]),
                        correct_option_index=data.get("correct_option_index", 0)
                    )
                    full_collectible_pool_list.append(item)
        
        for item in full_collectible_pool_list: 
            item.collected = False 
            # Add item back to a general pool if it was killed, so it can be re-selected.
            # The Collectible class's mark_collected calls self.kill().
            # For re-selection, we need to ensure sprites are "revived" or re-instantiated for the active list.
            # The current logic re-creates active_collectible_list_session from full_collectible_pool_list,
            # so we just need to ensure the objects in full_collectible_pool_list are usable.
            # If self.kill() removes them from ALL groups and somehow makes them unusable for re-adding,
            # it might be better for mark_collected to just set a flag and visual, and main loop handles removal from active group.
            # For now, assuming Collectible objects in full_collectible_pool_list are fine.

        active_collectible_list_session.clear()
        if full_collectible_pool_list:
            temp_pool = list(full_collectible_pool_list) 
            random.shuffle(temp_pool)
            num_to_activate = min(len(temp_pool), NUM_COLLECTIBLES_PER_SESSION)
            active_collectible_list_session = temp_pool[:num_to_activate]
            print(f"Activated {len(active_collectible_list_session)} collectibles for new session.")
        collectible_sprites = pygame.sprite.Group(active_collectible_list_session) 
        
        score = 0; time_left = GAME_DURATION_SECONDS
        active_info_msg = None; active_info_msg_timer = 0
        current_riddle_item = None 
        current_riddle_opt_rects.clear()
        game_flow_state = GAME_STATE_PLAYING
    # --- End of initialize_new_game_session ---

    running = True
    while running:
        dt = clock.tick(60) / 1000.0 
        mouse_pos = pygame.mouse.get_pos()
        joystick_direction_input = pygame.math.Vector2(0, 0)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

            if game_flow_state == GAME_STATE_MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: current_selected_menu_opt = (current_selected_menu_opt - 1) % len(menu_options_texts)
                    elif event.key == pygame.K_DOWN: current_selected_menu_opt = (current_selected_menu_opt + 1) % len(menu_options_texts)
                    elif event.key == pygame.K_RETURN:
                        if menu_options_texts[current_selected_menu_opt] == "Start New Game": initialize_new_game_session()
                        elif menu_options_texts[current_selected_menu_opt] == "Controls": game_flow_state = GAME_STATE_CONTROLS_DISPLAY
                        elif menu_options_texts[current_selected_menu_opt] == "Quit": running = False
                    elif event.key == pygame.K_ESCAPE: running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                     for i, rect in enumerate(current_menu_opt_rects):
                        if rect.collidepoint(mouse_pos):
                            current_selected_menu_opt = i
                            if menu_options_texts[current_selected_menu_opt] == "Start New Game": initialize_new_game_session()
                            elif menu_options_texts[current_selected_menu_opt] == "Controls": game_flow_state = GAME_STATE_CONTROLS_DISPLAY
                            elif menu_options_texts[current_selected_menu_opt] == "Quit": running = False
                            break
            
            elif game_flow_state == GAME_STATE_CONTROLS_DISPLAY:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN: game_flow_state = GAME_STATE_MENU
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: game_flow_state = GAME_STATE_MENU

            elif game_flow_state == GAME_STATE_RIDDLE:
                if event.type == pygame.KEYDOWN:
                    chosen_idx = -1
                    if event.key == pygame.K_1: chosen_idx = 0
                    elif event.key == pygame.K_2: chosen_idx = 1
                    elif event.key == pygame.K_3: chosen_idx = 2
                    elif event.key == pygame.K_4: chosen_idx = 3
                    
                    if chosen_idx != -1 and current_riddle_item:
                        if chosen_idx == current_riddle_item.correct_option_index:
                            score += current_riddle_item.points_value; active_info_msg = f"Correct! Info: {current_riddle_item.info_text}"; current_riddle_item.mark_collected() 
                        else: active_info_msg = "Incorrect. The item remains."
                        current_riddle_item = None; active_info_msg_timer = pygame.time.get_ticks(); game_flow_state = GAME_STATE_INFO_DISPLAY
                    elif event.key == pygame.K_ESCAPE: current_riddle_item = None; game_flow_state = GAME_STATE_PLAYING
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if current_riddle_item:
                        for i, rect in enumerate(current_riddle_opt_rects):
                            if rect.collidepoint(mouse_pos):
                                if i == current_riddle_item.correct_option_index:
                                    score += current_riddle_item.points_value; active_info_msg = f"Correct! Info: {current_riddle_item.info_text}"; current_riddle_item.mark_collected()
                                else: active_info_msg = "Incorrect. The item remains."
                                current_riddle_item = None; active_info_msg_timer = pygame.time.get_ticks(); game_flow_state = GAME_STATE_INFO_DISPLAY; break
            
            elif game_flow_state in [GAME_STATE_PLAYING, GAME_STATE_INFO_DISPLAY, GAME_STATE_SESSION_COMPLETE, GAME_STATE_TIME_UP]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: game_flow_state = GAME_STATE_MENU
                    elif (event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS) and game_map_obj and player_obj : game_map_obj.zoom(ZOOM_SPEED_MULTIPLIER, player_obj.rect.centerx, player_obj.rect.centery)
                    elif event.key == pygame.K_MINUS and game_map_obj and player_obj: game_map_obj.zoom(1 / ZOOM_SPEED_MULTIPLIER, player_obj.rect.centerx, player_obj.rect.centery)
                    elif event.key == pygame.K_c: debug_draw_collision_flag = not debug_draw_collision_flag
                    elif event.key == pygame.K_n and game_flow_state == GAME_STATE_PLAYING and obj_manager: 
                        if obj_manager.current_target_destination and not obj_manager.current_target_destination.visited:
                             obj_manager.current_target_destination.mark_visited(); score += 25 
                        all_main_obj_done_before_skip = obj_manager.all_session_objectives_visited()
                        obj_manager.set_next_objective()
                        if obj_manager.all_session_objectives_visited() and not all_main_obj_done_before_skip:
                            game_flow_state = GAME_STATE_SESSION_COMPLETE; active_info_msg = "Main objectives complete! Explore."; active_info_msg_timer = pygame.time.get_ticks()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if game_flow_state in [GAME_STATE_INFO_DISPLAY, GAME_STATE_SESSION_COMPLETE, GAME_STATE_TIME_UP]: 
                        active_info_msg = None 
                        if game_flow_state == GAME_STATE_INFO_DISPLAY: game_flow_state = GAME_STATE_PLAYING
                        elif game_flow_state in [GAME_STATE_SESSION_COMPLETE, GAME_STATE_TIME_UP]: game_flow_state = GAME_STATE_MENU
                elif event.type == pygame.MOUSEBUTTONDOWN and game_map_obj: 
                    if event.button == 4: game_map_obj.zoom(ZOOM_SPEED_MULTIPLIER, mouse_pos[0], mouse_pos[1])
                    elif event.button == 5: game_map_obj.zoom(1 / ZOOM_SPEED_MULTIPLIER, mouse_pos[0], mouse_pos[1])
                if event.type == pygame.JOYAXISMOTION and active_joystick:
                    dead_zone = 0.25
                    if event.axis == 0: joystick_direction_input.x = event.value if abs(event.value) > dead_zone else 0
                    elif event.axis == 1: joystick_direction_input.y = event.value if abs(event.value) > dead_zone else 0
        
        if game_flow_state == GAME_STATE_PLAYING or game_flow_state == GAME_STATE_INFO_DISPLAY :
            keys = pygame.key.get_pressed(); keyboard_direction = pygame.math.Vector2(0,0)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: keyboard_direction.x -=1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: keyboard_direction.x +=1
            if keys[pygame.K_UP] or keys[pygame.K_w]: keyboard_direction.y -=1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: keyboard_direction.y +=1
            if joystick_direction_input.length_squared() > 0 and player_obj: player_obj.set_movement_direction(joystick_direction_input)
            elif player_obj: player_obj.set_movement_direction(keyboard_direction)

        if game_flow_state not in [GAME_STATE_RIDDLE, GAME_STATE_MENU, GAME_STATE_CONTROLS_DISPLAY] :
            if player_obj: player_obj.update(dt, game_map_obj) 
            if dest_sprites:
                for dest_sprite in dest_sprites: dest_sprite.update_screen_position(game_map_obj)
            if collectible_sprites:
                for item_sprite in collectible_sprites: item_sprite.update_screen_position(game_map_obj)

            if game_flow_state == GAME_STATE_PLAYING :
                if time_left > 0:
                    time_left -= dt
                    if time_left <= 0:
                        time_left = 0; game_flow_state = GAME_STATE_TIME_UP
                        active_info_msg = f"Time's Up! Final Score: {score}"; active_info_msg_timer = pygame.time.get_ticks()
                
                if obj_manager:
                    target_dest = obj_manager.current_target_destination
                    if target_dest and not target_dest.visited:
                        dx = player_obj.world_x - target_dest.world_x; dy = player_obj.world_y - target_dest.world_y
                        player_eff_radius = player_obj.width / 2 
                        if (dx*dx + dy*dy) < (target_dest.radius + player_eff_radius)**2:
                            target_dest.mark_visited(); active_info_msg = f"Reached: {target_dest.name}\n{target_dest.info_text}"
                            active_info_msg_timer = pygame.time.get_ticks(); game_flow_state = GAME_STATE_INFO_DISPLAY
                            score += 50 
                            all_main_obj_done_before_next = obj_manager.all_session_objectives_visited()
                            obj_manager.set_next_objective()
                            if obj_manager.all_session_objectives_visited() and not all_main_obj_done_before_next:
                                game_flow_state = GAME_STATE_SESSION_COMPLETE 
                                active_info_msg = "Main objectives complete! You can still explore."; active_info_msg_timer = pygame.time.get_ticks()
                
                if game_flow_state == GAME_STATE_PLAYING and collectible_sprites: # Check state again
                    for item in collectible_sprites: 
                        if player_obj and not item.collected and player_obj.rect.colliderect(item.rect): 
                            dist_x = player_obj.world_x - item.world_x; dist_y = player_obj.world_y - item.world_y
                            item_eff_radius = item.default_size[0] / 2; player_eff_radius_for_item = player_obj.width / 2
                            if (dist_x**2 + dist_y**2) < (item_eff_radius + player_eff_radius_for_item)**2:
                                current_riddle_item = item; game_flow_state = GAME_STATE_RIDDLE; break 
            
            if game_flow_state == GAME_STATE_INFO_DISPLAY:
                if pygame.time.get_ticks() - active_info_msg_timer > INFO_MESSAGE_DURATION and active_info_msg is not None:
                    active_info_msg = None
                    if obj_manager and obj_manager.all_session_objectives_visited() and not current_riddle_item:
                         game_flow_state = GAME_STATE_SESSION_COMPLETE
                    else: game_flow_state = GAME_STATE_PLAYING
        
        elif game_flow_state == GAME_STATE_RIDDLE and player_obj:
            player_obj.set_movement_direction(pygame.math.Vector2(0,0))

        if game_map_obj and player_obj and game_map_obj.zoom_level > 0:
            game_map_obj.offset_x = player_obj.rect.centerx - (player_obj.world_x * game_map_obj.zoom_level)
            game_map_obj.offset_y = player_obj.rect.centery - (player_obj.world_y * game_map_obj.zoom_level)

        screen.fill(WHITE) 
        if game_flow_state == GAME_STATE_MENU:
            title_text_surf = menu_title_font.render("Campus Navigator Challenge", True, BLACK)
            screen.blit(title_text_surf, title_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5)))
            current_menu_opt_rects.clear()
            option_y_start = SCREEN_HEIGHT // 2 - 70
            for i, option_text in enumerate(menu_options_texts):
                color = RIDDLE_OPTION_HOVER_COLOR if i == current_selected_menu_opt else RIDDLE_OPTION_COLOR
                text_surf = ui_font.render(option_text, True, WHITE)
                button_rect = pygame.Rect(0, 0, max(250, text_surf.get_width() + 60), text_surf.get_height() + 20) # Ensure min width
                button_rect.center = (SCREEN_WIDTH // 2, option_y_start + i * 70)
                pygame.draw.rect(screen, color, button_rect, border_radius=10)
                screen.blit(text_surf, text_surf.get_rect(center=button_rect.center))
                current_menu_opt_rects.append(button_rect)
        elif game_flow_state == GAME_STATE_CONTROLS_DISPLAY:
            screen.fill(GREY); control_title_surf = ui_font.render("Controls", True, BLACK)
            screen.blit(control_title_surf, control_title_surf.get_rect(centerx=SCREEN_WIDTH/2, top=50))
            line_y = 120
            for line in controls_display_texts:
                line_surf = info_font.render(line, True, BLACK)
                screen.blit(line_surf, (50, line_y)); line_y += info_font.get_linesize() + 5
            dismiss_surf = option_font.render("Click or Press ESC/Enter to Return to Menu", True, DARK_GREY)
            screen.blit(dismiss_surf, dismiss_surf.get_rect(centerx=SCREEN_WIDTH/2, bottom=SCREEN_HEIGHT-30))
        elif game_flow_state in [GAME_STATE_PLAYING, GAME_STATE_RIDDLE, GAME_STATE_INFO_DISPLAY, GAME_STATE_SESSION_COMPLETE, GAME_STATE_TIME_UP]:
            if game_map_obj: game_map_obj.draw(debug_draw_collision_flag) 
            if dest_sprites: dest_sprites.draw(screen)
            if collectible_sprites: collectible_sprites.draw(screen) 
            if all_sprites: all_sprites.draw(screen)
            if obj_manager:
                obj_text_surface = ui_font.render(obj_manager.get_current_objective_text(), True, UI_TEXT_COLOR)
                screen.blit(obj_text_surface, (20, 20))
            
            score_text_surface = ui_font.render(f"Score: {score}", True, UI_TEXT_COLOR)
            score_rect_val = score_text_surface.get_rect(topright=(SCREEN_WIDTH - 20, 20)) # Used for timer pos
            screen.blit(score_text_surface, score_rect_val)
            
            minutes = int(time_left) // 60; seconds = int(time_left) % 60
            timer_text_str = f"Time: {minutes:02d}:{seconds:02d}"
            if game_flow_state == GAME_STATE_TIME_UP: timer_text_str = "Time's Up!"
            elif time_left <=0 : timer_text_str = "Time: 00:00"
            timer_color = RED if time_left <= 10 and game_flow_state == GAME_STATE_PLAYING else UI_TEXT_COLOR
            timer_surface = ui_font.render(timer_text_str, True, timer_color)
            timer_padding_below_score = 5 
            timer_rect = timer_surface.get_rect(topright=(score_rect_val.right, score_rect_val.bottom + timer_padding_below_score))
            screen.blit(timer_surface, timer_rect)

            if game_flow_state == GAME_STATE_RIDDLE and current_riddle_item:
                current_riddle_opt_rects.clear(); box_width, box_height = SCREEN_WIDTH*0.85, SCREEN_HEIGHT*0.75
                box_x,box_y = (SCREEN_WIDTH-box_width)/2, (SCREEN_HEIGHT-box_height)/2; riddle_box_rect = pygame.Rect(box_x,box_y,box_width,box_height)
                riddle_bg_surface = pygame.Surface(riddle_box_rect.size, pygame.SRCALPHA); riddle_bg_surface.fill(UI_BG_COLOR)
                screen.blit(riddle_bg_surface, riddle_box_rect.topleft); pygame.draw.rect(screen,BLACK,riddle_box_rect,2)
                riddle_padding=25; max_riddle_width = box_width - 2*riddle_padding; riddle_words = current_riddle_item.riddle_text.split(' '); riddle_lines=[]
                current_line = ""; line_y_pos = box_y + riddle_padding
                for word in riddle_words:
                    test_line = current_line + word + " "
                    if riddle_font.size(test_line)[0] <= max_riddle_width: current_line = test_line
                    else: riddle_lines.append(current_line); current_line = word + " "
                riddle_lines.append(current_line)
                for line_idx, line_text_content in enumerate(riddle_lines):
                    riddle_surf = riddle_font.render(line_text_content.strip(), True, UI_TEXT_COLOR)
                    text_rect = riddle_surf.get_rect(centerx=riddle_box_rect.centerx, top=line_y_pos + (line_idx * riddle_font.get_linesize()))
                    screen.blit(riddle_surf, text_rect)
                line_y_pos += len(riddle_lines)*riddle_font.get_linesize() + 20
                option_visual_height = option_font.get_linesize() + 15; option_spacing = 10
                for i, option_text_content in enumerate(current_riddle_item.riddle_options):
                    option_box_y = line_y_pos + i * (option_visual_height + option_spacing)
                    option_box = pygame.Rect(box_x+riddle_padding, option_box_y, max_riddle_width, option_visual_height)
                    current_riddle_opt_rects.append(option_box)
                    current_opt_color = RIDDLE_OPTION_HOVER_COLOR if option_box.collidepoint(mouse_pos) else RIDDLE_OPTION_COLOR
                    pygame.draw.rect(screen, current_opt_color, option_box, border_radius=5)
                    pygame.draw.rect(screen, DARK_GREY, option_box, 1, border_radius=5)
                    display_option_text = f"{i+1}. {option_text_content}"
                    opt_words = display_option_text.split(' '); opt_lines = []; current_opt_line = ""; opt_padding_x = 10
                    max_opt_text_width = max_riddle_width - 2 * opt_padding_x
                    for opt_word in opt_words:
                        test_opt_line = current_opt_line + opt_word + " "
                        if option_font.size(test_opt_line)[0] <= max_opt_text_width: current_opt_line = test_opt_line
                        else: opt_lines.append(current_opt_line); current_opt_line = opt_word + " "
                    opt_lines.append(current_opt_line)
                    opt_line_y_start = option_box.centery - (len(opt_lines) * option_font.get_linesize()) / 2
                    for line_idx, opt_line_text in enumerate(opt_lines):
                        option_surf = option_font.render(opt_line_text.strip(), True, WHITE)
                        opt_render_rect = option_surf.get_rect(left=option_box.left + opt_padding_x, top=opt_line_y_start + line_idx * option_font.get_linesize())
                        screen.blit(option_surf, opt_render_rect)
            
            elif (game_flow_state == GAME_STATE_INFO_DISPLAY or \
                  game_flow_state == GAME_STATE_SESSION_COMPLETE or \
                  game_flow_state == GAME_STATE_TIME_UP) and active_info_msg:
                max_width = SCREEN_WIDTH - 60; words = active_info_msg.split(' '); lines = []
                current_line_text = ""; line_height = info_font.get_linesize()
                for word in words:
                    if word == '\n': lines.append(current_line_text.strip()); current_line_text = ""; continue
                    test_line_text = current_line_text + word + " "
                    if info_font.size(test_line_text)[0] <= max_width: current_line_text = test_line_text
                    else: lines.append(current_line_text.strip()); current_line_text = word + " "
                lines.append(current_line_text.strip())
                num_lines = len(lines); total_text_height = num_lines * line_height; padding = 15
                info_bg_height = total_text_height + (2 * padding); actual_text_max_width = 0
                if lines:
                    for line_surf_text in lines:
                        line_width = info_font.size(line_surf_text)[0]
                        if line_width > actual_text_max_width: actual_text_max_width = line_width
                info_bg_width = min(actual_text_max_width + (2*padding), SCREEN_WIDTH - 20) if actual_text_max_width > 0 else SCREEN_WIDTH * 0.7
                info_bg_rect = pygame.Rect(0,0, info_bg_width, info_bg_height)
                info_bg_rect.centerx = SCREEN_WIDTH / 2; info_bg_rect.bottom = SCREEN_HEIGHT - 20
                info_bg_surface = pygame.Surface(info_bg_rect.size, pygame.SRCALPHA); info_bg_surface.fill(UI_BG_COLOR)
                screen.blit(info_bg_surface, info_bg_rect.topleft)
                pygame.draw.rect(screen, BLACK, info_bg_rect, 1, border_radius=5) 
                for i, line_text in enumerate(lines):
                    if line_text: 
                        info_surface = info_font.render(line_text, True, UI_TEXT_COLOR)
                        screen.blit(info_surface, info_surface.get_rect(centerx=info_bg_rect.centerx, top=info_bg_rect.top + padding + i * line_height))
        
        pygame.display.flip()

    pygame.quit()
    if active_joystick: pygame.joystick.quit()
    sys.exit()

if __name__ == "__main__":
    tiles_dir = "tiles"
    meta_file = os.path.join(tiles_dir, "map_meta.json")
    if not os.path.exists(meta_file):
        print(f"Error: Metadata file '{meta_file}' not found. Please run data generation workflow.")
        sys.exit()
    else:
        try:
            with open(meta_file, 'r') as f:
                temp_meta = json.load(f) 
                if not temp_meta.get("collision_grid_data") or \
                   (isinstance(temp_meta.get("collision_grid_data"), list) and not temp_meta.get("collision_grid_data")) or \
                   (isinstance(temp_meta.get("collision_grid_data"), list) and len(temp_meta.get("collision_grid_data")) > 0 and not temp_meta.get("collision_grid_data")[0]):
                    print(f"CRITICAL WARNING: 'collision_grid_data' in {meta_file} appears problematic.")
        except Exception as e:
            print(f"Warning: Could not quickly check metadata file {meta_file}: {e}")
    main()