import streamlit as st
import pandas as pd
from datetime import datetime, date

def render_general_affairs_page(sub_option, lang):
    st.title(f"🏢 總務管理系統 — {sub_option}")
    st.caption("管理公司固定資產、總務採購、零用金支應與行政公文等作業")

    # ----------------------------------------------------
    # 🗄️ 初始化 Session State 模擬資料庫
    # ----------------------------------------------------
    # 1. 零用金資料庫
    if "ga_petty_cash_data" not in st.session_state:
        st.session_state.ga_petty_cash_data = [
            {"單號": "PC-20260901-01", "申請日期": "2026-09-01", "申請人": "李大同", "費用類別": "車馬費", "金額 (USD)": 45.0, "說明": "拜訪客戶計程車費", "狀態": "🟢 已核銷"},
            {"單號": "PC-20260915-02", "申請日期": "2026-09-15", "申請人": "張小美", "費用類別": "快遞費", "金額 (USD)": 18.5, "說明": "寄送樣品至海外廠區", "狀態": "🟡 審核中"},
            {"單號": "PC-20260920-03", "申請日期": "2026-09-20", "申請人": "王阿明", "費用類別": "雜項採購", "金額 (USD)": 30.0, "說明": "茶水間咖啡豆補貨", "狀態": "🟡 審核中"}
        ]

    # 2. 行政公文與合同資料庫 (新增)
    if "ga_contract_data" not in st.session_state:
        st.session_state.ga_contract_data = [
            {
                "合同/公文編號": "CTR-2026-001",
                "文件類別": "廠商合約",
                "標題/主題": "廠區保全安防維護合約",
                "簽約對象/單位": "中興保全",
                "簽署日期": "2026-01-01",
                "到期日期": "2026-12-31",
                "負責人": "李總務",
                "狀態": "🟢 有效中"
            },
            {
                "合同/公文編號": "CTR-2026-002",
                "文件類別": "廠房租約",
                "標題/主題": "越南二廠廠房租賃合同",
                "簽約對象/單位": "VSIP 工業區",
                "簽署日期": "2024-05-01",
                "到期日期": "2026-10-15",
                "負責人": "張主管",
                "狀態": "⚠️ 即將到期"
            },
            {
                "合同/公文編號": "DOC-2026-008",
                "文件類別": "行政公文",
                "標題/主題": "環保局廢料排放稽查備查函",
                "簽約對象/單位": "市府環保局",
                "簽署日期": "2026-08-10",
                "到期日期": "2027-08-09",
                "負責人": "王專員",
                "狀態": "🟢 有效中"
            }
        ]

    # ----------------------------------------------------
    # 📌 1. 總務用品採購與庫存管理
    # ----------------------------------------------------
    if "總務用品" in sub_option or "Procurement" in sub_option or "Mua sắm" in sub_option:
        st.subheader("📦 總務用品採購與庫存管理")
        col1, col2, col3 = st.columns(3)
        col1.metric("本月總務採購金額", "$12,450 USD")
        col2.metric("待簽核採購單", "3 筆")
        col3.metric("低於安全庫存品項", "2 件")

        st.markdown("#### 📋 採購需求與庫存清單")
        df = pd.DataFrame([
            {"品項名稱": "A4 影印紙 (500張/包)", "分類": "辦公用品", "目前庫存": 15, "安全庫存": 20, "狀態": "⚠️ 需補貨", "申請人": "張小美"},
            {"品項名稱": "廠區清潔劑", "分類": "清潔用品", "目前庫存": 40, "安全庫存": 10, "狀態": "🟢 正常", "申請人": "李大同"},
            {"品項名稱": "辦公椅 (人體工學)", "分類": "辦公設備", "目前庫存": 2, "安全庫存": 1, "狀態": "🟢 正常", "申請人": "陳專員"}
        ])
        st.dataframe(df, use_container_width=True)

        with st.expander("➕ 新建總務採購請購單"):
            with st.form("ga_purchase_form"):
                st.text_input("物品名稱 / Description")
                st.number_input("數量 / Quantity", min_value=1, value=1)
                st.number_input("預估金額 (USD)", min_value=0.0, value=100.0)
                st.selectbox("費用歸屬部門", ["財務部", "總務部", "廠務部", "業務部"])
                st.form_submit_button("送出採購申請")

    # ----------------------------------------------------
    # 🏢 2. 公司固定資產與設備管理
    # ----------------------------------------------------
    elif "固定資產" in sub_option or "Asset" in sub_option or "Tài sản" in sub_option:
        st.subheader("🏢 公司固定資產與辦公設備管理")
        st.dataframe(pd.DataFrame([
            {"資產編號": "FA-2026-001", "資產名稱": "行政部公務車 Toyota", "保管人": "總務部 李專員", "放置地點": "台北總部停車場", "狀態": "使用中"},
            {"資產編號": "FA-2026-002", "資產名稱": "會議室高畫質投影機", "保管人": "資訊部", "放置地點": "大會議室", "狀態": "使用中"}
        ]), use_container_width=True)

    # ----------------------------------------------------
    # 💵 3. 零用金與行政費用申請
    # ----------------------------------------------------
    elif "零用金" in sub_option or "Petty Cash" in sub_option or "Tiền mặt" in sub_option:
        st.subheader("💵 零用金與行政費用報銷")
        st.info("💡 提供總務人員登記日常小額零用金支出、車馬費及快遞費報銷。")

        # ➕ 新增申請表單區塊
        with st.expander("➕ 新增零用金/費用報銷申請", expanded=True):
            with st.form("form_add_petty_cash", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    applicant = st.text_input("申請人姓名", value=st.session_state.user_info["name"])
                    exp_type = st.selectbox("費用類別", ["車馬費", "快遞費", "餐費", "雜項辦公採購", "其他"])
                with c2:
                    exp_date = st.date_input("申請日期")
                    amount = st.number_input("金額 (USD)", min_value=0.1, value=10.0, step=0.5)
                with c3:
                    desc = st.text_area("費用用途/說明", placeholder="請填寫費用事由與發票資訊...")

                submit_btn = st.form_submit_button("📤 提交報銷申請", type="primary")

                if submit_btn:
                    new_id = f"PC-{exp_date.strftime('%Y%m%d')}-{len(st.session_state.ga_petty_cash_data) + 1:02d}"
                    new_item = {
                        "單號": new_id,
                        "申請日期": str(exp_date),
                        "申請人": applicant,
                        "費用類別": exp_type,
                        "金額 (USD)": amount,
                        "說明": desc,
                        "狀態": "🟡 審核中"
                    }
                    st.session_state.ga_petty_cash_data.append(new_item)
                    st.success(f"✅ 成功建立申請單！單號：{new_id}")
                    st.rerun()

        st.markdown("---")

        # 📋 資料清單與刪除操作
        st.markdown("### 📋 歷史申請紀錄")
        if st.session_state.ga_petty_cash_data:
            df_pc = pd.DataFrame(st.session_state.ga_petty_cash_data)
            st.dataframe(df_pc, use_container_width=True)

            # 🗑️ 單筆刪除管理
            with st.expander("🗑️ 刪除或管理特定單據"):
                col_del_1, col_del_2 = st.columns([3, 1])
                with col_del_1:
                    item_ids = [item["單號"] for item in st.session_state.ga_petty_cash_data]
                    selected_id = st.selectbox("請選擇欲處理的單號：", item_ids, key="sb_del_pc")
                
                with col_del_2:
                    st.write("")
                    st.write("")
                    if st.button("❌ 刪除此單據", type="secondary", key="btn_del_pc"):
                        st.session_state.ga_petty_cash_data = [
                            item for item in st.session_state.ga_petty_cash_data if item["單號"] != selected_id
                        ]
                        st.success(f"已成功刪除單據：{selected_id}")
                        st.rerun()
        else:
            st.warning("目前尚無任何零用金申請紀錄，請透過上方表單新增。")

    # ----------------------------------------------------
    # 📄 4. 行政公文與合同管理 (完整新增/清單/刪除/預警功能)
    # ----------------------------------------------------
    else:
        st.subheader("📄 行政公文與合同管理")
        st.info("💡 集中管理全公司之行政公文、租賃合約、廠商合作協議及智慧財產權文件。")

        # 📊 頂部 KPI 統計指標
        c1, c2, c3 = st.columns(3)
        contracts = st.session_state.ga_contract_data
        total_cnt = len(contracts)
        expiring_cnt = sum(1 for c in contracts if "即將到期" in c["狀態"])
        c1.metric("總列管合同/公文數", f"{total_cnt} 件")
        c2.metric("30天內即將到期", f"{expiring_cnt} 件", delta_color="inverse")
        c3.metric("系統告警狀態", "🟢 正常" if expiring_cnt == 0 else "⚠️ 需注意到期日")

        # ➕ 新增合同/公文登記面板
        with st.expander("➕ 登記新合同 / 行政公文", expanded=True):
            with st.form("form_add_contract", clear_on_submit=True):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    doc_type = st.selectbox("文件類別", ["廠商合約", "廠房租約", "行政公文", "保密協議 (NDA)", "其他合同"])
                    title = st.text_input("合同/公文名稱", placeholder="例如：越南廠區設備維修合約")
                    owner = st.text_input("內部負責人", value=st.session_state.user_info["name"])
                with col_b:
                    partner = st.text_input("對外簽約單位/發文機關", placeholder="例如：OO科技股份有限公司")
                    sign_date = st.date_input("簽署/發文日期", value=date.today())
                with col_c:
                    end_date = st.date_input("合約到期日", value=date(2027, 12, 31))
                    uploaded_file = st.file_uploader("上傳合同掃描檔 (PDF/Word)", type=["pdf", "docx", "doc"])

                btn_add_doc = st.form_submit_button("📥 儲存並建立文件檔案", type="primary")

                if btn_add_doc:
                    if not title or not partner:
                        st.error("❌ 請填寫合同名稱與簽約單位！")
                    else:
                        prefix = "CTR" if "合約" in doc_type or "租約" in doc_type or "協議" in doc_type else "DOC"
                        doc_id = f"{prefix}-{sign_date.strftime('%Y')}-{len(contracts) + 1:03d}"
                        
                        # 自動計算狀態
                        days_left = (end_date - date.today()).days
                        if days_left < 0:
                            status = "🔴 已過期"
                        elif days_left <= 30:
                            status = "⚠️ 即將到期"
                        else:
                            status = "🟢 有效中"

                        new_doc = {
                            "合同/公文編號": doc_id,
                            "文件類別": doc_type,
                            "標題/主題": title,
                            "簽約對象/單位": partner,
                            "簽署日期": str(sign_date),
                            "到期日期": str(end_date),
                            "負責人": owner,
                            "狀態": status
                        }
                        st.session_state.ga_contract_data.append(new_doc)
                        st.success(f"✅ 成功新增文件！文件編號：{doc_id}")
                        st.rerun()

        st.markdown("---")

        # 📋 合同與公文列表展現
        st.markdown("### 📋 合同與行政公文列管清單")
        if st.session_state.ga_contract_data:
            df_contract = pd.DataFrame(st.session_state.ga_contract_data)
            st.dataframe(df_contract, use_container_width=True)

            # 🗑️ 單筆刪除與核銷管理
            with st.expander("🗑️ 刪除或結案特定合同/公文"):
                col_del_1, col_del_2 = st.columns([3, 1])
                with col_del_1:
                    doc_ids = [c["合同/公文編號"] + " - " + c["標題/主題"] for c in st.session_state.ga_contract_data]
                    selected_doc_str = st.selectbox("請選擇欲刪除的文件：", doc_ids, key="sb_del_doc")
                    selected_doc_id = selected_doc_str.split(" - ")[0]
                
                with col_del_2:
                    st.write("")
                    st.write("")
                    if st.button("❌ 刪除此文件", type="secondary", key="btn_del_doc"):
                        st.session_state.ga_contract_data = [
                            c for c in st.session_state.ga_contract_data if c["合同/公文編號"] != selected_doc_id
                        ]
                        st.success(f"已成功刪除文件：{selected_doc_id}")
                        st.rerun()
        else:
            st.warning("目前尚無任何合同或行政公文紀錄，請透過上方表單新增。")
