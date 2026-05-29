import json
import os
from shapely.geometry import shape, mapping

# Targets
submodule_root = "/Users/wuulong/github/bmad-pa/events/mountain-hydrology/mountain-hydrology-atlas"
targets = [
    "poc/20260501_nenggao_decipher/nenggao_real_streams.geojson",
    "qgis/data/nenggao_streams.geojson",
    "qgis/nenggao_streams.geojson"
]

def simplify_geojson_file(relative_path):
    full_path = os.path.join(submodule_root, relative_path)
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")
        return
        
    original_size = os.path.getsize(full_path) / (1024 * 1024)
    print(f"\nProcessing: {relative_path} (Original Size: {original_size:.2f} MB)...")
    
    with open(full_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    features = data.get("features", [])
    if not features:
        print("No features found in GeoJSON.")
        return
        
    # Auto-detect Tolerance based on coordinates
    # Let's inspect the first geometry's first coordinate
    sample_coord = None
    for feat in features:
        geom = feat.get("geometry")
        if geom and "coordinates" in geom:
            coords = geom["coordinates"]
            # drill down to get a single [x, y] coordinate
            while isinstance(coords, list) and len(coords) > 0 and isinstance(coords[0], list):
                coords = coords[0]
            if isinstance(coords, list) and len(coords) >= 2 and isinstance(coords[0], (int, float)):
                sample_coord = coords
                break
                
    if not sample_coord:
        print("Could not parse coordinates to auto-detect unit.")
        tolerance = 0.0001  # safe fallback (degrees)
    else:
        x, y = sample_coord
        if abs(x) < 360 and abs(y) < 360:
            # WGS84 Degrees
            tolerance = 0.0001  # ~10 meters
            print(f"--> Detected WGS84 coordinates ({x:.4f}, {y:.4f}). Setting tolerance to {tolerance} degrees (~10m).")
        else:
            # TWD97/UTM Meters
            tolerance = 5.0  # 5 meters
            print(f"--> Detected Projected coordinates ({x:.1f}, {y:.1f}). Setting tolerance to {tolerance} meters.")
            
    simplified_features = []
    simplified_count = 0
    
    for feat in features:
        geom = feat.get("geometry")
        if geom:
            try:
                # Convert to shapely shape
                geom_shape = shape(geom)
                # Simplify with preserve_topology=True to keep connectivity!
                simplified_shape = geom_shape.simplify(tolerance, preserve_topology=True)
                # Convert back to geojson format
                feat["geometry"] = mapping(simplified_shape)
                simplified_count += 1
            except Exception as e:
                print(f"Error simplifying a feature: {e}")
                
        simplified_features.append(feat)
        
    data["features"] = simplified_features
    
    # Overwrite the original file with formatted JSON (indent=2) or compact JSON
    # Compact JSON is better for Git file size
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        
    new_size = os.path.getsize(full_path) / (1024 * 1024)
    reduction = ((original_size - new_size) / original_size) * 100
    print(f"--> Completed! Simplified {simplified_count} features.")
    print(f"--> New Size: {new_size:.2f} MB (Reduced by {reduction:.1f}%!)")

if __name__ == "__main__":
    for target in targets:
        simplify_geojson_file(target)
    print("\n=== All target GeoJSON files automated simplification completed! ===")
