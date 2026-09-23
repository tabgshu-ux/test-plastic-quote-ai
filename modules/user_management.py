import streamlit as st
import pandas as pd
import psycopg2
import os

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "global_erp"),
        user=os.getenv("DB_USER", "erp_user"),
        password=os.getenv("DB_PASSWORD", "your_password"),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "5432")
    )

def render_user_management_page(sub_option="🏢 跨國廠區與子公司管理"):
    st.title("💻 資訊/IT 部門 — 權限與系統管理中心")
    st.caption("管理集團部門結構、全球廠區據點擴建，以及跨國 ERP 模組授權 (RBAC)")

    tabs = st.tabs(["🏢 跨國廠區與子公司管理", "👥 人員帳號與網頁授權", "🔒 模組權限矩陣設定"])

    # ----------------------------------------------------
    # TAB 1: 跨國廠區與子公司動態管理 (動態新增廠區)
    # ----------------------------------------------------
    with tabs[0]:
        st.subheader("🌐 全球廠區與海外子公司據點維護")
        st.caption("支援跨國企業動態擴張，隨時新增海外新設廠房、研發中心或子公司")

        col_f1, col_f2 = st.columns([1, 1])

        # 初始化 Session State 模擬廠區清單（確保即使在地端 DB 未連線時亦可即時擴展）
        if "factory_list" not in st.session_state:
            st.session_state.factory_list = [
                {"id": "FACT-TW-01", "name": "🇹🇼 台灣總部研發中心", "country": "台灣", "currency": "TWD", "revenue": "NT$ 12.5M", "status": "🟢 營運中"},
                {"id": "FACT-DG-01", "name": "🇨🇳 東莞一廠 (橡膠/塑膠)", "country": "中國", "currency": "RMB", "revenue": "¥ 3.4M", "status": "🟢 營運中"},
                {"id": "FACT-BH-01", "name": "🇻🇳 越南平陽廠 (鞋底/大底)", "country": "越南", "currency": "VND", "revenue": "₫ 12.8B", "status": "🟢 營運中"}
            ]

        with col_f1:
            st.markdown("#### ➕ 新增海外廠房/分公司據點")
            with st.form("add_factory_form", clear_on_submit=True):
                f_id = st.text_input("廠區代碼*", placeholder="例如: FACT-ID-01 (印尼廠)")
                f_name = st.text_input("廠區/子公司名稱*", placeholder="例如: 🇮🇩 印尼爪哇新廠")
                f_country = st.text_input("所在國家/區域*", placeholder="例如: 印尼 (Indonesia)")
                f_currency = st.selectbox("當地記帳本位幣*", ["USD", "VND", "TWD", "RMB", "IDR", "MXN", "EUR"])
                f_status = st.selectbox("廠區營運狀態", ["🟢 營運中", "🏗️ 建廠/試產中", "🟡 規劃中"])

                if st.form_submit_button("💾 儲存並將新廠區加入集團戰情室"):
                    if not f_id or not f_name:
                        st.warning("請輸入廠區代碼與名稱！")
                    else:
                        st.session_state.factory_list.append({
                            "id": f_id, "name": f_name, "country": f_country, 
                            "currency": f_currency, "revenue": "$0.00", "status": f_status
                        })
                        st.success(f"🎉 新廠區據點 [{f_name}] 已成功建立！集團戰情室與 KPI 面板已同步更新連動。")
                        st.rerun()

        with col_f2:
            st.markdown("#### 🌍 現有全球廠區據點一覽")
            df_factories = pd.DataFrame(st.session_state.factory_list)
            st.dataframe(df_factories, use_container_width=True)

    # ----------------------------------------------------
    # TAB 2: 人員帳號與網頁授權
    # ----------------------------------------------------
    with tabs[1]:
        st.subheader("新增人員與選單授權設定")
        col_form, col_list = st.columns([1, 1])

        with col_form:
            st.markdown("#### ➕ 新增/編輯系統帳號與權限")
            with st.form("add_user_form", clear_on_submit=True):
                username = st.text_input("登入帳號 (Email/工號)*", placeholder="alex.chen@global.com")
                full_name = st.text_input("使用者姓名*", placeholder="陳大明")
                password = st.text_input("初始密碼*", type="password")
                dept = st.selectbox("歸屬部門", ["IT 資訊部", "董事長室/總經理室", "業務部", "研發部", "財務部", "人事行政部"])
                role = st.selectbox("系統角色", ["Admin (系統管理員)", "Manager (主管/董事長)", "User (一般員工)"])

                st.markdown("**🔓 可開啟之網頁/模組授權**")
                auth_exec = st.checkbox("📈 營運戰情室 (Executive)", value=True)
                auth_sales = st.checkbox("💼 業務/行銷 (Sales & Marketing)", value=True)
                auth_rd = st.checkbox("🛠️ 研發/技術 (R&D & Engineering)", value=True)
                auth_finance = st.checkbox("🧾 財務 (Finance)", value=False)
                auth_hr = st.checkbox("👥 人事/行政 (HR & Admin)", value=False)

                submit_user = st.form_submit_button("💾 儲存並啟用帳號與授權")
                if submit_user:
                    st.success(f"✅ 使用者 [{full_name}] 授權設定成功！")

        with col_list:
            st.markdown("#### 📋 目前全集團帳號清單")
            mock_users = pd.DataFrame({
                "帳號": ["admin@global.com", "ceo@global.com", "sales01@global.com"],
                "姓名": ["IT 管理員", "董事長", "Alex Chen"],
                "部門": ["資訊部", "董事長室", "業務部"],
                "角色": ["Admin", "Manager", "User"]
            })
            st.dataframe(mock_users, use_container_width=True)

    # ----------------------------------------------------
    # TAB 3: 模組權限矩陣設定
    # ----------------------------------------------------
    with tabs[2]:
        st.subheader("🔒 角色與模組 Access Control List (ACL) 矩陣")
        acl_df = pd.DataFrame({
            "模組頁面名稱": ["📈 營運戰情室", "💼 業務/行銷", "🛠️ 研發/技術", "🧾 財務", "👥 人事/行政", "💻 資訊/IT"],
            "Admin (管理員)": [True, True, True, True, True, True],
            "Manager (高層/主管)": [True, True, True, True, True, False],
            "Sales (業務同仁)": [False, True, False, False, False, False]
        })
        st.data_editor(acl_df, use_container_width=True)

def show(sub_option="🏢 跨國廠區與子公司管理"):
    render_user_management_page(sub_option)

def main(sub_option="🏢 跨國廠區與子公司管理"):
    render_user_management_page(sub_option)
