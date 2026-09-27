import datetime
import pandas as pd
import streamlit as st

def render_warehouse_management(*args, **kwargs):
    st.title("📦 倉儲與物料管理系統 (Warehouse & Inventory Management)")
    st.caption("支援多廠區倉庫物料/成品管理，包含建立物料條碼、雙人驗收進倉、條碼比對領料出倉與實體盤點稽核。")

    # ----------------------------------------------------
    # 🗄️ 1. 初始化 Session State 倉儲資料庫
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

    for item in st.session_state.warehouse_stock:
        if "barcode" not in item or not item["barcode"]:
            item["barcode"] = "未建檔條碼"

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
                "checker": "張主管",
                "date": "2026-09-20", 
                "remark": "採購單 PO-2026-088 到貨入庫"
            }
        ]

    tab_stock, tab_add_item, tab_in, tab_out, tab_audit = st.tabs([
        "📊 庫存監視與安全預警", 
        "➕ 新建品項條碼建檔",
        "📥 雙人核可進倉驗收", 
        "📤 條碼比對領料出倉", 
        "📜 實體盤點與稽核軌跡"
    ])

    # ====================================================
    # TAB 1: 庫存監視與安全預警
    # ====================================================
    with tab_stock:
        st.subheader("📊 多廠區庫存監視視窗")
        low_stock_items = [item for item in st.session_state.warehouse_stock if item["qty"] < item["min_safety_qty"]]
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("📦 現有管制品項", str(len(st.session_state.warehouse_stock)) + " 項")
        col_m2.metric("⚠️ 安全庫存預警", str(len(low_stock_items)) + " 項", delta_color="inverse")
        col_m3.metric("🏷️ 條碼防錯機制", "全時段強制比對")

        if low_stock_items:
            st.warning("⚠️ **安全庫存過低預警：** 以下品項庫存已低於安全標準，請安排補充：")
            low_stock_display = []
            for l_item in low_stock_items:
                low_stock_display.append({
                    "物料/產品料號": l_item["item_code"],
                    "🏷️ 物品條碼": l_item.get("barcode", "未建檔"),
                    "品名規格": l_item["item_name"],
                    "存放倉庫位置": l_item["wh_location"],
                    "目前庫存": f"{l_item['qty']:,.1f} {l_item['unit']}",
                    "安全庫存": f"{l_item['min_safety_qty']:,.1f} {l_item['unit']}"
                })
            st.dataframe(pd.DataFrame(low_stock_display), use_container_width=True)

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
                or search_code in str(s["item_code"]).lower() 
                or search_code in str(s.get("barcode", "")).lower() 
                or search_code in str(s["item_name"]).lower() 
                or search_code in str(s["wh_location"]).lower()
            )
            match_cat = filter_cat == "全部 (All)" or s["category"] == filter_cat
            if match_search and match_cat:
                filtered_stock.append({
                    "物料/產品料號": s["item_code"],
                    "🏷️ 條碼 (Barcode)": s.get("barcode", "未建檔"),
                    "品名規格": s["item_name"],
                    "物料類別": s["category"],
                    "📍 儲位": s["wh_location"],
                    "帳面庫存": f"{s['qty']:,.1f} {s['unit']}",
                    "安全庫存": f"{s['min_safety_qty']:,.1f} {s['unit']}",
                    "狀態": "🔴 庫存偏低" if s["qty"] < s["min_safety_qty"] else "🟢 正常",
                    "規格細節與備註": s.get("spec_note", "-"),
                    "最後更新日": s["last_update"]
                })

        st.dataframe(pd.DataFrame(filtered_stock), use_container_width=True)

    # ====================================================
    # TAB 2: 新建品項條碼建檔
    # ====================================================
    with tab_add_item:
        st.subheader("➕ 物品條碼建檔與規格設定")
        st.caption("所有物料或成品建議綁定條碼（可使用掃描槍輸入），維護物品辨識精準度。")

        with st.form("form_add_new_warehouse_item"):
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                new_cat = st.selectbox("物料類別 *", ["塑膠原料 (Raw Material)", "完成品 (Finished Product)", "模具備件/耗材 (Spare Parts)"])
                new_code = st.text_input("物料/產品料號 (Item Code) *", "RM-ABS-003")
            with col_a2:
                new_name = st.text_input("品名規格名稱 *", "高散熱 PA66 尼龍原料")
                new_barcode = st.text_input("🏷️ 物品條碼 (EAN/UPC/自訂碼) *", "4710123456036")
            with col_a3:
                new_wh = st.selectbox("指定存放倉庫/儲位 *", [
                    "🇻🇳 越南廠 - 原料倉 (VN-RAW-A1)",
                    "🇻🇳 越南廠 - 成品倉 (VN-FG-B2)",
                    "🇹🇼 台灣總部 - 原料倉 (TW-RAW-01)",
                    "🇹🇼 台灣總部 - 成品倉 (TW-FG-01)",
                    "🇨🇳 中國廠 - 原料倉 (CN-RAW-01)",
                    "🇮🇩 印尼廠 - 綜合倉 (ID-WH-01)"
                ])
                new_unit = st.selectbox("計量單位 *", ["kg", "pcs", "包", "箱", "捲", "組"])

            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                new_qty = st.number_input("初始帳面數量", min_value=0.0, value=0.0, step=10.0)
            with col_b2:
                new_min = st.number_input("安全庫存下限", min_value=0.0, value=1000.0, step=100.0)
            with col_b3:
                new_price = st.number_input("單價成本", min_value=0.0, value=100.0, step=10.0)
                new_curr = st.selectbox("幣別", ["TWD", "VND", "RMB", "IDR", "USD"])

            new_spec = st.text_input("規格與包裝特徵說明 (如：材質牌號、顏色標記)", "顏色: 黑色, 牌號: PA66-GF30, 重量規格: 25kg/包")

            btn_create_item = st.form_submit_button("✅ 完成建檔並保存條碼", type="primary")

            if btn_create_item:
                if not new_code or not new_name or not new_barcode:
                    st.error("❌ 請填寫料號、品名與條碼等必填欄位！")
                else:
                    code_exists = any(s["item_code"] == new_code or s.get("barcode") == new_barcode for s in st.session_state.warehouse_stock)
                    if code_exists:
                        st.error("❌ 料號或條碼已存在，請確認後重新輸入！")
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
                        st.success("🎉 成功建檔物料 `" + str(new_name) + "`，條碼 `" + str(new_barcode) + "` 已儲存！")
                        st.rerun()

    # ====================================================
    # TAB 3: 雙人核可進倉驗收
    # ====================================================
    with tab_in:
        st.subheader("📥 雙人核可進倉驗收單")
        
        with st.form("form_inbound_stock"):
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                item_options = [s["item_code"] + " - " + s["item_name"] + " [條碼: " + str(s.get("barcode","未建檔")) + "]" for s in st.session_state.warehouse_stock]
                selected_item_str = st.selectbox("選擇驗收入庫品項", item_options if item_options else ["無庫存資料"])
                in_qty = st.number_input("驗收數量 *", min_value=0.1, value=100.0, step=10.0)
            with col_in2:
                in_date = st.date_input("入庫日期", datetime.date.today())
                operator_name = st.text_input("倉管點交人 *", "李總務")
                checker_name = st.text_input("主管/稽核複核人 *", "張主管")

            in_remark = st.text_input("驗收單據/發票號碼", "PO-2026-0099")
            btn_inbound = st.form_submit_button("✅ 雙人簽核並完成進倉", type="primary")

            if btn_inbound and selected_item_str != "無庫存資料":
                if not operator_name or not checker_name:
                    st.error("❌ 請填寫『點交人』與『稽核複核人』進行雙重簽核！")
                else:
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
                            "checker": checker_name,
                            "date": str(in_date),
                            "remark": in_remark
                        })
                        st.success("🎉 進倉驗收成功！點交人：" + str(operator_name) + " | 複核人：" + str(checker_name))
                        st.rerun()

    # ====================================================
    # TAB 4: 條碼比對領料出仓
    # ====================================================
    with tab_out:
        st.subheader("📤 條碼比對領料出倉")
        st.info("💡 領料時請使用條碼槍刷取實物條碼，系統將自動比對條碼與需求品項是否一致。")

        with st.form("form_outbound_stock"):
            col_out1, col_out2 = st.columns(2)
            with col_out1:
                item_options_out = [s["item_code"] + " - " + s["item_name"] + " [帳面庫存: " + str(s["qty"]) + " " + s["unit"] + "]" for s in st.session_state.warehouse_stock]
                selected_out_str = st.selectbox("1️⃣ 選擇領料單據需求品項", item_options_out if item_options_out else ["無庫存資料"])
                out_qty = st.number_input("申請領料/出貨數量 *", min_value=0.1, value=50.0, step=10.0)
            with col_out2:
                scanned_barcode = st.text_input("2️⃣ 🏷️ 刷取實物條碼 (條碼槍輸入/手動) *", placeholder="請掃描實物條碼...")
                out_operator = st.text_input("領料申請人 *", "張工程師")
                out_checker = st.text_input("倉管發料複核人 *", "李總務")

            out_date = st.date_input("出庫日期", datetime.date.today())
            out_remark = st.text_input("領料工單號 / 客戶訂單號", "WO-2026-0512")
            btn_outbound = st.form_submit_button("🚀 驗證條碼並發料扣庫", type="primary")

            if btn_outbound and selected_out_str != "無庫存資料":
                code = selected_out_str.split(" - ")[0]
                item_idx = next((i for i, s in enumerate(st.session_state.warehouse_stock) if s["item_code"] == code), None)

                if item_idx is not None:
                    target_item = st.session_state.warehouse_stock[item_idx]
                    real_barcode = str(target_item.get("barcode", "")).strip()

                    if not scanned_barcode.strip():
                        st.error("❌ 請輸入或刷取實物條碼以執行出庫！")
                    elif scanned_barcode.strip() != real_barcode:
                        st.error("🚨 **條碼不符告警！**\n單據需求條碼為 `" + str(real_barcode) + "`，但掃描條碼為 `" + str(scanned_barcode) + "`。請確認實物規格是否正確！")
                        
                        log_id = "LOG-ERR-" + datetime.date.today().strftime('%Y%m%d') + "-" + str(len(st.session_state.inventory_logs)+1).zfill(2)
                        st.session_state.inventory_logs.append({
                            "log_id": log_id,
                            "type": "⚠️ 條碼比對異常記錄",
                            "item_code": code,
                            "item_name": target_item["item_name"],
                            "wh_location": target_item["wh_location"],
                            "change_qty": 0.0,
                            "unit": target_item["unit"],
                            "operator": out_operator,
                            "checker": out_checker,
                            "date": str(out_date),
                            "remark": "條碼不符 (嘗試使用 " + str(scanned_barcode) + " 領取 " + str(real_barcode) + ")"
                        })
                    else:
                        current_qty = target_item["qty"]
                        if out_qty > current_qty:
                            st.error("❌ 庫存不足！目前帳面僅有 " + str(current_qty) + "，無法發料 " + str(out_qty))
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
                                "checker": out_checker,
                                "date": str(out_date),
                                "remark": out_remark + " (條碼驗證通過)"
                            })
                            st.success("✅ **條碼比對正確！** 成功發料 " + str(out_qty) + " " + target_item["unit"] + "。")
                            st.rerun()

    # ====================================================
    # TAB 5: 實體盤點與稽核軌跡
    # ====================================================
    with tab_audit:
        st.subheader("📜 實體庫存盤點與稽核紀錄")

        with st.expander("🔍 執行實體庫存盤點登記 (盤盈 / 盤虧修正)", expanded=False):
            with st.form("form_stock_taking"):
                emp_list_take = [s["item_code"] + " - " + s["item_name"] + " (帳面: " + str(s["qty"]) + " " + s["unit"] + ")" for s in st.session_state.warehouse_stock]
                selected_take_str = st.selectbox("選擇盤點品項", emp_list_take)
                actual_qty = st.number_input("現場實際清點數量 *", min_value=0.0, value=100.0, step=1.0)
                taker_name = st.text_input("盤點稽核主管 *", "王會計")
                take_reason = st.text_input("盤點差異說明", "定期例行盤點")

                btn_take = st.form_submit_button("⚖️ 儲存盤點結果並自動修正庫存", type="primary")

                if btn_take and selected_take_str:
                    code = selected_take_str.split(" - ")[0]
                    item_idx = next((i for i, s in enumerate(st.session_state.warehouse_stock) if s["item_code"] == code), None)

                    if item_idx is not None:
                        old_qty = st.session_state.warehouse_stock[item_idx]["qty"]
                        diff_qty = actual_qty - old_qty

                        st.session_state.warehouse_stock[item_idx]["qty"] = actual_qty
                        st.session_state.warehouse_stock[item_idx]["last_update"] = str(datetime.date.today())

                        log_type = "⚠️ 盤虧調整" if diff_qty < 0 else "📈 盤盈調整"
                        log_id = "LOG-AUDIT-" + datetime.date.today().strftime('%Y%m%d') + "-" + str(len(st.session_state.inventory_logs)+1).zfill(2)

                        st.session_state.inventory_logs.append({
                            "log_id": log_id,
                            "type": log_type,
                            "item_code": code,
                            "item_name": st.session_state.warehouse_stock[item_idx]["item_name"],
                            "wh_location": st.session_state.warehouse_stock[item_idx]["wh_location"],
                            "change_qty": diff_qty,
                            "unit": st.session_state.warehouse_stock[item_idx]["unit"],
                            "operator": taker_name,
                            "checker": "系統稽核員",
                            "date": str(datetime.date.today()),
                            "remark": take_reason + " [差異: " + f"{diff_qty:+,.1f}" + "]"
                        })

                        if diff_qty < 0:
                            st.warning("⚠️ 盤點調整完成：帳實差異為 " + f"{diff_qty:,.1f}" + " " + st.session_state.warehouse_stock[item_idx]["unit"] + "，已寫入紀錄。")
                        else:
                            st.success("✅ 盤點調整完成！")
                        st.rerun()

        st.markdown("---")
        st.markdown("#### 📋 庫存出入庫與異動流水帳")
        if st.session_state.inventory_logs:
            df_logs = pd.DataFrame(st.session_state.inventory_logs)
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("💡 尚無異動紀錄。")

def show(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)

def main(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)
