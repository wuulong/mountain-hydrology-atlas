# Mountain Hydrology Atlas Build Log

This log tracks the architectural decisions and data engineering steps for the Mountain Hydrology project.

## 2026-04-30: 專案啟動與架構辯證

### 重大決策：採用「第三路徑」開發模式
- **議題**：當前書本大綱與 DB Schema 成熟度不足，是否應在能高古道 POC 前鎖定資料庫結構？
- **辯證紀錄**：
    - **選項 A (Schema-First)**：先定 DB 再填資料。優點是結構嚴謹，缺點是若地形現實不符則修改成本極高。
    - **選項 B (Data-First)**：先做 POC 再定 DB。優點是靈活，缺點是數據可能零散難以入庫。
- **最終決策**：**採用「第三路徑：結構化草稿 (Lean Schema)」**。
    - **實作方式**：在能高古道 POC 階段，使用 YAML/JSON 格式進行數據紀錄，而非直接寫入 SQL。
    - **目標**：利用 POC 的靈活性來發掘真正的數據本體 (Ontology)，待模式成熟後再執行「正式入庫 (SQL Ingestion)」。

### 進度里程碑
- [x] 初始化 `Triad-Methodology-Architect` 技能。
- [x] 完成兩層式目錄 (v3.0) 與初步 Schema 定義。
- [x] 沉澱技能：`dtm-acquisition-navigator`。
- [x] **能高古道 POC 最終全要素驗證完成 (2024-04-30)**
    - 實現「山、河、古道」三位一體數據注入。
    - 建立 **VRT 虛擬圖層架構**，落實「軟體定義地圖 (SDM)」開發 Discipline。
    - 產出 `nenggao_analysis.qgs` 樣式注入專案。
    - 數據驗證越嶺對稱性與最佳解辯證成功。

### POC 核心資產清冊 (Asset Inventory)
#### 1. 數據分析 Toolkit (scripts/)
- `extract_full_nodes.py`: 從 KML 提取全量頂點，解決斷層問題。
- `extract_dtm_elevation_v3.py`: 批次高程提取與 TWD97 座標對合。
- `rebuild_path.py`: 路徑拓樸重建與 200m 距離門檻校正。
- `calculate_nenggao_efficiency_pro.py`: 坡度分析與解析度對齊運算。
- `analyze_ridge_optimization.py`: 動態脊線搜索與鞍部定位。
- `compare_energy_cost.py`: 跨流域路徑能量成本模擬對比。
- `create_virtual_layer.py`: 建立 OGR VRT 虛擬表與 QGIS 樣式注入。

#### 2. 成果與模版 (practice/)
- `nenggao_path_final.yaml`: 包含 2533 點的能高古道全要素數據檔。
- `nenggao_poc_observation.md`: 能高越嶺效率與最佳解辯證報告。
- `atlas_template.db`: 支援虛擬架構的 SQLite 模版資料庫。
- `atlas_nodes.vrt`: 虛擬空間圖層定義檔 (SDM 核心)。
- `nenggao_analysis.qgs`: QGIS 分析與渲染配置專案檔。

## 未來數據獲取與 DB 入庫建議 (Best Practices)

為了確保後續從 YAML 遷移至 SQLite (Atlas DB) 的過程順暢，並避免重複踩雷，特此記錄以下建議：

### 1. 座標系統與投影陷阱
- **原則**: 資料庫內部的 WKT 雖然儲存 WGS84，但進行 DTM 對合或坡度運算時，**必須暫存轉換為 TWD97 (EPSG:3826)**。
- **避免**: 嚴禁在未經校正的情況下，直接將 WGS84 座標套用至 `.grd` 或本地 DTM 磁磚，這會造成 800-1000m 的偏移。

### 2. 資料獲取與標準化 (ETL)
- **下載**: 凡是從 TGOS/政府平台獲取資料，應預設腳本具備 `wget --referer` 功能。
- **標準化**: 建議在入庫前，統一將所有 `.grd` 轉換為負解析度的標準 GeoTIFF，或是在 Python 提取層級統一使用 `(target - origin) / res` 的像素計算邏輯，以解決「由南往北」排列的數據異常。

### 3. 大量數據處理 (Scalability)
- **快取機制**: 對於大規模點位對合，必須先建立磁磚 BBox 快取。
- **入庫檢核**: 寫入 SQLite 前，應先產出帶有 `alt` 欄位的 YAML進行人工抽檢，確認高度數值與該區域（如：能高埡口應在 2800m 左右）符合常識。

### 4. DB 寫入技巧
- **JSON Metadata**: 將所有非幾何屬性（如：來源 KML 名稱、處理時間、DTM 磁磚編號）封裝進一個 `meta_data` JSON 欄位，這能大幅降低 Schema 修改頻率。
- **原子性**: 執行正式寫入 DB 時，應確保單一任務（如「能高古道數據注入」）為一個完整的 Transaction，避免資料殘缺。

### 5. KML 幾何提取與拓樸陷阱 (實戰心得 2024-04-30)
- **頭尾點陷阱 (The Start-End Trap)**: 
    - **現象**: 西段數據出現 6km 巨大斷層。
    - **成因**: 轉換腳本若僅提取 `LineString` 的 `StartPoint` 與 `EndPoint`，會忽略中間所有頂點 (Vertices)。
    - **對策**: 必須執行「全量頂點提取 (Full Vertex Extraction)」。
- **路徑拓樸亂序 (Disordered Topology)**:
    - **對策**: 開發「路徑重建器 (Path Rebuilder)」，使用最近鄰居與 200m 門檻限制。
- **解析度對齊 (Resolution Alignment)**:
    - **對策**: 計算坡度前必須進行 20m「解析度過濾」，消除微地形雜訊。

### 6. 最優性測試方法論 (Optimality Testing Methodology)
- **動態脊線搜索**: 沿著分山嶺進行橫切片掃描，尋找物理鞍部（局部低點）。
- **能量成本模擬 (Energy Budget)**: 模擬起點到鞍部的「累積爬升」。
- **連續性評估**: 判斷路徑是否能利用穩定的構造面，避開水文切割。

### 7. QGIS 可視化支撐性檢查 (Visualization Readiness Check)
- **數據支撐**: 已擁有 2533 個帶有 `alt` 與 `slope_pct` 的高密度節點。
- **Schema 支撐**: 已定義 `atlas_nodes` 結構，確保 QGIS 屬性能直接驅動樣式。
- **目錄支撐**: `TOC.md` 已增補 5.3 節「空間視覺化」。
- **未來動作**: 開發 `export_to_gpkg.py`。
