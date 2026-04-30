import os
import glob
import subprocess
from osgeo import gdal

def get_alt_batch(dtm_dir, pts):
    # 優化版批次提取
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
    for i, (lng, lat) in enumerate(pts):
        tx, ty = float(transformed[i][0]), float(transformed[i][1])
        alt = None
        for item in cache:
            if item['bbox'][0] <= tx <= item['bbox'][2] and item['bbox'][1] <= ty <= item['bbox'][3]:
                ds = gdal.Open(item['path'])
                gt = item['gt']
                px = int((tx - gt[0]) / gt[1])
                py = int((ty - gt[3]) / gt[5])
                val = ds.GetRasterBand(1).ReadAsArray(px, py, 1, 1)[0][0]
                if val != -9999:
                    alt = float(val)
                    break
        results.append(alt)
    return results

def find_true_saddles(dtm_dir):
    # 緯度範圍: 能高周邊 15km
    lat_range = [i/1000.0 for i in range(23950, 24101, 5)] # 500m 間隔
    lng_range = [i/1000.0 for i in range(121250, 121301, 2)] # 200m 間隔
    
    print(f"Analyzing {len(lat_range)} latitude slices...")
    
    ridge_peaks = []
    
    for lat in lat_range:
        pts = [(lng, lat) for lng in lng_range]
        alts = get_alt_batch(dtm_dir, pts)
        valid_alts = [a for a in alts if a is not None]
        if valid_alts:
            max_alt = max(valid_alts)
            # 找到最大值對應的經度
            max_lng = lng_range[alts.index(max_alt)]
            ridge_peaks.append((lat, max_lng, max_alt))
            
    # 尋找 ridge_peaks 中的局部最小值 (Saddles)
    print("\n--- 中央山脈動態脊線掃描結果 (Peaks per Latitude) ---")
    saddles = []
    for i in range(1, len(ridge_peaks) - 1):
        if ridge_peaks[i][2] < ridge_peaks[i-1][2] and ridge_peaks[i][2] < ridge_peaks[i+1][2]:
            saddles.append(ridge_peaks[i])
            
    for lat, lng, alt in sorted(ridge_peaks):
        is_saddle = " <--- SADDLE" if (lat, lng, alt) in saddles else ""
        print(f"  緯度 {lat:.3f}: 脊線高度 {alt:.1f}m (Lng: {lng:.3f}) {is_saddle}")

    if saddles:
        best_saddle = min(saddles, key=lambda x: x[2])
        print(f"\n最佳地理鞍部: 緯度 {best_saddle[0]:.3f}, 經度 {best_saddle[1]:.3f}, 海拔 {best_saddle[2]:.1f}m")
    
if __name__ == "__main__":
    find_true_saddles("data/open-data/dtm/nenggao_combined/")
