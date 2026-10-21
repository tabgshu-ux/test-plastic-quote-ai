import streamlit as st
import pandas as pd

# 引入各大部門模組
from modules.executive_bi import render_executive_bi
from modules.pos_retail import render_pos_retail
from modules.mes_factory import render_mes_factory
from modules.app_store import render_app_store
from modules.org_chart import render_org_chart
from modules.rbac import render_rbac
from modules.departments_manager import render_departments_manager

# 引入總經理室戰情室與租戶 IT 授權模組
import executive_office
import system_licensing

st.set_page_config(
    page_title="裕豐電機工業 (Reetech Industrial) ERP 系統",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card-container { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); margin-bottom: 20px; }
    h1, h2, h3 { color: #1e293b; }
    .stButton>button { border-radius: 6px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 初始化登入狀態
if "tenant_logged_in" not in st.session_state:
    st.session_state.tenant_logged_in = False
if "current_tenant_user" not in st.session_state:
    st.session_state.current_tenant_user = None

# 初始化租戶動態勾選的模組清單（預設全部開啟）
if "tenant_active_modules" not in st.session_state:
    st.session_state.tenant_active_modules = [
        "總經理室 (Executive Office)",
        "管理部 (Management Dept)",
        "全方位電子簽核中心 (Approval Center)",
        "工程與設計管理中心 (Engineering & Design Center)",
        "生產部 (Production Dept)",
        "資訊管理部 (IT & System)"
    ]

# 裕豐電機工業專屬租戶資料
tenant_info = {
    "name": "裕豐電機工業 (Reetech Industrial)",
    "logo_url": "https://img.icons8.com/color/96/factory.png",
    "plan": "企業旗艦版",
    "staff": [
        {"name": "許福村", "account": "boss", "password": "123", "role": "總經理 / 管理員", "dept": "總經理室"}
    ]
}

# ==================== 側邊欄動態選單導覽 ====================
with st.sidebar:
    st.image(tenant_info["logo_url"], width=64)
    st.markdown(f"### {tenant_info['name']}")
    st.markdown("---")
    
    if st.session_state.tenant_logged_in:
        user_info = st.session_state.current_tenant_user
        st.markdown(f"**登入員工**: `{user_info['name']}`")
        if st.button("登出系統", use_container_width=True):
            st.session_state.tenant_logged_in = False
            st.session_state.current_tenant_user = None
            st.rerun()
    else:
        st.markdown("狀態: 未登入")
        
    st.markdown("---")
    if st.session_state.tenant_logged_in:
        st.markdown("讀取選擇一個部門/系統：")
        
        # 🔗 核心動態連動：只抓取租戶 IT 在後台有勾選啟用的模組清單來生成選項
        allowed_menu_options = st.session_state.tenant_active_modules
        
        if allowed_menu_options:
            tenant_menu = st.radio(
                "部門選單",
                allowed_menu_options,
                label_visibility="collapsed"
            )
        else:
            st.warning("⚠️ 目前無任何啟用模組，請至「資訊管理部」勾選開通。")
            tenant_menu = "資訊管理部 (IT & System)"
    else:
        tenant_menu = "請先登入"

# ==================== 主畫面邏輯 ====================
if not st.session_state.tenant_logged_in:
    st.markdown("## 裕豐電機工業 (Reetech Industrial) ERP 系統登入")
    st.markdown("---")
    
    with st.form("tenant_login_form"):
        t_acc = st.text_input("帳號", placeholder="請輸入內部員工帳號...")
        t_pass = st.text_input("密碼", type="password", placeholder="請輸入密碼...")
        
        if st.form_submit_button("登入系統", type="primary", use_container_width=True):
            matched = next((s for s in tenant_info["staff"] if s["account"] == t_acc and s["password"] == t_pass), None)
            if matched:
                st.session_state.tenant_logged_in = True
                st.session_state.current_tenant_user = matched
                st.rerun()
            else:
                st.error("帳號或密碼錯誤")
else:
    # 依照租戶選單動態路由載入對應模組
    if "總經理室" in tenant_menu:
        executive_office.show(tenant_info)
    elif "管理部" in tenant_menu:
        render_pos_retail(tenant_info)
    elif "全方位電子簽核" in tenant_menu:
        render_app_store(tenant_info, [])
    elif "工程與設計" in tenant_menu:
        render_mes_factory(tenant_info)
    elif "生產部" in tenant_menu:
        render_org_chart(tenant_info)
    elif "資訊管理部" in tenant_menu:
        # 這裡整合原本的 RBAC 權限與我們專屬的 system_licensing (租戶自主勾選模組與 API 設定)
        st.markdown("### 💻 資訊管理部 (IT & System) 專屬後台")
        it_tab1, it_tab2 = st.tabs(["🔒 組織權限與角色管理 (RBAC)", "🧩 租戶模組勾選與外部 API 設定"])
        with it_tab1:
            render_rbac(tenant_info)
        with it_tab2:
            system_licensing.show(tenant_info)
