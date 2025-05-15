from PIL import Image, ImageStat
import os
import json

# --- Configuration for Collision Detection ---
# Define what constitutes a "white" pixel (RGB values)
# Pure white is (255, 255, 255). We'll use a threshold.
WHITE_THRESHOLD_MIN_RGB_VALUE = 240 # Pixels with R, G, and B all >= this value are 'white'
# Percentage of 'white' pixels required for a tile to be considered walkable
WALKABLE_WHITE_PERCENTAGE_THRESHOLD = 0.85 # 85%

def is_pixel_white(pixel):
    """Checks if a pixel (RGB tuple) is considered white."""
    r, g, b = pixel[:3] # Handle RGBA by taking only RGB
    return r >= WHITE_THRESHOLD_MIN_RGB_VALUE and \
           g >= WHITE_THRESHOLD_MIN_RGB_VALUE and \
           b >= WHITE_THRESHOLD_MIN_RGB_VALUE

def analyze_tile_for_walkability(tile_image_crop):
    """
    Analyzes a PIL Image crop (representing a tile) to determine if it's walkable.
    Returns True if walkable (mostly white), False otherwise.
    """
    # Ensure image is in RGB mode for consistent pixel data
    if tile_image_crop.mode != 'RGB':
        tile_image_crop = tile_image_crop.convert('RGB')

    width, height = tile_image_crop.size
    total_pixels = width * height
    if total_pixels == 0:
        return False # Not walkable if no pixels

    white_pixel_count = 0
    for x in range(width):
        for y in range(height):
            if is_pixel_white(tile_image_crop.getpixel((x, y))):
                white_pixel_count += 1
    
    white_percentage = white_pixel_count / total_pixels
    return white_percentage >= WALKABLE_WHITE_PERCENTAGE_THRESHOLD


def convert_map_to_tiles(map_image_path, tile_width, tile_height, output_dir="tiles", meta_file_name="map_meta.json"):
    """
    Converts a map image into individual tiles, generates a collision grid based on white paths,
    and saves tile data and metadata.
    """
    try:
        map_image_pil = Image.open(map_image_path)
    except FileNotFoundError:
        print(f"Error: Map image not found at {map_image_path}")
        return None

    map_w, map_h = map_image_pil.size
    grid_width_tiles = map_w // tile_width
    grid_height_tiles = map_h // tile_height

    print(f"Map size: {map_w} x {map_h} pixels")
    print(f"Tile size: {tile_width} x {tile_height} pixels")
    print(f"Grid size: {grid_width_tiles} x {grid_height_tiles} tiles")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    generated_tile_filenames = []
    generated_collision_grid = [] # 0 for walkable, 1 for unwalkable

    for y_idx in range(grid_height_tiles):
        row_filenames = []
        row_collision_values = []
        for x_idx in range(grid_width_tiles):
            left = x_idx * tile_width
            top = y_idx * tile_height
            right = left + tile_width
            bottom = top + tile_height

            tile_crop_pil = map_image_pil.crop((left, top, right, bottom))
            
            # --- Save the tile image ---
            tile_filename = f"tile_{y_idx}_{x_idx}.png" # Consistent naming
            tile_path = os.path.join(output_dir, tile_filename)
            tile_crop_pil.save(tile_path)
            row_filenames.append(tile_filename)

            # --- Analyze for walkability ---
            if analyze_tile_for_walkability(tile_crop_pil):
                row_collision_values.append(0) # Walkable
            else:
                row_collision_values.append(1) # Unwalkable
            
        generated_tile_filenames.append(row_filenames)
        generated_collision_grid.append(row_collision_values)

    metadata = {
        "tile_pixel_width": tile_width,
        "tile_pixel_height": tile_height,
        "grid_width_in_tiles": grid_width_tiles,
        "grid_height_in_tiles": grid_height_tiles,
        "tile_filenames_grid": generated_tile_filenames,
        "collision_grid_data": generated_collision_grid # Add the collision grid
    }
    meta_file_path = os.path.join(output_dir, meta_file_name)
    try:
        with open(meta_file_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        print(f"Saved metadata (including collision grid) to: {meta_file_path}")
    except IOError as e:
        print(f"Error saving metadata file: {e}")
        return None

    print(f"Successfully converted map. Total tiles: {grid_width_tiles * grid_height_tiles}")
    # You can print a small part of the collision grid for verification:
    print("Generated Collision Grid (sample top-left 5x5):")
    for i in range(min(5, grid_height_tiles)):
        print(generated_collision_grid[i][:min(5, grid_width_tiles)])
        
    return generated_tile_filenames, generated_collision_grid

if __name__ == "__main__":
    # --- CONFIGURATION FOR TILING ---
    # Make sure your map image is in the same directory as this script,
    # or provide the full path.
    # The user's log indicated 'campus_map.png' was processed.
    map_image_file_to_process = "campus_map.png"
    
    desired_tile_pixel_width = 64 # Should match what your game expects
    desired_tile_pixel_height = 64
    output_tile_directory = "tiles"

    if not os.path.exists(map_image_file_to_process):
        print(f"Error: The map image '{map_image_file_to_process}' was not found.")
        print("Please ensure the image is present in the same directory or provide the correct path.")
    else:
        print(f"Processing '{map_image_file_to_process}' with tile size {desired_tile_pixel_width}x{desired_tile_pixel_height}...")
        print(f"Using White Threshold (RGB >= {WHITE_THRESHOLD_MIN_RGB_VALUE}) and Walkable Percentage (>= {WALKABLE_WHITE_PERCENTAGE_THRESHOLD*100}%)")
        
        result = convert_map_to_tiles(
            map_image_file_to_process,
            desired_tile_pixel_width,
            desired_tile_pixel_height,
            output_tile_directory
        )
        if result:
            print("Tile data and collision grid generation complete.")
        else:
            print("Tile data and collision grid generation failed.")