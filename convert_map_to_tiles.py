# convert_map_to_tiles.py
from PIL import Image
import os
import json

def slice_map_into_visual_tiles(map_image_path, tile_width, tile_height, output_dir="tiles", meta_file_name="map_meta.json"):
    """
    Slices a map image into individual visual tiles and saves basic metadata.
    Collision data is NOT generated here; it will come from Tiled.
    """
    try:
        map_image_pil = Image.open(map_image_path)
        print(f"Successfully opened image: {map_image_path}")
    except FileNotFoundError:
        print(f"Error: Map image not found at {map_image_path}")
        return None
    except Exception as e:
        print(f"Error opening image {map_image_path}: {e}")
        return None

    map_w, map_h = map_image_pil.size
    grid_width_tiles = map_w // tile_width
    grid_height_tiles = map_h // tile_height

    print(f"Map original size: {map_w}x{map_h} pixels")
    print(f"Tile size: {tile_width}x{tile_height} pixels")
    print(f"Grid dimensions: {grid_width_tiles}x{grid_height_tiles} tiles")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    else: # Clear out old tiles if directory exists, to prevent mix-ups
        for f_name in os.listdir(output_dir):
            if f_name.startswith("tile_") and f_name.endswith(".png"):
                try:
                    os.remove(os.path.join(output_dir, f_name))
                except OSError as e:
                    print(f"Could not remove old tile {f_name}: {e}")
        print(f"Cleaned old visual tiles from {output_dir}")


    generated_tile_filenames = []
    for y_idx in range(grid_height_tiles):
        row_filenames = []
        for x_idx in range(grid_width_tiles):
            left = x_idx * tile_width
            top = y_idx * tile_height
            right = left + tile_width
            bottom = top + tile_height

            tile_crop_pil = map_image_pil.crop((left, top, right, bottom))
            tile_filename = f"tile_{y_idx}_{x_idx}.png"
            tile_path = os.path.join(output_dir, tile_filename)
            
            try:
                tile_crop_pil.save(tile_path, "PNG")
            except Exception as e:
                print(f"Error saving tile {tile_path}: {e}")
                row_filenames.append(None) # Placeholder for failed tile
                continue
            row_filenames.append(tile_filename)
            
        generated_tile_filenames.append(row_filenames)

    # Basic metadata: visual tile info. Collision grid will be added later.
    metadata = {
        "tile_pixel_width": tile_width,
        "tile_pixel_height": tile_height,
        "grid_width_in_tiles": grid_width_tiles,
        "grid_height_in_tiles": grid_height_tiles,
        "tile_filenames_grid": generated_tile_filenames,
        "collision_grid_data": [] # Placeholder - to be populated by tiled_importer.py
    }
    meta_file_path = os.path.join(output_dir, meta_file_name)
    try:
        with open(meta_file_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        print(f"Saved initial visual metadata to: {meta_file_path}")
    except IOError as e:
        print(f"Error saving metadata file: {e}")
        return None

    print(f"Successfully sliced map into visual tiles. Total tiles: {grid_width_tiles * grid_height_tiles}")
    return metadata

if __name__ == "__main__":
    # IMPORTANT: Convert your campus_map.jpg to campus_map.png first for best results.
    # Ensure this image is in the same directory as this script.
    map_image_file_to_process = "campus_map.png" 
    
    # Define your desired tile size. This MUST match what you use in Tiled.
    desired_tile_pixel_width = 32 
    desired_tile_pixel_height = 32
    output_tile_directory = "tiles" # Tiles and map_meta.json will be saved here

    if not os.path.exists(map_image_file_to_process):
        print(f"Error: The map image '{map_image_file_to_process}' was not found.")
        print("Please ensure the image (preferably a .png version) is present and named correctly.")
    else:
        print(f"Processing '{map_image_file_to_process}' for visual tiles with tile size {desired_tile_pixel_width}x{desired_tile_pixel_height}...")
        
        # Delete old metadata if it exists, as it's an initial generation
        meta_file_to_delete = os.path.join(output_tile_directory, "map_meta.json")
        if os.path.exists(meta_file_to_delete):
            try:
                os.remove(meta_file_to_delete)
                print(f"Deleted old metadata file: {meta_file_to_delete} for fresh generation.")
            except OSError as e:
                print(f"Error deleting old metadata file {meta_file_to_delete}: {e}")

        result_meta = slice_map_into_visual_tiles(
            map_image_file_to_process,
            desired_tile_pixel_width,
            desired_tile_pixel_height,
            output_tile_directory
        )
        if result_meta:
            print("Visual tile slicing and initial metadata generation complete.")
            print(f"Next step: Use Tiled to create your collision layer, then run 'tiled_importer.py'.")
        else:
            print("Visual tile slicing failed.")