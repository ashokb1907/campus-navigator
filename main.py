# main.py
import pygame
import sys
import os
import random
import json

# Import classes and settings from separate files
from settings import * # Imports all constants and game state strings
from map_class import Map
from destination_class import Destination 
from collectible_class import Collectible 
from player_class import Player 
from objective_manager_class import ObjectiveManager 
# At the top of main.py
# ... other imports ...
try:
    from destinations_data import destinations_data
    print(f"DEBUG: main.py - destinations_data imported, length: {len(destinations_data)}")
except ImportError:
    print("CRITICAL ERROR: main.py - destinations_data.py not found or failed to import! Using empty list.")
    destinations_data = [] 
try:
    from collectibles_data import collectibles_data 
    print(f"DEBUG: main.py - collectibles_data imported, length: {len(collectibles_data)}")
except ImportError:
    print("WARNING: main.py - collectibles_data.py not found! No collectibles. Using empty list.")
    collectibles_data = []
# ...
# --- Leaderboard Functions ---
def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE): return []
    try:
        with open(LEADERBOARD_FILE, 'r') as f: return json.load(f)
    except (json.JSONDecodeError, IOError): 
        print(f"Warning: Corrupt or unreadable leaderboard: {LEADERBOARD_FILE}. Returning empty.")
        return []

def save_leaderboard(leaderboard_data):
    try:
        with open(LEADERBOARD_FILE, 'w') as f: json.dump(leaderboard_data, f, indent=4)
    except IOError: print(f"Error: Could not save leaderboard to '{LEADERBOARD_FILE}'.")

def add_score_to_leaderboard(player_name, score, leaderboard_data):
    if not player_name: player_name = "Anonymous" # Default name
    leaderboard_data.append({"name": player_name, "score": score})
    leaderboard_data.sort(key=lambda x: x["score"], reverse=True)
    return leaderboard_data[:MAX_LEADERBOARD_ENTRIES]

# main.py
# (Make sure all your imports are at the TOP of this file, especially from settings)
# Example:
# import pygame, sys, os, random, json
# from settings import *
# from map_class import Map
# from destination_class import Destination
# from collectible_class import Collectible
# from player_class import Player
# from objective_manager_class import ObjectiveManager
# try:
#     from destinations_data import destinations_data
# except ImportError: destinations_data = []
# try:
#     from collectibles_data import collectibles_data
# except ImportError: collectibles_data = []

# ... (Leaderboard functions should be defined here, before main_game_loop) ...

