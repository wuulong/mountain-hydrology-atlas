-- mountain-hydrology-atlas Database Schema
-- Version: v0.1.1
-- Standards: WKT for geometry, JSON for metadata

-- 1. 地理節點表: 紀錄山峰、鞍部、河源等關鍵點位
CREATE TABLE IF NOT EXISTS geography_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,      -- 'Peak', 'Saddle', 'RiverSource', 'POI'
    mountain_range TEXT,      -- 所屬山脈
    watershed_a TEXT,         -- 分水嶺側 A 流域
    watershed_b TEXT,         -- 分水嶺側 B 流域
    geom_wkt TEXT,            -- 地理座標 (WKT 格式, e.g., 'POINT(121.1 23.5)')
    alt REAL,
    description TEXT,         -- 定性描述
    metadata_json TEXT,       -- 擴充元數據 (JSON 格式)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 歷史古道表: 紀錄古道基礎屬性與軌跡關聯
CREATE TABLE IF NOT EXISTS historical_trails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    trail_type TEXT,           -- 'PoliceTrail', 'HuntingPath', 'TradeRoute'
    total_length_km REAL,
    max_alt REAL,
    avg_slope_ratio REAL,
    geom_wkt TEXT,             -- 軌跡線條 (WKT 格式, e.g., 'LINESTRING(...)')
    kml_path TEXT,
    tr_link TEXT,
    metadata_json TEXT,        -- 擴充元數據 (JSON 格式)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 效率分析表: 紀錄古道相對於分水嶺鞍部的空間效率指標
CREATE TABLE IF NOT EXISTS efficiency_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trail_id INTEGER,
    saddle_id INTEGER,
    straight_slope REAL,
    actual_slope REAL,
    efficiency_index_e REAL,
    metadata_json TEXT,        -- 擴充元數據 (JSON 格式)
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trail_id) REFERENCES historical_trails(id),
    FOREIGN KEY (saddle_id) REFERENCES geography_nodes(id)
);

-- 4. 水文耦合表: 紀錄鞍部與兩側河源的空間連結關係
CREATE TABLE IF NOT EXISTS hydro_coupling (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    saddle_id INTEGER,
    source_a_id INTEGER,
    source_b_id INTEGER,
    dist_to_source_a REAL,
    dist_to_source_b REAL,
    alt_diff_a REAL,
    alt_diff_b REAL,
    coupling_score REAL,
    metadata_json TEXT,        -- 擴充元數據 (JSON 格式)
    FOREIGN KEY (saddle_id) REFERENCES geography_nodes(id),
    FOREIGN KEY (source_a_id) REFERENCES geography_nodes(id),
    FOREIGN KEY (source_b_id) REFERENCES geography_nodes(id)
);
