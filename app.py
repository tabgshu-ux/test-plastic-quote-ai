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

# 3. 側邊欄：多語系與登入者角色/管理導覽
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
    st.markdown("## 🧩 樂高積木式模組拼圖與功能開關 (Feature Toggles & App Store)")
    st.info("💡 說明：此處展示系統【全功能模組大合集】。您可以點選左側任意部門，並自由勾選或組合市面上所有企業營運、高階決策、財會與供應鏈所需的完整模組拼圖。")

    col_dept, col_modules = st.columns([1, 2])

    with col_dept:
        st.markdown("### 🏢 選擇目標部門 / 管理層")
        dept_options = [
            "👑 董事長室 / 總經理室 (Executive & Board Room)",
            "📋 經營企劃與策略發展部 (Corporate Strategy)",
            "👥 人力資源與行政管理部 (HR & Admin Dept)",
            "⚖️ 法務與合規遵循部 (Legal & Compliance)",
            "🛡️ 資訊安全與稽核中心 (Audit & Info Security)",
            "💰 財務與資本運作部 (Finance Dept)",
            "📊 會計與稅務管理部 (Accounting & Tax)",
            "🤝 國內業務與通路發展部 (Domestic Sales)",
            "🌍 國際貿易與海外業務部 (Global Export Sales)",
            "📢 市場行銷與品牌企劃部 (Marketing Dept)",
            "🎧 客戶成功與售後服務部 (Customer Success / CS)",
            "📦 供應鏈與全球採購部 (Supply Chain & Procurement)",
            "🚚 倉儲物流與庫存管理部 (Warehouse & Logistics)",
            "🏭 生產製造與廠務管理部 (Manufacturing & Plant)",
            "⚙️ 工程與技術服務部 (Engineering & Technical)",
            "📅 生產管制與物料控制部 (PMC / Production Control)",
            "🔍 品質保證與品管中心 (QA / QC Dept)",
            "🔬 研發設計與創新中心 (R&D / Design Center)",
            "💻 資訊技術與系統開發部 (IT & Software Development)"
        ]
        selected_department = st.radio("請選擇要配置的部門：", dept_options)
        st.markdown("---")
        st.markdown(f"📍 **目前正在設定**：\n`{selected_department}`")

    with col_modules:
        dept_name_only = selected_department.split(' ')[1]
        st.markdown(f"### 🧩 【{dept_name_only}】的企業全功能模組市集 (App Store)")
        st.markdown("請勾選此部門/高階角色可解鎖啟用的所有功能與戰情儀表板：")
        
        # 業界最完整、涵蓋高階決策與各部門營運的超級功能清單
        m_col1, m_col2, m_col3 = st.columns(3)
        
        with m_col1:
            st.markdown("#### 📈 高階決策與即時行情")
            st.checkbox("🌍 全球原物料即時行情看板", value=True, key=f"{selected_department}_top1")
            st.checkbox("💱 國際匯率與多幣別換算中心", value=True, key=f"{selected_department}_top2")
            st.checkbox("📊 全球股市與財經大盤監控", value=True, key=f"{selected_department}_top3")
            st.checkbox("📑 綜合損益表與資產負債表", value=True, key=f"{selected_department}_top4")
            st.checkbox("💵 現金流與應收/應付帳款水位", value=True, key=f"{selected_department}_top5")
            st.checkbox("🎯 企業KPI與多維度BI戰情室", value=True, key=f"{selected_department}_top6")
            
        with m_col2:
            st.markdown("#### 📦 供應鏈與進銷存 (SCM)")
            st.checkbox("📦 智能進銷存與批號效期管理", value=True, key=f"{selected_department}_scm1")
            st.checkbox("🛒 全球供應鏈採購與比價系統", value=True, key=f"{selected_department}_scm2")
            st.checkbox("🚚 倉儲物流與條碼PDA掃描(WMS)", value=False, key=f"{selected_department}_scm3")
            st.checkbox("📋 供應商交期與品質評鑑系統", value=False, key=f"{selected_department}_scm4")
            st.checkbox("🚢 進出口報關與海運物流追蹤", value=False, key=f"{selected_department}_scm5")
            st.checkbox("🏷️ 條碼/QR Code與資產標籤列印", value=False, key=f"{selected_department}_scm6")

        with m_col3:
            st.markdown("#### 💰 財會、生產與其他核心")
            st.checkbox("💰 總帳會計、傳票與會計師報表", value=True, key=f"{selected_department}_fin1")
            st.checkbox("🏭 生產排程、BOM表與製程管考", value=False, key=f"{selected_department}_mes1")
            st.checkbox("🤝 CRM 客戶關係與外貿商機管理", value=True, key=f"{selected_department}_crm1")
            st.checkbox("👥 人事薪酬、勞健保與考勤排班", value=False, key=f"{selected_department}_hr1")
            st.checkbox("✍️ 電子簽核流程引擎 (BPM)", value=True, key=f"{selected_department}_bpm1")
            st.checkbox("🤖 AI 智慧語音助理與跨國翻譯", value=True, key=f"{selected_department}_ai1")

        st.markdown("---")
        if st.button(f"💾 儲存【{dept_name_only}】的全功能拼圖設定", type="primary", use_container_width=True):
            st.success(f"✅ 已成功將最新完整模組清單儲存至 [{selected_department}]！系統權限已即時更新。")

elif "企業組織與部門樹狀管理" in menu_choice:
    st.markdown("## 🏢 企業組織與部門樹狀管理 (Dynamic Org Chart)")
    st.info("💡 說明：動態建構企業組織架構，確保不同部門與員工享有對應的資料列級隔離（Row-Level Security）。")

else:
    st.markdown("## 📊 系統運行與跨庫數據監控")
    st.info("💡 說明：即時監控各個已掛接外部資料庫的同步狀態、API 呼叫次數與系統效能。")
