# map_class.py
import pygame
import os
import json

class Map:
    def __init__(self, screen, tile_directory):
        self.screen = screen
        self.tile_dir = tile_directory
        self.tile_cache = {}  # Cache for loaded tile images (pygame.Surface objects)

        # Properties to be loaded from metadata
        self.tile_pixel_width = 0
        self.tile_pixel_height = 0
        self.grid_width_in_tiles = 0
        self.grid_height_in_tiles = 0
        self.tile_filenames_grid = [] # 2D list of tile filenames in correct order
        self.collision_grid = [] # Will be loaded/updated
        self._loaded_successfully = False # <--- ADD THIS ATTRIBUTE

        self.load_map_metadata()

        # Total map dimensions in pixels (at 1x zoom)
        # These should only be calculated if loading was successful
        if self._loaded_successfully:
            self.full_map_pixel_width = self.grid_width_in_tiles * self.tile_pixel_width
            self.full_map_pixel_height = self.grid_height_in_tiles * self.tile_pixel_height
        else:
            self.full_map_pixel_width = 0
            self.full_map_pixel_height = 0


        self.zoom_level = 1.0
        self.offset_x = 0  # Top-left corner of the map relative to the screen's top-left
        self.offset_y = 0

    # --- ADD THIS METHOD ---
    def is_loaded_successfully(self):
        return self._loaded_successfully
    # --- END OF ADDED METHOD ---

    def load_map_metadata(self, meta_filename="map_meta.json"):
        meta_file_path = os.path.join(self.tile_dir, meta_filename)
        try:
            with open(meta_file_path, 'r') as f:
                metadata = json.load(f)

            self.tile_pixel_width = metadata["tile_pixel_width"]
            self.tile_pixel_height = metadata["tile_pixel_height"]
            self.grid_width_in_tiles = metadata["grid_width_in_tiles"]
            self.grid_height_in_tiles = metadata["grid_height_in_tiles"]
            self.tile_filenames_grid = metadata["tile_filenames_grid"]
            self.collision_grid = metadata.get("collision_grid_data")

            if not self.collision_grid: # Check if collision_grid is None or empty
                print("Warning: 'collision_grid_data' not found or is empty in metadata.")
                # If you are using tiled_importer.py, this should be populated.
                # If it's critical and missing, you might not want to default to all walkable.
                # For now, let's make it an empty grid if missing, error will be caught below.
                self.collision_grid = []

            # More robust check for essential data
            if not all([
                self.tile_pixel_width > 0,
                self.tile_pixel_height > 0,
                self.grid_width_in_tiles > 0,
                self.grid_height_in_tiles > 0,
                self.tile_filenames_grid, # Check if it's not empty
                isinstance(self.collision_grid, list) # Check if it's a list (even if empty, to be checked later)
            ]):
                # Don't raise ValueError here, instead set _loaded_successfully to False
                print("Error: Metadata is missing essential information or has invalid values.")
                self._loaded_successfully = False
                return # Stop further processing in this method if basic data is bad

            # Check if collision grid dimensions match map dimensions (if collision grid is not empty)
            if self.collision_grid and \
               (len(self.collision_grid) != self.grid_height_in_tiles or \
                (self.grid_height_in_tiles > 0 and len(self.collision_grid[0]) != self.grid_width_in_tiles)):
                print("Error: Collision grid dimensions do not match map grid dimensions.")
                self._loaded_successfully = False
                return

            print(f"Map metadata loaded: Grid {self.grid_width_in_tiles}x{self.grid_height_in_tiles}, Tile Size: {self.tile_pixel_width}x{self.tile_pixel_height}px")
            if self.collision_grid and len(self.collision_grid) > 0: # Check if collision_grid is not empty before accessing its dimensions
                print(f"Collision grid loaded with dimensions: {len(self.collision_grid)}x{len(self.collision_grid[0])}")
            elif not self.collision_grid: # Specifically if it's an empty list after .get() and our assignment
                 print("Warning: Collision grid is present but empty. Player may not collide correctly.")


            self._loaded_successfully = True # <--- SET TO TRUE ON SUCCESSFUL LOAD

        except FileNotFoundError:
            print(f"Error: Metadata file '{meta_file_path}' not found in '{self.tile_dir}'.")
            print("Ensure 'map_meta.json' exists. Run tile generation and Tiled import scripts.")
            self._loaded_successfully = False
        except (json.JSONDecodeError, KeyError, TypeError) as e: # Added TypeError for metadata access
            print(f"Error parsing metadata file '{meta_file_path}' or accessing key: {e}")
            self._loaded_successfully = False
        
        # If loading failed, ensure critical attributes are in a safe state
        if not self._loaded_successfully:
            self.tile_pixel_width = 0
            self.tile_pixel_height = 0
            self.grid_width_in_tiles = 0
            self.grid_height_in_tiles = 0
            self.tile_filenames_grid = []
            self.collision_grid = []


    def is_tile_walkable(self, tile_x_idx, tile_y_idx):
        """Checks if a tile at given grid indices is walkable."""
        if not self._loaded_successfully or not self.collision_grid:
            # print("Debug: is_tile_walkable called but map not loaded or no collision_grid. Defaulting to False (unwalkable).")
            return False 

        if 0 <= tile_y_idx < len(self.collision_grid) and \
           0 <= tile_x_idx < len(self.collision_grid[0]):
            return self.collision_grid[tile_y_idx][tile_x_idx] == 0 # 0 means walkable
        return False # Out of bounds is not walkable

    def get_tile_image(self, tile_filename):
        """Loads a tile image if not cached, then returns it. Handles transparency."""
        if not tile_filename: # Can happen if a tile failed to save/process
            return None
        if tile_filename not in self.tile_cache:
            try:
                tile_path = os.path.join(self.tile_dir, tile_filename)
                image = pygame.image.load(tile_path).convert_alpha()
                self.tile_cache[tile_filename] = image
            except pygame.error as e:
                print(f"Error loading tile image: {tile_filename} from {tile_path} - {e}")
                self.tile_cache[tile_filename] = None 
        return self.tile_cache[tile_filename]

    def draw(self, debug_collision=False): # Added debug_collision parameter
        if not self._loaded_successfully or self.tile_pixel_width == 0 or self.tile_pixel_height == 0 :
            # print("Map not loaded or tile size is zero. Cannot draw.")
            return

        screen_rect = self.screen.get_rect()
        current_scaled_tile_width = int(self.tile_pixel_width * self.zoom_level)
        current_scaled_tile_height = int(self.tile_pixel_height * self.zoom_level)

        if current_scaled_tile_width <= 0 or current_scaled_tile_height <= 0:
            return 

        for row_idx, tile_row in enumerate(self.tile_filenames_grid):
            for col_idx, tile_filename in enumerate(tile_row):
                # tile_filename could be None if convert_map_to_tiles had an issue for a specific tile
                if tile_filename is None:
                    continue 
                
                original_tile_surface = self.get_tile_image(tile_filename)
                
                draw_x = self.offset_x + (col_idx * current_scaled_tile_width)
                draw_y = self.offset_y + (row_idx * current_scaled_tile_height)
                tile_on_screen_rect = pygame.Rect(draw_x, draw_y, current_scaled_tile_width, current_scaled_tile_height)
                
                if not screen_rect.colliderect(tile_on_screen_rect):
                    continue

                if original_tile_surface: 
                    if self.zoom_level == 1.0:
                        image_to_draw = original_tile_surface
                    else:
                        image_to_draw = pygame.transform.smoothscale(
                            original_tile_surface,
                            (current_scaled_tile_width, current_scaled_tile_height)
                        )
                    self.screen.blit(image_to_draw, (draw_x, draw_y))
                
                if debug_collision and self.collision_grid:
                    # Check bounds for collision_grid access, as it might be smaller or improperly formed
                    if 0 <= row_idx < len(self.collision_grid) and \
                       0 <= col_idx < len(self.collision_grid[row_idx]):
                        if not self.is_tile_walkable(col_idx, row_idx): # Use the method which includes bounds checks
                            s = pygame.Surface((current_scaled_tile_width, current_scaled_tile_height), pygame.SRCALPHA)
                            s.fill((255, 0, 0, 100)) # Semi-transparent red for walls
                            self.screen.blit(s, (draw_x, draw_y))
                    # else:
                        # print(f"Debug draw: collision_grid access out of bounds for {row_idx}, {col_idx}")


    def zoom(self, zoom_increment_factor, screen_focus_px, screen_focus_py):
        """
        Zooms the map, keeping the point (screen_focus_px, screen_focus_py)
        on the screen stable.
        """
        if self.zoom_level == 0: return # Avoid division by zero
        
        world_focus_x = (screen_focus_px - self.offset_x) / self.zoom_level
        world_focus_y = (screen_focus_py - self.offset_y) / self.zoom_level

        self.zoom_level *= zoom_increment_factor
        self.zoom_level = max(0.1, min(self.zoom_level, 10.0)) # Clamp zoom

        self.offset_x = screen_focus_px - (world_focus_x * self.zoom_level)
        self.offset_y = screen_focus_py - (world_focus_y * self.zoom_level)