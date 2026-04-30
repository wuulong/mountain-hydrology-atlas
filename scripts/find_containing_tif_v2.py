import os
import glob
from osgeo import gdal

def get_bbox(tif_path):
    try:
        ds = gdal.Open(tif_path)
        if not ds: return None
        gt = ds.GetGeoTransform()
        min_x = gt[0]
        max_y = gt[3]
        max_x = gt[0] + ds.RasterXSize * gt[1]
        min_y = gt[3] + ds.RasterYSize * gt[5]
        if min_y > max_y: min_y, max_y = max_y, min_y
        if min_x > max_x: min_x, max_x = max_x, min_x
        return (min_x, min_y, max_x, max_y)
    except:
        return None

# 能高越嶺道某點 (TWD97 近似值)
target_x = 282800
target_y = 2658100

print(f"Searching in nenggao_combined for X={target_x}, Y={target_y}...")

combined_dir = "data/open-data/dtm/nenggao_combined/"
for tif in glob.glob(os.path.join(combined_dir, "*.tif")):
    bbox = get_bbox(tif)
    if bbox and bbox[0] <= target_x <= bbox[2] and bbox[1] <= target_y <= bbox[3]:
        print(f"MATCH FOUND: {tif}")
        print(f"  BBox: {bbox}")
