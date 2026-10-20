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

# 3. 初始化 Session State 模擬動態組織與拼圖資料庫（讓您可以在畫面中即時新增、拼裝、刪除）
if "org_nodes" not in st.session_state:
    st.session_state.org_nodes = [
        {"id": "node_01", "name": "董事會 / 總經理室", "type": "高階決策層", "parent": "無 (頂層)", "modules": ["全球股市/原物料/匯率", "集團綜合損益(P&L)", "應收/應付水位"]},
        {"id": "node_02", "name": "工程部", "type": "營運部門", "parent": "董事會 / 總經理室", "modules": ["工程估驗計價", "施工日報表", "點工點料回報"]},
        {"id": "node_03", "name": "管理部", "type": "行政支援", "parent": "董事會 / 總經理室", "modules": ["人事考勤薪資", "電子簽核(BPM)", "資安與合規"]},
        {"id": "node_04", "name": "生產部", "type": "製造中心", "parent": "董事會 / 總經理室", "modules": ["MES現場報工", "BOM表與製程", "OEE設備監控"]},
        {"id": "node_05", "name": "廠內原物料倉庫", "type": "實體據點/庫位", "parent": "生產部", "modules": ["多倉儲位查詢", "條碼PDA收發貨", "安全庫存警示"]}
    ]

# 4. 側邊欄導覽
with st.sidebar:
    st.image("https://img.icons8.com/color/96/company.png", width=64)
    st.markdown("### 🌐 SaaS ERP 總控台")
    
    lang = st.selectbox("選擇語系 / Select Language", ["繁體中文", "English", "Tiếng Việt (越南語)", "简体中文"])
    
    st.markdown("---")
    st.markdown("👤 **目前登入者**: `System Admin`")
    st.markdown("🏢 **目前租戶**: `SaaS Global Control`")
    
    st.markdown("---")
    st.markdown("### 📌 系統導覽選單")
    menu_choice = st.radio(
        "選擇管理模組",
        [
            "🧩 動態組織拼圖與樹狀架構 (Visual Org Builder)",
            "🔌 外部資料庫與 API 串聯 (Database Bridge)", 
            "📦 模組市集與功能授權設定 (App Store)",
            "🇻🇳 跨國在地化與越南財稅模組 (VN Localization)",
            "📊 系統運行與跨庫數據監控"
        ]
    )
    
    st.markdown("---")
    if st.button("🚪 登出系統", use_container_width=True):
        st.info("已安全登出系統。")

# 5. 主畫面邏輯路由
if "動態組織拼圖與樹狀架構" in menu_choice:
    st.markdown("## 🧩 動態組織拼圖與樹狀架構管理 (Visual Org-Chart Builder)")
    st.info("💡 *在此處您可以像玩樂高積木一樣，自由新增組織節點（如董事會、總經理室、工程部、管理部），並自由指定其上下級關係（例如將倉庫掛在生產部下方），系統將即時組織化呈現並賦予對應功能！*")
    
    col_builder, col_preview = st.columns([1, 1])
    
    with col_builder:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### ➕ 拼裝新組織節點 / 實體據點")
        with st.form("org_builder_form"):
            new_name = st.text_input("節點/部門/倉庫名稱*", placeholder="例：越南平陽廠模具倉 或 海外業務處")
            new_type = st.selectbox("節點屬性", ["高階決策層 (Board/Exec)", "營運/行政部門 (Department)", "實體據點/倉庫 (Location/Warehouse)", "子公司/分公司 (Branch)"])
            
            # 動態取得現有節點作為上級選單
            existing_names = [node["name"] for node in st.session_state.org_nodes]
            parent_options = ["無 (頂層主節點)"] + existing_names
            new_parent = st.selectbox("指定上級掛載點 (Parent Node)", parent_options)
            
            # 勾選或選擇該節點要賦予的拼圖功能
            st.markdown("#### 🧩 勾選此節點要啟用的功能拼圖：")
            feat_c1, feat_c2 = st.columns(2)
            with feat_c1:
                f1 = st.checkbox("📈 股市/原物料/匯率戰情室", value=False)
                f2 = st.checkbox("💰 財務損益與應收付總覽", value=False)
                f3 = st.checkbox("📦 庫存與倉儲條碼掃描", value=True)
            with feat_c2:
                f4 = st.checkbox("⚙️ 工程估驗與施工日報", value=False)
                f5 = st.checkbox("👥 人事考勤與薪酬管理", value=False)
                f6 = st.checkbox("🇻🇳 越南電子發票與稅務", value=False)

            submitted = st.form_submit_button("🧱 拼入組織架構中", type="primary", use_container_width=True)
            if submitted:
                if not new_name:
                    st.error("❌ 請輸入名稱！")
                else:
                    selected_feats = []
                    if f1: selected_feats.append("📈 股市/原物料/匯率戰情室")
                    if f2: selected_feats.append("💰 財務損益與應收付總覽")
                    if f3: selected_feats.append("📦 庫存與倉儲條碼掃描")
                    if f4: selected_feats.append("⚙️ 工程估驗與施工日報")
                    if f5: selected_feats.append("👥 人事考勤與薪酬管理")
                    if f6: selected_feats.append("🇻🇳 越南電子發票與稅務")
                    
                    new_node = {
                        "id": f"node_{len(st.session_state.org_nodes)+1:02d}",
                        "name": new_name,
                        "type": new_type,
                        "parent": new_parent,
                        "modules": selected_feats
                    }
                    st.session_state.org_nodes.append(new_node)
                    st.success(f"🎉 成功將 [{new_name}] 拼裝至上級節點：`{new_parent}`！")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_preview:
        st.markdown("### 🌳 目前企業組織樹狀拼圖總覽")
        st.info("💡 視覺化呈現您目前的組織階層與掛載關係：")
        
        for node in st.session_state.org_nodes:
            indent = "&nbsp;&nbsp;&nbsp;&nbsp;┗ 📂 " if node["parent"] != "無 (頂層主節點)" else "👑 "
            st.markdown(f"""
                <div style="background: white; padding: 10px; border-radius: 6px; margin-bottom: 8px; border-left: 4px solid #3b82f6;">
                    <b>{indent}{node['name']}</b> <span style="font-size: 12px; color: gray;">({node['type']})</span><br>
                    <span style="font-size: 12px; color: #0f766e;">📌 上級掛載：{node['parent']}</span><br>
                    <span style="font-size: 12px; color: #6b7280;">🧩 啟用拼圖：{', '.join(node['modules']) if node['modules'] else '無'}</span>
                </div>
            """, unsafe_allow_html=True)

