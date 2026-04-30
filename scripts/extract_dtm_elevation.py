import os
import glob
import re
import yaml
import subprocess

def wgs84_to_twd97(lng, lat):
    """
    簡單的座標轉換（近似值），用於篩選磁磚。
    實際提取高度時，建議使用 gdallocationinfo 並指定 -wgs84。
    """
    # 這裡省略複雜轉換，直接使用 gdal 的功能
    return lng, lat

def get_alt_from_dtm_dir(dtm_dir, lng, lat):
    """
    遍歷目錄，先將 GRD 轉為臨時 TIF 再查詢高度。
    """
    for grd_tile in glob.glob(os.path.join(dtm_dir, "9620*.grd")):
        tif_tile = grd_tile.replace(".grd", ".tif")
        
        # 如果還沒轉換過，先轉成 TIF
        if not os.path.exists(tif_tile):
            try:
                subprocess.run(f"gdal_translate -q \"{grd_tile}\" \"{tif_tile}\"", shell=True, check=True)
            except:
                continue

        # 使用 gdallocationinfo 查詢
        cmd = f"gdallocationinfo -wgs84 -valonly \"{tif_tile}\" {lng} {lat}"
        try:
            result = subprocess.check_output(cmd, shell=True).decode().strip()
            if result and result != "-9999":
                return float(result)
        except:
            continue
    return None

def extract_coords(wkt):
    match = re.search(r'POINT\(([-\d.]+) ([-\d.]+)\)', wkt)
    if match:
        return match.group(1), match.group(2)
    return None, None

def process_nenggao_elevation(input_yaml, dtm_dir, output_yaml, limit=30):
    with open(input_yaml, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    count = 0
    for node in data.get('nodes', []):
        if count >= limit: break
        
        lng, lat = extract_coords(node['geom_wkt'])
        if lng and lat:
            print(f"Checking DTM for {node['name']} at {lng}, {lat}...")
            alt = get_alt_from_dtm_dir(dtm_dir, lng, lat)
            if alt:
                node['alt'] = alt
                print(f"  -> Found in DTM: {alt}m")
            else:
                print(f"  -> Not found in current DTM tiles.")
            count += 1

    with open(output_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    dtm_path = "data/open-data/dtm/moi_hualien_dtm_2024_20m_zip/"
    input_f = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_auto_nodes.yaml"
    output_f = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_dtm_nodes.yaml"
    
    process_nenggao_elevation(input_f, dtm_path, output_f)
