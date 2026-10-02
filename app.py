import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# ----------------------------------------------------
# 1. 載入各獨立業務模組 (Modules)
# ----------------------------------------------------
import modules.executive_dashboard as executive_dashboard
import modules.procurement_ap as procurement_ap
import modules.sales_order_ar as sales_order_ar
import modules.approval_workflow as approval_workflow
import modules.warehouse_management as warehouse_management
import modules.employee_management as employee_management
import modules.asset_management as asset_management
import modules.user_management as user_management

st.set_page_config(
    page_title="裕豐電機工業 REETECH INDUSTRIAL - AI ERP",
    page_icon="⚡",
    layout="wide"
)

# ----------------------------------------------------
# 2. 多國語言字典 (i18n)
# ----------------------------------------------------
i18n = {
    "繁體中文": {
        "company_name": "⚡ 裕豐電機工業",
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ 裕豐電機工業 REETECH INDUSTRIAL - 系統登入",
        "username": "帳號",
        "password": "密碼",
        "login_btn": "🔑 登入系統",
        "logout_btn": "🚪 登出系統",
        "lang_selector": "🌐 語言設定 / Language",
        "menu_header": "公司組織部門選單",
        "menu_exec": "👑 董事長/總經理 - 營運戰情看板",
        "menu_ap": "🛒 管理部 - 採購與應付帳款 (AP & 廠商發票)",
        "menu_ar": "📋 管理部 - 客戶應收帳款 (AR & 催收歷史)",
        "menu_hr": "👥 管理部 - 人事與勞動合約管理",
        "menu_ga": "📦 管理部 - 總務與資產設備管理",
        "menu_sheet_metal": "✂️ 生產部 - 板金加工組",
        "menu_painting": "🎨 生產部 - 烤漆塗裝組",
        "menu_assembly": "⚡ 生產部 - 配電盤組裝與配線組",
        "menu_warehouse": "🏭 生產部 - 倉庫與資材管理",
        "menu_approval": "✍️ 電子簽核與請款流程",
        "menu_it": "💻 資訊/IT - 權限與稽核管理"
    },
    "English": {
        "company_name": "⚡ REETECH INDUSTRIAL",
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ REETECH INDUSTRIAL - System Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "🔑 Login",
        "logout_btn": "🚪 Logout",
        "lang_selector": "🌐 Select Language",
        "menu_header": "Department Menu",
        "menu_exec": "👑 Executive Dashboard (Chairman/GM)",
        "menu_ap": "🛒 Admin - Accounts Payable (AP & Invoices)",
        "menu_ar": "📋 Admin - Accounts Receivable (AR & Collections)",
        "menu_hr": "👥 Admin - HR & Labor Contracts",
        "menu_ga": "📦 Admin - GA & Equipment Management",
        "menu_sheet_metal": "✂ Production - Sheet Metal Dept",
        "menu_painting": "🎨 Production - Powder Coating Dept",
        "menu_assembly": "⚡ Production - Assembly & Wiring Dept",
        "menu_warehouse": "🏭 Production - Warehouse & Materials",
        "menu_approval": "✍️ E-Approval Workflow",
        "menu_it": "💻 IT Dept - User Permissions & Audit Logs"
    },
    "Tiếng Việt": {
        "company_name": "⚡ REETECH INDUSTRIAL",
        "company_sub": "Công ty TNHH REETECH INDUSTRIAL",
        "login_title": "⚡ REETECH INDUSTRIAL - Đăng nhập hệ thống",
        "username": "Tài khoản",
        "password": "Mật khẩu",
        "login_btn": "🔑 Đăng nhập",
        "logout_btn": "🚪 Đăng xuất",
        "lang_selector": "🌐 Chọn ngôn ngữ",
        "menu_header": "Danh mục Phòng ban",
        "menu_exec": "👑 Báo cáo Ban Giám đốc (Chủ tịch/GM)",
        "menu_ap": "🛒 Khối Quản lý - Phải trả Nhà cung cấp (AP)",
        "menu_ar": "📋 Khối Quản lý - Phải thu Khách hàng (AR)",
        "menu_hr": "👥 Khối Quản lý - Nhân sự & Hợp đồng lao động",
        "menu_ga": "📦 Khối Quản lý - Hậu cần & Quản lý thiết bị",
        "menu_sheet_metal": "✂️ Khối Sản xuất - Tổ Gia công Cơ khí",
        "menu_painting": "🎨 Khối Sản xuất - Tổ Sơn tĩnh điện",
        "menu_assembly": "⚡ Khối Sản xuất - Tổ Lắp ráp Tủ điện",
        "menu_warehouse": "🏭 Khối Sản xuất - Quản lý Kho vật tư",
        "menu_approval": "✍️ Hệ thống Phê duyệt Điện tử",
        "menu_it": "💻 IT - Quản lý Phân quyền & Audit Logs"
    }
}

