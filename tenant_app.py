import streamlit as st
import pandas as pd

# 引入獨立模組
from modules.executive_bi import render_executive_bi
from modules.pos_retail import render_pos_retail
from modules.mes_factory import render_mes_factory
from modules.app_store import render_app_store
from modules.org_chart import render_org_chart
from modules.rbac import render_rbac

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

    # 預設載入裕豐電機工業 (Reetech Industrial) 專屬資料
    if "current_tenant_data" not in st.session_state:
        st.session_state.current_tenant_data = {
            "tenant_id": "tenant_reetech",
            "name": "裕豐電機工業 (Reetech Industrial)",
            "logo_url": "https://img.icons8.com/color/96/factory.png",
            "plan": "🚀 旗艦集團版 (Enterprise)",
            "dept_modules_db": {
                "👑 董事長室 / 總經理室 (Executive & Board Room)": ["老闆級即時經營戰情室 (Executive BI)"]
            },
            "staff": [
                {"name": "許福村", "account": "boss", "password": "123", "role": "👑 Tenant Admin (董仔/管理員)", "dept": "董事長室"},
                {"name": "財務副理", "account": "finance", "password": "123", "role": "💰 財務副理", "dept": "財務與資本運作部"}
            ],
            "org_nodes": [
                {"id": "node_root", "name": "董事長室", "type": "👑 頂層 (Board)", "parent": "無 (頂層)"},
                {"id": "node_eng", "name": "工程技術部", "type": "⚙️ 工程製造", "parent": "董事長室"}
            ]
        }

    tenant_info = st.session_state.current_tenant_data

    ALL_ENTERPRISE_DEPARTMENTS = [
        "👑 董事長室 / 總經理室 (Executive & Board Room)",
        "☕ 智慧零售、POS 收銀與會員行銷生態系 (Smart Retail & POS)",
        "🏭 生產製造與廠務管理部 (Manufacturing & Plant)",
        "📦 倉儲物流與庫存管理部 (Warehouse & Logistics)"
        "🏢 企業部門與廠區動態管理 (Departments)"
    ]

    # ==================== 側邊欄導覽 (支援動態 Logo 與公司名稱) ====================
    with st.sidebar:
        logo = tenant_info.get("logo_url", "https://img.icons8.com/color/96/factory.png")
        c_name = tenant_info.get("name", "裕豐電機工業")
        
        st.image(logo, width=64)
        st.markdown(f"### 🏭 {c_name}")
        st.markdown(f"**目前方案**: `{tenant_info.get('plan', 'Enterprise')}`")
        st.markdown("---")
        
        if st.session_state.tenant_logged_in:
            user_info = st.session_state.current_tenant_user
            st.markdown(f"**登入員工**: `{user_info['name']}`")
            st.markdown(f"**身分角色**: `{user_info['role']}`")
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
                    "👥 員工帳號與權限管理 (RBAC)",
                    "🎨 企業品牌識別與 Logo 自訂"
                ]
            )
        else:
            tenant_menu = "🔒 請先登入"

    # ==================== 路由分發與權限控管 ====================
    if not st.session_state.tenant_logged_in:
        st.markdown("## 🔐 裕豐電機工業 (Reetech) ERP 系統安全登入")
        st.info("💡 *請輸入企業端內部帳號與密碼 (預設老闆帳號: `boss` / 密碼: `123`)*")
        with st.form("tenant_login_form"):
            t_acc = st.text_input("帳號 (Account)", placeholder="例: boss 或 finance")
            t_pass = st.text_input("密碼 (Password)", type="password", placeholder="請輸入密碼...")
            if st.form_submit_button("🔓 登入企業 ERP", type="primary", use_container_width=True):
                matched = next((s for s in tenant_info["staff"] if s["account"] == t_acc and s["password"] == t_pass), None)
                if matched:
                    st.session_state.tenant_logged_in = True
                    st.session_state.current_tenant_user = matched
                    st.success("🎉 登入成功！歡迎回到裕豐電機工業 ERP 系統。")
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
        elif "員工帳號與權限管理" in tenant_menu:
            render_rbac(tenant_info)
        else:
            # 🎨 新增的品牌識別與 Logo 自訂模組
            st.markdown("## 🎨 企業品牌識別與 Logo 自訂中心 (Tenant Branding)")
            st.info("💡 *在此您可以自由更改系統左上角顯示的企業標誌 (Logo 圖片網址) 與公司顯示名稱，裕豐專屬識別可隨時一鍵更新。*")
            
            with st.form("branding_form"):
                current_name = tenant_info.get("name", "裕豐電機工業 (Reetech Industrial)")
                current_logo = tenant_info.get("logo_url", "https://img.icons8.com/color/96/factory.png")
                
                new_company_name = st.text_input("公司顯示名稱 (Company Display Name)", value=current_name)
                new_logo_url = st.text_input("左上角 Logo 圖片網址 (Logo Image URL)", value=current_logo)
                
                st.markdown("---")
                st.markdown("### 👁️ 即時預覽效果")
                col_p1, col_p2 = st.columns([1, 4])
                with col_p1:
                    st.image(new_logo_url, width=64)
                with col_p2:
                    st.markdown(f"### {new_company_name}")
                    
                if st.form_submit_button("💾 儲存並更新品牌識別", type="primary", use_container_width=True):
                    tenant_info["name"] = new_company_name
                    tenant_info["logo_url"] = new_logo_url
                    st.success(f"🎉 成功更新！左上角圖案與公司名稱已即時套用至 [{new_company_name}]。")
                    st.rerun()
