# settings.py
import pygame
import os
# --- Screen and Display ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
IS_FULLSCREEN_DEFAULT = False # Set to True if you want to start in fullscreen

# --- File Paths & Game Data ---
TILE_DIRECTORY = "tiles" # Directory for map tiles and map_meta.json
LEADERBOARD_FILE = "leaderboard.json"
ASSETS_SPRITES_PLAYER_DIR = "assets/sprites/player/" # For player character images
ASSETS_ICONS_DIR = "assets/icons/" # For collectible icons, etc.

# --- Player and Game Mechanics ---
REFERENCE_TILE_SIZE = 32 
PLAYER_DEFAULT_WIDTH = 20
PLAYER_DEFAULT_HEIGHT = 20
PLAYER_SPRITE_DISPLAY_SIZE = (40, 40)
PLAYER_SPEED = 150
PLAYER_NAME_MAX_LENGTH = 12
ZOOM_SPEED_MULTIPLIER = 1.1
NUM_OBJECTIVES_TO_COMPLETE = 5
NUM_COLLECTIBLES_PER_SESSION = 3 
GAME_DURATION_SECONDS = 300 # 5 minutes
INFO_MESSAGE_DURATION = 3500 # Milliseconds
MAX_LEADERBOARD_ENTRIES = 10

# --- Colors ---
WHITE = (255,255,255)
BLACK = (0,0,0) 
RED = (255,0,0) 
GREEN = (0,255,0) 
BLUE = (0,0,255) 
GREY = (200,200,200) 
DARK_GREY = (100,100,100) 
LIGHT_BLUE = (173,216,230)
UI_TEXT_COLOR = (10,10,10) 
UI_BG_COLOR = (230,230,230,220) # RGBA for semi-transparency
RIDDLE_OPTION_COLOR = (70,70,170) 
RIDDLE_OPTION_HOVER_COLOR = (120,120,220) 
MENU_OPTION_COLOR = (60,60,160) 
MENU_OPTION_HOVER_COLOR = (110,110,200) 
MENU_SELECTED_COLOR = (255,165,0) # Orange for selected
INPUT_BOX_ACTIVE_BORDER = (0,150,255) 
INPUT_BOX_INACTIVE_BORDER = DARK_GREY
PLAYER_SPRITE_PREVIEW_BG = (210, 210, 210)

# --- Game States (Strings for clarity) ---
GAME_STATE_MENU = "menu"
GAME_STATE_PLAYER_SETUP = "player_setup"
GAME_STATE_CONTROLS_DISPLAY = "controls_display"
GAME_STATE_LEADERBOARD_VIEW = "leaderboard_view"
GAME_STATE_PLAYING = "playing"
GAME_STATE_RIDDLE = "riddle"
GAME_STATE_INFO_DISPLAY = "info_display"
GAME_STATE_SESSION_COMPLETE = "session_complete" 
GAME_STATE_TIME_UP = "time_up"

# --- Player Sprite Options ---
# User must place their player sprite images in ASSETS_SPRITES_PLAYER_DIR
# and list their filenames here.
PLAYER_SPRITE_FILENAMES = [
    "woman.png", # Example - replace with your actual filenames
    "man.png", # Example
    # "player_avatar3.png", # Example
]
# Fallback if no sprites are listed or found - ensure you have a default_player.png
DEFAULT_PLAYER_SPRITE_FILENAME = "man.png" 

# Function to get full sprite paths, helps centralize asset directory logic
def get_player_sprite_paths():
    paths = [os.path.join(ASSETS_SPRITES_PLAYER_DIR, fname) for fname in PLAYER_SPRITE_FILENAMES]
    valid_paths = [p for p in paths if os.path.exists(p)]
    if not valid_paths:
        print(f"Warning: No player sprites found from PLAYER_SPRITE_FILENAMES. Using default.")
        default_path = os.path.join(ASSETS_SPRITES_PLAYER_DIR, DEFAULT_PLAYER_SPRITE_FILENAME)
        if os.path.exists(default_path):
            return [default_path]
        else: # Absolute fallback if even default is missing
            print(f"CRITICAL WARNING: Default player sprite '{default_path}' not found either!")
            return [None] # Player class will handle this by drawing a blue square
    return valid_paths

# --- UI Text / Content ---
CONTROLS_TEXT_LINES = [
    "Campus Navigator Controls:", "", 
    "Move Player: Arrow Keys / WASD / Joystick Left Stick",
    "Zoom Map: +/- Keys / Mouse Wheel", 
    "Answer Riddle (Keyboard): Number Keys 1, 2, 3, 4",
    "Answer Riddle (Mouse): Click on the Option Box", 
    "Debug Skip Objective: N", 
    "Debug Toggle Collision: C", 
    "Fullscreen Toggle: F11",
    "Dismiss Info / To Menu: Mouse Click or ESC"
]

MENU_OPTIONS_TEXTS = ["Start New Game", "Player Setup", "View Leaderboard", "Controls", "Quit"]