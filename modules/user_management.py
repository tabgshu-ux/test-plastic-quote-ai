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

def render_user_management_page(sub_option="👥 人員帳號與網頁授權"):
    st.title("💻 資訊/IT 部門 — 權限與系統管理中心")
    st.caption("管理集團部門結構、使用者帳號新增，以及跨國 ERP 模組授權 (RBAC)")

    tabs = st.tabs(["👥 人員帳號與網頁授權", "🏢 部門管理", "🔒 模組權限矩陣設定"])

    # ----------------------------------------------------
    # TAB 1: 人員帳號與網頁授權
    # ----------------------------------------------------
    with tabs[0]:
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
                auth_it = st.checkbox("💻 資訊/IT (IT & Admin)", value=False)

                submit_user = st.form_submit_button("💾 儲存並啟用帳號與授權")
                if submit_user:
                    if not username or not full_name:
                        st.warning("請填寫帳號與姓名！")
                    else:
                        st.success(f"✅ 使用者 [{full_name} ({username})] 新增成功！已更新模組授權矩陣。")

        with col_list:
            st.markdown("#### 📋 目前全集團帳號與權限清單")
            mock_users = pd.DataFrame({
                "帳號": ["admin@global.com", "ceo@global.com", "sales01@global.com", "fin01@global.com"],
                "姓名": ["IT 管理員", "董事長", "Alex Chen", "Nguyen Van A"],
                "部門": ["資訊部", "董事長室", "業務部", "越南財務部"],
                "角色": ["Admin", "Manager", "User", "User"],
                "可用模組權限": ["全模組 (Full)", "戰情室/業務/研發", "業務/行銷", "財務/發票"]
            })
            st.dataframe(mock_users, use_container_width=True)

    # ----------------------------------------------------
    # TAB 2: 部門管理
    # ----------------------------------------------------
    with tabs[1]:
        st.subheader("跨國廠區部門主檔")
        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            with st.form("add_dept_form", clear_on_submit=True):
                st.markdown("#### ➕ 新增組織部門")
                dept_id = st.text_input("部門代碼", placeholder="DEPT-BH-SALES")
                dept_name = st.text_input("部門名稱", placeholder="越南平陽廠 — 業務二組")
                factory = st.selectbox("歸屬廠區", ["TW (台灣總部)", "DG (東莞廠)", "BH (平陽廠)"])
                if st.form_submit_button("💾 新增部門"):
                    st.success(f"✅ 部門 [{dept_name}] 已成功新增！")
        
        with col_d2:
            st.markdown("#### 🏢 現有部門組織")
            depts_df = pd.DataFrame({
                "部門代碼": ["DEPT-TW-HQ", "DEPT-DG-ENG", "DEPT-BH-PROD", "DEPT-BH-FIN"],
                "部門名稱": ["台灣總部管理階層", "東莞工程研發部", "平陽射出製造部", "平陽財務課"],
                "廠區": ["台灣總部", "東莞廠", "平陽廠"]
            })
            st.table(depts_df)

    # ----------------------------------------------------
    # TAB 3: 模組權限矩陣設定
    # ----------------------------------------------------
    with tabs[2]:
        st.subheader("🔒 角色與模組 Access Control List (ACL) 矩陣")
        st.caption("勾選不同角色對各網頁頁面的存取權限")

        acl_df = pd.DataFrame({
            "模組頁面名稱": ["📈 營運戰情室", "💼 業務/行銷", "🛠️ 研發/技術", "🧾 財務", "👥 人事/行政", "💻 資訊/IT"],
            "Admin (管理員)": [True, True, True, True, True, True],
            "Manager (高層/主管)": [True, True, True, True, True, False],
            "Sales (業務同仁)": [False, True, False, False, False, False],
            "Finance (財務人員)": [False, False, False, True, False, False],
            "Worker (一般員工)": [False, False, True, False, True, False],
        })
        st.data_editor(acl_df, use_container_width=True)

def show(sub_option="👥 人員帳號與網頁授權"):
    render_user_management_page(sub_option)

def main(sub_option="👥 人員帳號與網頁授權"):
    render_user_management_page(sub_option)
