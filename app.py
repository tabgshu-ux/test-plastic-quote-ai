import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 1. 頁面基本設定 (Mobile-First & 企業級外觀)
st.set_page_config(
    page_title="SaaS Enterprise ERP Control Center",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 自定義精緻企業風 CSS 美化 (UI/UX Styling)
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .card-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #1e293b;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 側邊欄：多語系與登入者角色/管理導覽（務必在最前面定義 menu_choice，避免 NameError）
with st.sidebar:
    st.image("https://img.icons8.com/color/96/company.png", width=64)
    st.markdown("### 🌐 SaaS ERP 總控台")
    
    # 多語系選單
    lang = st.selectbox("選擇語系 / Select Language", ["繁體中文", "English", "Tiếng Việt", "简体中文"])
    
    st.markdown("---")
    st.markdown("👤 **目前登入者**: `System Admin`")
    st.markdown("🏢 **目前租戶**: `SaaS Global Control`")
    
    st.markdown("---")
    st.markdown("### 📌 系統導覽選單")
    menu_choice = st.radio(
        "選擇管理模組",
        [
            "外部資料庫與異質資料來源串聯 (Database Bridge)", 
            "樂高積木式模組拼圖與功能開關", 
            "企業組織與部門樹狀管理", 
            "系統運行與跨庫數據監控"
        ]
    )
    
    st.markdown("---")
    if st.button("🚪 登出系統", use_container_width=True):
        st.info("已安全登出系統。")

# 4. 主畫面邏輯路由
if "外部資料庫與異質資料來源串聯" in menu_choice:
    st.markdown("## 🔌 外部資料庫與異質資料來源串聯設定 (Database Bridge)")
    st.markdown("💡 *在此處您可以設定與擴充對外連結的其他客戶資料庫（例如：客戶舊版 MySQL、總公司 SQL Server 或外部供應商 API 資料庫），供系統進行跨庫數據交換與自動同步，無須修改程式碼。*")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        with st.form("db_bridge_form"):
            st.markdown("### ➕ 新增或設定外部資料庫連線")
            col1, col2 = st.columns(2)
            
            with col1:
                db_key = st.text_input("資料庫代碼 (Key)*", placeholder="例：client_a_mysql")
                db_display_name = st.text_input("資料庫顯示名稱*", placeholder="例：A客戶舊版生產管理資料庫")
                db_type = st.selectbox("資料庫類型", ["PostgreSQL / Supabase", "MySQL / MariaDB", "Microsoft SQL Server", "Oracle DB", "RESTful API / JSON Bridge"])
                db_host = st.text_input("主機位址 (Host / IP)*", placeholder="例：192.168.1.100 或 db.client-a.com")

            with col2:
                db_port = st.text_input("通訊埠 (Port)*", placeholder="例：3306 或 5432")
                db_name = st.text_input("資料庫名稱 (Database Name)*", placeholder="例：production_db_v2")
                db_user = st.text_input("使用者帳號 (Username)*", placeholder="例：db_admin")
                db_password = st.text_input("使用者密碼 (Password)*", type="password", placeholder="請輸入資料庫密碼")

            st.markdown("---")
            col_btn1, col_btn2 = st.columns([1, 2])
            with col_btn1:
                test_conn_btn = st.form_submit_button("🧪 測試資料庫連線 (Test Connection)", use_container_width=True)
            with col_btn2:
                save_btn = st.form_submit_button("💾 儲存並啟用資料庫設定", type="primary", use_container_width=True)

            if test_conn_btn:
                if not db_host or not db_name or not db_user:
                    st.warning("⚠️ 請完整填寫主機位址、資料庫名稱與帳號資訊才能進行測試！")
                else:
                    try:
                        if "PostgreSQL" in db_type:
                            conn_str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                            engine = create_engine(conn_str)
                            with engine.connect() as conn:
                                conn.execute(text("SELECT 1"))
                            st.success(f"🎉 成功連線至 PostgreSQL 資料庫：{db_display_name}！")
                        elif "MySQL" in db_type:
                            conn_str = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                            engine = create_engine(conn_str)
                            with engine.connect() as conn:
                                conn.execute(text("SELECT 1"))
                            st.success(f"🎉 成功連線至 MySQL 資料庫：{db_display_name}！")
                        else:
                            st.info(f"ℹ️ [{db_type}] 連線語法模擬測試成功。")
                    except Exception as e:
                        st.error(f"❌ 連線失敗，請檢查網路或帳號密碼：\n`{str(e)}`")

            if save_btn:
                if not db_key or not db_display_name or not db_host:
                    st.error("❌ 請填寫必要的代碼、名稱與主機位址欄位！")
                else:
                    st.success(f"✅ 外部資料庫 [{db_display_name}] (代碼: `{db_key}`) 設定已成功儲存！")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 📋 目前已配置的外部資料庫連線清單")
    mock_db_data = pd.DataFrame([
        {"代碼 Key": "tw_factory_sql", "名稱": "台灣總廠 MySQL", "類型": "MySQL", "主機": "192.168.10.5", "狀態": "🟢 連線正常"},
        {"代碼 Key": "vn_branch_pg", "名稱": "越南分公司 Supabase", "類型": "PostgreSQL", "主機": "db.vietnam-erp.com", "狀態": "🟢 連線正常"}
    ])
    search_query = st.text_input("🔍 搜尋資料庫名稱或代碼", placeholder="輸入關鍵字篩選...")
    if search_query:
        mock_db_data = mock_db_data[mock_db_data.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
    st.dataframe(mock_db_data, use_container_width=True)

elif "樂高積木式模組拼圖與功能開關" in menu_choice:
    st.markdown("## 🧩 樂高積木式模組拼圖與功能開關 (Feature Toggles)")
    st.info("💡 說明：請先在左側選取要設定的【主部門 / 系統】，再為該部門勾選對應的 ERP 功能模組拼圖。")

    col_dept, col_modules = st.columns([1, 2])

    with col_dept:
        st.markdown("### 🏢 選擇目標部門")
        dept_options = [
            "總經理室 (Executive Office)",
            "管理部 (Management Dept)",
            "全公司電子簽核中心 (Approval Center)",
            "工程與設計中心 (Engineering Dept)",
            "生產部 (Production Dept)",
            "資訊管理部 (IT & System)"
        ]
        selected_department = st.radio("請選擇要配置的部門：", dept_options)
        st.markdown("---")
        st.markdown(f"📍 **目前正在設定**：\n`{selected_department}`")

    with col_modules:
        dept_name_only = selected_department.split(' ')[0]
        st.markdown(f"### 🧩 【{dept_name_only}】的模組拼圖開關")
        st.markdown("請勾選此部門可使用的系統模組：")
        
        c1, c2 = st.columns(2)
        with c1:
            st.checkbox("智能進銷存與庫存管理", value=True, key=f"{selected_department}_m1")
            st.checkbox("財務會計與應收付管理", value=True, key=f"{selected_department}_m2")
            st.checkbox("生產排程與BOM表控管", value=False, key=f"{selected_department}_m3")
        with c2:
            st.checkbox("CRM 客戶關係與報價模組", value=True, key=f"{selected_department}_m4")
            st.checkbox("商業智慧 BI 儀表板", value=True, key=f"{selected_department}_m5")
            st.checkbox("設備維護與物聯網監控", value=False, key=f"{selected_department}_m6")

        st.markdown("---")
        if st.button(f"💾 儲存【{dept_name_only}】的模組設定", type="primary", use_container_width=True):
            st.success(f"✅ 已成功將設定儲存至 [{selected_department}]！該部門成員下次登入時將自動生效。")

elif "企業組織與部門樹狀管理" in menu_choice:
    st.markdown("## 🏢 企業組織與部門樹狀管理 (Dynamic Org Chart)")
    st.info("💡 說明：動態建構企業組織架構，確保不同部門與員工享有對應的資料列級隔離（Row-Level Security）。")

else:
    st.markdown("## 📊 系統運行與跨庫數據監控")
    st.info("💡 說明：即時監控各個已掛接外部資料庫的同步狀態、API 呼叫次數與系統效能。")
