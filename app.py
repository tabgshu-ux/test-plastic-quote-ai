import streamlit as st
import pandas as pd
import datetime

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
    page_title="多租戶 AI ERP 系統 - 平台總控、方案定價與租戶管理中心",
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

# 初始化總控登入狀態與管理員權限
if "master_logged_in" not in st.session_state:
    st.session_state.master_logged_in = False
if "selected_tenant" not in st.session_state:
    st.session_state.selected_tenant = None

# 初始化總控台管理員權限清單
if "master_roles_db" not in st.session_state:
    st.session_state.master_roles_db = [
        {"role": "平台最高營運長 (Super Admin)", "account": "admin", "permissions": "全系統租戶控管、方案定價設定、模組派發"},
        {"role": "財務定價專員 (Billing Manager)", "account": "billing", "permissions": "訂閱方案定價、合約到期與帳務審核"}
    ]

# 🌟 核心：初始化三大商業授權方案（旗艦版、正式版、訂閱版）的功能與費用設定資料庫
if "subscription_plans_db" not in st.session_state:
    st.session_state.subscription_plans_db = {
        "🚀 企業旗艦版 (Enterprise Flagship)": {
            "price_usd_year": 3000.0,
            "max_seats": "無限席位 (Unlimited)",
            "features": [
                "總經理室戰情室 (AR/AP, P&L, 全球股市與金屬原物料即時監控)",
                "工程與設計管理中心 (雙層報價、BOM 自動展開、工程驗收)",
                "管理部 (人事薪資、越南 Thông tư 200 財稅、電子發票)",
                "全方位電子簽核中心 (跨部門呈核)",
                "生產部 (倉庫資材、板金加工、粉體塗裝)",
                "資訊管理部 (IT 專屬後台、租戶自主模組開關與外部 API 串聯)"
            ]
        },
        "💼 正式商業版 (Standard Official)": {
            "price_usd_year": 1200.0,
            "max_seats": "30 席位",
            "features": [
                "工程與設計管理中心 (雙層報價與 BOM)",
                "管理部 (人事薪資與考勤打卡)",
                "全方位電子簽核中心",
                "生產部 (倉庫資材管理)"
            ]
        },
        "⏱️ 彈性訂閱版 (Flexible Subscription)": {
            "price_usd_month": 150.0, # 月繳
            "max_seats": "10 席位",
            "features": [
                "模組按需租用 (可選配總經理室戰情室或倉庫資材)",
                "雲端 Storage 基礎支援",
                "標準技術支援"
            ]
        }
    }

