import streamlit as st
import pandas as pd
import os
import json

def render_asset_management_page():
    st.title("📦 跨國資產與模具管理系統")
    st.caption("管理台灣總部、東莞廠與平陽廠之射出機台、模具與固定資產")

    tabs = st.tabs(["📋 資產總覽與查詢", "➕ 新增資產", "🛠️ 維修保養登記"])

    # TAB 1: 資產總覽
    with tabs[0]:
        st.subheader("廠區資產清單")
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_factory = st.selectbox("廠區篩選", ["全部", "TW (台灣總部)", "DG (東莞廠)", "BH (平陽廠)"])
        with col2:
            filter_category = st.selectbox("資產類別", ["全部", "射出機", "週邊設備", "模具", "IT設備"])
        with col3:
            filter_status = st.selectbox("資產狀態", ["全部", "在用", "閒置", "維修中", "報廢"])

        # 預設示範資料
        mock_assets = pd.DataFrame({
            "資產編號": ["EQ-BH-001", "MOLD-BH-088", "EQ-DG-003"],
            "資產名稱": ["日精 250T 射出機", "喬丹10代橡膠大底模具", "發熱油溫機"],
            "分類": ["射出機", "模具", "週邊設備"],
            "廠區": ["BH (平陽)", "BH (平陽)", "DG (東莞)"],
            "狀態": ["在用", "在用", "維修中"],
            "計價幣別": ["USD", "USD", "RMB"],
            "採購金額": ["$85,000", "$7,200", "¥ 24,000"]
        })
        st.dataframe(mock_assets, use_container_width=True)

    # TAB 2: 新增資產
    with tabs[1]:
        st.subheader("新增資產/模具資料")
        with st.form("add_asset_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                asset_id = st.text_input("資產編號*", placeholder="例如: MOLD-BH-2026-001")
                asset_name = st.text_input("資產名稱*", placeholder="例如: 喬丹10代鞋底橡膠射出模具")
                category = st.selectbox("資產類別*", ["射出機", "週邊設備", "模具", "IT設備"])
                factory = st.selectbox("歸屬廠區*", ["BH", "DG", "TW"], format_func=lambda x: {"TW": "台灣總部", "DG": "東莞廠", "BH": "平陽廠"}[x])
            
            with col_b:
                status = st.selectbox("初始狀態", ["在用", "閒置", "維修中"])
                purchase_date = st.date_input("採購/進廠日期")
                cost = st.number_input("採購金額", min_value=0.0, step=100.0)
                currency = st.selectbox("計價幣別", ["USD", "VND", "TWD", "RMB"])

            st.markdown("**設備/模具詳細規格 (JSON 格式選填)**")
            spec_tonnage = st.number_input("射出機噸數/模具適用噸數 (Tons)", min_value=0, value=250)
            spec_cavities = st.number_input("模穴數 (Cavities)", min_value=0, value=2)

            submitted = st.form_submit_button("💾 儲存資產資料")
            if submitted:
                if not asset_id or not asset_name:
                    st.warning("請填寫資產編號與名稱！")
                else:
                    st.success(f"✅ 資產 {asset_id} 資料格式正確，已暫存於 local/session 中！")

    # TAB 3: 維修保養登記
    with tabs[2]:
        st.subheader("登記設備/模具保養履歷")
        with st.form("maintenance_form", clear_on_submit=True):
            m_asset_id = st.text_input("資產編號*", placeholder="輸入欲保養的資產編號")
            m_type = st.selectbox("保養類別", ["定期保養", "緊急維修", "模具修模/拆洗", "零件更換"])
            m_date = st.date_input("保養日期")
            m_tech = st.text_input("負責技術員/廠商", placeholder="例如: 平陽廠維修組-阮文A")
            m_cost = st.number_input("維修花費金額", min_value=0.0)
            m_currency = st.selectbox("費用幣別", ["VND", "RMB", "TWD", "USD"])
            m_desc = st.text_area("維修/保養細節說明", placeholder="更新橡膠射出機油封、清洗水路與潤滑模具導柱...")

            m_submit = st.form_submit_button("🛠️ 提交保養紀錄")
            if m_submit:
                if not m_asset_id:
                    st.warning("請輸入資產編號！")
                else:
                    st.success(f"🛠️ 資產 {m_asset_id} 保養紀錄新增成功！")

def show():
    render_asset_management_page()

def main():
    render_asset_management_page()
