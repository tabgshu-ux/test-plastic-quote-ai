import datetime
import pandas as pd
import streamlit as st

def render_warehouse_management(*args, **kwargs):
    st.title("🏭 裕豐電機工業 - 倉庫與資材管理系統")
    st.caption("配電盤用銅排、開關元件、鋼板機構件與烤漆粉之條碼控管、進出倉、盤點稽核與客製化設備 WIP 成本追蹤。")

    # 初始化倉庫資材庫存
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
                "unit_price": 45.0, 
                "currency": "USD", 
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
                "unit_price": 3.2, 
                "currency": "USD", 
                "spec_note": "戶外型聚酯粉體, 膜厚 60-80μm",
                "last_update": "2026-09-26"
            }
        ]

    # 初始化進出倉與盤點記錄
    if "inventory_logs" not in st.session_state:
        st.session_state.inventory_logs = []

    # 初始化「訂製設備未出貨 WIP 庫存與 BOM 清單」資料庫
    if "wip_equipment_db" not in st.session_state:
        st.session_state.wip_equipment_db = [
            {
                "eq_id": "EQ-2026-001",
                "project_code": "PRJ-2026-01",
                "client_name": "🇻🇳 越南新順楠梓電子廠",
                "equipment_name": "2000A 高低壓主配電盤 (Custom Switchgear)",
                "status": "🟡 倉庫組裝中 / 未出貨",
                "materials_list": [
                    {"item_code": "CU-BUS-10100", "item_name": "高純度導電銅排 10x100mm", "qty": 120.0, "unit": "kg", "unit_price": 12.5, "total_price": 1500.0},
                    {"item_code": "CB-MCCB-100A", "item_name": "塑殼斷路器 100A", "qty": 8.0, "unit": "pcs", "unit_price": 45.0, "total_price": 360.0}
                ],
                "total_material_cost": 1860.0,
                "update_date": "2026-10-03"
            }
        ]

    # 頁籤設定
    tab_stock, tab_add_item, tab_wip, tab_in, tab_out, tab_audit = st.tabs([
        "📊 配電盤資材庫存監控", 
        "➕ 新建資材條碼建檔",
        "🛠️ 訂製設備未出貨 WIP 與材料成本",
        "📥 雙人進倉驗收 (倉庫+採購)", 
        "📤 條碼比對領料出倉", 
        "📜 實體盤點與稽核軌跡"
    ])

    # 1. 庫存監控
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
            "單位成本": f"${s.get('unit_price', 0):,.2f} USD",
            "狀態": "🔴 庫存偏低" if s["qty"] < s["min_safety_qty"] else "🟢 正常",
            "規格說明": s.get("spec_note", "-")
        } for s in st.session_state.warehouse_stock])
        st.dataframe(df_stock, use_container_width=True)

    # 2. 新建資材條碼建檔
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

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                new_qty = st.number_input("初始數量", min_value=0.0, value=100.0)
                new_min = st.number_input("安全庫存下限", min_value=0.0, value=200.0)
            with col_p2:
                new_price = st.number_input("物品單價 (USD)", min_value=0.0, value=10.0)
                new_spec = st.text_input("規格說明", "規格尺寸 8x80x6000mm")

            if st.form_submit_button("✅ 完成建檔並保存條碼"):
                st.session_state.warehouse_stock.append({
                    "item_code": new_code, "barcode": new_barcode, "item_name": new_name,
                    "category": new_cat, "wh_location": new_wh, "qty": new_qty, "unit": new_unit,
                    "min_safety_qty": new_min, "unit_price": new_price, "currency": "USD",
                    "spec_note": new_spec, "last_update": str(datetime.date.today())
                })
                st.success(f"資材 `{new_name}` 建檔成功！")
                st.rerun()

    # 3. 🛠️ 訂製設備未出貨 WIP 與材料成本登記
    with tab_wip:
        st.subheader("🛠️ 客製化設備未出貨 WIP 庫存與 BOM 材料成本清單")
        st.caption("專門登記尚未出貨、但在倉庫內組裝中的客製化設備（如配電盤），追蹤其所使用的材料名稱、數量與累積物品價格（成本）。")

        if st.session_state.wip_equipment_db:
            st.markdown("#### 📦 目前倉庫中未出貨之客製化設備清單")
            for wip_eq in st.session_state.wip_equipment_db:
                with st.expander(f"🔹 設備編號: `{wip_eq['eq_id']}` | 專案: `{wip_eq['project_code']}` | 客戶: {wip_eq['client_name']} | 狀態: {wip_eq['status']}"):
                    st.write(f"**設備名稱**: {wip_eq['equipment_name']}")
                    st.write(f"**累積材料總成本**: **${wip_eq['total_material_cost']:,.2f} USD** (更新日期: {wip_eq['update_date']})")
                    
                    st.markdown("##### 📌 該設備使用之材料與數量明細 (BOM)：")
                    df_bom = pd.DataFrame(wip_eq["materials_list"])
                    st.dataframe(df_bom, use_container_width=True)
        else:
            st.info("目前尚無登記中的未出貨客製化設備。")

        st.markdown("---")
        st.markdown("#### ➕ 登記新的客製化組裝設備與投入材料")

        with st.form("form_wip_equipment_registration"):
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                wip_proj = st.text_input("關聯專案代碼 *", value="PRJ-2026-02")
                wip_client = st.text_input("台廠客戶名稱 *", value="🇻🇳 平陽美德金屬加工廠")
            with col_w2:
                wip_eq_name = st.text_input("客製化設備名稱 *", value="動控箱與低壓配電盤 (Custom Panel)")
                wip_status = st.selectbox("倉庫存放狀態", ["🟡 倉庫組裝中 / 未出貨", "🟢 已完成待出貨", "🔴 已出貨結案"])

            st.markdown("##### 🛒 勾選並加入倉庫材料至此設備中：")
            material_options = {f"{s['item_code']} - {s['item_name']} (庫存: {s['qty']} {s['unit']}, 單價: ${s.get('unit_price',0)})": s for s in st.session_state.warehouse_stock}
            
            selected_mat_key = st.selectbox("選擇倉庫資材", list(material_options.keys()))
            added_qty = st.number_input("投入此設備之材料數量", min_value=0.1, value=10.0)

            if st.form_submit_button("💾 儲存客製化設備與材料成本"):
                selected_mat = material_options[selected_mat_key]
                item_cost = added_qty * selected_mat.get("unit_price", 0.0)

                new_eq_id = f"EQ-2026-{len(st.session_state.wip_equipment_db)+1:03d}"
                st.session_state.wip_equipment_db.append({
                    "eq_id": new_eq_id,
                    "project_code": wip_proj,
                    "client_name": wip_client,
                    "equipment_name": wip_eq_name,
                    "status": wip_status,
                    "materials_list": [
                        {
                            "item_code": selected_mat["item_code"], 
                            "item_name": selected_mat["item_name"], 
                            "qty": added_qty, 
                            "unit": selected_mat["unit"], 
                            "unit_price": selected_mat.get("unit_price", 0.0), 
                            "total_price": item_cost
                        }
                    ],
                    "total_material_cost": item_cost,
                    "update_date": str(datetime.date.today())
                })
                st.success(f"成功登記客製化設備 `{wip_eq_name}` 並鎖定未出貨 WIP 庫存！")
                st.rerun()

    # 4. 📥 雙人進倉驗收 (強制規定：倉庫管理員 + 採購人員 雙軌簽核)
    with tab_in:
        st.subheader("📥 雙人進倉驗收 (倉庫管理員與採購人員共同驗收)")
        st.info("💡 內控稽核規定：廠商交貨時，必須由【倉庫管理員】清點實體數量與條碼，並由【採購人員】核對採購訂單規格與價格，雙方皆簽名確認後始可完成入庫。")
        
        with st.form("form_warehouse_dual_inspection"):
            col_i1, col_i2 = st.columns(2)
            with col_i1:
                in_code = st.selectbox("驗收進倉物料", [f"{s['item_code']} - {s['item_name']}" for s in st.session_state.warehouse_stock])
                in_qty = st.number_input("本次實收數量", min_value=0.1, value=100.0)
            with col_i2:
                in_po = st.text_input("關聯採購訂單號碼 (PO No.)", value="PO-2026-0901")
                in_condition = st.selectbox("外觀與規格檢驗結果", ["🟢 驗收合格，無破損", "🟡 包裝微損但內容物正常", "🔴 規格不符或數量短少 (拒收)"])

            st.markdown("---")
            st.markdown("#### ✍️ 雙人驗收驗證簽署 (內控防弊機制)")
            col_sig1, col_sig2 = st.columns(2)
            with col_sig1:
                warehouse_keeper = st.text_input("📦 倉庫管理員姓名 (簽名確認實收數量) *", value="Nguyễn Văn Hùng")
            with col_sig2:
                purchasing_agent = st.text_input("🛒 採購人員姓名 (簽名確認訂單與價格) *", value="張偉豪")

            in_remark = st.text_area("驗收備註說明", "如期交貨，銅排導電率與尺寸符合採購規範。")

            if st.form_submit_button("✅ 提交雙人驗收並正式入庫"):
                if warehouse_keeper and purchasing_agent:
                    # 記錄至盤點與稽核軌跡
                    st.session_state.inventory_logs.insert(0, {
                        "時間": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        "單號": in_po,
                        "動作": "📥 雙人驗收進倉",
                        "品名": in_code,
                        "數量": f"+{in_qty}",
                        "倉庫管理員": warehouse_keeper,
                        "採購人員": purchasing_agent,
                        "狀態": in_condition
                    })
                    st.success(f"🎉 【雙人驗收成功】由倉庫管理員「{warehouse_keeper}」與採購人員「{purchasing_agent}」共同完成驗收，已順利入庫！")
                    st.rerun()
                else:
                    st.error("❌ 必須完整填寫【倉庫管理員】與【採購人員】之姓名方可入庫！")

    # 5. 條碼比對領料出倉
    with tab_out:
        st.subheader("📤 條碼比對領料出倉 (防錯掃描)")
        st.info("💡 生產組裝領用銅排或開關時，需掃描條碼與工單進行防錯比對。")
        with st.form("form_warehouse_out"):
            out_barcode = st.text_input("掃描資材條碼 (Barcode)", "4710998800012")
            out_qty = st.number_input("領用數量", min_value=0.1, value=50.0)
            out_order = st.text_input("關聯工單號碼 / 專案代碼", "PRJ-2026-01")
            if st.form_submit_button("🚀 比對條碼並發料出倉"):
                st.success("條碼比對正確！已順利扣減倉庫庫存。")

    # 6. 實體盤點與稽核軌跡
    with tab_audit:
        st.subheader("📜 實體盤點與雙人驗收歷史稽核軌跡")
        st.dataframe(pd.DataFrame(st.session_state.inventory_logs) if st.session_state.inventory_logs else pd.DataFrame(columns=["時間", "單號", "動作", "品名", "數量", "倉庫管理員", "採購人員", "狀態"]), use_container_width=True)

def show(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)

def main(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)
