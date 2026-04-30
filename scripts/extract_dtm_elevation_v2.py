import os
import yaml
import subprocess
import glob
from osgeo import gdal

def get_bbox(tif_path):
    try:
        ds = gdal.Open(tif_path)
        if not ds: return None
        gt = ds.GetGeoTransform()
        # min_x, min_y, max_x, max_y
        x1 = gt[0]
        y1 = gt[3]
        x2 = gt[0] + ds.RasterXSize * gt[1]
        y2 = gt[3] + ds.RasterYSize * gt[5]
        return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
    except:
        return None

_dtm_cache = []

def get_alt_python(dtm_dir, lng, lat):
    global _dtm_cache
    if not _dtm_cache:
        search_path = os.path.join(dtm_dir, "*.tif")
        tifs = glob.glob(search_path)
        for tif in tifs:
            ds = gdal.Open(tif)
            if ds:
                gt = ds.GetGeoTransform()
                x1 = gt[0]
                y1 = gt[3]
                x2 = gt[0] + ds.RasterXSize * gt[1]
                y2 = gt[3] + ds.RasterYSize * gt[5]
                bbox = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                _dtm_cache.append({'path': tif, 'bbox': bbox, 'gt': gt})

    # Transform WGS84 to TWD97
    try:
        cmd = f"echo {lng} {lat} | gdaltransform -s_srs EPSG:4326 -t_srs EPSG:3826"
        res = subprocess.check_output(cmd, shell=True).decode().split()
        tx, ty = float(res[0]), float(res[1])
    except:
        return None

    for item in _dtm_cache:
        bbox = item['bbox']
        if bbox[0] <= tx <= bbox[2] and bbox[1] <= ty <= bbox[3]:
            try:
                ds = gdal.Open(item['path'])
                gt = item['gt']
                px = int((tx - gt[0]) / gt[1])
                py = int((ty - gt[3]) / gt[5])
                band = ds.GetRasterBand(1)
                # Ensure px, py are within raster size
                if 0 <= px < ds.RasterXSize and 0 <= py < ds.RasterYSize:
                    val = band.ReadAsArray(px, py, 1, 1)[0][0]
                    if val != -9999:
                        return float(val)
            except:
                continue
    return None

if __name__ == "__main__":
    dtm_path = "data/open-data/dtm/nenggao_combined/"
    input_f = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_auto_nodes.yaml"
    output_f = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_dtm_nodes_final.yaml"
    
    with open(input_f, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    nodes = data.get('nodes', [])
    print(f"Processing {len(nodes)} nodes using Python GDAL API...")
    
    count = 0
    for node in nodes:
        wkt = node['geom_wkt']
        parts = wkt.replace("POINT(", "").replace(")", "").strip().split()
        if len(parts) < 2: continue
        lng, lat = parts[0], parts[1]
        
        alt = get_alt_python(dtm_path, lng, lat)
        if alt is not None:
            node['alt'] = alt
            count += 1
            if count % 10 == 0:
                print(f"  [{count}] Matched {node['name']} -> {alt:.2f}m")

    with open(output_f, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
    print(f"Done! Matched {count}/{len(nodes)} nodes. Saved to {output_f}")
