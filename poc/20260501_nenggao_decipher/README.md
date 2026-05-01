# 能高古道「物理地景解碼」實證資產清單 (POC 2026-05-01)

本目錄存放了 2026-05-01 針對能高古道進行「真實對合」實證的所有產出。

## 🛠️ 核心工具箱 (位於技能目錄下)
為了保持技能的通用性，腳本存放在：`.agent/skills/mountain-hydrology-explorer/scripts/`
1.  **`merge_moi_dtm_to_standard.py`**: 合併 MOI 磁磚並校正座標方向。
2.  **`extract_dtm_elevation_v2.py`**: 從 DTM 提取精確點位高程。
3.  **`decipher_coupling_engine.py`**: 計算路脈與水脈的耦合距離與背離異常。

## 📊 實證數據 (本目錄)
1.  **`nenggao_real_streams.geojson`**: 基於 DTM 萃取出的塔羅灣溪物理流路（TWD97 座標）。
2.  **`nenggao_actual_nodes.yaml`**: 本次分析的輸入節點（包含座標與角色）。
3.  **`nenggao_dtm_actual_final.yaml`**: 提取高程後的輸出節點（埡口 2799m）。
4.  **`coupling_analysis_report.md`**: 量化分析報告，紀錄了路脈與水脈的偏離發現。

## 💡 使用場景與修改建議
*   **分析新流域**: 
    1. 使用 `merge` 腳本準備 DTM TIFF。
    2. 使用 `decipher_coupling_engine.py` 修改輸入參數即可分析新古道。
*   **優化演算法**:
    如果未來發現「異常判定」不夠精準，可修改 `decipher_coupling_engine.py` 中的 `avg_dist * 1.5` 門檻。

---
**維護者**: Antigravity (AI Agent)
**隸屬專案**: Mountain Hydrology Atlas
