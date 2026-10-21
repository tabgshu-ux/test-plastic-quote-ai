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
from modules import executive_office
from modules import system_licensing

st.set_page_config(
    page_title="多租戶 AI ERP 系統 - 平台總控與租戶管理中心",
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

# 初始化總控與登入狀態
if "master_logged_in" not in st.session_state:
    st.session_state.master_logged_in = False
if "selected_tenant" not in st.session_state:
    st.session_state.selected_tenant = None

# 初始化全系統租戶清單資料庫
if "tenant_licensing_db" not in st.session_state:
    st.session_state.tenant_licensing_db = [
        {
            "tenant_id": "TENANT-001",
            "company_name": "裕豐電機工業 (Reetech Industrial)",
            "tax_id": "0312345678",
            "plan": "企業旗艦統包版 (Enterprise)",
            "max_seats": 50,
            "expiry_date": "2027-12-31",
            "modules": [
                "總經理室 (Executive Office)",
                "管理部 (Management Dept)",
                "全方位電子簽核中心 (Approval Center)",
                "工程與設計管理中心 (Engineering & Design Center)",
                "生產部 (Production Dept)",
                "資訊管理部 (IT & System)"
            ],
            "status": "🟢 正常運行 (Active)"
        }
    ]

# 初始化租戶動態勾選的模組清單
if "tenant_active_modules" not in st.session_state:
    st.session_state.tenant_active_modules = [
        "總經理室 (Executive Office)",
        "管理部 (Management Dept)",
        "全方位電子簽核中心 (Approval Center)",
        "工程與設計管理中心 (Engineering & Design Center)",
        "生產部 (Production Dept)",
        "資訊管理部 (IT & System)"
    ]

# ==================== 側邊欄：總控與租戶切換導覽 ====================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/factory.png", width=64)
    st.markdown("### ⚡ AI ERP 總控台 (Master Portal)")
    st.markdown("---")
    
    if not st.session_state.master_logged_in:
        st.markdown("狀態: 請先登入總控台")
    else:
        st.success("🟢 總控管理員已登入")
        if st.session_state.selected_tenant:
            st.markdown(f"**當前租戶**: `{st.session_state.selected_tenant}`")
            if st.button("🔄 返回總控台總覽", use_container_width=True):
                st.session_state.selected_tenant = None
                st.rerun()
        
        if st.button("登出總控系統", use_container_width=True):
            st.session_state.master_logged_in = False
            st.session_state.selected_tenant = None
            st.rerun()

    st.markdown("---")
    
    # 若已登入總控且已進入特定租戶，顯示該租戶的部門動態選單
    if st.session_state.master_logged_in and st.session_state.selected_tenant:
        st.markdown("##### 🏢 租戶端部門選單：")
        allowed_menu_options = st.session_state.get("tenant_active_modules", [])
        if allowed_menu_options:
            tenant_menu = st.radio("租戶部門選單", allowed_menu_options, label_visibility="collapsed")
        else:
            tenant_menu = "資訊管理部 (IT & System)"
    else:
        tenant_menu = "總控台總覽"

# ==================== 主畫面邏輯：雙層架構路由 ====================

# 1. 尚未登入總控台：顯示總控登入畫面
if not st.session_state.master_logged_in:
    st.markdown("## 🔐 AI ERP 系統 - 平台總控管理員登入")
    st.markdown("---")
    with st.form("master_login_form"):
        m_acc = st.text_input("總控管理員帳號", value="admin")
        m_pass = st.text_input("密碼", type="password", value="123")
        if st.form_submit_button("登入總控台", type="primary", use_container_width=True):
            if m_acc == "admin" and m_pass == "123":
                st.session_state.master_logged_in = True
                st.rerun()
            else:
                st.error("總控管理員帳號或密碼錯誤 (預設 admin / 123)")

# 2. 已登入總控台，但尚未選擇特定租戶：顯示總控台首頁（租戶合約總覽與切換）
elif not st.session_state.selected_tenant:
    st.markdown("### 🏢 平台總控台 - 全球企業租戶（Tenant）總覽與合約管理")
    st.caption("在此處您可以檢視所有客戶租戶合約、新增租戶，或點擊進入指定租戶的內部作業環境。")

    # 顯示目前所有租戶清單
    tenants = st.session_state.tenant_licensing_db
    df_tenants = pd.DataFrame(tenants)
    st.dataframe(df_tenants, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 🚀 快速進入租戶端作業環境")
    tenant_names = [t["company_name"] for t in tenants]
    chosen_t = st.selectbox("選擇要進入的企業租戶：", tenant_names)

    col_enter, col_new = st.columns(2)
    with col_enter:
        if st.button("🚀 進入該租戶工作環境", type="primary", use_container_width=True):
            st.session_state.selected_tenant = chosen_t
            st.rerun()
    with col_new:
        if st.button("➕ 註冊新企業租戶合約", use_container_width=True):
            st.info("您可以直接進入該租戶的「資訊管理部」進行合約與模組開關設定。")

# 3. 已進入特定租戶環境：渲染該租戶內部的各部門與模組
else:
    st.markdown(f"### ⚡ 當前操作租戶環境：`{st.session_state.selected_tenant}`")
    st.markdown("---")

    # 依照租戶選單動態路由載入對應模組
    if "總經理室" in tenant_menu:
        executive_office.show({"name": st.session_state.selected_tenant})
    elif "管理部" in tenant_menu:
        render_pos_retail({"name": st.session_state.selected_tenant})
    elif "全方位電子簽核" in tenant_menu:
        render_app_store({"name": st.session_state.selected_tenant}, [])
    elif "工程與設計" in tenant_menu:
        render_mes_factory({"name": st.session_state.selected_tenant})
    elif "生產部" in tenant_menu:
        render_org_chart({"name": st.session_state.selected_tenant})
    elif "資訊管理部" in tenant_menu:
        st.markdown("### 💻 資訊管理部 (IT & System) 專屬後台")
        it_tab1, it_tab2 = st.tabs(["🔒 組織權限與角色管理 (RBAC)", "🧩 租戶模組自主勾選與外部 API 設定"])
        with it_tab1:
            render_rbac({"name": st.session_state.selected_tenant})
        with it_tab2:
            system_licensing.show({"name": st.session_state.selected_tenant})
