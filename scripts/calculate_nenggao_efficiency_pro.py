import yaml
import math

def calculate_distance(p1, p2):
    dx = (p1[0] - p2[0]) * 101000
    dy = (p1[1] - p2[1]) * 111000
    return math.sqrt(dx**2 + dy**2)

def run_analysis_pro(input_f):
    with open(input_f, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    nodes = data.get('nodes', [])
    if not nodes: return

    # 1. 解析度對齊：合併過短的線段 (小於 20m)
    aligned_nodes = [nodes[0]]
    for i in range(1, len(nodes)):
        p1 = [float(x) for x in aligned_nodes[-1]['geom_wkt'].replace("POINT(", "").replace(")", "").split()]
        p2 = [float(x) for x in nodes[i]['geom_wkt'].replace("POINT(", "").replace(")", "").split()]
        if calculate_distance(p1, p2) > 20: # DTM 解析度閥值
            aligned_nodes.append(nodes[i])
    
    print(f"Aligned nodes (20m filter): {len(nodes)} -> {len(aligned_nodes)}")

    total_dist = 0
    total_climb = 0
    total_descent = 0
    segments = []

    for i in range(len(aligned_nodes) - 1):
        n1, n2 = aligned_nodes[i], aligned_nodes[i+1]
        p1 = [float(x) for x in n1['geom_wkt'].replace("POINT(", "").replace(")", "").split()]
        p2 = [float(x) for x in n2['geom_wkt'].replace("POINT(", "").replace(")", "").split()]
        
        alt1 = n1.get('alt')
        alt2 = n2.get('alt')
        
        if alt1 is None or alt2 is None: continue

        dist = calculate_distance(p1, p2)
        dh = alt2 - alt1
        slope = (dh / dist) if dist > 0 else 0
        
        total_dist += dist
        if dh > 0: total_climb += dh
        else: total_descent += abs(dh)

        segments.append({
            'from': n1['name'],
            'to': n2['name'],
            'dist': dist,
            'dh': dh,
            'slope_pct': slope * 100
        })

    # 計算整體效率 E
    start_p = [float(x) for x in aligned_nodes[0]['geom_wkt'].replace("POINT(", "").replace(")", "").split()]
    end_p = [float(x) for x in aligned_nodes[-1]['geom_wkt'].replace("POINT(", "").replace(")", "").split()]
    direct_dist = calculate_distance(start_p, end_p)
    direct_climb = aligned_nodes[-1]['alt'] - aligned_nodes[0]['alt']
    
    actual_climb_sum = total_climb + total_descent
    actual_avg_slope = actual_climb_sum / total_dist if total_dist > 0 else 0
    direct_slope = direct_climb / direct_dist if direct_dist > 0 else 0
    
    efficiency = (abs(direct_slope) / actual_avg_slope) * (direct_dist / total_dist) if actual_avg_slope > 0 else 0

    print(f"\n--- 能高越嶺道 POC 效率分析報告 (Pro) ---")
    print(f"有效路徑距離: {total_dist/1000:.2f} km")
    print(f"直線距離: {direct_dist/1000:.2f} km")
    print(f"有效累積爬升: {total_climb:.1f} m")
    print(f"有效累積下降: {total_descent:.1f} m (大幅減少，代表消除雜訊)")
    print(f"修正後平均坡度: {actual_avg_slope*100:.2f}%")
    print(f"越嶺效率指標 (E): {efficiency:.4f}")
    
    steepest = sorted(segments, key=lambda x: abs(x['slope_pct']), reverse=True)[:5]
    print(f"\n最陡路段排行 (Top 5):")
    for s in steepest:
        print(f"  {s['from']} -> {s['to']}: {s['slope_pct']:.2f}% (Dist: {s['dist']:.1f}m)")

if __name__ == "__main__":
    run_analysis_pro("events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_path_final.yaml")
