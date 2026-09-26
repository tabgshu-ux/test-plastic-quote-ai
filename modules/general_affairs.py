import streamlit as st
import pandas as pd

def render_general_affairs_page(sub_option, lang):
    st.title(f"🏢 總務管理系統 — {sub_option}")
    st.caption("管理公司固定資產、總務採購、零用金支應與行政公文等作業")

    # 初始化 Session State 中的模擬資料庫
    if "ga_petty_cash_data" not in st.session_state:
        st.session_state.ga_petty_cash_data = [
            {"單號": "PC-20260901-01", "申請日期": "2026-09-01", "申請人": "李大同", "費用類別": "車馬費", "金額 (USD)": 45.0, "說明": "拜訪客戶計程車費", "狀態": "🟢 已核銷"},
            {"單號": "PC-20260915-02", "申請日期": "2026-09-15", "申請人": "張小美", "費用類別": "快遞費", "金額 (USD)": 18.5, "說明": "寄送樣品至海外廠區", "狀態": "🟡 審核中"},
            {"單號": "PC-20260920-03", "申請日期": "2026-09-20", "申請人": "王阿明", "費用類別": "雜項採購", "金額 (USD)": 30.0, "說明": "茶水間咖啡豆補貨", "狀態": "🟡 審核中"}
        ]

    # 1. 總務用品採購與庫存
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

    # 2. 公司固定資產與設備管理
    elif "固定資產" in sub_option or "Asset" in sub_option or "Tài sản" in sub_option:
        st.subheader("🏢 公司固定資產與辦公設備管理")
        st.dataframe(pd.DataFrame([
            {"資產編號": "FA-2026-001", "資產名稱": "行政部公務車 Toyota", "保管人": "總務部 李專員", "放置地點": "台北總部停車場", "狀態": "使用中"},
            {"資產編號": "FA-2026-002", "資產名稱": "會議室高畫質投影機", "保管人": "資訊部", "放置地點": "大會議室", "狀態": "使用中"}
        ]), use_container_width=True)

    # 3. 零用金與行政費用申請（已新增表單、新增與刪除功能）
    elif "零用金" in sub_option or "Petty Cash" in sub_option or "Tiền mặt" in sub_option:
        st.subheader("💵 零用金與行政費用報銷")
        st.info("💡 提供總務人員登記日常小額零用金支出、車馬費及快遞費報銷。")

        # --- ➕ 新增申請表單區塊 ---
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

        # --- 📋 資料清單與刪除操作 ---
        st.markdown("### 📋 歷史申請紀錄")
        if st.session_state.ga_petty_cash_data:
            df_pc = pd.DataFrame(st.session_state.ga_petty_cash_data)
            st.dataframe(df_pc, use_container_width=True)

            # 🗑️ 單筆刪除或核銷管理選單
            with st.expander("🗑️ 刪除或管理特定單據"):
                col_del_1, col_del_2 = st.columns([3, 1])
                with col_del_1:
                    item_ids = [item["單號"] for item in st.session_state.ga_petty_cash_data]
                    selected_id = st.selectbox("請選擇欲處理的單號：", item_ids)
                
                with col_del_2:
                    st.write("") # 垂直對齊用
                    st.write("")
                    if st.button("❌ 刪除此單據", type="secondary"):
                        st.session_state.ga_petty_cash_data = [
                            item for item in st.session_state.ga_petty_cash_data if item["單號"] != selected_id
                        ]
                        st.success(f"已成功刪除單據：{selected_id}")
                        st.rerun()
        else:
            st.warning("目前尚無任何零用金申請紀錄，請透過上方表單新增。")

    # 4. 行政公文與合同管理
    else:
        st.subheader("📄 行政公文與合同管理")
        st.success("✅ 目前系統運作正常，無逾期未處理合同。")