def main_game_loop():
    # --- Ensure all these are initialized before the main loop ---
    # Game-wide state variables
    game_flow_state = GAME_STATE_MENU  # <<< INITIALIZE HERE
    active_joystick = None
    screen = None # Initialized after pygame.init()
    is_fullscreen = IS_FULLSCREEN_DEFAULT 
    current_player_name = "Player" 
    player_sprite_paths_list = get_player_sprite_paths()
    selected_player_sprite_idx = 0 
    player_name_input_active = False 
    leaderboard_entries = load_leaderboard()
    
    # Session-specific variables (will be reset)
    game_map_obj = None; player_obj = None; all_sprites = None 
    dest_obj_list = []; dest_sprites = None; obj_manager = None
    full_collectible_pool_obj_list = [] 
    active_collectible_list_session = []; collectible_sprites = None
    score = 0; time_left = GAME_DURATION_SECONDS
    active_info_msg = None; active_info_msg_timer = 0; # INFO_MESSAGE_DURATION is from settings
    current_riddle_item = None; current_riddle_opt_rects = []
    debug_draw_collision_flag = False
    current_selected_menu_opt = 0
    menu_option_display_rects = [] 
    player_setup_input_box_rect_ui = None 
    player_setup_sprite_arrow_rects_ui = {} 
    player_setup_confirm_button_rect_ui = None 

    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        active_joystick = pygame.joystick.Joystick(0)
        print(f"Controller found: {active_joystick.get_name()}")
    else:
        print("No controller detected. Using keyboard.")

    if is_fullscreen:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Aston Campus Navigator - Game")
    clock = pygame.time.Clock()
    
    try: 
        ui_font = pygame.font.Font(None, 36); menu_title_font = pygame.font.Font(None, 48)
        riddle_font = pygame.font.Font(None, 30); option_font = pygame.font.Font(None, 28)
        info_font = pygame.font.Font(None, 28); leaderboard_font = pygame.font.Font(None, 32)
        input_font = pygame.font.Font(None, 32)
    except pygame.error as e: 
        print(f"Font loading error: {e}. Using system fallback.")
        ui_font=pygame.font.SysFont("arial",30); menu_title_font=pygame.font.SysFont("arial",40)
        riddle_font=pygame.font.SysFont("arial",28); option_font=pygame.font.SysFont("arial",26)
        info_font=pygame.font.SysFont("arial",24); leaderboard_font=pygame.font.SysFont("arial",30)
        input_font=pygame.font.SysFont("arial",30)

    # --- Nested Function to Initialize/Reset a Game Session ---
    def initialize_new_game_session():
        # Declare nonlocal for variables in main_game_loop scope that this function MODIFIES
        nonlocal game_map_obj, player_obj, all_sprites, dest_obj_list, dest_sprites
        nonlocal obj_manager, active_collectible_list_session, collectible_sprites
        nonlocal score, time_left, active_info_msg, active_info_msg_timer, current_riddle_item
        nonlocal game_flow_state, debug_draw_collision_flag # game_flow_state is crucial
        nonlocal current_riddle_opt_rects 
        nonlocal full_collectible_pool_obj_list # This is populated once, then items reset

        print(f"\n--- Initializing New Game Session for {current_player_name} ---")
        debug_draw_collision_flag = False 
        game_map_obj = Map(screen, TILE_DIRECTORY) 
        if not game_map_obj.is_loaded_successfully(): print("CRITICAL: Map load failed in init."); pygame.quit(); sys.exit()

        temp_initial_player_world_x = game_map_obj.full_map_pixel_width / 2
        temp_initial_player_world_y = game_map_obj.full_map_pixel_height / 2
        if game_map_obj.grid_width_in_tiles > 0 and game_map_obj.grid_height_in_tiles > 0 and \
           game_map_obj.collision_grid and len(game_map_obj.collision_grid) > 0:
            preferred_start_tile_x = game_map_obj.grid_width_in_tiles - 1 ; preferred_start_tile_y = 0 
            found_tile_coords = None; max_search_radius = max(game_map_obj.grid_width_in_tiles, game_map_obj.grid_height_in_tiles) 
            if game_map_obj.is_tile_walkable(preferred_start_tile_x, preferred_start_tile_y): found_tile_coords = (preferred_start_tile_x, preferred_start_tile_y)
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
        
        selected_sprite_file = player_sprite_paths_list[selected_player_sprite_idx] if player_sprite_paths_list else None
        player_obj = Player(temp_initial_player_world_x, temp_initial_player_world_y, selected_sprite_file)
        all_sprites = pygame.sprite.Group(player_obj)

        dest_obj_list.clear() 
        for data_item in destinations_data: # Using module-level destinations_data
            if data_item.get("world_x") is not None and data_item.get("world_y") is not None:
                dest = Destination(id=data_item["id"], name=data_item["name"], world_x=data_item["world_x"], world_y=data_item["world_y"],
                                   radius=data_item.get("radius", 30), info_text=data_item.get("info_text", ""))
                dest_obj_list.append(dest)
        dest_sprites = pygame.sprite.Group(dest_obj_list)
        obj_manager = ObjectiveManager(dest_obj_list, NUM_OBJECTIVES_TO_COMPLETE) 
        
        if not full_collectible_pool_obj_list: 
            print("Populating full collectible pool for the first time...")
            for data_item in collectibles_data: # Using module-level collectibles_data
                if data_item.get("world_x") is not None and data_item.get("world_y") is not None:
                    item = Collectible( id=data_item.get("id"), name=data_item.get("name"), world_x=data_item["world_x"], world_y=data_item["world_y"],
                                       image_path=data_item.get("image_path"), info_text=data_item.get("info_text"), points_value=data_item.get("points_value"),
                                       riddle_text=data_item.get("riddle_text", "Riddle Missing!"), 
                                       riddle_options=data_item.get("riddle_options", ["A","B","C","D?"]),
                                       correct_option_index=data_item.get("correct_option_index", 0),
                                       default_size=(int(REFERENCE_TILE_SIZE*0.75), int(REFERENCE_TILE_SIZE*0.75)))
                    full_collectible_pool_obj_list.append(item)
        
        for item in full_collectible_pool_obj_list: item.collected = False 
        active_collectible_list_session.clear()
        if full_collectible_pool_obj_list:
            temp_pool = list(full_collectible_pool_obj_list); random.shuffle(temp_pool)
            num_to_activate = min(len(temp_pool), NUM_COLLECTIBLES_PER_SESSION)
            active_collectible_list_session = temp_pool[:num_to_activate]
        collectible_sprites = pygame.sprite.Group(active_collectible_list_session)
        print(f"Activated {len(active_collectible_list_session)} collectibles.")
        
        score = 0; time_left = GAME_DURATION_SECONDS
        active_info_msg = None; active_info_msg_timer = 0
        current_riddle_item = None; current_riddle_opt_rects.clear()
        game_flow_state = GAME_STATE_PLAYING # Transition to playing state
    # --- End of initialize_new_game_session ---

    # --- Drawing Helper Functions (DEFINED EARLIER, as in your last script) ---
    def draw_text(text, font, color, surface, x, y, center_x=False, center_y=False, topright_x=None, bottom_y=None, topleft_x=None):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center_x: text_rect.centerx = x
        elif topright_x is not None: text_rect.topright = (topright_x, y)
        elif topleft_x is not None: text_rect.topleft = (topleft_x, y)
        else: text_rect.x = x
        
        if center_y: text_rect.centery = y
        elif bottom_y is not None: text_rect.bottom = bottom_y
        else: text_rect.y = y 
        surface.blit(text_surface, text_rect)
        return text_rect 

    def draw_multiline_message_box(surface, text, font_to_use, text_color, bg_color, border_color, 
                                   box_rect_dims, padding=20, border_radius=5, position="custom_rect_top_left_within_box"): # Added position for flexibility if needed elsewhere
        words = str(text).split(' '); lines = []
        current_line_text_content = ""; 
        # Use box_rect_dims.width directly for max_text_width calculation based on the provided rect
        max_text_width = box_rect_dims.width - (2 * padding)
        
        for word in words:
            if word == '\n': lines.append(current_line_text_content.strip()); current_line_text_content = ""; continue
            test_line_text_content = current_line_text_content + word + " "
            if font_to_use.size(test_line_text_content)[0] <= max_text_width: current_line_text_content = test_line_text_content
            else: lines.append(current_line_text_content.strip()); current_line_text_content = word + " "
        lines.append(current_line_text_content.strip())

        line_height = font_to_use.get_linesize()
        
        # Background is drawn onto the main surface at box_rect_dims.topleft
        bg_surface_for_box = pygame.Surface(box_rect_dims.size, pygame.SRCALPHA)
        bg_surface_for_box.fill(bg_color)
        surface.blit(bg_surface_for_box, box_rect_dims.topleft)
        if border_color: pygame.draw.rect(surface, border_color, box_rect_dims, 2, border_radius=border_radius) 

        current_y_draw = box_rect_dims.top + padding
        for line_text_content_item in lines:
            if line_text_content_item: 
                line_surface = font_to_use.render(line_text_content_item, True, text_color)
                # Position text relative to the box_rect_dims passed
                line_render_rect = line_surface.get_rect(
                    centerx=box_rect_dims.centerx, 
                    top=current_y_draw
                )
                if line_render_rect.bottom > box_rect_dims.bottom - padding + 5 : break 
                surface.blit(line_surface, line_render_rect)
                current_y_draw += line_height
    # --- Main Game Loop ---
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0 
        mouse_pos = pygame.mouse.get_pos()
        joystick_direction_input = pygame.math.Vector2(0, 0)
        
        # --- Event Handling (State Dependant) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_F11:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen: screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    else: screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

            # Pass screen to event handling relevant for drawing interactive elements like menu options
            if game_flow_state == GAME_STATE_MENU:
                # ... (menu event handling, using MENU_OPTIONS_TEXTS) ...
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: current_selected_menu_opt = (current_selected_menu_opt - 1) % len(MENU_OPTIONS_TEXTS)
                    elif event.key == pygame.K_DOWN: current_selected_menu_opt = (current_selected_menu_opt + 1) % len(MENU_OPTIONS_TEXTS)
                    elif event.key == pygame.K_RETURN:
                        if MENU_OPTIONS_TEXTS[current_selected_menu_opt] == "Start New Game": game_flow_state = GAME_STATE_PLAYER_SETUP; current_player_name = ""; player_name_input_active = True
                        elif MENU_OPTIONS_TEXTS[current_selected_menu_opt] == "Player Setup": game_flow_state = GAME_STATE_PLAYER_SETUP; current_player_name = ""; player_name_input_active = True
                        elif MENU_OPTIONS_TEXTS[current_selected_menu_opt] == "View Leaderboard": leaderboard_entries = load_leaderboard(); game_flow_state = GAME_STATE_LEADERBOARD_VIEW
                        elif MENU_OPTIONS_TEXTS[current_selected_menu_opt] == "Controls": game_flow_state = GAME_STATE_CONTROLS_DISPLAY
                        elif MENU_OPTIONS_TEXTS[current_selected_menu_opt] == "Quit": running = False
                    elif event.key == pygame.K_ESCAPE: running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                     for i, rect in enumerate(menu_option_display_rects):
                        if rect.collidepoint(mouse_pos):
                            current_selected_menu_opt = i
                            if MENU_OPTIONS_TEXTS[i] == "Start New Game": game_flow_state = GAME_STATE_PLAYER_SETUP; current_player_name = ""; player_name_input_active = True
                            elif MENU_OPTIONS_TEXTS[i] == "Player Setup": game_flow_state = GAME_STATE_PLAYER_SETUP; current_player_name = ""; player_name_input_active = True
                            elif MENU_OPTIONS_TEXTS[i] == "View Leaderboard": leaderboard_entries = load_leaderboard(); game_flow_state = GAME_STATE_LEADERBOARD_VIEW
                            elif MENU_OPTIONS_TEXTS[i] == "Controls": game_flow_state = GAME_STATE_CONTROLS_DISPLAY
                            elif MENU_OPTIONS_TEXTS[i] == "Quit": running = False; break
            
            elif game_flow_state == GAME_STATE_PLAYER_SETUP:
                # ... (player setup event handling) ...
                if event.type == pygame.KEYDOWN:
                    if player_name_input_active: 
                        if event.key == pygame.K_RETURN:
                            if current_player_name.strip(): player_name_input_active = False 
                            else: active_info_msg = "Player name cannot be empty."; active_info_msg_timer = pygame.time.get_ticks() 
                        elif event.key == pygame.K_BACKSPACE: current_player_name = current_player_name[:-1]
                        elif len(current_player_name) < PLAYER_NAME_MAX_LENGTH: 
                            if event.unicode.isalnum() or event.unicode == ' ': current_player_name += event.unicode
                    else: 
                        if event.key == pygame.K_LEFT: selected_player_sprite_idx = (selected_player_sprite_idx - 1) % len(player_sprite_paths_list)
                        elif event.key == pygame.K_RIGHT: selected_player_sprite_idx = (selected_player_sprite_idx + 1) % len(player_sprite_paths_list)
                        elif event.key == pygame.K_RETURN: 
                            if not current_player_name.strip(): current_player_name = "Player" 
                            initialize_new_game_session()
                        elif event.key == pygame.K_ESCAPE: game_flow_state = GAME_STATE_MENU; player_name_input_active = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if player_setup_input_box_ui_rect and player_setup_input_box_ui_rect.collidepoint(mouse_pos): player_name_input_active = True
                    elif player_setup_sprite_arrow_rects_ui.get("left") and player_setup_sprite_arrow_rects_ui["left"].collidepoint(mouse_pos):
                        selected_player_sprite_idx = (selected_player_sprite_idx - 1) % len(player_sprite_paths_list); player_name_input_active = False
                    elif player_setup_sprite_arrow_rects_ui.get("right") and player_setup_sprite_arrow_rects_ui["right"].collidepoint(mouse_pos):
                        selected_player_sprite_idx = (selected_player_sprite_idx + 1) % len(player_sprite_paths_list); player_name_input_active = False
                    elif player_setup_confirm_button_ui_rect and player_setup_confirm_button_ui_rect.collidepoint(mouse_pos):
                        if not current_player_name.strip(): current_player_name = "Player"
                        initialize_new_game_session()
                    else: player_name_input_active = False

            elif game_flow_state == GAME_STATE_LEADERBOARD_VIEW or game_flow_state == GAME_STATE_CONTROLS_DISPLAY:
                # ... (leaderboard/controls event handling) ...
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN: game_flow_state = GAME_STATE_MENU
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: game_flow_state = GAME_STATE_MENU

            elif game_flow_state == GAME_STATE_RIDDLE:
                # ... (riddle event handling, ensuring correct key checks) ...
                if event.type == pygame.KEYDOWN:
                    chosen_idx = -1
                    if event.key == pygame.K_1: chosen_idx = 0
                    elif event.key == pygame.K_2: chosen_idx = 1
                    elif event.key == pygame.K_3: chosen_idx = 2
                    elif event.key == pygame.K_4: chosen_idx = 3
                    if chosen_idx != -1 and current_riddle_item:
                        if chosen_idx == current_riddle_item.correct_option_index:
                            score += current_riddle_item.points_value; active_info_msg = f"Correct! (+{current_riddle_item.points_value} pts)\n{current_riddle_item.info_text}"; current_riddle_item.mark_collected() 
                        else: active_info_msg = "Incorrect. The item remains."
                        current_riddle_item = None; active_info_msg_timer = pygame.time.get_ticks(); game_flow_state = GAME_STATE_INFO_DISPLAY
                    elif event.key == pygame.K_ESCAPE: current_riddle_item = None; game_flow_state = GAME_STATE_PLAYING
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if current_riddle_item:
                        for i, rect in enumerate(current_riddle_opt_rects): # current_riddle_opt_rect_list
                            if rect.collidepoint(mouse_pos):
                                if i == current_riddle_item.correct_option_index:
                                    score += current_riddle_item.points_value; active_info_msg = f"Correct! (+{current_riddle_item.points_value} pts)\n{current_riddle_item.info_text}"; current_riddle_item.mark_collected()
                                else: active_info_msg = "Incorrect. The item remains."
                                current_riddle_item = None; active_info_msg_timer = pygame.time.get_ticks(); game_flow_state = GAME_STATE_INFO_DISPLAY; break
            
            elif game_flow_state in [GAME_STATE_PLAYING, GAME_STATE_INFO_DISPLAY, GAME_STATE_SESSION_COMPLETE, GAME_STATE_TIME_UP]:
                # ... (event handling for these states, ensuring ESC to MENU works) ...
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
                            game_flow_state = GAME_STATE_SESSION_COMPLETE; active_info_msg = f"Main objectives complete, {current_player_name}! Score: {score}"; active_info_msg_timer = pygame.time.get_ticks()
                            leaderboard_entries = add_score_to_leaderboard(current_player_name, score, leaderboard_entries); save_leaderboard(leaderboard_entries)
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
        
        # --- Input Processing & Game Logic ---
        if game_flow_state == GAME_STATE_PLAYING or game_flow_state == GAME_STATE_INFO_DISPLAY:
            if player_obj: 
                keys = pygame.key.get_pressed(); keyboard_direction = pygame.math.Vector2(0,0)
                if keys[pygame.K_LEFT] or keys[pygame.K_a]: keyboard_direction.x -=1
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]: keyboard_direction.x +=1
                if keys[pygame.K_UP] or keys[pygame.K_w]: keyboard_direction.y -=1
                if keys[pygame.K_DOWN] or keys[pygame.K_s]: keyboard_direction.y +=1
                if joystick_direction_input.length_squared() > 0: player_obj.set_movement_direction(joystick_direction_input)
                else: player_obj.set_movement_direction(keyboard_direction)

        if game_flow_state not in [GAME_STATE_RIDDLE, GAME_STATE_MENU, GAME_STATE_CONTROLS_DISPLAY, GAME_STATE_PLAYER_SETUP] :
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
                        active_info_msg = f"Time's Up, {current_player_name}! Final Score: {score}"; active_info_msg_timer = pygame.time.get_ticks()
                        leaderboard_entries = add_score_to_leaderboard(current_player_name, score, leaderboard_entries); save_leaderboard(leaderboard_entries)
                
                if obj_manager and player_obj:
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
                                active_info_msg = f"Objectives Complete, {current_player_name}! Score: {score}"; active_info_msg_timer = pygame.time.get_ticks()
                                leaderboard_entries = add_score_to_leaderboard(current_player_name, score, leaderboard_entries); save_leaderboard(leaderboard_entries)
                
                if game_flow_state == GAME_STATE_PLAYING and collectible_sprites and player_obj: 
                    for item in collectible_sprites: 
                        if not item.collected and player_obj.rect.colliderect(item.rect): 
                            dist_x = player_obj.world_x - item.world_x; dist_y = player_obj.world_y - item.world_y
                            item_eff_radius = item.default_size[0] / 2; player_eff_radius_for_item = player_obj.width / 2
                            if (dist_x**2 + dist_y**2) < (item_eff_radius + player_eff_radius_for_item)**2:
                                current_riddle_item = item; game_flow_state = GAME_STATE_RIDDLE; break 
            
            if game_flow_state == GAME_STATE_INFO_DISPLAY:
                if pygame.time.get_ticks() - active_info_msg_timer > INFO_MESSAGE_DURATION and active_info_msg is not None:
                    active_info_msg = None
                    if obj_manager and obj_manager.all_session_objectives_visited() and not current_riddle_item:
                         game_flow_state = GAME_STATE_SESSION_COMPLETE
                         if not active_info_msg: 
                            active_info_msg = f"Objectives Complete, {current_player_name}! Score: {score}"
                            active_info_msg_timer = pygame.time.get_ticks()
                    else: game_flow_state = GAME_STATE_PLAYING
        
        elif game_flow_state == GAME_STATE_RIDDLE and player_obj:
            player_obj.set_movement_direction(pygame.math.Vector2(0,0))

        if game_map_obj and player_obj and game_map_obj.zoom_level > 0 and \
            game_flow_state not in [GAME_STATE_MENU, GAME_STATE_PLAYER_SETUP, GAME_STATE_LEADERBOARD_VIEW, GAME_STATE_CONTROLS_DISPLAY]:
            game_map_obj.offset_x = player_obj.rect.centerx - (player_obj.world_x * game_map_obj.zoom_level)
            game_map_obj.offset_y = player_obj.rect.centery - (player_obj.world_y * game_map_obj.zoom_level)

        # --- Drawing ---
        screen.fill(WHITE) 
        if game_flow_state == GAME_STATE_MENU:
            # ... (Menu drawing as before, using menu_option_display_rect_list and current_selected_menu_opt) ...
            draw_text("Campus Navigator Challenge", menu_title_font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 20, center_x=True)
            menu_option_display_rects.clear() # Correct name
            option_y_start = SCREEN_HEIGHT // 2 - 80
            for i, option_text in enumerate(MENU_OPTIONS_TEXTS): 
                is_selected = (i == current_selected_menu_opt) 
                btn_color = MENU_SELECTED_COLOR if is_selected else MENU_OPTION_COLOR
                temp_rect = pygame.Rect(0,0,350, 50); temp_rect.center = (SCREEN_WIDTH//2, option_y_start + i * 70)
                if not is_selected and temp_rect.collidepoint(mouse_pos): btn_color = MENU_OPTION_HOVER_COLOR
                pygame.draw.rect(screen, btn_color, temp_rect, border_radius=10)
                if is_selected: pygame.draw.rect(screen, WHITE, temp_rect, 3, border_radius=10)
                draw_text(option_text, ui_font, WHITE, screen, temp_rect.centerx, temp_rect.centery, center_x=True, center_y=True)
                menu_option_display_rects.append(temp_rect)
        
        elif game_flow_state == GAME_STATE_PLAYER_SETUP:
            # ... (Player Setup drawing as before, using player_setup_input_box_ui_rect etc.) ...
            screen.fill(GREY)
            draw_text("Player Setup", menu_title_font, BLACK, screen, SCREEN_WIDTH // 2, 70, center_x=True)
            draw_text("Enter Your Name (Max {} Chars):".format(PLAYER_NAME_MAX_LENGTH), ui_font, BLACK, screen, 50, 150, topleft_x=50)
            player_setup_input_box_ui_rect = pygame.Rect(50, 190, SCREEN_WIDTH - 100, input_font.get_height() + 10)
            border_color = INPUT_BOX_ACTIVE_BORDER if player_name_input_active else INPUT_BOX_INACTIVE_BORDER
            pygame.draw.rect(screen, WHITE, player_setup_input_box_ui_rect); pygame.draw.rect(screen, border_color, player_setup_input_box_ui_rect, 2)
            name_surf = input_font.render(current_player_name, True, UI_TEXT_COLOR)
            screen.blit(name_surf, (player_setup_input_box_ui_rect.x + 5, player_setup_input_box_ui_rect.y + 5))
            if player_name_input_active and int(pygame.time.get_ticks() / 500) % 2 == 0:
                cursor_x = player_setup_input_box_ui_rect.x + 5 + name_surf.get_width() + 2
                pygame.draw.line(screen, BLACK, (cursor_x, player_setup_input_box_ui_rect.y + 5), (cursor_x, player_setup_input_box_ui_rect.y + input_font.get_height() + 5), 2)
            draw_text("Select Your Sprite:", ui_font, BLACK, screen, 50, 280, topleft_x=50)
            sprite_preview_x = SCREEN_WIDTH // 2; sprite_preview_y = 350; arrow_y_pos = sprite_preview_y 
            player_setup_sprite_arrow_rects_ui["left"] = draw_text("<", menu_title_font, DARK_GREY if not player_setup_sprite_arrow_rects_ui.get("left", pygame.Rect(0,0,1,1)).collidepoint(mouse_pos) else BLACK, screen, sprite_preview_x - 80, arrow_y_pos, center_y=True)
            if player_sprite_paths_list and selected_player_sprite_idx < len(player_sprite_paths_list) and player_sprite_paths_list[selected_player_sprite_idx]:
                try:
                    sprite_img = pygame.image.load(player_sprite_paths_list[selected_player_sprite_idx]).convert_alpha()
                    sprite_img_scaled = pygame.transform.scale(sprite_img, PLAYER_SPRITE_DISPLAY_SIZE)
                    preview_rect = sprite_img_scaled.get_rect(center=(sprite_preview_x, sprite_preview_y))
                    pygame.draw.rect(screen, PLAYER_SPRITE_PREVIEW_BG, preview_rect.inflate(10,10), border_radius=5)
                    screen.blit(sprite_img_scaled, preview_rect)
                except pygame.error: pygame.draw.rect(screen, RED, (sprite_preview_x - PLAYER_SPRITE_DISPLAY_SIZE[0]//2, sprite_preview_y - PLAYER_SPRITE_DISPLAY_SIZE[1]//2, PLAYER_SPRITE_DISPLAY_SIZE[0], PLAYER_SPRITE_DISPLAY_SIZE[1]))
            player_setup_sprite_arrow_rects_ui["right"] = draw_text(">", menu_title_font, DARK_GREY if not player_setup_sprite_arrow_rects_ui.get("right", pygame.Rect(0,0,1,1)).collidepoint(mouse_pos) else BLACK, screen, sprite_preview_x + 80, arrow_y_pos, center_y=True)
            
            confirm_btn_text = "Start Game!"; confirm_btn_surf = ui_font.render(confirm_btn_text, True, WHITE)
            confirm_btn_width = max(200, confirm_btn_surf.get_width() + 40)
            player_setup_confirm_button_ui_rect = pygame.Rect(0,0, confirm_btn_width, confirm_btn_surf.get_height() + 20)
            player_setup_confirm_button_ui_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120)
            btn_bg_color = MENU_OPTION_HOVER_COLOR if player_setup_confirm_button_ui_rect.collidepoint(mouse_pos) else MENU_OPTION_COLOR
            pygame.draw.rect(screen, btn_bg_color, player_setup_confirm_button_ui_rect, border_radius=10)
            screen.blit(confirm_btn_surf, confirm_btn_surf.get_rect(center=player_setup_confirm_button_ui_rect.center))
            draw_text("ESC to Menu", option_font, DARK_GREY, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, center_x=True)

        elif game_flow_state == GAME_STATE_LEADERBOARD_VIEW:
            # ... (Leaderboard drawing, using draw_text) ...
            screen.fill(GREY); draw_text("Leaderboard", menu_title_font, BLACK, screen, SCREEN_WIDTH//2, 70, center_x=True)
            if not leaderboard_entries: draw_text("No scores yet! Be the first!", ui_font, BLACK, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, center_x=True, center_y=True)
            else:
                y_offset = 150; rank_x = 100; name_x = 180; score_x_right_align = SCREEN_WIDTH - 100
                draw_text("Rank", leaderboard_font, BLACK, screen, rank_x, y_offset - 40, center_x=True)
                draw_text("Name", leaderboard_font, BLACK, screen, name_x, y_offset - 40, topleft_x=name_x)
                draw_text("Score", leaderboard_font, BLACK, screen, score_x_right_align, y_offset - 40, topright_x=score_x_right_align)
                for i, entry in enumerate(leaderboard_entries):
                    draw_text(f"{i+1}.", leaderboard_font, BLACK, screen, rank_x, y_offset, center_x=True)
                    draw_text(entry["name"], leaderboard_font, BLACK, screen, name_x, y_offset, topleft_x=name_x)
                    draw_text(str(entry["score"]), leaderboard_font, BLACK, screen, score_x_right_align, y_offset, topright_x=score_x_right_align)
                    y_offset += 40
            draw_text("Click or Press ESC/Enter to Return to Menu", option_font, DARK_GREY, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT-30, center_x=True)

        elif game_flow_state == GAME_STATE_CONTROLS_DISPLAY:
            # ... (Controls drawing, using draw_text and CONTROLS_TEXT_LINES from settings) ...
            screen.fill(GREY); draw_text("Controls", ui_font, BLACK, screen, SCREEN_WIDTH//2, 70, center_x=True)
            line_y = 120
            for line in CONTROLS_TEXT_LINES: 
                draw_text(line, info_font, BLACK, screen, 50, line_y, topleft_x=50); line_y += info_font.get_linesize() + 5
            draw_text("Click or Press ESC/Enter to Return to Menu", option_font, DARK_GREY, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT-30, center_x=True)

        elif game_flow_state in [GAME_STATE_PLAYING, GAME_STATE_RIDDLE, GAME_STATE_INFO_DISPLAY, GAME_STATE_SESSION_COMPLETE, GAME_STATE_TIME_UP]:
            # ... (Your complete in-game drawing logic from previous version, using draw_text and draw_multiline_message_box) ...
            if game_map_obj: game_map_obj.draw(debug_draw_collision_flag) 
            if dest_sprites: dest_sprites.draw(screen)
            if collectible_sprites: collectible_sprites.draw(screen) 
            if all_sprites: all_sprites.draw(screen)
            if obj_manager: draw_text(obj_manager.get_current_objective_text(), ui_font, UI_TEXT_COLOR, screen, 20, 20, topleft_x=20)
            
            score_surf = ui_font.render(f"Score: {score}", True, UI_TEXT_COLOR)
            score_display_rect_val = screen.blit(score_surf, score_surf.get_rect(topright=(SCREEN_WIDTH - 20, 20)))
            
            minutes = int(time_left) // 60; seconds = int(time_left) % 60
            timer_text_str = f"Time: {minutes:02d}:{seconds:02d}"
            if game_flow_state == GAME_STATE_TIME_UP: timer_text_str = "Time's Up!"
            elif time_left <=0 : timer_text_str = "Time: 00:00"
            timer_color = RED if time_left <= 10 and game_flow_state == GAME_STATE_PLAYING else UI_TEXT_COLOR
            draw_text(timer_text_str, ui_font, timer_color, screen, score_display_rect_val.right, score_display_rect_val.bottom + 5, topright_x=score_display_rect_val.right)

            if game_flow_state == GAME_STATE_RIDDLE and current_riddle_item:
                current_riddle_opt_rects.clear(); box_width, box_height = SCREEN_WIDTH*0.85, SCREEN_HEIGHT*0.75
                box_x,box_y = (SCREEN_WIDTH-box_width)/2, (SCREEN_HEIGHT-box_height)/2; riddle_box_rect = pygame.Rect(box_x,box_y,box_width,box_height)
                riddle_bg_surface = pygame.Surface(riddle_box_rect.size, pygame.SRCALPHA); riddle_bg_surface.fill(UI_BG_COLOR)
                screen.blit(riddle_bg_surface, riddle_box_rect.topleft); pygame.draw.rect(screen,BLACK,riddle_box_rect,2, border_radius=5)
                riddle_padding=25; max_riddle_text_draw_width = box_width - 2*riddle_padding 
                riddle_text_draw_rect = pygame.Rect(box_x + riddle_padding, box_y + riddle_padding, max_riddle_text_draw_width, box_height * 0.35)
                draw_multiline_message_box(screen, current_riddle_item.riddle_text, riddle_font, UI_TEXT_COLOR, (0,0,0,0), None, riddle_text_draw_rect, padding=0) # position="custom_rect_top_left_within_box" not needed as rect is given

                option_y_start_abs = riddle_text_draw_rect.bottom + 20 
                option_visual_height = option_font.get_linesize() + 15; option_spacing = 10
                for i, option_text_content in enumerate(current_riddle_item.riddle_options):
                    option_box_y = option_y_start_abs + i * (option_visual_height + option_spacing)
                    option_box = pygame.Rect(box_x+riddle_padding, option_box_y, max_riddle_text_draw_width, option_visual_height)
                    if option_box.bottom > riddle_box_rect.bottom - riddle_padding: break 
                    current_riddle_opt_rects.append(option_box)
                    current_opt_color = RIDDLE_OPTION_HOVER_COLOR if option_box.collidepoint(mouse_pos) else RIDDLE_OPTION_COLOR
                    pygame.draw.rect(screen, current_opt_color, option_box, border_radius=5)
                    pygame.draw.rect(screen, DARK_GREY, option_box, 1, border_radius=5)
                    draw_text(f"{i+1}. {option_text_content}", option_font, WHITE, screen, option_box.x + 10, option_box.centery, center_y=True, topleft_x=option_box.x+10)
            
            elif (game_flow_state == GAME_STATE_INFO_DISPLAY or \
                  game_flow_state == GAME_STATE_SESSION_COMPLETE or \
                  game_flow_state == GAME_STATE_TIME_UP) and active_info_msg:
                info_box_r = pygame.Rect(0,0, SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.4) 
                info_box_r.centerx = SCREEN_WIDTH/2 ; info_box_r.bottom = SCREEN_HEIGHT - 20
                draw_multiline_message_box(screen, active_info_msg, info_font, UI_TEXT_COLOR, UI_BG_COLOR, BLACK, info_box_r, padding=20) # position="custom_rect_top_left_within_box" not needed

        pygame.display.flip()

    if obj_manager: 
        leaderboard_entries = add_score_to_leaderboard(current_player_name, score, leaderboard_entries)
        save_leaderboard(leaderboard_entries)

    pygame.quit()
    if active_joystick: pygame.joystick.quit()
    sys.exit()

# --- Entry Point ---
if __name__ == "__main__":
    tiles_dir = TILE_DIRECTORY 
    meta_file = os.path.join(tiles_dir, "map_meta.json") 
    if not os.path.exists(meta_file):
        print(f"Error: Metadata file '{meta_file}' not found. Please run data generation workflow."); sys.exit()
    else:
        try:
            with open(meta_file, 'r') as f:
                temp_meta = json.load(f) 
                if not temp_meta.get("collision_grid_data") or \
                   (isinstance(temp_meta.get("collision_grid_data"), list) and not temp_meta.get("collision_grid_data")) or \
                   (isinstance(temp_meta.get("collision_grid_data"), list) and len(temp_meta.get("collision_grid_data")) > 0 and not temp_meta.get("collision_grid_data")[0]):
                    print(f"CRITICAL WARNING: 'collision_grid_data' in {meta_file} appears problematic.")
        except Exception as e: print(f"Warning: Could not quickly check metadata file {meta_file}: {e}")
    
    main_game_loop()