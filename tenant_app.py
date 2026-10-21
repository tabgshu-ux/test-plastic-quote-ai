import streamlit as st
import pandas as pd

# 引入獨立模組
from modules.executive_bi import render_executive_bi
from modules.pos_retail import render_pos_retail
from modules.mes_factory import render_mes_factory
from modules.app_store import render_app_store
from modules.org_chart import render_org_chart
from modules.rbac import render_rbac

st.set_page_config(
    page_title="Tenant Enterprise ERP System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card-container { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); margin-bottom: 20px; }
    h1, h2, h3 { color: #1e293b; }
    .stButton>button { border-radius: 6px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

if "tenant_logged_in" not in st.session_state:
    st.session_state.tenant_logged_in = False
if "current_tenant_user" not in st.session_state:
    st.session_state.current_tenant_user = None

if "current_tenant_data" not in st.session_state:
    st.session_state.current_tenant_data = {
        "tenant_id": "tenant_vina_group",
        "name": "🇻🇳 越南平陽控股集團 (暨環保鞋業與咖啡廳)",
        "plan": "🚀 旗艦集團版 (Enterprise)",
        "dept_modules_db": {
            "👑 董事長室 / 總經理室 (Executive & Board Room)": ["老闆級即時經營戰情室 (Executive BI)"]
        },
        "staff": [
            {"name": "許福村", "account": "boss", "password": "123", "role": "👑 Tenant Admin (老闆)", "dept": "董事長室"},
            {"name": "Trần Văn Minh", "account": "minh", "password": "123", "role": "💰 財務主管", "dept": "財務部"}
        ],
        "org_nodes": [
            {"id": "node_root", "name": "集團董事長室", "type": "👑 頂層 (Board)", "parent": "無 (頂層)"},
            {"id": "node_eng", "name": "越南平陽廠區", "type": "🏭 製造廠區", "parent": "集團董事長室"}
        ]
    }

tenant_info = st.session_state.current_tenant_data

ALL_ENTERPRISE_DEPARTMENTS = [
    "👑 董事長室 / 總經理室 (Executive & Board Room)",
    "☕ 智慧零售、POS 收銀與會員行銷生態系 (Smart Retail & POS)",
    "🏭 生產製造與廠務管理部 (Manufacturing & Plant)",
    "📦 倉儲物流與庫存管理部 (Warehouse & Logistics)"
]

# 側邊欄導覽
with st.sidebar:
    st.image("https://img.icons8.com/color/96/factory.png", width=64)
    st.markdown(f"### 🏭 {tenant_info['name']}")
    st.markdown("---")
    
    if st.session_state.tenant_logged_in:
        user_info = st.session_state.current_tenant_user
        st.markdown(f"**登入員工**: `{user_info['name']}`")
        if st.button("🔒 登出租戶系統", use_container_width=True):
            st.session_state.tenant_logged_in = False
            st.session_state.current_tenant_user = None
            st.rerun()
    else:
        st.markdown("🔒 **身分**: `請先登入企業帳號`")
        
    st.markdown("---")
    if st.session_state.tenant_logged_in:
        tenant_menu = st.radio(
            "企業內部模組選單",
            [
                "👑 老闆級即時經營戰情室 (Executive BI)",
                "☕ 智慧零售與 POS 咖啡廳管理",
                "🎨 顏色喜好連動 MES 車間排程",
                "🛒 樂高積木式模組市集 (App Store)",
                "🖱️ 組織架構圖與節點管理",
                "👥 員工帳號與權限管理 (RBAC)"
            ]
        )
    else:
        tenant_menu = "🔒 請先登入"

# 路由分發
if not st.session_state.tenant_logged_in:
    st.markdown("## 🔐 企業租戶 ERP 系統安全登入")
    with st.form("tenant_login_form"):
        t_acc = st.text_input("帳號 (Account)", placeholder="例: boss 或 minh")
        t_pass = st.text_input("密碼 (Password)", type="password", placeholder="請輸入密碼 (預設: 123)...")
        if st.form_submit_button("🔓 登入企業 ERP", type="primary", use_container_width=True):
            matched = next((s for s in tenant_info["staff"] if s["account"] == t_acc and s["password"] == t_pass), None)
            if matched:
                st.session_state.tenant_logged_in = True
                st.session_state.current_tenant_user = matched
                st.success("🎉 登入成功！")
                st.rerun()
            else:
                st.error("❌ 帳號或密碼錯誤！")
else:
    if "老闆級即時經營戰情室" in tenant_menu:
        render_executive_bi(tenant_info)
    elif "智慧零售與 POS 咖啡廳管理" in tenant_menu:
        render_pos_retail(tenant_info)
    elif "顏色喜好連動 MES 車間排程" in tenant_menu:
        render_mes_factory(tenant_info)
    elif "樂高積木式模組市集" in tenant_menu:
        render_app_store(tenant_info, ALL_ENTERPRISE_DEPARTMENTS)
    elif "組織架構圖" in tenant_menu:
        render_org_chart(tenant_info)
    else:
        render_rbac(tenant_info)