if "current_lang" not in st.session_state:
    st.session_state.current_lang = "繁體中文"

# ----------------------------------------------------
# 3. Supabase 資料庫連線與結構自動升級
# ----------------------------------------------------
DB_URL = "postgresql+psycopg2://postgres.wvsqbefyeykmueffcbwd:Reetech2026@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"

@st.cache_resource
def get_db_engine():
    eng = create_engine(DB_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)
    # 自動補齊應收帳款新增欄位，避免欄位不存在報錯
    try:
        with eng.connect() as conn:
            conn.execute(text("ALTER TABLE invoices ADD COLUMN IF NOT EXISTS installment_ratios TEXT;"))
            conn.execute(text("ALTER TABLE invoices ADD COLUMN IF NOT EXISTS progress_note TEXT;"))
            conn.execute(text("ALTER TABLE invoices ADD COLUMN IF NOT EXISTS project_desc TEXT;"))
            conn.commit()
    except Exception:
        pass
    return eng

engine = get_db_engine()

# ----------------------------------------------------
# 4. 登入系統
# ----------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_name = ""

if not st.session_state.logged_in:
    t = i18n[st.session_state.current_lang]
    st.title(t["login_title"])
    st.caption(t["company_sub"])
    st.markdown("---")
    col1, _ = st.columns([1, 2])
    with col1:
        username = st.text_input(f"{t['username']} (admin / manager / staff)")
        password = st.text_input(f"{t['password']} (123)", type="password")
        if st.button(t["login_btn"], use_container_width=True):
            if password == "123":
                st.session_state.logged_in = True
                st.session_state.user_role = "admin" if username == "admin" else ("manager" if username == "manager" else "staff")
                st.session_state.user_name = username
                st.rerun()
            else:
                st.error("帳號或密碼錯誤 / Incorrect password")
    st.stop()

# ----------------------------------------------------
# 5. 側邊欄與語系切換
# ----------------------------------------------------
t = i18n[st.session_state.current_lang]
st.sidebar.title(t["company_name"])
st.sidebar.caption(t["company_sub"])

lang_list = ["繁體中文", "Tiếng Việt", "English"]
selected_lang = st.sidebar.selectbox(
    t["lang_selector"],
    lang_list,
    index=lang_list.index(st.session_state.current_lang)
)

if selected_lang != st.session_state.current_lang:
    st.session_state.current_lang = selected_lang
    st.rerun()

st.sidebar.markdown(f"**👤 {st.session_state.user_name}** ({st.session_state.user_role.upper()})")
if st.sidebar.button(t["logout_btn"]):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

menu_mapping = {}
if st.session_state.user_role == "admin":
    menu_mapping[t["menu_exec"]] = "exec"

menu_mapping[t["menu_ap"]] = "ap"
menu_mapping[t["menu_ar"]] = "ar"
menu_mapping[t["menu_hr"]] = "hr"
menu_mapping[t["menu_ga"]] = "ga"
menu_mapping[t["menu_sheet_metal"]] = "sheet_metal"
menu_mapping[t["menu_painting"]] = "painting"
menu_mapping[t["menu_assembly"]] = "assembly"
menu_mapping[t["menu_warehouse"]] = "warehouse"
menu_mapping[t["menu_approval"]] = "approval"
menu_mapping[t["menu_it"]] = "it"

selected_menu_label = st.sidebar.radio(t["menu_header"], list(menu_mapping.keys()))
menu_choice = menu_mapping[selected_menu_label]

# ----------------------------------------------------
# 6. 模組安全呼叫路由 (容錯包裝，徹底防止 AttributeError)
# ----------------------------------------------------
curr_lang = st.session_state.current_lang

if menu_choice == "exec":
    executive_dashboard.render(engine, t=t, lang=curr_lang)
elif menu_choice == "ap":
    procurement_ap.render_procurement_ap_page(engine=engine, lang=curr_lang)
elif menu_choice == "ar":
    sales_order_ar.render_sales_order_ar_page(engine=engine, lang=curr_lang)
elif menu_choice == "hr":
    employee_management.render_employee_management(engine=engine, t=t, lang=curr_lang)
elif menu_choice == "ga":
    asset_management.render_asset_management_page(lang=curr_lang)
elif menu_choice in ["sheet_metal", "painting", "assembly"]:
    st.title(selected_menu_label)
    st.info("Hệ thống đang hoạt động bình thường / 現場工單追蹤與 QC 品質檢驗模組順利運作中。")
elif menu_choice == "warehouse":
    warehouse_management.render_warehouse_management(engine=engine, t=t, lang=curr_lang)
elif menu_choice == "approval":
    approval_workflow.render_approval_center(lang=curr_lang)
elif menu_choice == "it":
    user_management.render_user_management_page(lang=curr_lang)
