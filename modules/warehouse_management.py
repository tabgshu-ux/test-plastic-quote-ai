import datetime
import pandas as pd
import streamlit as st

def render_warehouse_management(*args, **kwargs):
    st.title("🏭 裕豐電機工業 - 倉庫與資材管理系統")
    st.caption("配電盤用銅排、開關元件、鋼板機構件與烤漆粉之條碼控管、進出倉與盤點稽核。")

    if "warehouse_stock" not in st.session_state:
        st.session_state.warehouse_stock = [
            {
                "item_code": "CU-BUS-10100", 
                "barcode": "4710998800012",
                "item_name": "高純度導電銅排 10x100mm", 
                "category": "銅材與母線 (Busbar)",
                "wh_location": "🇻🇳 越南西寧廠 - 銅材專用倉", 
                "qty": 1500.0, 
                "unit": "kg",
                "min_safety_qty": 2000.0, 
                "unit_price": 12.5, 
                "currency": "USD", 
                "spec_note": "導電率 98% IACS, 長度 6000mm",
                "last_update": "2026-09-20"
            },
            {
                "item_code": "CB-MCCB-100A", 
                "barcode": "4710998800029",
                "item_name": "塑殼斷路器 100A (Schneider Electric)", 
                "category": "開關與控制元件",
                "wh_location": "🇻🇳 越南西寧廠 - 電氣元件倉", 
                "qty": 350.0, 
                "unit": "pcs",
                "min_safety_qty": 100.0, 
                "unit_price": 1143000.0, 
                "currency": "VND", 
                "spec_note": "NSX100F 3P3T, 啟斷容量 36kA",
                "last_update": "2026-09-25"
            },
            {
                "item_code": "POWDER-RAL7035", 
                "barcode": "4710998800036",
                "item_name": "粉體塗裝烤漆粉 (RAL 7035 淺灰色)", 
                "category": "塗裝粉體資材",
                "wh_location": "🇻🇳 越南西寧廠 - 烤漆原料倉", 
                "qty": 800.0, 
                "unit": "kg",
                "min_safety_qty": 300.0, 
                "unit_price": 45000.0, 
                "currency": "VND", 
                "spec_note": "戶外型聚酯粉體, 膜厚 60-80μm",
                "last_update": "2026-09-26"
            }
        ]

    if "inventory_logs" not in st.session_state:
        st.session_state.inventory_logs = []

    tab_stock, tab_add_item, tab_in, tab_out, tab_audit = st.tabs([
        "📊 配電盤資材庫存監控", 
        "➕ 新建資材條碼建檔",
        "📥 雙人進倉驗收", 
        "📤 條碼比對領料出倉", 
        "📜 實體盤點與稽核軌跡"
    ])

    with tab_stock:
        st.subheader("📊 倉庫即時庫存視窗")
        low_stock_items = [item for item in st.session_state.warehouse_stock if item["qty"] < item["min_safety_qty"]]
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("📦 現有管制資材品項", str(len(st.session_state.warehouse_stock)) + " 項")
        col_m2.metric("⚠️ 安全庫存預警", str(len(low_stock_items)) + " 項", delta_color="inverse")
        col_m3.metric("🏷️ 防錯掃描", "全時段條碼比對")

        if low_stock_items:
            st.warning("⚠️ **安全庫存過低預警：** 以下配電盤資材已低於安全下限：")
            st.dataframe(pd.DataFrame([{
                "料號": l["item_code"],
                "條碼": l.get("barcode", "未建檔"),
                "品名規格": l["item_name"],
                "儲位": l["wh_location"],
                "目前庫存": f"{l['qty']:,.1f} {l['unit']}",
                "安全庫存": f"{l['min_safety_qty']:,.1f} {l['unit']}"
            } for l in low_stock_items]), use_container_width=True)

        st.markdown("---")
        df_stock = pd.DataFrame([{
            "物料料號": s["item_code"],
            "條碼": s.get("barcode", "未建檔"),
            "品名規格": s["item_name"],
            "資材類別": s["category"],
            "儲位": s["wh_location"],
            "帳面庫存": f"{s['qty']:,.1f} {s['unit']}",
            "安全庫存": f"{s['min_safety_qty']:,.1f} {s['unit']}",
            "狀態": "🔴 庫存偏低" if s["qty"] < s["min_safety_qty"] else "🟢 正常",
            "規格說明": s.get("spec_note", "-")
        } for s in st.session_state.warehouse_stock])
        st.dataframe(df_stock, use_container_width=True)

    with tab_add_item:
        st.subheader("➕ 新建資材條碼建檔")
        with st.form("form_add_new_warehouse_item"):
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                new_cat = st.selectbox("資材類別 *", ["銅材與母線 (Busbar)", "開關與控制元件", "鋼板與外殼機構件", "塗裝粉體資材", "線材與端子"])
                new_code = st.text_input("物料料號 *", "CU-BUS-08080")
            with col_a2:
                new_name = st.text_input("品名規格名稱 *", "高純度導電銅排 8x80mm")
                new_barcode = st.text_input("條碼 (Barcode) *", "4710998800043")
            with col_a3:
                new_wh = st.selectbox("指定儲位 *", ["🇻🇳 越南西寧廠 - 銅材專用倉", "🇻🇳 越南西寧廠 - 電氣元件倉", "🇻🇳 越南西寧廠 - 烤漆原料倉"])
                new_unit = st.selectbox("單位 *", ["kg", "pcs", "米", "包", "套"])

            new_qty = st.number_input("初始數量", min_value=0.0, value=100.0)
            new_min = st.number_input("安全庫存下限", min_value=0.0, value=200.0)
            new_spec = st.text_input("規格說明", "規格尺寸 8x80x6000mm")

            if st.form_submit_button("✅ 完成建檔並保存條碼"):
                st.session_state.warehouse_stock.append({
                    "item_code": new_code, "barcode": new_barcode, "item_name": new_name,
                    "category": new_cat, "wh_location": new_wh, "qty": new_qty, "unit": new_unit,
                    "min_safety_qty": new_min, "spec_note": new_spec, "last_update": str(datetime.date.today())
                })
                st.success(f"資材 `{new_name}` 建檔成功！")
                st.rerun()

def show(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)

def main(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)
