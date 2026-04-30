import os

def create_vrt(db_path, vrt_path):
    # 建立 VRT 描述檔，這就是 QGIS 看到的「虛擬表」
    vrt_content = f"""<OGRVRTDataSource>
    <OGRVRTLayer name="atlas_nodes_virtual">
        <SrcDataSource>{db_path}</SrcDataSource>
        <SrcSql>SELECT id, name, category, alt, slope_pct, geom_wkt FROM atlas_nodes</SrcSql>
        <GeometryType>wkbPoint</GeometryType>
        <LayerSRS>EPSG:4326</LayerSRS>
        <GeometryField encoding="WKT" field="geom_wkt"/>
    </OGRVRTLayer>
</OGRVRTDataSource>
"""
    with open(vrt_path, 'w', encoding='utf-8') as f:
        f.write(vrt_content)
    print(f"VRT Virtual Table created: {vrt_path}")

def update_qgs_with_vrt(vrt_path, qgs_path):
    # 讓 QGIS 讀取 VRT
    vrt_abs = os.path.abspath(vrt_path)
    qgs_content = f"""<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis projectname="能高越嶺水文分析 (Virtual)" version="3.22.0">
  <layer-tree-group>
    <layer-tree-layer id="atlas_v1" name="能高越嶺 (山河古道-虛擬表)" providerKey="ogr" source="{vrt_abs}"/>
  </layer-tree-group>
  <projectlayers>
    <maplayer id="atlas_v1" type="vector">
      <datasource>{vrt_abs}</datasource>
      <layername>能高全要素分析</layername>
      <renderer-v2 type="categorizedSymbol" attr="category" symbollevels="0">
        <categories>
          <category value="Trail" label="古道" symbol="0"/>
          <category value="Mountain" label="山 (脊線)" symbol="1"/>
          <category value="River" label="河 (水源)" symbol="2"/>
        </categories>
        <symbols>
          <symbol name="0" type="marker"><layer class="SimpleMarker"><prop k="color" v="0,255,0"/><prop k="size" v="2"/></layer></symbol>
          <symbol name="1" type="marker"><layer class="SimpleMarker"><prop k="color" v="255,0,0"/><prop k="size" v="5"/></layer></symbol>
          <symbol name="2" type="marker"><layer class="SimpleMarker"><prop k="color" v="0,0,255"/><prop k="size" v="5"/></layer></symbol>
        </symbols>
      </renderer-v2>
    </maplayer>
  </projectlayers>
</qgis>
"""
    with open(qgs_path, 'w', encoding='utf-8') as f:
        f.write(qgs_content)
    print(f"QGIS Project updated with Virtual Table: {qgs_path}")

if __name__ == "__main__":
    db = "events/mountain-hydrology/mountain-hydrology-atlas/practice/atlas_template.db"
    vrt = "events/mountain-hydrology/mountain-hydrology-atlas/practice/atlas_nodes.vrt"
    qgs = "events/mountain-hydrology/mountain-hydrology-atlas/practice/nenggao_analysis.qgs"
    
    create_vrt(os.path.abspath(db), vrt)
    update_qgs_with_vrt(vrt, qgs)
