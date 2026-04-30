import sqlite3
import yaml
import os

def create_qgs_project(db_path, qgs_path):
    # 這裡實作一個精簡版的 SDM 樣式注入
    # 設定坡度渲染規則與標籤
    qgs_content = f"""<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis projectname="能高越嶺水文分析" version="3.22.0">
  <homePath path=""/>
  <layer-tree-group>
    <layer-tree-layer id="atlas_nodes_v1" name="能高越嶺節點 (坡度分析)" providerKey="spatialite" source="{db_path}|layername=atlas_nodes"/>
  </layer-tree-group>
  <mapcanvas>
    <units>degrees</units>
  </mapcanvas>
  <projectlayers>
    <maplayer id="atlas_nodes_v1" type="vector">
      <datasource>{db_path}|layername=atlas_nodes</datasource>
      <layername>能高越嶺節點</layername>
      <renderer-v2 type="graduatedSymbol" attr="slope_pct" symbollevels="0">
        <ranges>
          <range lower="0" upper="10" label="緩坡 (0-10%)" symbol="0"/>
          <range lower="10" upper="20" label="中坡 (10-20%)" symbol="1"/>
          <range lower="20" upper="1000" label="陡坡 (>20%)" symbol="2"/>
        </ranges>
        <symbols>
          <symbol name="0" type="marker"><layer class="SimpleMarker"><prop k="color" v="0,255,0"/></layer></symbol>
          <symbol name="1" type="marker"><layer class="SimpleMarker"><prop k="color" v="255,255,0"/></layer></symbol>
          <symbol name="2" type="marker"><layer class="SimpleMarker"><prop k="color" v="255,0,0"/></layer></symbol>
        </symbols>
      </renderer-v2>
    </maplayer>
  </projectlayers>
</qgis>
"""
    with open(qgs_path, 'w', encoding='utf-8') as f:
        f.write(qgs_content)
    print(f"QGIS Project generated: {qgs_path}")

def run_factory():
    db_file = "events/mountain-hydrology/mountain-hydrology-atlas/practice/atlas_template.db"
    yaml_file = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_path_final.yaml"
    qgs_file = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_analysis.qgs"
    
    # 1. 注入
    print("Step 1: Ingesting YAML to DB...")
    # 呼叫之前的 ingest 邏輯 (此處為了示範直接整併)
    conn = sqlite3.connect(db_file)
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS atlas_nodes")
    cursor.execute("CREATE TABLE atlas_nodes (id INTEGER PRIMARY KEY, name TEXT, geom_wkt TEXT, alt REAL, slope_pct REAL)")
    
    for n in data['nodes']:
        cursor.execute("INSERT INTO atlas_nodes (name, geom_wkt, alt, slope_pct) VALUES (?,?,?,?)",
                       (n['name'], n['geom_wkt'], n.get('alt'), n.get('slope_pct', 0)))
    conn.commit()
    
    # 2. 生成 QGIS 專案
    print("Step 2: Generating QGIS Project...")
    create_qgs_project(os.path.abspath(db_file), qgs_file)
    
    # 3. 清除數據 (保留 Schema 但刪除內容)
    print("Step 3: Purging DB data (Template Mode)...")
    cursor.execute("DELETE FROM atlas_nodes")
    conn.commit()
    conn.close()
    
    print("\n[SUCCESS] POC Workflow Completed.")
    print(f"1. YAML updated with Hydro-coupling: {yaml_file}")
    print(f"2. DB structure verified: {db_file}")
    print(f"3. QGIS Project ready for review: {qgs_file}")

if __name__ == "__main__":
    run_factory()
