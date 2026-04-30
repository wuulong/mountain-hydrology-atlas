import os
import xml.etree.ElementTree as ET
import yaml
from pathlib import Path

def parse_kml_to_triad(kml_path, output_yaml):
    """
    將 KML 檔案中的點位提取為三柱架構所需的 YAML 格式草稿。
    """
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    tree = ET.parse(kml_path)
    root = tree.getroot()

    nodes = []
    
    # 搜尋所有 Placemark
    for pm in root.findall('.//kml:Placemark', ns):
        name = pm.find('kml:name', ns)
        name_text = name.text if name is not None else "Unnamed Node"
        
        # 尋找 Point
        point = pm.find('.//kml:Point/kml:coordinates', ns)
        if point is not None:
            coords = point.text.strip().split(',')
            if len(coords) >= 2:
                lng, lat = coords[0], coords[1]
                nodes.append({
                    'name': name_text,
                    'type': 'POI',
                    'geom_wkt': f"POINT({lng} {lat})",
                    'metadata': {'source': 'kml_point'}
                })
        
        # 尋找 LineString (提取起點與終點)
        lines = pm.findall('.//kml:LineString/kml:coordinates', ns)
        for line in lines:
            coord_list = line.text.strip().split()
            if coord_list:
                # 提取起點
                start_coords = coord_list[0].split(',')
                nodes.append({
                    'name': f"{name_text}_START",
                    'type': 'PathNode',
                    'geom_wkt': f"POINT({start_coords[0]} {start_coords[1]})",
                    'metadata': {'source': 'kml_line_start'}
                })
                # 提取終點
                end_coords = coord_list[-1].split(',')
                nodes.append({
                    'name': f"{name_text}_END",
                    'type': 'PathNode',
                    'geom_wkt': f"POINT({end_coords[0]} {end_coords[1]})",
                    'metadata': {'source': 'kml_line_end'}
                })

    # 封裝為 YAML
    data = {
        'case_info': {
            'source_file': os.path.basename(kml_path),
            'status': 'EXTRACTED'
        },
        'nodes': nodes
    }

    with open(output_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    # 預設範例：能高古道
    kml_file = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_trail_unzipped/doc.kml"
    output_file = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_auto_nodes.yaml"
    
    if os.path.exists(kml_file):
        parse_kml_to_triad(kml_file, output_file)
        print(f"Successfully extracted nodes to {output_file}")
    else:
        print(f"Error: {kml_file} not found.")
