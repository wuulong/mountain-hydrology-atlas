import yaml
import math

def calculate_distance(p1, p2):
    dx = (p1[0] - p2[0]) * 101000
    dy = (p1[1] - p2[1]) * 111000
    return math.sqrt(dx**2 + dy**2)

def rebuild_full_path(input_f, output_f):
    with open(input_f, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    nodes = data.get('nodes', [])
    if not nodes: return

    # 1. 座標去重 (防止原地打轉)
    unique_pool = {}
    for n in nodes:
        wkt = n['geom_wkt']
        if wkt not in unique_pool:
            coords = [float(x) for x in wkt.replace("POINT(", "").replace(")", "").strip().split()]
            unique_pool[wkt] = {'name': n['name'], 'coord': coords, 'alt': n.get('alt'), 'wkt': wkt}
    
    pool = list(unique_pool.values())
    # 2. 從最西邊發起 (屯原)
    pool.sort(key=lambda x: x['coord'][0])
    
    path = []
    current = pool.pop(0)
    path.append(current)
    
    while pool:
        best_dist = float('inf')
        best_idx = -1
        
        for i, target in enumerate(pool):
            d = calculate_distance(current['coord'], target['coord'])
            if d < best_dist:
                best_dist = d
                best_idx = i
        
        # 使用 200m 門檻，若斷開則從剩餘點中最西端重新發起
        if best_idx != -1 and best_dist < 200:
            current = pool.pop(best_idx)
            path.append(current)
        else:
            if pool:
                pool.sort(key=lambda x: x['coord'][0])
                current = pool.pop(0)
                path.append(current)
            else:
                break

    # 重新構建 YAML
    new_nodes = []
    for p in path:
        new_nodes.append({'name': p['name'], 'geom_wkt': p['wkt'], 'alt': p['alt']})
    
    data['nodes'] = new_nodes
    data['case_info']['status'] = "FULL_REBUILT"
    with open(output_f, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
    
    print(f"Original unique nodes: {len(unique_pool)}")
    print(f"Rebuilt full path: {len(new_nodes)} nodes.")

if __name__ == "__main__":
    rebuild_full_path("events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_full_dtm_nodes.yaml", 
                      "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_path_final.yaml")
