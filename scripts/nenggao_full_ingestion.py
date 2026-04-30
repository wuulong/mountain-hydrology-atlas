import sqlite3
import yaml
import os

def run_full_poc_ingestion():
    db_file = "events/mountain-hydrology/mountain-hydrology-atlas/practice/atlas_template.db"
    yaml_file = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_path_final.yaml"
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS atlas_nodes")
    cursor.execute("""
    CREATE TABLE atlas_nodes (
        id INTEGER PRIMARY KEY, 
        name TEXT, 
        category TEXT, 
        geom_wkt TEXT, 
        alt REAL, 
        slope_pct REAL,
        metadata TEXT
    )""")
    
    # 1. 注入「古道」 (2533 點)
    print("Ingesting Trail nodes...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    for n in data['nodes']:
        cursor.execute("INSERT INTO atlas_nodes (name, category, geom_wkt, alt, slope_pct, metadata) VALUES (?,?,?,?,?,?)",
                       (n['name'], 'Trail', n['geom_wkt'], n.get('alt'), n.get('slope_pct', 0), str(n.get('metadata'))))
    
    # 2. 注入「山」 (脊線關鍵點 - 根據之前的掃描)
    print("Ingesting Mountain nodes (Ridge Peaks)...")
    ridge_points = [
        ("能高主山主脊", "121.282 24.050", 3057.6),
        ("能高南峰主脊", "121.276 24.025", 2748.8),
    ]
    for name, wkt, alt in ridge_points:
        cursor.execute("INSERT INTO atlas_nodes (name, category, geom_wkt, alt, slope_pct) VALUES (?,?,?,?,?)",
                       (name, 'Mountain', f"POINT({wkt})", alt, 0))

    # 3. 注入「河」 (水文關鍵點)
    print("Ingesting River nodes (Water Sources)...")
    water_points = [
        ("天池水源", "121.286 24.028", 2827.0),
        ("萬大溪源頭", "121.270 24.050", 2500.0),
    ]
    for name, wkt, alt in water_points:
        cursor.execute("INSERT INTO atlas_nodes (name, category, geom_wkt, alt, slope_pct) VALUES (?,?,?,?,?)",
                       (name, 'River', f"POINT({wkt})", alt, 0))

    conn.commit()
    conn.close()
    print(f"\n[DONE] DB Refilled with Mountain, River, and Trail data.")

if __name__ == "__main__":
    run_full_poc_ingestion()
