import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "global_erp"),
        user=os.getenv("DB_USER", "erp_user"),
        password=os.getenv("DB_PASSWORD", "your_password"),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "5432")
    )

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

        try:
            conn = get_db_connection()
            query = "SELECT asset_id, asset_name, category, factory_location, status, purchase_date, purchase_cost, currency FROM assets WHERE 1=1"
            params = []

            if filter_factory != "全部":
                query += " AND factory_location = %s"
                params.append(filter_factory.split()[0])
            if filter_category != "全部":
                query += " AND category = %s"
                params.append(filter_category)
            if filter_status != "全部":
                query += " AND status = %s"
                params.append(filter_status)

            df_assets = pd.read_sql_query(query, conn, params=params)
            conn.close()

            if not df_assets.empty:
                st.dataframe(df_assets, use_container_width=True)
                st.markdown("---")
                m1, m2, m3 = st.columns(3)
                m1.metric("總資產筆數", f"{len(df_assets)} 筆")
                m2.metric("運作中設備", f"{len(df_assets[df_assets['status'] == '在用'])} 台/套")
                m3.metric("維修中設備", f"{len(df_assets[df_assets['status'] == '維修中'])} 台/套")
            else:
                st.info("尚無符合條件的資產資料。")
        except Exception as e:
            st.info("提示：目前處於線上預覽模式。於地端 Linux 連接 PostgreSQL 後即可啟用動態查詢。")

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
                    spec_data = json.dumps({"tonnage": spec_tonnage, "cavities": spec_cavities})
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        insert_query = """
                            INSERT INTO assets (asset_id, asset_name, category, factory_location, status, purchase_date, purchase_cost, currency, specifications)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cur.execute(insert_query, (asset_id, asset_name, category, factory, status, purchase_date, cost, currency, spec_data))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"資產 {asset_id} 新增成功！")
                    except Exception as e:
                        st.error(f"寫入資料庫失敗: {e}")

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
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        m_query = """
                            INSERT INTO asset_maintenance (asset_id, maintenance_date, maintenance_type, description, cost, currency, technician)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        cur.execute(m_query, (m_asset_id, m_date, m_type, m_desc, m_cost, m_currency, m_tech))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"資產 {m_asset_id} 保養紀錄新增成功！")
                    except Exception as e:
                        st.error(f"保養紀錄寫入失敗: {e}")
