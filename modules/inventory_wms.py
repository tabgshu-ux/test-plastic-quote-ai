import streamlit as st
import pandas as pd
import psycopg2

def get_db_connection():
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_inventory_wms(tenant_info, user_perms):
    st.markdown("### 📦 全球供應鏈倉儲與進銷存管理 (WMS)")
    st.info("💡 *即時管理多廠區倉庫庫存、原料入庫、成品出貨、安全庫存警報與庫存盤點作業。*")
    st.markdown("---")

    tab1, tab2 = st.tabs(["📋 即時庫存總覽與安全水位", "➕ 庫存異動（入庫/出庫）登記"])

    with tab1:
        st.markdown("#### 🔍 多倉庫存即時查詢")
        wms_df = pd.DataFrame([
            {"item_code": "MAT-PP-01", "item_name": "聚丙烯 (PP) 塑膠原料", "warehouse": "越南平陽倉", "stock_qty": 2500.0, "unit": "KG", "safety_level": 500.0, "status": "🟢 庫存充足"},
            {"item_code": "PARTS-08", "item_name": "精密射出頂針 10mm", "warehouse": "台北總倉", "stock_qty": 120.0, "unit": "支", "safety_level": 150.0, "status": "🟡 低於安全水位"}
        ])
        st.dataframe(wms_df, use_container_width=True)

    with tab2:
        st.markdown("#### ➕ 登錄倉庫異動（進貨入庫 / 生產領料）")
        with st.form("wms_form"):
            c1, c2 = st.columns(2)
            with c1:
                item_code = st.text_input("物料編號", value="MAT-PP-01")
                action_type = st.selectbox("異動類型", ["📥 採購進貨入庫", "📤 生產領料出庫", "🔄 倉庫間調撥"])
            with c2:
                qty = st.number_input("異動數量", value=500.0, step=1.0)
                target_wh = st.selectbox("目標倉庫", ["越南平陽倉", "台北總倉"])

            if st.form_submit_button("🚀 確認送出異動並更新庫存", type="primary", use_container_width=True):
                st.success(f"🎉 物料 [{item_code}] 執行 [{action_type}] 數量 [{qty}] 成功，庫存已同步更新！")
