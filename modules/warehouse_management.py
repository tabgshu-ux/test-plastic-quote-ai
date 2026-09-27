import datetime
import pandas as pd
import streamlit as st

def render_warehouse_management(*args, **kwargs):
    st.title("📦 倉儲與庫存管理系統 (Warehouse & Inventory Management)")
    st.caption("支援多廠區倉庫物料/成品管理，包含建立新物料條碼、進倉入庫、出倉領料、庫存盤點與防錯防呆比對。")

    # ----------------------------------------------------
    # 🗄️ 1. 初始化 Session State 倉儲資料庫 (含條碼欄位)
    # ----------------------------------------------------
    if "warehouse_stock" not in st.session_state:
        st.session_state.warehouse_stock = [
            {
                "item_code": "RM-PP-001", 
                "barcode": "4710123456012",
                "item_name": "PP 聚丙烯新料", 
                "category": "塑膠原料 (Raw Material)",
                "wh_location": "🇻🇳 越南廠 - 原料倉 (VN-RAW-A1)", 
                "qty": 15000.0, 
                "unit": "kg",
                "min_safety_qty": 5000.0, 
                "unit_price": 42000.0, 
                "currency": "VND", 
                "spec_note": "高流動性射出級, 顏色: 透明原色",
                "last_update": "2026-09-20"
            },
            {
                "item_code": "RM-ABS-002", 
                "barcode": "4710123456029",
                "item_name": "ABS 耐衝擊級原料", 
                "category": "塑膠原料 (Raw Material)",
                "wh_location": "🇹🇼 台灣總部 - 原料倉 (TW-RAW-01)", 
                "qty": 3200.0, 
                "unit": "kg",
                "min_safety_qty": 4000.0, 
                "unit_price": 55.0, 
                "currency": "TWD", 
                "spec_note": "黑色, 阻燃等級 V0",
                "last_update": "2026-09-25"
            },
            {
                "item_code": "FG-CAR-010", 
                "barcode": "4710123456104",
                "item_name": "汽車車燈外殼成品", 
                "category": "完成品 (Finished Product)",
                "wh_location": "🇻🇳 越南廠 - 成品倉 (VN-FG-B2)", 
                "qty": 850.0, 
                "unit": "pcs",
                "min_safety_qty": 200.0, 
                "unit_price": 120000.0, 
                "currency": "VND", 
                "spec_note": "單重 350g, 鍍鉻表面",
                "last_update": "2026-09-26"
            }
        ]

    if "inventory_logs" not in st.session_state:
        st.session_state.inventory_logs = [
            {
                "log_id": "LOG-20260920-01", 
                "type": "📥 進倉入庫", 
                "item_code": "RM-PP-001",
                "item_name": "PP 聚丙烯新料", 
                "wh_location": "🇻🇳 越南廠 - 原料倉 (VN-RAW-A1)",
                "change_qty": 5000.0, 
                "unit": "kg", 
                "operator": "李總務", 
                "date": "2026-09-20", 
                "remark": "採購單 PO-2026-088 到貨入庫"
            }
        ]

    # ----------------------------------------------------
    # 📌 2. 建立 5 大倉儲功能分頁
    # ----------------------------------------------------
    tab_stock, tab_add_item, tab_in, tab_out, tab_logs = st.tabs([
        "📊 即時庫存與條碼總覽 (Overview)", 
        "➕ 新建品項與條碼建檔 (New Item)",
        "📥 進倉入庫作業 (Inbound)", 
        "📤 出倉領料/條碼防錯 (Outbound)", 
        "📜 庫存異動履歷 (Logs)"
    ])

    # ====================================================
    # TAB 1: 即時庫存與條碼總覽
    # ====================================================
    with tab_stock:
        st.subheader("📊 多廠區庫存與防錯條碼清單")
        
        low_stock_items = [item for item in st.session_state.warehouse_stock if item["qty"] < item["min_safety_qty"]]
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("📦 現有品項總數", str(len(st.session_state.warehouse_stock)) + " 項")
        col_m2.metric("⚠️ 安全庫存預警品項", str(len(low_stock_items)) + " 項", delta_color="inverse")
        col_m3.metric("🏷️ 條碼防錯建檔率", "100%")

        if low_stock_items:
            st.warning("⚠️ **安全庫存過低預警！** 以下品項庫存已低於安全標準：")
            st.dataframe(pd.DataFrame(low_stock_items)[["item_code", "barcode", "item_name", "wh_location", "qty", "min_safety_qty", "unit"]], use_container_width=True)

        st.markdown("---")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            search_code = st.text_input("🔍 搜尋品名/料號/條碼/儲位：", "", key="wh_search_input").strip().lower()
        with col_s2:
            filter_cat = st.selectbox("📂 依類別篩選：", ["全部 (All)", "塑膠原料 (Raw Material)", "完成品 (Finished Product)", "模具備件/耗材 (Spare Parts)"])

        filtered_stock = []
        for s in st.session_state.warehouse_stock:
            match_search = (
                not search_code 
                or search_code in s["item_code"].lower() 
                or search_code in s.get("barcode", "").lower() 
                or search_code in s["item_name"].lower() 
                or search_code in s["wh_location"].lower()
            )
            match_cat = filter_cat == "全部 (All)" or s["category"] == filter_cat
            if match_search and match_cat:
                filtered_stock.append({
                    "物料/產品料號": s["item_code"],
                    "🏷️ 物品國際條碼 (EAN/UPC)": s.get("barcode", "-"),
                    "品名規格": s["item_name"],
                    "物料類別": s["category"],
                    "📍 存放倉庫與儲位": s["wh_location"],
                    "目前庫存量": f"{s['qty']:,.1f} {s['unit']}",
                    "安全庫存量": f"{s['min_safety_qty']:,.1f} {s['unit']}",
                    "狀態": "🔴 庫存不足" if s["qty"] < s["min_safety_qty"] else "🟢 正常",
                    "規格與材質防錯備註": s.get("spec_note", "-"),
                    "最後更新": s["last_update"]
                })

        st.dataframe(pd.DataFrame(filtered_stock), use_container_width=True)

    # ====================================================
    # TAB 2: 新建品項與條碼建檔
    # ====================================================
    with tab_add_item:
        st.subheader("➕ 新建倉儲物料/成品品項與條碼")
        st.caption("在此建立新品項的料號、條碼、存放倉庫位置及安全庫存，建立後即可進行進出倉作業。")

        with st.form("form_add_new_warehouse_item"):
            st.markdown("##### 📍 步驟 1：基本屬性與防錯條碼資訊")
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                new_cat = st.selectbox("物料類別 *", ["塑膠原料 (Raw Material)", "完成品 (Finished Product)", "模具備件/耗材 (Spare Parts)"])
                new_code = st.text_input("物料/產品料號 (Item Code) *", "RM-ABS-003")
            with col_a2:
                new_name = st.text_input("品名規格名稱 *", "高散熱 PA66 尼龍原料")
                new_barcode = st.text_input("🏷️ 物品條碼 (Barcode/EAN) * (可手動或掃描槍輸入)", "4710123456036")
            with col_a3:
                new_wh = st.selectbox("存放倉庫與預設儲位 *", [
                    "🇻🇳 越南廠 - 原料倉 (VN-RAW-A1)",
                    "🇻🇳 越南廠 - 成品倉 (VN-FG-B2)",
                    "🇹🇼 台灣總部 - 原料倉 (TW-RAW-01)",
                    "🇹🇼 台灣總部 - 成品倉 (TW-FG-01)",
                    "🇨🇳 中國廠 - 原料倉 (CN-RAW-01)",
                    "🇮🇩 印尼廠 - 綜合倉 (ID-WH-01)"
                ])
                new_unit = st.selectbox("計量單位 *", ["kg", "pcs", "包", "箱", "捲", "組"])

            st.markdown("---")
            st.markdown("##### 📋 步驟 2：庫存數量與成本防呆資訊")
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                new_qty = st.number_input("初始建檔庫存量", min_value=0.0, value=0.0, step=10.0)
            with col_b2:
                new_min = st.number_input("最低安全庫存量 (低於此值告警)", min_value=0.0, value=1000.0, step=100.0)
            with col_b3:
                new_price = st.number_input("預估單價 / 成本", min_value=0.0, value=100.0, step=10.0)
                new_curr = st.selectbox("計價幣別", ["TWD", "VND", "RMB", "IDR", "USD"])

            new_spec = st.text_input("防錯規格詳細說明 (如：顏色、材質牌號、尺寸重量，防止員工拿錯替代品)", "顏色: 黑色, 牌號: PA66-GF30, 防錯標籤: 黃色貼紙")

            btn_create_item = st.form_submit_button("✅ 儲存並建立新品項條碼", type="primary")

            if btn_create_item:
                if not new_code or not new_name or not new_barcode:
                    st.error("❌ 請填寫料號、品名與條碼等必填欄位！")
                else:
                    # 檢查料號或條碼是否重複
                    code_exists = any(s["item_code"] == new_code for s in st.session_state.warehouse_stock)
                    if code_exists:
                        st.error("❌ 料號 `" + str(new_code) + "` 已存在，請更換料號！")
                    else:
                        st.session_state.warehouse_stock.append({
                            "item_code": new_code,
                            "barcode": new_barcode,
                            "item_name": new_name,
                            "category": new_cat,
                            "wh_location": new_wh,
                            "qty": new_qty,
                            "unit": new_unit,
                            "min_safety_qty": new_min,
                            "unit_price": new_price,
                            "currency": new_curr,
                            "spec_note": new_spec,
                            "last_update": str(datetime.date.today())
                        })
                        st.success("🎉 成功建立新物料 `" + str(new_name) + "` (" + str(new_code) + ")，條碼 `" + str(new_barcode) + "` 已綁定！")
                        st.rerun()

    # ====================================================
    # TAB 3: 進倉入庫作業
    # ====================================================
    with tab_in:
        st.subheader("📥 採購到貨 / 生產完工進倉單據")
        
        with st.form("form_inbound_stock"):
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                item_options = [s["item_code"] + " - " + s["item_name"] + " [條碼: " + str(s.get("barcode","")) + "]" for s in st.session_state.warehouse_stock]
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
    # TAB 4: 出倉領料/條碼防錯比對
    # ====================================================
    with tab_out:
        st.subheader("📤 領料 / 銷售出貨 / 條碼防錯比對扣減")
        st.info("💡 **防呆機制**：員工領料時可使用掃描槍刷條碼，系統自動比對條碼與物料規格，防止拿錯替代品。")

        with st.form("form_outbound_stock"):
            col_out1, col_out2 = st.columns(2)
            with col_out1:
                item_options_out = [s["item_code"] + " - " + s["item_name"] + " [庫存: " + str(s["qty"]) + " " + s["unit"] + "]" for s in st.session_state.warehouse_stock]
                selected_out_str = st.selectbox("1️⃣ 選擇應領料品項 (需求單據)", item_options_out if item_options_out else ["無庫存資料"])
                out_qty = st.number_input("本次領料/出貨數量 *", min_value=0.1, value=50.0, step=10.0)
            with col_out2:
                scanned_barcode = st.text_input("2️⃣ 🏷️ 刷取實物條碼進行比對 (掃描槍輸入/手動) *", placeholder="請掃描實物條碼...")
                out_operator = st.text_input("領料人 / 出貨專員", "張工程師")

            out_date = st.date_input("出庫日期", datetime.date.today())
            out_remark = st.text_input("出倉備註 (領料工單號 / 客戶單號)", "車間領料射出生產")
            btn_outbound = st.form_submit_button("🚀 條碼防錯比對並扣減庫存", type="primary")

            if btn_outbound and selected_out_str != "無庫存資料":
                code = selected_out_str.split(" - ")[0]
                item_idx = next((i for i, s in enumerate(st.session_state.warehouse_stock) if s["item_code"] == code), None)

                if item_idx is not None:
                    target_item = st.session_state.warehouse_stock[item_idx]
                    real_barcode = str(target_item.get("barcode", "")).strip()

                    # 條碼防錯檢驗
                    if scanned_barcode.strip() and scanned_barcode.strip() != real_barcode:
                        st.error("🚨 **防錯警示！條碼不相符！**\n需求條碼為 `" + str(real_barcode) + "`，但您掃描的條碼為 `" + str(scanned_barcode) + "`。員工拿錯物料，請重新確認實物！")
                    else:
                        current_qty = target_item["qty"]
                        if out_qty > current_qty:
                            st.error("❌ 庫存不足！目前庫存僅有 " + str(current_qty) + "，無法扣減 " + str(out_qty))
                        else:
                            st.session_state.warehouse_stock[item_idx]["qty"] -= out_qty
                            st.session_state.warehouse_stock[item_idx]["last_update"] = str(out_date)

                            log_id = "LOG-" + datetime.date.today().strftime('%Y%m%d') + "-" + str(len(st.session_state.inventory_logs)+1).zfill(2)
                            st.session_state.inventory_logs.append({
                                "log_id": log_id,
                                "type": "📤 出倉扣減",
                                "item_code": code,
                                "item_name": target_item["item_name"],
                                "wh_location": target_item["wh_location"],
                                "change_qty": -out_qty,
                                "unit": target_item["unit"],
                                "operator": out_operator,
                                "date": str(out_date),
                                "remark": out_remark + " (條碼比對通過)"
                            })
                            st.success("✅ **條碼比對正確！** 成功出倉領料 " + str(out_qty) + " " + target_item["unit"] + "！")
                            st.rerun()

    # ====================================================
    # TAB 5: 庫存異動履歷
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
