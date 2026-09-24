import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

def render_sales_order_ar_page(sub_option=None, lang="繁體中文"):
    st.title("📦 訂單與應收帳款系統 (Sales Orders & AR ERP)")
    st.caption("跨國塑膠/橡膠射出成型 — 專用客戶訂單、出貨履歷與銷項核銷模組")

    # ----------------------------------------------------
    # Session State 資料庫初始化（模擬真實 ERP 資料）
    # ----------------------------------------------------
    if "ar_customers" not in st.session_state:
        st.session_state.ar_customers = pd.DataFrame([
            {"客戶編號": "CUST-001", "客戶名稱": "鴻海科技 (Foxconn)", "國家/區域": "🇹🇼 台灣/🇻🇳 越南", "信用額度 ($)": 500000, "已用額度 ($)": 180000, "付款條件": "Net 60", "評分": 98},
            {"客戶編號": "CUST-002", "客戶名稱": "Tesla Inc.", "國家/區域": "🇺🇸 美國", "信用額度 ($)": 1200000, "已用額度 ($)": 420000, "付款條件": "Net 30", "評分": 95},
            {"客戶編號": "CUST-003", "客戶名稱": "廣達電腦 (Quanta)", "國家/區域": "🇹🇼 台灣/🇨🇳 中國", "信用額度 ($)": 300000, "已用額度 ($)": 290000, "付款條件": "30% 定金 / 70% 驗收", "評分": 89},
        ])

    if "ar_orders" not in st.session_state:
        st.session_state.ar_orders = pd.DataFrame([
            {"客戶訂單號": "SO-20260901-01", "客戶名稱": "Tesla Inc.", "產品品名/料號": "車用中央扶手外殼 (PC+ABS)", "訂購數量": 20000, "單位": "PCS", "單價 ($)": 15, "總金額 ($)": 300000, "預收定金": 0, "訂單狀態": "已接單 (待排產)", "已轉出貨": False},
            {"客戶訂單號": "SO-20260902-02", "客戶名稱": "鴻海科技 (Foxconn)", "產品品名/料號": "精密連接器雙色模塑件", "訂購數量": 50000, "單位": "PCS", "單價 ($)": 2.4, "總金額 ($)": 120000, "預收定金": 36000, "訂單狀態": "已核准 (生產中)", "已轉出貨": True},
        ])

    if "ar_shipments" not in st.session_state:
        st.session_state.ar_shipments = pd.DataFrame([
            {"出貨單號": "DN-20260915-01", "客戶訂單號": "SO-20260902-02", "出貨批號 (Lot)": "LOT-20260912-INJ", "實出數量": 50000, "報關單號": "EXP-2026-VN-9821", "出貨日期": "2026-09-15", "狀態": "已送達 (已簽收)"}
        ])

    if "ar_invoices" not in st.session_state:
        st.session_state.ar_invoices = pd.DataFrame([
            {"銷項發票單號": "INV-OUT-20260915-01", "客戶訂單號": "SO-20260902-02", "出貨單號": "DN-20260915-01", "發票金額 ($)": 120000, "SO金額 ($)": 120000, "三方媒合": "✅ 完美比對 (Pass)", "收款狀態": "未收款", "到期日": "2026-11-15"}
        ])

    if "ar_logs" not in st.session_state:
        st.session_state.ar_logs = [
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [System] Sales Order & AR 模組初始化完成"
        ]

    # ----------------------------------------------------
    # 頂部分頁頁籤：5 大核心子系統
    # ----------------------------------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 1. 客戶與信用額度",
        "📝 2. 客戶訂單與預收定金",
        "🚚 3. 出貨驗收與銷退",
        "💰 4. AR 立帳與三方比對",
        "📈 5. 帳齡分析與催收"
    ])

    # ----------------------------------------------------
    # 👥 Tab 1: 客戶與信用額度管理
    # ----------------------------------------------------
    with tab1:
        st.subheader("👥 客戶主資料與風控信用額度 (Credit Control)")
        st.dataframe(st.session_state.ar_customers, use_container_width=True)

        with st.expander("➕ 新增/修改客戶資料與信用風險額度"):
            with st.form("form_add_customer"):
                c1, c2, c3 = st.columns(3)
                c_code = c1.text_input("客戶編號", value=f"CUST-00{len(st.session_state.ar_customers)+1}")
                c_name = c2.text_input("客戶公司名稱")
                c_region = c3.selectbox("主要營運區域", ["🇹🇼 台灣", "🇻🇳 越南", "🇨🇳 中國/香港", "🇺🇸 美國", "🇪🇺 歐洲", "🇯🇵 日本"])

                c4, c5, c6 = st.columns(3)
                c_limit = c4.number_input("核定信用額度 ($ USD)", min_value=10000, value=200000, step=50000)
                c_terms = c5.selectbox("交易付款條件 (Payment Terms)", ["Net 30", "Net 60", "Net 90", "30% 定金 / 70% 出貨", "100% 預付全款"])
                c_score = c6.slider("客戶評等/評分", 0, 100, 90)

                if st.form_submit_button("💾 儲存客戶資料"):
                    if c_name.strip():
                        new_cust = {
                            "客戶編號": c_code,
                            "客戶名稱": c_name,
                            "國家/區域": c_region,
                            "信用額度 ($)": c_limit,
                            "已用額度 ($)": 0,
                            "付款條件": c_terms,
                            "評分": c_score
                        }
                        st.session_state.ar_customers = pd.concat([st.session_state.ar_customers, pd.DataFrame([new_cust])], ignore_index=True)
                        st.session_state.ar_logs.append(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Customer] 新增客戶: {c_name} (額度: ${c_limit:,})")
                        st.success(f"已成功建立客戶：{c_name}")
                    else:
                        st.error("請輸入客戶名稱！")

    # ----------------------------------------------------
    # 📝 Tab 2: 客戶訂單與預收定金 (Sales Orders & Deposit)
    # ----------------------------------------------------
    with tab2:
        st.subheader("📝 客戶訂單 (Sales Order) 登錄與預收定金核銷")

        col_so_left, col_so_right = st.columns([3, 2])

        with col_so_left:
            st.markdown("##### 📌 客戶訂單歷史紀錄")
            st.dataframe(st.session_state.ar_orders, use_container_width=True)

            # 一鍵生成出貨單邏輯
            approved_orders = st.session_state.ar_orders[
                (st.session_state.ar_orders["已轉出貨"] == False)
            ]
            if not approved_orders.empty:
                st.markdown("##### 🚀 訂單排產完成 — 一鍵生成廠區出貨單 (DN)")
                selected_so_id = st.selectbox("選擇要出貨的訂單：", approved_orders["客戶訂單號"].tolist())
                shipping_lot = st.text_input("出貨生產批號 (INJ Lot)", value=f"LOT-{datetime.datetime.now().strftime('%Y%m%d')}-INJ")
                customs_no = st.text_input("報關/物流單號", value=f"EXP-{datetime.datetime.now().strftime('%Y')}-VN-1029")

                if st.button("🔄 一鍵生成廠區出貨單 (Delivery Note)"):
                    so_row = approved_orders[approved_orders["客戶訂單號"] == selected_so_id].iloc[0]
                    new_dn_id = f"DN-{datetime.datetime.now().strftime('%Y%m%d')}-0{len(st.session_state.ar_shipments)+1}"
                    new_dn = {
                        "出貨單號": new_dn_id,
                        "客戶訂單號": selected_so_id,
                        "出貨批號 (Lot)": shipping_lot,
                        "實出數量": so_row["訂購數量"],
                        "報關單號": customs_no,
                        "出貨日期": datetime.date.today().strftime('%Y-%m-%d'),
                        "狀態": "已出貨 (運送中)"
                    }
                    st.session_state.ar_shipments = pd.concat([st.session_state.ar_shipments, pd.DataFrame([new_dn])], ignore_index=True)
                    st.session_state.ar_orders.loc[st.session_state.ar_orders["客戶訂單號"] == selected_so_id, "已轉出貨"] = True
                    st.session_state.ar_logs.append(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [DN] 訂單 {selected_so_id} 轉為出貨單 {new_dn_id}")
                    st.success(f"已成功生成出貨單 {new_dn_id}！")

        with col_so_right:
            st.markdown("##### ➕ 建立新客戶訂單 (Sales Order)")
            with st.form("form_create_so"):
                so_cust = st.selectbox("選擇客戶", st.session_state.ar_customers["客戶名稱"].tolist())
                so_item = st.text_input("產品名稱/射出件料號", value="汽車雙色空調按鈕件 (PC/ABS)")
                so_qty = st.number_input("訂購數量", min_value=1, value=10000)
                so_unit = st.selectbox("單位", ["PCS", "組", "套", "箱"])
                so_price = st.number_input("單價 ($ USD)", min_value=0.1, value=5.5)
                so_total = so_qty * so_price

                deposit_rate = st.slider("預收定金比例 (%)", 0, 100, 30)
                deposit_amount = so_total * (deposit_rate / 100)

                # 風控檢核：檢查是否超過信用額度
                cust_info = st.session_state.ar_customers[st.session_state.ar_customers["客戶名稱"] == so_cust]
                if not cust_info.empty:
                    c_limit = cust_info.iloc[0]["信用額度 ($)"]
                    c_used = cust_info.iloc[0]["已用額度 ($)"]
                    rem_limit = c_limit - c_used
                    st.caption(f"💳 客戶可用信用餘額: **${rem_limit:,} USD** (本次訂單總額: **${so_total:,} USD**)")
                    if so_total > rem_limit:
                        st.warning("⚠️ 警告：此訂單金額已超過客戶授信餘額！需要總經理特採核准。")

                if st.form_submit_button("送出訂單並鎖定產能"):
                    new_so = {
                        "客戶訂單號": f"SO-{datetime.datetime.now().strftime('%Y%m%d')}-{len(st.session_state.ar_orders)+1:02d}",
                        "客戶名稱": so_cust,
                        "產品品名/料號": so_item,
                        "訂購數量": so_qty,
                        "單位": so_unit,
                        "單價 ($)": so_price,
                        "總金額 ($)": so_total,
                        "預收定金": deposit_amount,
                        "訂單狀態": "已核准 (排產中)",
                        "已轉出貨": False
                    }
                    st.session_state.ar_orders = pd.concat([st.session_state.ar_orders, pd.DataFrame([new_so])], ignore_index=True)
                    # 更新客戶已用額度
                    st.session_state.ar_customers.loc[st.session_state.ar_customers["客戶名稱"] == so_cust, "已用額度 ($)"] += so_total
                    st.session_state.ar_logs.append(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [SO] 新增訂單 {new_so['客戶訂單號']}, 總額: ${so_total:,}")
                    st.success("客戶訂單已成功登錄！")

    # ----------------------------------------------------
    # 🚚 Tab 3: 出貨驗收與銷退管理 (Shipping & Sales Return)
    # ----------------------------------------------------
    with tab3:
        st.subheader("🚚 跨國出貨履歷、海關報關與客戶簽收管理")

        st.dataframe(st.session_state.ar_shipments, use_container_width=True)

        st.markdown("---")
        st.markdown("##### 🛎️ 客戶簽收狀態更新與銷退 (RMA) 登記")
        with st.form("form_shipment_status"):
            c_s1, c_s2, c_s3 = st.columns(3)
            dn_id = c_s1.selectbox("選擇出貨單號", st.session_state.ar_shipments["出貨單號"].tolist())
            ship_status = c_s2.selectbox("簽收結果", ["已送達 (已簽收)", "運輸中", "客戶檢驗不良 (申請 RMA 銷退)"])
            rma_reason = c_s3.text_input("銷退原因 (若無可留空)", value="")

            if st.form_submit_button("💾 更新簽收狀態"):
                st.session_state.ar_shipments.loc[st.session_state.ar_shipments["出貨單號"] == dn_id, "狀態"] = ship_status
                st.session_state.ar_logs.append(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Shipment] {dn_id} 狀態更新為: {ship_status}")
                st.success(f"已更新 {dn_id} 的物流狀態為：{ship_status}")

    # ----------------------------------------------------
    # 💰 Tab 4: AR 立帳與三方比對 (AR & 3-Way Matching)
    # ----------------------------------------------------
    with tab4:
        st.subheader("💰 應收帳款 (AR) 立帳與 3-Way Matching 自動核銷比對")
        st.info("💡 **自動比對邏輯**：系統自動比對 **[客戶 PO 訂單] = [出貨簽收單 DN] = [開立銷項發票 INV]** 之數量與單價，確保開票與營收認列 100% 正確！")

        st.dataframe(st.session_state.ar_invoices, use_container_width=True)

        st.markdown("---")
        st.markdown("##### 🧾 銷項電子發票開立與自動比對測試")

        with st.form("form_ar_matching"):
            col_m1, col_m2, col_m3 = st.columns(3)
            inv_so = col_m1.selectbox("對應客戶訂單 (SO)", st.session_state.ar_orders["客戶訂單號"].tolist())
            inv_dn = col_m2.selectbox("對應出貨單號 (DN)", st.session_state.ar_shipments["出貨單號"].tolist())
            out_inv_no = col_m3.text_input("銷項發票號碼", value=f"INV-OUT-{datetime.datetime.now().strftime('%Y%m%d')}-02")

            inv_out_amount = st.number_input("開立發票總金額 ($ USD)", value=120000)

            if st.form_submit_button("🔍 執行 AR 3-Way Matching 比對與開票"):
                so_row = st.session_state.ar_orders[st.session_state.ar_orders["客戶訂單號"] == inv_so]
                if not so_row.empty:
                    expected_amount = so_row.iloc[0]["總金額 ($)"]

                    if inv_out_amount == expected_amount:
                        match_result = "✅ 完美比對 (Pass)"
                        st.success(f"比對成功！開票金額 (${inv_out_amount:,}) 與 SO 訂單一致。已自動生成應收帳款傳票！")
                    else:
                        match_result = f"❌ 金額不符警告 (SO: ${expected_amount:,} vs 發票: ${inv_out_amount:,})"
                        st.error(f"異常警告！{match_result}。請確認是否有折扣或銷退折讓。")

                    new_inv_out = {
                        "銷項發票單號": out_inv_no,
                        "客戶訂單號": inv_so,
                        "出貨單號": inv_dn,
                        "發票金額 ($)": inv_out_amount,
                        "SO金額 ($)": expected_amount,
                        "三方媒合": match_result,
                        "收款狀態": "未收款",
                        "到期日": (datetime.date.today() + datetime.timedelta(days=60)).strftime('%Y-%m-%d')
                    }
                    st.session_state.ar_invoices = pd.concat([st.session_state.ar_invoices, pd.DataFrame([new_inv_out])], ignore_index=True)
                    st.session_state.ar_logs.append(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [AR Matching] {out_inv_no} 比對結果: {match_result}")

        # 會計自動分錄展示
        with st.expander("📄 查看系統自動生成之應收帳款會計傳票分錄 (Journal Entry)"):
            st.code("""
借：應收帳款 - 客戶款項 (Accounts Receivable)   $120,000
    貸：銷貨收入 (Sales Revenue)               $114,285
    貸：銷項稅額 (VAT Output Tax)              $  5,715
            """, language="text")

    # ----------------------------------------------------
    # 📈 Tab 5: 帳齡分析與催收 (AR Aging & Collection)
    # ----------------------------------------------------
    with tab5:
        st.subheader("📈 應收帳款帳齡分析 (AR Aging Report) 與催收追蹤")

        # 模擬 AR 帳齡分布數據
        ar_aging_data = pd.DataFrame({
            "帳齡區間": ["未到期 (Current)", "1-30 天", "31-60 天", "61-90 天", "90+ 天 (逾期警告)"],
            "應收金額 ($ USD)": [600000, 180000, 120000, 0, 0]
        })

        col_ar1, col_ar2 = st.columns([3, 2])

        with col_ar1:
            fig = px.bar(
                ar_aging_data,
                x="帳齡區間",
                y="應收金額 ($ USD)",
                text_auto='.2s',
                title="全球客戶 AR 帳齡分布圖 (AR Aging Summary)",
                color="帳齡區間",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_ar2:
            st.markdown("##### 💵 預計現金流入與催收預警")
            st.dataframe(ar_aging_data, use_container_width=True)
            st.metric("本月預計應收款項總額", "$900,000 USD", delta="12.3%")

        st.markdown("---")
        st.markdown("##### 🛡️ 系統資安與內控稽核日誌 (Security Audit Log)")
        st.text_area("AR Audit Logs", value="\n".join(st.session_state.ar_logs), height=200)
