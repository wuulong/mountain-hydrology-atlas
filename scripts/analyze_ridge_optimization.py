import os
import glob
import subprocess
from osgeo import gdal

def get_alt_precise(dtm_dir, lng, lat):
    # 簡單的 BBox 匹配提取 (複用之前的邏輯)
    search_path = os.path.join(dtm_dir, "*.tif")
    tifs = glob.glob(search_path)
    
    # 座標轉換
    cmd = f"echo {lng} {lat} | gdaltransform -s_srs EPSG:4326 -t_srs EPSG:3826"
    res = subprocess.check_output(cmd, shell=True).decode().split()
    tx, ty = float(res[0]), float(res[1])

    for tif in tifs:
        ds = gdal.Open(tif)
        gt = ds.GetGeoTransform()
        x1, y1 = gt[0], gt[3]
        x2 = gt[0] + ds.RasterXSize * gt[1]
        y2 = gt[3] + ds.RasterYSize * gt[5]
        bbox = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        
        if bbox[0] <= tx <= bbox[2] and bbox[1] <= ty <= bbox[3]:
            px = int((tx - gt[0]) / gt[1])
            py = int((ty - gt[3]) / gt[5])
            val = ds.GetRasterBand(1).ReadAsArray(px, py, 1, 1)[0][0]
            if val != -9999: return val
    return None

def scan_ridge(dtm_dir):
    lng = 121.282 # 中央山脈主脊能高段概略經度
    results = []
    
    print(f"Scanning ridge at Longitude {lng} from Lat 23.95 to 24.10...")
    
    # 每 500 公尺掃描一個點 (約 0.005 度)
    for i in range(23950, 24101, 2):
        lat = i / 1000.0
        alt = get_alt_precise(dtm_dir, lng, lat)
        if alt:
            results.append((lat, alt))
            
    # 找出局部最小值 (Saddles)
    saddles = []
    for i in range(1, len(results) - 1):
        if results[i][1] < results[i-1][1] and results[i][1] < results[i+1][1]:
            saddles.append(results[i])
            
    print("\n--- 中央山脈脊線鞍部掃描結果 ---")
    for lat, alt in sorted(results):
        is_saddle = " <--- SADDLE" if (lat, alt) in saddles else ""
        print(f"  緯度 {lat:.3f}: 海拔 {alt:.1f}m {is_saddle}")
        
    if saddles:
        best_saddle = min(saddles, key=lambda x: x[1])
        print(f"\n最佳越嶺點建議: 緯度 {best_saddle[0]:.3f}, 海拔 {best_saddle[1]:.1f}m")
    else:
        print("\n未偵測到明顯鞍部，可能需要更高精度的掃描。")

if __name__ == "__main__":
    scan_ridge("data/open-data/dtm/nenggao_combined/")
