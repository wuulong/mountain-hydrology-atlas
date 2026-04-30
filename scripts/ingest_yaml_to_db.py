import yaml
import sqlite3
import os

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # 建立節點表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS atlas_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        geom_wkt TEXT,
        alt REAL,
        slope_pct REAL,
        meta_data TEXT
    )
    """)
    conn.commit()
    return conn

def ingest_yaml(conn, yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    nodes = data.get('nodes', [])
    cursor = conn.cursor()
    
    print(f"Ingesting {len(nodes)} nodes into DB...")
    
    for i in range(len(nodes)):
        n = nodes[i]
        alt = n.get('alt')
        
        # 計算坡度 (簡單示範：與前一點對比)
        slope = 0
        if i > 0 and alt is not None and nodes[i-1].get('alt') is not None:
            # 這裡我們簡化處理，實際建議使用之前計算好的 slope_pct
            # 為了讓 QGIS 好看，我們先從 YAML 中提取
            slope = n.get('slope_pct', 0)
        
        cursor.execute("""
        INSERT INTO atlas_nodes (name, geom_wkt, alt, slope_pct, meta_data)
        VALUES (?, ?, ?, ?, ?)
        """, (n['name'], n['geom_wkt'], alt, slope, str(n.get('metadata', {}))))
        
    conn.commit()
    print("Ingestion complete.")

def purge_db(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM atlas_nodes")
    # 重置自增 ID
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='atlas_nodes'")
    conn.commit()
    print("Database cleared. Template mode active.")

if __name__ == "__main__":
    db_file = "events/mountain-hydrology/mountain-hydrology-atlas/practice/atlas_template.db"
    yaml_file = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_path_final.yaml"
    
    # 1. 初始化
    connection = init_db(db_file)
    
    # 2. 寫入 (驗證)
    ingest_yaml(connection, yaml_file)
    
    # 3. 檢查 (範例查詢)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM atlas_nodes")
    print(f"Verification: DB now has {cursor.fetchone()[0]} nodes.")
    
    # 4. 清空 (根據使用者需求，進入模版模式)
    # purge_db(connection)
    
    connection.close()
