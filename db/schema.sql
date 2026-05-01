-- mountain-hydrology-atlas Database Schema
-- Version: v0.1.1
-- Standards: WKT for geometry, JSON for metadata

-- 1. 地理節點表: 紀錄山峰、鞍部、河源、部落聚落等關鍵點位
CREATE TABLE IF NOT EXISTS geography_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,      -- 'Peak', 'Saddle', 'RiverSource', 'Settlement', 'Relic', 'POI'
    external_ref_id TEXT,    -- 外部資料庫關聯 ID (如: indigenous_db_communities_001)
    external_ref_type TEXT,  -- 外部資料庫類型 (如: 'IndigenousDB')
    mountain_range TEXT,      -- 所屬山脈
    watershed_a TEXT,         -- 分水嶺側 A 流域
    watershed_b TEXT,         -- 分水嶺側 B 流域
    geom_wkt TEXT,            -- 地理座標 (WKT 格式)
    alt REAL,
    description TEXT,         -- 定性描述
    metadata_json TEXT,       -- 擴充元數據 (JSON 格式)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 歷史古道表: 紀錄古道基礎屬性
CREATE TABLE IF NOT EXISTS historical_trails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    trail_type TEXT,           -- 'PoliceTrail', 'HuntingPath', 'TradeRoute'
    traditional_territory TEXT, 
    total_length_km REAL,
    geom_wkt TEXT,             
    metadata_json TEXT,        
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. [NEW] 古道路段表: 紀錄路網拓樸與流量熱度 (Hot Paths)
CREATE TABLE IF NOT EXISTS trail_segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trail_id INTEGER,
    start_node_id INTEGER,     -- 起始節點 (geography_nodes.id)
    end_node_id INTEGER,       -- 終止節點 (geography_nodes.id)
    segment_length REAL,
    traffic_load_index INTEGER, -- 流量負荷指數 (服務部落數)
    centrality_score REAL,      -- 中介中心性評分
    geom_wkt TEXT,              -- 段落幾何
    FOREIGN KEY (trail_id) REFERENCES historical_trails(id),
    FOREIGN KEY (start_node_id) REFERENCES geography_nodes(id),
    FOREIGN KEY (end_node_id) REFERENCES geography_nodes(id)
);

-- 5. [NEW] 高精度頂點表: 支撐能量預算
CREATE TABLE IF NOT EXISTS trail_vertices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trail_id INTEGER,
    vertex_index INTEGER,      -- 頂點順序 (0 to N)
    dist_from_start REAL,      -- 距起點之累積距離 (m)
    alt_z REAL,                -- 高程 (m)
    slope_instant REAL,        -- 瞬時坡度
    cost_energy REAL,          -- 模擬能量損耗 (e.g., kcal)
    geom_wkt TEXT,             -- 單點座標
    FOREIGN KEY (trail_id) REFERENCES historical_trails(id)
);

-- 4. 效率與能量分析表: 紀錄量化指標 (The Evidence)
CREATE TABLE IF NOT EXISTS efficiency_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trail_id INTEGER,
    saddle_id INTEGER,
    straight_slope REAL,
    actual_slope REAL,
    efficiency_index_e REAL,
    total_energy_budget REAL,  -- 全量步行能量預算 (Simulation Result)
    metadata_json TEXT,        -- 擴充元數據 (分析模型參數等)
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trail_id) REFERENCES historical_trails(id),
    FOREIGN KEY (saddle_id) REFERENCES geography_nodes(id)
);

-- 5. [NEW] 河道中心線表: 紀錄河流的主幹與支流幾何 (探索的粽子頭)
CREATE TABLE IF NOT EXISTS river_channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,       -- e.g., '塔羅灣溪', '濁水溪主流'
    river_order INTEGER,      -- 河川分級 (Strahler Order)
    watershed TEXT,           -- 所屬流域
    geom_wkt TEXT,            -- 河道中心線 (WKT 格式, LINESTRING)
    metadata_json TEXT,       -- 擴充元數據
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. [NEW] 資料來源索引表: 紀錄外部開放資料的元數據
CREATE TABLE IF NOT EXISTS data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,       -- e.g., '20m DTM (V2)', '全台河道中心線'
    source_type TEXT,         -- 'Raster', 'Vector', 'WFS'
    provider TEXT,            -- '內政部', '水利署'
    url TEXT,                 -- 原始下載或 WFS 連結
    local_path_hint TEXT,     -- 本地端檔案存放路徑指引
    version_tag TEXT,         -- 版本或時間戳
    metadata_json TEXT,       -- 擴充元數據
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 水文耦合表: 紀錄鞍部與兩側河源的空間連結關係
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
    metadata_json TEXT,        -- 擴充元數據
    FOREIGN KEY (saddle_id) REFERENCES geography_nodes(id),
    FOREIGN KEY (source_a_id) REFERENCES geography_nodes(id),
    FOREIGN KEY (source_b_id) REFERENCES geography_nodes(id)
);
