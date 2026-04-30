import xml.etree.ElementTree as ET
import yaml

def extract_full_nodes(kml_path, output_f):
    tree = ET.parse(kml_path)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    nodes = []
    
    # 尋找所有 LineString
    for ls in root.findall('.//kml:LineString', ns):
        coords_text = ls.find('kml:coordinates', ns).text.strip()
        points = coords_text.split()
        
        for i, p in enumerate(points):
            parts = p.split(',')
            if len(parts) < 2: continue
            lng, lat = parts[0], parts[1]
            
            nodes.append({
                'name': f"能高越嶺道_V{len(nodes)}",
                'type': 'PathNode',
                'geom_wkt': f"POINT({lng} {lat})",
                'metadata': {
                    'source': 'kml_vertex',
                    'original_index': i
                }
            })

    data = {
        'case_info': {
            'source_file': 'doc.kml',
            'status': 'FULL_EXTRACTED'
        },
        'nodes': nodes
    }

    with open(output_f, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
    
    print(f"Extracted {len(nodes)} full vertices from KML.")

if __name__ == "__main__":
    extract_full_nodes('events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_trail_unzipped/doc.kml',
                      'events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_full_nodes.yaml')