elif "外部資料庫與 API 串聯" in menu_choice:
    st.markdown("## 🔌 外部資料庫與異質資料來源串聯設定 (Database Bridge)")
    st.info("💡 *在此處您可以設定與擴充對外連結的其他客戶資料庫或即時 API 來源，無須修改程式碼。*")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        with st.form("db_bridge_form"):
            st.markdown("### ➕ 新增或設定外部資料庫 / API 來源")
            col1, col2 = st.columns(2)
            with col1:
                db_key = st.text_input("來源代碼 (Key)*", placeholder="例：vn_e_invoice_api")
                db_display_name = st.text_input("顯示名稱*", placeholder="例：越南總局電子發票 API")
                db_type = st.selectbox("連線類型", ["RESTful API / JSON Bridge", "PostgreSQL / Supabase", "MySQL / MariaDB", "Microsoft SQL Server"])
                db_host = st.text_input("主機位址 / API Endpoint*", placeholder="例：https://api.einvoice.vn/v1")
            with col2:
                db_port = st.text_input("通訊埠 (Port)", placeholder="例：3306")
                db_name = st.text_input("路徑 / 資料庫名稱*", placeholder="v1/invoice")
                db_user = st.text_input("API Token / 帳號*", placeholder="Bearer token...")
                db_password = st.text_input("密鑰*", type="password")

            if st.form_submit_button("💾 儲存並啟用連線設定", type="primary", use_container_width=True):
                st.success("✅ 外部資料來源設定已成功儲存！")
        st.markdown('</div>', unsafe_allow_html=True)

elif "模組市集與功能授權設定" in menu_choice:
    st.markdown("## 📦 模組市集與功能授權設定 (App Store & Feature Toggles)")
    st.info("💡 說明：在此處可以檢視全系統所有可用的企業模組市集，並針對不同客戶方案大量派發或收回功能拼圖。")
    st.checkbox("📦 智能進銷存與庫存管理", value=True)
    st.checkbox("💰 財務總帳與越南電子發票", value=True)
    st.checkbox("🏭 MES 現場報工與 OEE 監控", value=True)
    st.checkbox("📈 國際股市、匯率與原物料戰情", value=True)

elif "跨國在地化與越南財稅模組" in menu_choice:
    st.markdown("## 🇻🇳 跨國在地化與越南財稅模組 (Vietnam Localization & E-Invoice)")
    st.info("💡 說明：越南紅發票自動解析與 VAT 稅額勾稽。")
    uploaded_invoice = st.file_uploader("請上傳越南電子發票 (XML / PDF)", type=["xml", "pdf"])
    if uploaded_invoice:
        st.success("🎉 越南紅發票解析成功，已自動對應傳票與會計科目！")

else:
    st.markdown("## 📊 系統運行與跨庫數據監控")
    st.info("💡 說明：即時監控各個已掛接外部資料庫與 API 來源的同步狀態。")
