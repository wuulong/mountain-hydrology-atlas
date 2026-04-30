import yaml
import math

def calculate_distance(p1, p2):
    """使用 TWD97 (或簡單歐幾里得) 計算兩點距離，單位：公尺"""
    # 這裡假設傳入的是 WGS84，簡單使用 Haversine 或近似公式
    # 由於點位極近，使用近似常數即可
    # 1 deg lat ~ 111000m, 1 deg lng ~ 101000m (at 24N)
    dx = (p1[0] - p2[0]) * 101000
    dy = (p1[1] - p2[1]) * 111000
    return math.sqrt(dx**2 + dy**2)

def run_analysis(input_f):
    with open(input_f, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    nodes = data.get('nodes', [])
    if not nodes: return

    total_dist = 0
    total_climb = 0
    total_descent = 0
    segments = []

    for i in range(len(nodes) - 1):
        n1, n2 = nodes[i], nodes[i+1]
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

    # 計算整體效率 E (假設起點為 nodes[0], 終點為最後一個點)
    start_p = [float(x) for x in nodes[0]['geom_wkt'].replace("POINT(", "").replace(")", "").split()]
    end_p = [float(x) for x in nodes[-1]['geom_wkt'].replace("POINT(", "").replace(")", "").split()]
    direct_dist = calculate_distance(start_p, end_p)
    direct_climb = nodes[-1]['alt'] - nodes[0]['alt']
    
    actual_avg_slope = (total_climb + total_descent) / total_dist if total_dist > 0 else 0
    direct_slope = direct_climb / direct_dist if direct_dist > 0 else 0
    
    # 效率指標 E = (直攻坡度 / 實際路徑坡度) x (直線距離 / 實際路徑距離)
    # 這裡的實際路徑坡度我們取絕對值總和的平均
    efficiency = (abs(direct_slope) / actual_avg_slope) * (direct_dist / total_dist) if actual_avg_slope > 0 else 0

    print(f"--- 能高越嶺道 POC 效率分析報告 ---")
    print(f"總路徑距離: {total_dist/1000:.2f} km")
    print(f"直線距離: {direct_dist/1000:.2f} km (路徑彎曲率: {total_dist/direct_dist:.2f})")
    print(f"累積爬升: {total_climb:.1f} m")
    print(f"累積下降: {total_descent:.1f} m (無謂高程損失指標)")
    print(f"實際平均坡度: {actual_avg_slope*100:.2f}%")
    print(f"理想指標 (日治警備道): 10.00%")
    print(f"越嶺效率指標 (E): {efficiency:.4f}")
    
    # 找出最陡路段
    steepest = sorted(segments, key=lambda x: abs(x['slope_pct']), reverse=True)[:5]
    print(f"\n最陡路段排行 (Top 5):")
    for s in steepest:
        print(f"  {s['from']} -> {s['to']}: {s['slope_pct']:.2f}% (Dist: {s['dist']:.1f}m)")

if __name__ == "__main__":
    run_analysis("events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_path_final.yaml")
