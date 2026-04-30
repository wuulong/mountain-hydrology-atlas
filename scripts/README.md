# Mountain Hydrology DTM Toolkit

本目錄包含用於處理台灣山脈地形數據的核心腳本。

## 1. 高程對合工具 (`extract_dtm_elevation_v2.py`)

這是本次 POC 最核心的工具，解決了內政部 DTM 非標準坐標系下的提取問題。

- **功能**: 將 YAML 節點中的 WGS84 座標轉換為 TWD97，並從指定的 DTM 磁磚目錄中提取精確海拔。
- **特點**:
    - **高效能**: 具備 BBox 快取機制，處理上千個點位僅需數秒。
    - **高容錯**: 採用 Python GDAL API 手動像素計算，繞過 `gdallocationinfo` 的解析度警告陷阱。
- **修改指南**:
    - 若要更換古道，請修改 `input_f` 指向新的 YAML。
    - 若要更換區域，請修改 `dtm_path` 指向包含該區域 TIF 的目錄。

## 2. 磁磚搜尋工具 (`find_containing_tif_v2.py`)

- **功能**: 給定一個 TWD97 座標，在地毯式掃描目錄後，找出所有涵蓋該座標的 TIF 檔案。
- **用途**: 用於手動檢查數據涵蓋範圍，或排查 DTM 資料缺失。

## 3. 獲取指令參考 (CLI Snippets)

### 下載 TGOS 資料
```bash
wget --user-agent="Mozilla/5.0" --referer="https://data.gov.tw/" "URL"
```

### 檢視圖資 Meta
```bash
gdalinfo filename.tif
```

---
**維護建議**: 每次技術突破後，請更新此 README，確保工具箱的知識始終最新。