# 初始化全系統租戶清單
if "tenant_licensing_db" not in st.session_state:
    st.session_state.tenant_licensing_db = [
        {
            "tenant_id": "TENANT-001",
            "company_name": "裕豐電機工業 (Reetech Industrial)",
            "tax_id": "0312345678",
            "plan": "🚀 企業旗艦版 (Enterprise Flagship)",
            "pricing_usd": 3000.0,
            "max_seats": "無限席位 (Unlimited)",
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
            st.markdown(f"**當前操作租戶**: `{st.session_state.selected_tenant}`")
            if st.button("🔄 返回總控台首頁", use_container_width=True):
                st.session_state.selected_tenant = None
                st.rerun()
        
        if st.button("登出總控系統", use_container_width=True):
            st.session_state.master_logged_in = False
            st.session_state.selected_tenant = None
            st.rerun()

    st.markdown("---")
    
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

# 1. 尚未登入總控台
if not st.session_state.master_logged_in:
    st.markdown("## 🔐 AI ERP 系統 - 平台總控管理員登入")
    st.markdown("---")
    with st.form("master_login_form"):
        m_acc = st.text_input("總控管理員帳號", value="admin")
        m_pass = st.text_input("密碼", type="password", value="123")
        if st.form_submit_button("登入總控台", type="primary", use_container_width=True):
            if m_acc in ["admin", "billing"] and m_pass == "123":
                st.session_state.master_logged_in = True
                st.rerun()
            else:
                st.error("總控管理員帳號或密碼錯誤 (預設 admin / 123)")

# 2. 已登入總控台，但尚未選擇特定租戶：顯示三大總控功能分頁
elif not st.session_state.selected_tenant:
    st.markdown("### 🏢 平台總控台 - 全球企業租戶與商業授權方案管理中心")
    st.caption("在此處管理所有客戶租戶、檢視與設定「旗艦版、正式版、訂閱版」之功能與費用，並可快速進入各租戶環境。")

    master_tab1, master_tab2, master_tab3, master_tab4 = st.tabs([
        "🏢 租戶總覽與快速進入", 
        "🏷️ 方案與費用設定 (旗艦版/正式版/訂閱版)",
        "➕ 註冊新租戶合約",
        "🔒 總控台管理員權限設定 (Master RBAC)"
    ])

    # Tab 1: 租戶總覽與快速進入 (支援即時搜尋)
    with master_tab1:
        st.markdown("#### 📋 平台現有企業租戶清單")
        search_query = st.text_input("🔍 快速搜尋租戶（可輸入公司名稱、代碼或統編）：", placeholder="例如：裕豐 或 TENANT-001")

        tenants = st.session_state.tenant_licensing_db
        if search_query:
            filtered_tenants = [
                t for t in tenants 
                if search_query.lower() in t["company_name"].lower() 
                or search_query.lower() in t["tenant_id"].lower() 
                or search_query.lower() in t["tax_id"].lower()
            ]
        else:
            filtered_tenants = tenants

        if filtered_tenants:
            df_tenants = pd.DataFrame(filtered_tenants)
            st.dataframe(df_tenants, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("#### 🚀 點擊下方按鈕直接進入對應租戶環境：")
            for t in filtered_tenants:
                col_info, col_btn = st.columns([3, 1])
                with col_info:
                    st.markdown(f"**{t['company_name']}** (`{t['tenant_id']}`) | 方案：{t['plan']} | 定價：${t.get('pricing_usd', 0):,.2f}")
                with col_btn:
                    if st.button(f"🚀 進入", key=f"btn_enter_{t['tenant_id']}", use_container_width=True):
                        st.session_state.selected_tenant = t["company_name"]
                        st.rerun()
        else:
            st.warning("⚠️ 找不到符合搜尋條件的企業租戶。")

    # Tab 2: 方案與費用設定 (旗艦版、正式版、訂閱版)
    with master_tab2:
        st.markdown("#### 🏷️ 平台商業授權方案：旗艦版、正式版、訂閱版功能與費用設定")
        st.info("💡 在此處您可以檢視與自訂三大核心方案所包含的模組功能範圍與官方定價標準。")

        plans_db = st.session_state.subscription_plans_db
        
        p_col1, p_col2, p_col3 = st.columns(3)

        with p_col1:
            st.markdown("### 🚀 企業旗艦版")
            st.markdown(f"**年費定價**：`${plans_db['🚀 企業旗艦版 (Enterprise Flagship)']['price_usd_year']:,.2f} USD / 年`")
            st.markdown(f"**授權席位**：{plans_db['🚀 企業旗艦版 (Enterprise Flagship)']['max_seats']}")
            st.markdown("**包含功能模組**：")
            for f in plans_db['🚀 企業旗艦版 (Enterprise Flagship)']['features']:
                st.markdown(f"- {f}")

        with p_col2:
            st.markdown("### 💼 正式商業版")
            st.markdown(f"**年費定價**：`${plans_db['💼 正式商業版 (Standard Official)']['price_usd_year']:,.2f} USD / 年`")
            st.markdown(f"**授權席位**：{plans_db['💼 正式商業版 (Standard Official)']['max_seats']}")
            st.markdown("**包含功能模組**：")
            for f in plans_db['💼 正式商業版 (Standard Official)']['features']:
                st.markdown(f"- {f}")

        with p_col3:
            st.markdown("### ⏱️ 彈性訂閱版")
            st.markdown(f"**月費定價**：`${plans_db['⏱️ 彈性訂閱版 (Flexible Subscription)']['price_usd_month']:,.2f} USD / 月`")
            st.markdown(f"**授權席位**：{plans_db['⏱️ 彈性訂閱版 (Flexible Subscription)']['max_seats']}")
            st.markdown("**包含功能模組**：")
            for f in plans_db['⏱️ 彈性訂閱版 (Flexible Subscription)']['features']:
                st.markdown(f"- {f}")

        st.markdown("---")
        with st.expander("⚙️ 調整方案定價與內容 (方案管理編輯器)"):
            with st.form("form_edit_plans"):
                sel_plan_to_edit = st.selectbox("選擇要修改的方案", list(plans_db.keys()))
                curr_p = plans_db[sel_plan_to_edit]
                
                if "年費定價" in str(curr_p):
                    new_p_val = st.number_input("更新年費定價 (USD / 年)", value=float(curr_p.get("price_usd_year", 1000.0)))
                else:
                    new_p_val = st.number_input("更新月費定價 (USD / 月)", value=float(curr_p.get("price_usd_month", 100.0)))

                if st.form_submit_button("💾 儲存方案定價變更", type="primary"):
                    if "年費定價" in str(curr_p) or "price_usd_year" in curr_p:
                        plans_db[sel_plan_to_edit]["price_usd_year"] = new_p_val
                    else:
                        plans_db[sel_plan_to_edit]["price_usd_month"] = new_p_val
                    st.success(f"🎉 方案 [{sel_plan_to_edit}] 的定價已成功更新！")
                    st.rerun()

    # Tab 3: 註冊新租戶合約
    with master_tab3:
        st.markdown("#### ➕ 註冊新企業租戶合約與方案綁定")
        with st.form("form_add_master_tenant"):
            c1, c2 = st.columns(2)
            with c1:
                new_cname = st.text_input("客戶公司名稱 *", placeholder="例: 越南電力工程股份公司")
                new_tax = st.text_input("統一編號 / 稅號 (MST)", placeholder="例: 0309988776")
                selected_plan_key = st.selectbox("選擇商業授權方案", list(st.session_state.subscription_plans_db.keys()))
            with c2:
                default_price = st.session_state.subscription_plans_db[selected_plan_key].get("price_usd_year", 1200.0)
                new_price = st.number_input("合約定價金額 (USD)", min_value=0.0, value=float(default_price), step=100.0)
                new_seats = st.text_input("授權使用者席位數", value=st.session_state.subscription_plans_db[selected_plan_key].get("max_seats", "30 席位"))
                new_expiry = st.date_input("合約到期日", value=datetime.date(2027, 12, 31) if 'datetime' in globals() else "2027-12-31")

            if st.form_submit_button("💾 註冊新企業租戶並套用方案", type="primary", use_container_width=True):
                if new_cname:
                    new_tid = f"TENANT-{len(st.session_state.tenant_licensing_db)+1:03d}"
                    plan_modules = st.session_state.subscription_plans_db[selected_plan_key]["features"]
                    st.session_state.tenant_licensing_db.append({
                        "tenant_id": new_tid,
                        "company_name": new_cname,
                        "tax_id": new_tax,
                        "plan": selected_plan_key,
                        "pricing_usd": new_price,
                        "max_seats": new_seats,
                        "expiry_date": str(new_expiry),
                        "modules": ["總經理室 (Executive Office)", "管理部 (Management Dept)", "工程與設計管理中心 (Engineering & Design Center)", "生產部 (Production Dept)", "資訊管理部 (IT & System)"],
                        "status": "🟢 正常運行 (Active)"
                    })
                    st.success(f"🎉 成功新增企業租戶 [{new_cname}]，並綁定 [{selected_plan_key}]！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫客戶公司名稱！")

    # Tab 4: 總控台管理員權限設定 (Master RBAC)
    with master_tab4:
        st.markdown("#### 🔒 總控台管理員權限設定 (Master Portal RBAC)")
        df_roles = pd.DataFrame(st.session_state.master_roles_db)
        st.dataframe(df_roles, use_container_width=True, hide_index=True)

        with st.form("form_add_master_role"):
            st.markdown("##### ➕ 新增總控台管理角色")
            r_name = st.text_input("角色名稱", placeholder="例: 亞太區業務總監")
            r_acc = st.text_input("登入帳號", placeholder="例: asia_boss")
            r_desc = st.text_input("權限範圍說明", placeholder="例: 僅檢視亞太區租戶與營收")

            if st.form_submit_button("💾 儲存總控角色設定", type="primary"):
                if r_name and r_acc:
                    st.session_state.master_roles_db.append({
                        "role": r_name,
                        "account": r_acc,
                        "permissions": r_desc
                    })
                    st.success("🎉 總控角色已成功建立！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫角色名稱與帳號！")

# 3. 已進入特定租戶環境
else:
    st.markdown(f"### ⚡ 當前操作租戶環境：`{st.session_state.selected_tenant}`")
    st.markdown("---")

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
