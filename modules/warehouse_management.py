import datetime
import pandas as pd
import streamlit as st

def render_warehouse_management(*args, **kwargs):
    st.title("📦 倉儲與庫存管理系統 (Warehouse & Inventory Management)")
    st.caption("支援多廠區倉庫物料/成品管理，包含進倉入庫、出倉領料、庫存盤點、跨廠調撥與即時安全庫存預警。")

    # ----------------------------------------------------
    # 🗄️ 1. 初始化 Session State 倉儲資料庫
    # ----------------------------------------------------
    if "warehouse_stock" not in st.session_state:
        st.session_state.warehouse_stock = [
            {
                "item_code": "RM-PP-001", "item_name": "PP 聚丙烯新料", "category": "塑膠原料 (Raw Material)",
                "wh_location": "🇻🇳 越南廠 - 原料倉 (VN-RAW-A1)", "qty": 15000.0, "unit": "kg",
                "min_safety_qty": 5000.0, "unit_price": 42000.0, "currency": "VND", "last_update": "2026-09-20"
            },
            {
                "item_code": "RM-ABS-002", "name": "ABS 耐衝擊級原料", "category": "塑膠原料 (Raw Material)",
                "item_name": "ABS 耐衝擊級原料",
                "wh_location": "🇹🇼 台灣總部 - 原料倉 (TW-RAW-01)", "qty": 3200.0, "unit": "kg",
                "min_safety_qty": 4000.0, "unit_price": 55.0, "currency": "TWD", "last_update": "2026-09-25"
            },
            {
                "item_code": "FG-CAR-010", "item_name": "汽車車燈外殼成品", "category": "完成品 (Finished Product)",
                "wh_location": "🇻🇳 越南廠 - 成品倉 (VN-FG-B2)", "qty": 850.0, "unit": "pcs",
                "min_safety_qty": 200.0, "unit_price": 120000.0, "currency": "VND", "last_update": "2026-09-26"
            }
        ]

    if "inventory_logs" not in st.session_state:
        st.session_state.inventory_logs = [
            {
                "log_id": "LOG-20260920-01", "type": "📥 進倉入庫", "item_code": "RM-PP-001",
                "item_name": "PP 聚丙烯新料", "wh_location": "🇻🇳 越南廠 - 原料倉 (VN-RAW-A1)",
                "change_qty": 5000.0, "unit": "kg", "operator": "李總務", "date": "2026-09-20", "remark": "採購單 PO-2026-088 到貨入庫"
            }
        ]

    # ----------------------------------------------------
    # 📌 2. 建立 4 大倉儲功能分頁
    # ----------------------------------------------------
    tab_stock, tab_in, tab_out, tab_logs = st.tabs([
        "📊 即時庫存與預警 (Stock Overview)", 
        "📥 進倉入庫作業 (Inbound)", 
        "📤 出倉領料/出貨 (Outbound)", 
        "📜 庫存異動履歷 (Inventory Logs)"
    ])

    # ====================================================
    # TAB 1: 即時庫存與預警
    # ====================================================
    with tab_stock:
        st.subheader("📊 多廠區庫存監控")
        
        # 預警指標卡片
        low_stock_items = [item for item in st.session_state.warehouse_stock if item["qty"] < item["min_safety_qty"]]
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("📦 現有品項總數", str(len(st.session_state.warehouse_stock)) + " 項")
        col_m2.metric("⚠️ 安全庫存預警品項", str(len(low_stock_items)) + " 項", delta_color="inverse")
        col_m3.metric("🏭 涵蓋倉庫據點", "4 個廠區 (VN / TW / CN / ID)")

        if low_stock_items:
            st.warning("⚠️ **安全庫存過低預警！** 以下品項庫存已低於安全標準，請盡快補充採購：")
            st.dataframe(pd.DataFrame(low_stock_items)[["item_code", "item_name", "wh_location", "qty", "min_safety_qty", "unit"]], use_container_width=True)

        st.markdown("---")
        # 篩選器
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            search_code = st.text_input("🔍 搜尋品名/料號/倉庫：", "", key="wh_search_input").strip().lower()
        with col_s2:
            filter_cat = st.selectbox("📂 依類別篩選：", ["全部 (All)", "塑膠原料 (Raw Material)", "完成品 (Finished Product)", "模具備件/耗材 (Spare Parts)"])

        # 過濾數據
        filtered_stock = []
        for s in st.session_state.warehouse_stock:
            match_search = not search_code or search_code in s["item_code"].lower() or search_code in s["item_name"].lower() or search_code in s["wh_location"].lower()
            match_cat = filter_cat == "全部 (All)" or s["category"] == filter_cat
            if match_search and match_cat:
                filtered_stock.append({
                    "物料/產品料號": s["item_code"],
                    "品名規格": s["item_name"],
                    "物料類別": s["category"],
                    "存放倉庫位置": s["wh_location"],
                    "目前庫存量": f"{s['qty']:,.1f} {s['unit']}",
                    "安全庫存量": f"{s['min_safety_qty']:,.1f} {s['unit']}",
                    "狀態": "🔴 庫存不足" if s["qty"] < s["min_safety_qty"] else "🟢 正常",
                    "預估單價": f"{s['unit_price']:,.0f} {s['currency']}",
                    "最後異動日期": s["last_update"]
                })

        st.dataframe(pd.DataFrame(filtered_stock), use_container_width=True)

    # ====================================================
    # TAB 2: 進倉入庫作業
    # ====================================================
    with tab_in:
        st.subheader("📥 採購到貨 / 生產完工進倉單據填寫")
        
        with st.form("form_inbound_stock"):
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                item_options = [s["item_code"] + " - " + s["item_name"] + " (" + s["wh_location"] + ")" for s in st.session_state.warehouse_stock]
                selected_item_str = st.selectbox("選擇進倉品項 (既有物料/成品)", item_options if item_options else ["無庫存資料"])
                in_qty = st.number_input("本次進倉數量 *", min_value=0.1, value=100.0, step=10.0)
            with col_in2:
                in_date = st.date_input("入庫日期", datetime.date.today())
                operator_name = st.text_input("經手人 / 倉管人員", "李總務")

            in_remark = st.text_input("進倉備註 (如：採購單號 / 供應商名稱 / 批號)", "採購進貨入庫")
            btn_inbound = st.form_submit_button("✅ 確認進倉並更新庫存", type="primary")

            if btn_inbound and selected_item_str != "無庫存資料":
                code = selected_item_str.split(" - ")[0]
                item_idx = next((i for i, s in enumerate(st.session_state.warehouse_stock) if s["item_code"] == code), None)

                if item_idx is not None:
                    st.session_state.warehouse_stock[item_idx]["qty"] += in_qty
                    st.session_state.warehouse_stock[item_idx]["last_update"] = str(in_date)

                    # 紀錄履歷
                    log_id = "LOG-" + datetime.date.today().strftime('%Y%m%d') + "-" + str(len(st.session_state.inventory_logs)+1).zfill(2)
                    st.session_state.inventory_logs.append({
                        "log_id": log_id,
                        "type": "📥 進倉入庫",
                        "item_code": code,
                        "item_name": st.session_state.warehouse_stock[item_idx]["item_name"],
                        "wh_location": st.session_state.warehouse_stock[item_idx]["wh_location"],
                        "change_qty": +in_qty,
                        "unit": st.session_state.warehouse_stock[item_idx]["unit"],
                        "operator": operator_name,
                        "date": str(in_date),
                        "remark": in_remark
                    })
                    st.success("🎉 成功進倉 " + str(in_qty) + " " + st.session_state.warehouse_stock[item_idx]["unit"] + "！庫存已同步更新。")
                    st.rerun()

    # ====================================================
    # TAB 3: 出倉領料/出貨
    # ====================================================
    with tab_out:
        st.subheader("📤 領料 / 銷售出貨 / 庫存扣減")

        with st.form("form_outbound_stock"):
            col_out1, col_out2 = st.columns(2)
            with col_out1:
                item_options_out = [s["item_code"] + " - " + s["item_name"] + " [目前庫存: " + str(s["qty"]) + " " + s["unit"] + "]" for s in st.session_state.warehouse_stock]
                selected_out_str = st.selectbox("選擇出倉品項", item_options_out if item_options_out else ["無庫存資料"])
                out_qty = st.number_input("本次領料/出貨數量 *", min_value=0.1, value=50.0, step=10.0)
            with col_out2:
                out_date = st.date_input("出庫日期", datetime.date.today())
                out_operator = st.text_input("領料人 / 出貨專員", "張工程師")

            out_remark = st.text_input("出倉備註 (如：領料工單號 / 銷售訂單 SO / 客戶名稱)", "車間領料射出生產")
            btn_outbound = st.form_submit_button("🚀 確認扣減庫存並出倉", type="primary")

            if btn_outbound and selected_out_str != "無庫存資料":
                code = selected_out_str.split(" - ")[0]
                item_idx = next((i for i, s in enumerate(st.session_state.warehouse_stock) if s["item_code"] == code), None)

                if item_idx is not None:
                    current_qty = st.session_state.warehouse_stock[item_idx]["qty"]
                    if out_qty > current_qty:
                        st.error("❌ 庫存不足！目前庫存僅有 " + str(current_qty) + "，無法扣減 " + str(out_qty))
                    else:
                        st.session_state.warehouse_stock[item_idx]["qty"] -= out_qty
                        st.session_state.warehouse_stock[item_idx]["last_update"] = str(out_date)

                        # 紀錄履歷
                        log_id = "LOG-" + datetime.date.today().strftime('%Y%m%d') + "-" + str(len(st.session_state.inventory_logs)+1).zfill(2)
                        st.session_state.inventory_logs.append({
                            "log_id": log_id,
                            "type": "📤 出倉扣減",
                            "item_code": code,
                            "item_name": st.session_state.warehouse_stock[item_idx]["item_name"],
                            "wh_location": st.session_state.warehouse_stock[item_idx]["wh_location"],
                            "change_qty": -out_qty,
                            "unit": st.session_state.warehouse_stock[item_idx]["unit"],
                            "operator": out_operator,
                            "date": str(out_date),
                            "remark": out_remark
                        })
                        st.success("✅ 成功出倉領料 " + str(out_qty) + " " + st.session_state.warehouse_stock[item_idx]["unit"] + "！")
                        st.rerun()

    # ====================================================
    # TAB 4: 庫存異動履歷
    # ====================================================
    with tab_logs:
        st.subheader("📜 歷史出入庫紀錄與稽核軌跡")
        if st.session_state.inventory_logs:
            df_logs = pd.DataFrame(st.session_state.inventory_logs)
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("💡 尚無任何庫存異動紀錄。")

def show(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)

def main(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)
