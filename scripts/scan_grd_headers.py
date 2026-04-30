import os
import glob

def get_grd_header_bbox(grd_path):
    """
    讀取 ASCII Grid Header 並計算 BBox.
    格式通常為:
    ncols         132
    nrows         143
    xllcorner     276210
    yllcorner     2652050
    cellsize      20
    NODATA_value  -9999
    """
    header = {}
    try:
        with open(grd_path, 'r') as f:
            for _ in range(6):
                line = f.readline().split()
                if len(line) == 2:
                    header[line[0].lower()] = float(line[1])
        
        min_x = header['xllcorner']
        min_y = header['yllcorner']
        cellsize = header['cellsize']
        max_x = min_x + header['ncols'] * cellsize
        max_y = min_y + header['nrows'] * cellsize
        return (min_x, min_y, max_x, max_y)
    except:
        return None

target_x = 279222
target_y = 2657836

print(f"Scanning GRD files for X={target_x}, Y={target_y}...")

dtm_dir = "data/open-data/dtm/moi_hualien_dtm_2024_20m_zip/"
for grd in glob.glob(os.path.join(dtm_dir, "9620*.grd")):
    bbox = get_grd_header_bbox(grd)
    if bbox and bbox[0] <= target_x <= bbox[2] and bbox[1] <= target_y <= bbox[3]:
        print(f"MATCH FOUND: {grd}")
        print(f"  BBox: {bbox}")
