import streamlit as st
import pandas as pd

from modules.executive_bi import render_executive_bi
from modules.pos_retail import render_pos_retail
from modules.mes_factory import render_mes_factory
from modules.app_store import render_app_store
from modules.org_chart import render_org_chart
from modules.rbac import render_rbac
from modules.departments_manager import render_departments_manager

def render_tenant_app():
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

    # 多租戶資料庫初始化（支援多個不同的租戶切換）
    if "multi_tenants_db" not in st.session_state:
        st.session_state.multi_tenants_db = {
            "tenant_reetech": {
                "name": "裕豐電機工業 (Reetech Industrial)",
                "logo_url": "https://img.icons8.com/color/96/factory.png",
                "plan": "🚀 旗艦集團版 (Enterprise)",
                "staff": [
                    {"name": "許福村", "account": "boss", "password": "123", "role": "Tenant Admin (老闆)", "dept": "董事長室"}
                ],
                "org_nodes": [{"id": "n1", "name": "董事長室", "type": "👑 頂層", "parent": "無"}]
            },
            "tenant_vina_group": {
                "name": "🇻🇳 越南平陽控股集團",
                "logo_url": "https://img.icons8.com/color/96/company.png",
                "plan": "💼 標準商業版",
                "staff": [
                    {"name": "Trần Văn Minh", "account": "admin", "password": "123", "role": "Tenant Admin (老闆)", "dept": "總管理處"}
                ],
                "org_nodes": [{"id": "n2", "name": "總管理處", "type": "👑 頂層", "parent": "無"}]
            }
        }

    if "active_tenant_id" not in st.session_state:
        st.session_state.active_tenant_id = "tenant_reetech"

    tenant_info = st.session_state.multi_tenants_db[st.session_state.active_tenant_id]

    ALL_ENTERPRISE_DEPARTMENTS = [
        "👑 董事長室 / 總經理室",
        "🏭 生產製造與廠務管理部",
        "💼 商務與業務管理部"
    ]

    with st.sidebar:
        logo = tenant_info.get("logo_url", "https://img.icons8.com/color/96/factory.png")
        st.image(logo, width=64)
        st.markdown(f"### 🏭 {tenant_info['name']}")
        st.markdown(f"**方案**: `{tenant_info.get('plan')}`")
        st.markdown("---")
        
        if st.session_state.tenant_logged_in:
            user_info = st.session_state.current_tenant_user
            st.markdown(f"**登入員工**: `{user_info['name']}`")
            if st.button("🔒 登出當前租戶", use_container_width=True):
                st.session_state.tenant_logged_in = False
                st.session_state.current_tenant_user = None
                st.rerun()
        else:
            st.markdown("🔒 **身分**: `未登入`")
            
        st.markdown("---")
        if st.session_state.tenant_logged_in:
            tenant_menu = st.radio(
                "企業內部模組選單",
                [
                    "👑 老闆級即時經營戰情室 (Executive BI)",
                    "💼 商務接單與多幣別報價",
                    "🏭 MES 電機製造與車間排程",
                    "🏢 組織架構與部門管理",
                    "🛒 拼圖式模組市集 (App Store)",
                    "👥 員工帳號與權限管理 (RBAC)",
                    "🎨 企業品牌識別與 Logo 自訂"
                ]
            )
        else:
            tenant_menu = "🔒 請先登入"

    if not st.session_state.tenant_logged_in:
        st.markdown("## 🔐 企業租戶 ERP 系統登入")
        
        # 允許選擇要登入哪一家租戶
        selected_tenant_key = st.selectbox(
            "選擇目標企業租戶 (Select Tenant)",
            list(st.session_state.multi_tenants_db.keys()),
            format_func=lambda x: st.session_state.multi_tenants_db[x]["name"]
        )
        st.session_state.active_tenant_id = selected_tenant_key
        curr_t = st.session_state.multi_tenants_db[selected_tenant_key]

        with st.form("tenant_login_form"):
            t_acc = st.text_input("帳號 (Account)", placeholder="請輸入帳號...")
            t_pass = st.text_input("密碼 (Password)", type="password", placeholder="請輸入密碼...")
            if st.form_submit_button("🔓 登入該企業 ERP", type="primary", use_container_width=True):
                matched = next((s for s in curr_t["staff"] if s["account"] == t_acc and s["password"] == t_pass), None)
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
        elif "商務接單" in tenant_menu:
            render_pos_retail(tenant_info)
        elif "MES" in tenant_menu:
            render_mes_factory(tenant_info)
        elif "組織架構與部門管理" in tenant_menu:
            render_departments_manager(tenant_info)
        elif "拼圖式模組市集" in tenant_menu:
            render_app_store(tenant_info, ALL_ENTERPRISE_DEPARTMENTS)
        elif "員工帳號與權限管理" in tenant_menu:
            render_rbac(tenant_info)
        else:
            st.markdown("## 🎨 企業品牌識別與 Logo 自訂")
            with st.form("branding_form"):
                new_name = st.text_input("公司顯示名稱", value=tenant_info["name"])
                new_logo = st.text_input("Logo 圖片網址", value=tenant_info["logo_url"])
                if st.form_submit_button("💾 儲存", type="primary", use_container_width=True):
                    tenant_info["name"] = new_name
                    tenant_info["logo_url"] = new_logo
                    st.success("🎉 更新成功！")
                    st.rerun()
