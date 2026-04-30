# Atlas Database Schema (可視化導向架構)

為了支撐 QGIS 的空間論證，資料庫必須儲存以下關鍵欄位：

## 1. 節點表 (`atlas_nodes`)
存放古道上的每一個立體點位。

| 欄位名 | 類型 | 說明 | QGIS 用途 |
| :--- | :--- | :--- | :--- |
| `id` | UUID | 唯一識別碼 | 關聯屬性 |
| `name` | STRING | 節點名稱 | 地圖標註 (Label) |
| `geom` | GEOMETRY | POINT (EPSG:4326/3826) | 空間定位 |
| `alt` | DOUBLE | 海拔高度 (DTM 提取值) | 地形剖面與高度分級樣式 |
| `slope_pct` | DOUBLE | 該點至下一點的坡度 % | **色帶渲染 (Color Ramp)**: 紅(陡) -> 綠(緩) |
| `efficiency_val` | DOUBLE | 局部效率指標 | 顯示路徑優劣區段 |
| `meta_data` | JSON | 原始來源 (KML/GPX)、磁磚 ID | 彈出式視窗 (Popup) 詳情 |

## 2. 路段表 (`atlas_segments`)
存放連續的軌跡線段。

| 欄位名 | 類型 | 說明 | QGIS 用途 |
| :--- | :--- | :--- | :--- |
| `id` | UUID | 唯一識別碼 | |
| `geom` | GEOMETRY | LINESTRING | 軌跡顯示 |
| `avg_slope` | DOUBLE | 平均坡度 | 線段粗細或顏色渲染 |
| `type` | STRING | 類型 (Ridge/Valley/Pass) | **類別化樣式 (Categorized)** |

## 3. QGIS 樣式建議 (Styling Advice)
- **坡度熱圖**: 使用 `slope_pct` 欄位，設定 0-10% (綠), 10-20% (黃), >20% (紅)。
- **高度標籤**: 針對 `alt` 設定「僅在放大至特定比例尺時顯示」。
- **動態過濾**: 利用 `efficiency_val` 過濾出「低效率路段」，分析崩壁或障礙點。
