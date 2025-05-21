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

        self.load_map_metadata()

        # Total map dimensions in pixels (at 1x zoom)
        self.full_map_pixel_width = self.grid_width_in_tiles * self.tile_pixel_width
        self.full_map_pixel_height = self.grid_height_in_tiles * self.tile_pixel_height

        self.zoom_level = 1.0
        self.offset_x = 0  # Top-left corner of the map relative to the screen's top-left
        self.offset_y = 0

    # Inside Map class in map_class.py
    # ... (other initializations) ...
    # self.collision_grid = [] # Already there

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

            # --- Load the collision grid ---
            self.collision_grid = metadata.get("collision_grid_data") # Use .get for safety
            if not self.collision_grid:
                print("Warning: Collision grid data not found in metadata or is empty.")
                print("Defaulting to all tiles walkable for safety (collision will be off).")
                # Create a default all-walkable grid if missing
                if self.grid_width_in_tiles > 0 and self.grid_height_in_tiles > 0:
                    self.collision_grid = [[0 for _ in range(self.grid_width_in_tiles)] for _ in range(self.grid_height_in_tiles)]
                else:
                    self.collision_grid = [] # Should not happen if other metadata loaded
            # --- End loading collision grid ---

            if not all([self.tile_pixel_width, self.tile_pixel_height, self.grid_width_in_tiles, self.grid_height_in_tiles, self.tile_filenames_grid]):
                raise ValueError("Metadata is missing essential tile information.")

            print(f"Map metadata loaded: Grid {self.grid_width_in_tiles}x{self.grid_height_in_tiles}, Tile Size: {self.tile_pixel_width}x{self.tile_pixel_height}px")
            if self.collision_grid:
                print(f"Collision grid loaded with dimensions: {len(self.collision_grid)}x{len(self.collision_grid[0]) if self.collision_grid else 0}")
        except FileNotFoundError:
            print(f"Error: Metadata file '{meta_file_path}' not found in '{self.tile_dir}'.")
            print("Please run the 'convert_map_to_tiles.py' script first.")
            self.collision_grid = [] # Ensure it's empty on error
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing metadata file '{meta_file_path}': {e}")
            self.collision_grid = [] # Ensure it's empty on error

    # The is_tile_walkable method you added previously should now work with this loaded grid.
    def is_tile_walkable(self, tile_x_idx, tile_y_idx):
        """Checks if a tile at given grid indices is walkable."""
        if not self.collision_grid: # Safety check if grid didn't load
            # print("Debug: is_tile_walkable called but no collision_grid exists. Defaulting to True.")
            return True # Or False, depending on desired safety behavior

        if 0 <= tile_y_idx < len(self.collision_grid) and \
        0 <= tile_x_idx < len(self.collision_grid[0]):
            return self.collision_grid[tile_y_idx][tile_x_idx] == 0 # 0 means walkable
        # print(f"Debug: is_tile_walkable called for out-of-bounds indices: x={tile_x_idx}, y={tile_y_idx}")
        return False # Out of bounds is not walkable

    def get_tile_image(self, tile_filename):
        """Loads a tile image if not cached, then returns it. Handles transparency."""
        if not tile_filename:
            return None
        if tile_filename not in self.tile_cache:
            try:
                tile_path = os.path.join(self.tile_dir, tile_filename)
                # Use convert_alpha() for images with transparency (like PNGs often have)
                # Use convert() if you are sure your tiles have no alpha.
                image = pygame.image.load(tile_path).convert_alpha()
                self.tile_cache[tile_filename] = image
            except pygame.error as e:
                print(f"Error loading tile image: {tile_filename} from {tile_path} - {e}")
                self.tile_cache[tile_filename] = None # Mark as failed
        return self.tile_cache[tile_filename]

    def draw(self):
        if not self.tile_filenames_grid or self.tile_pixel_width == 0:
            # print("No tile data to draw or tile size is zero.")
            return

        screen_rect = self.screen.get_rect()
        current_scaled_tile_width = int(self.tile_pixel_width * self.zoom_level)
        current_scaled_tile_height = int(self.tile_pixel_height * self.zoom_level)

        if current_scaled_tile_width <= 0 or current_scaled_tile_height <= 0:
            return # Cannot draw tiles with no size

        for row_idx, tile_row in enumerate(self.tile_filenames_grid):
            for col_idx, tile_filename in enumerate(tile_row):
                original_tile_surface = self.get_tile_image(tile_filename)
                if not original_tile_surface:
                    continue

                # Calculate tile's top-left position on the screen
                draw_x = self.offset_x + (col_idx * current_scaled_tile_width)
                draw_y = self.offset_y + (row_idx * current_scaled_tile_height)

                # Basic Culling: Check if the tile is on screen before scaling and blitting
                tile_on_screen_rect = pygame.Rect(draw_x, draw_y, current_scaled_tile_width, current_scaled_tile_height)
                if not screen_rect.colliderect(tile_on_screen_rect):
                    continue

                # Scale the tile if zoom level requires it
                if self.zoom_level == 1.0:
                    image_to_draw = original_tile_surface
                else:
                    # For better performance, you might cache scaled versions of tiles
                    # if zoom levels are discrete or change infrequently.
                    # pygame.transform.smoothscale is generally better quality for shrinking/growing
                    image_to_draw = pygame.transform.smoothscale(
                        original_tile_surface,
                        (current_scaled_tile_width, current_scaled_tile_height)
                    )
                
                self.screen.blit(image_to_draw, (draw_x, draw_y))

    def zoom(self, zoom_increment_factor, screen_focus_px, screen_focus_py):
        """
        Zooms the map, keeping the point (screen_focus_px, screen_focus_py)
        on the screen stable.
        """
        # World coordinates (pixels on the full unzoomed map) of the focus point before zoom
        world_focus_x = (screen_focus_px - self.offset_x) / self.zoom_level
        world_focus_y = (screen_focus_py - self.offset_y) / self.zoom_level

        self.zoom_level *= zoom_increment_factor
        self.zoom_level = max(0.1, min(self.zoom_level, 10.0)) # Clamp zoom

        # New offset to keep the world focus point at the same screen position
        self.offset_x = screen_focus_px - (world_focus_x * self.zoom_level)
        self.offset_y = screen_focus_py - (world_focus_y * self.zoom_level)