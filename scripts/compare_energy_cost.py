import os
import glob
import subprocess
from osgeo import gdal

def get_alt_batch(dtm_dir, pts):
    search_path = os.path.join(dtm_dir, "*.tif")
    tifs = glob.glob(search_path)
    cache = []
    for tif in tifs:
        ds = gdal.Open(tif)
        if not ds: continue
        gt = ds.GetGeoTransform()
        x1, y1 = gt[0], gt[3]
        x2 = gt[0] + ds.RasterXSize * gt[1]
        y2 = gt[3] + ds.RasterYSize * gt[5]
        cache.append({'path': tif, 'bbox': (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)), 'gt': gt})

    wkt_input = "\n".join([f"{p[0]} {p[1]}" for p in pts])
    cmd = "gdaltransform -s_srs EPSG:4326 -t_srs EPSG:3826"
    process = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = process.communicate(input=wkt_input)
    transformed = [line.split() for line in out.strip().split("\n")]
    
    results = []
    for i, _ in enumerate(pts):
        tx, ty = float(transformed[i][0]), float(transformed[i][1])
        alt = None
        for item in cache:
            if item['bbox'][0] <= tx <= item['bbox'][2] and item['bbox'][1] <= ty <= item['bbox'][3]:
                ds = gdal.Open(item['path'])
                gt = item['gt']
                px = int((tx - gt[0]) / gt[1])
                py = int((ty - gt[3]) / gt[5])
                val = ds.GetRasterBand(1).ReadAsArray(px, py, 1, 1)[0][0]
                if val != -9999: alt = float(val); break
        results.append(alt)
    return results

def compare_energy_cost(dtm_dir):
    start = (121.215, 24.050) # 屯原
    target_a = (121.282, 24.024) # 能高埡口 (2800m)
    target_b = (121.294, 24.095) # 北方低點 (2200m)
    
    # 模擬直線路徑的高程剖面
    def get_profile_stats(p1, p2):
        steps = 50
        pts = []
        for i in range(steps + 1):
            lng = p1[0] + (p2[0] - p1[0]) * i / steps
            lat = p1[1] + (p2[1] - p1[1]) * i / steps
            pts.append((lng, lat))
        
        alts = get_alt_batch(dtm_dir, pts)
        alts = [a for a in alts if a is not None]
        
        climb = 0
        for i in range(1, len(alts)):
            if alts[i] > alts[i-1]:
                climb += (alts[i] - alts[i-1])
        return climb, max(alts), min(alts)

    climb_a, max_a, min_a = get_profile_stats(start, target_a)
    climb_b, max_b, min_b = get_profile_stats(start, target_b)
    
    print(f"--- 能量成本對比報告 (Energy Budget) ---")
    print(f"路徑 A (能高埡口): 總爬升 {climb_a:.1f}m, 最高點 {max_a:.1f}m, 最低點 {min_a:.1f}m")
    print(f"路徑 B (北方低點): 總爬升 {climb_b:.1f}m, 最高點 {max_b:.1f}m, 最低點 {min_b:.1f}m")
    
    if climb_a < climb_b:
        print(f"\n結論: 能高古道雖然終點海拔較高，但路徑更為『一氣呵成』，總功耗更低。")
    else:
        print(f"\n結論: 北方低點在能量上具備優勢，其未被選中可能源於地形破碎、水源或政治因素。")

if __name__ == "__main__":
    compare_energy_cost("data/open-data/dtm/nenggao_combined/")
