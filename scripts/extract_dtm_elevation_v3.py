import os
import yaml
import subprocess
import glob
from osgeo import gdal

def get_alt_batch(dtm_dir, nodes):
    # 1. 預加載 BBox 快取
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

    # 2. 批次座標轉換 (EPSG:4326 -> 3826)
    wkt_input = "\n".join([n['geom_wkt'].replace("POINT(", "").replace(")", "") for n in nodes])
    cmd = "gdaltransform -s_srs EPSG:4326 -t_srs EPSG:3826"
    process = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = process.communicate(input=wkt_input)
    
    transformed_coords = []
    for line in out.strip().split("\n"):
        parts = line.split()
        if len(parts) >= 2:
            transformed_coords.append((float(parts[0]), float(parts[1])))

    # 3. 提取高程
    count = 0
    for i, node in enumerate(nodes):
        if i >= len(transformed_coords): break
        tx, ty = transformed_coords[i]
        
        found = False
        for item in cache:
            bbox = item['bbox']
            if bbox[0] <= tx <= bbox[2] and bbox[1] <= ty <= bbox[3]:
                ds = gdal.Open(item['path'])
                gt = item['gt']
                px = int((tx - gt[0]) / gt[1])
                py = int((ty - gt[3]) / gt[5])
                if 0 <= px < ds.RasterXSize and 0 <= py < ds.RasterYSize:
                    val = ds.GetRasterBand(1).ReadAsArray(px, py, 1, 1)[0][0]
                    if val != -9999:
                        node['alt'] = float(val)
                        found = True
                        count += 1
                        break
        if not found:
            node['alt'] = None
        
        if (i+1) % 500 == 0:
            print(f"  Processed {i+1}/{len(nodes)} nodes...")

    return count

if __name__ == "__main__":
    dtm_path = "data/open-data/dtm/nenggao_combined/"
    input_f = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_full_nodes.yaml"
    output_f = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_full_dtm_nodes.yaml"
    
    with open(input_f, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    nodes = data.get('nodes', [])
    print(f"Injecting elevation for {len(nodes)} nodes...")
    matched = get_alt_batch(dtm_path, nodes)
    
    with open(output_f, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
    print(f"Done! Matched {matched}/{len(nodes)} nodes. Saved to {output_f}")
