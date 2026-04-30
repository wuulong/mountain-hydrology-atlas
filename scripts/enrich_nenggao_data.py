import yaml
import math

def enrich_hydro_and_profile(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    nodes = data.get('nodes', [])
    if not nodes: return

    # 1. 補齊 metadata 欄位並標註關鍵水文耦合
    for i, n in enumerate(nodes):
        if 'metadata' not in n: n['metadata'] = {}
        
        # 尋找埡口點 (最高點)
        if i == 0: 
            max_node = max(nodes, key=lambda x: x.get('alt', 0))
            max_idx = nodes.index(max_node)
        
        if i == max_idx:
            n['metadata']['hydro_type'] = 'Pass'
            n['metadata']['stable_water'] = 'Tianchi'
            n['metadata']['hydro_coupling_score'] = 0.95

    # 2. 產出 ASCII 剖面圖
    profile_data = [n.get('alt', 0) for n in nodes if n.get('alt') is not None]
    if not profile_data: return

    # 取樣 60 點
    sample_size = 60
    step = max(1, len(profile_data) // sample_size)
    sampled = profile_data[::step][:sample_size]
    
    max_h = max(sampled)
    min_h = min(sampled)
    
    print("\n--- 能高古道高程剖面 (ASCII Profile) ---")
    print(f"最高: {max_h:.1f}m | 最低: {min_h:.1f}m")
    for h in range(int(max_h), int(min_h)-100, -200):
        row = f"{h:4d}m |"
        for val in sampled:
            row += "█" if val >= h else " "
        print(row)
    print("      " + "-" * len(sampled))
    
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)

if __name__ == "__main__":
    enrich_hydro_and_profile("events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_path_final.yaml")
