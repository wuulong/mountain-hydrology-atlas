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

target_x = 279222
target_y = 2657836

print(f"Searching for TIF covering X={target_x}, Y={target_y}...")

# 搜尋 data 目錄
for root, dirs, files in os.walk("data"):
    for file in files:
        if file.endswith(".tif"):
            path = os.path.join(root, file)
            bbox = get_bbox(path)
            if bbox and bbox[0] <= target_x <= bbox[2] and bbox[1] <= target_y <= bbox[3]:
                print(f"MATCH FOUND: {path}")
                print(f"  BBox: {bbox}")
