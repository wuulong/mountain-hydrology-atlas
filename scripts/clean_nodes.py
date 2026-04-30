import yaml

def clean_nodes(input_f, output_f):
    with open(input_f, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    nodes = data.get('nodes', [])
    if not nodes: return

    unique_nodes = []
    last_coord = None
    
    for node in nodes:
        coord = node['geom_wkt']
        # 簡單的經緯度比對去重
        if coord != last_coord:
            unique_nodes.append(node)
            last_coord = coord
    
    # 更新數據
    data['nodes'] = unique_nodes
    data['case_info']['status'] = "CLEANED"
    
    with open(output_f, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
    
    print(f"Original nodes: {len(nodes)}")
    print(f"Cleaned nodes: {len(unique_nodes)}")

if __name__ == "__main__":
    clean_nodes("events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_dtm_nodes_final.yaml", 
                "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_cleaned_nodes.yaml")
