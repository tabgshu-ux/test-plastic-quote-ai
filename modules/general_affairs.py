import streamlit as st
import pandas as pd

def render_general_affairs_page(sub_option, lang):
    st.title(f"🏢 總務管理系統 — {sub_option}")
    st.caption("管理公司固定資產、總務採購、零用金支應與行政公文等作業")

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

    elif "固定資產" in sub_option or "Asset" in sub_option or "Tài sản" in sub_option:
        st.subheader("🏢 公司固定資產與辦公設備管理")
        st.dataframe(pd.DataFrame([
            {"資產編號": "FA-2026-001", "資產名稱": "行政部公務車 Toyota", "保管人": "總務部 李專員", "放置地點": "台北總部停車場", "狀態": "使用中"},
            {"資產編號": "FA-2026-002", "資產名稱": "會議室高畫質投影機", "保管人": "資訊部", "放置地點": "大會議室", "狀態": "使用中"}
        ]), use_container_width=True)

    elif "零用金" in sub_option or "Petty Cash" in sub_option or "Tiền mặt" in sub_option:
        st.subheader("💵 零用金與行政費用報銷")
        st.info("💡 提供總務人員登記日常小額零用金支出、車馬費及快遞費報銷。")

    else:
        st.subheader("📄 行政公文與合同管理")
        st.success("✅ 目前系統運作正常，無逾期未處理合同。")
