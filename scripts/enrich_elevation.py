import yaml
import requests
import time
import re

def get_elevation(lat, lng):
    """
    透過 Open-Elevation API 獲取高度。
    註：若點位過多，建議分批處理。
    """
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lng}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['results'][0]['elevation']
    except Exception as e:
        print(f"Error fetching elevation for {lat},{lng}: {e}")
    return None

def extract_coords(wkt):
    # 從 POINT(lng lat) 提取數值
    match = re.search(r'POINT\(([-\d.]+) ([-\d.]+)\)', wkt)
    if match:
        return match.group(1), match.group(2) # lng, lat
    return None, None

def enrich_yaml_elevation(input_yaml, output_yaml, limit=50):
    """
    更新 YAML 中的高度欄位。為了保護 API，預設限制處理前 50 個點。
    """
    with open(input_yaml, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    count = 0
    for node in data.get('nodes', []):
        if count >= limit:
            break
        
        lng, lat = extract_coords(node['geom_wkt'])
        if lat and lng:
            print(f"Fetching elevation for {node['name']} ({lat}, {lng})...")
            alt = get_elevation(lat, lng)
            if alt is not None:
                node['alt'] = alt
                print(f"  -> Success: {alt}m")
            
            count += 1
            time.sleep(0.5) # 禮貌性延遲

    with open(output_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    input_f = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_auto_nodes.yaml"
    output_f = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_enriched_nodes.yaml"
    enrich_yaml_elevation(input_f, output_f, limit=20) # 先跑 20 個點作為 POC
