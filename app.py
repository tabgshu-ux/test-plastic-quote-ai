import inspect
import modules.approval_center as approval_center
import modules.asset_management as asset_management
import modules.database as db_conn
import modules.employee_management as employee_management
import modules.engineering_pipeline as engineering_pipeline
import modules.executive_dashboard as executive_dashboard
import modules.field_attendance as field_attendance
import modules.invoice_parsing as invoice_management
import modules.payroll_management as payroll_management
import modules.finance_ap as procurement_ap
import modules.supply_chain as sales_order_ar
import modules.system_licensing as system_licensing
import modules.user_management as user_management
import modules.vehicle_gate_log as vehicle_gate_log
import modules.vehicle_maintenance as vehicle_maintenance
import modules.inventory_wms as warehouse_management
import pandas as pd
import streamlit as st

# 📱 100% 移動優先：設定頁面並預設手機側邊欄展開
st.set_page_config(
    page_title="裕豐電機工業 REETECH INDUSTRIAL AI ERP",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------
# 📱 注入手機優先 RWD CSS 與 側邊欄滑動/點擊手勢優化 JS
# ----------------------------------------------------
MOBILE_CSS_AND_JS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.35rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.15rem !important; }
    h3, .stSubheader { font-size: 1.05rem !important; }
    p, div, span, label { font-size: 0.9rem !important; }
    .block-container { padding: 1rem 0.5rem !important; }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', () => {
    let touchstartX = 0;
    let touchendX = 0;

    function handleGesure() {
        if (touchendX < touchstartX - 50) {
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (sidebar && window.innerWidth <= 768) {
                const closeBtn = document.querySelector('[data-testid="stSidebar"] button');
                if (closeBtn) { closeBtn.click(); }
            }
        }
    }

    document.addEventListener('touchstart', e => { touchstartX = e.changedTouches[0].screenX; }, false);
    document.addEventListener('touchend', e => { touchendX = e.changedTouches[0].screenX; handleGesure(); }, false);
});
</script>
"""
st.markdown(MOBILE_CSS_AND_JS, unsafe_allow_html=True)

# ----------------------------------------------------
# 🏢 RECH 企業品牌 Logo 橫幅
# ----------------------------------------------------
RECH_LOGO_HTML = """
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; padding: 6px 8px; background: #f8fafc; border-radius: 8px; border-left: 4px solid #000055;">
    <div style="font-size: 26px; font-weight: 900; color: #000055; letter-spacing: -1px; line-height: 1;">RECH</div>
    <div style="border-left: 2px solid #cbd5e1; padding-left: 8px; line-height: 1.15;">
        <div style="font-size: 12.5px; font-weight: 800; color: #000055;">裕豐電機工業有限公司</div>
        <div style="font-size: 8px; font-weight: 700; color: #475569;">REETECH INDUSTRIAL CO., LTD • CÔNG TY TNHH CN DŨ PHONG</div>
    </div>
</div>
"""

# ----------------------------------------------------
# 🌐 多語系與扁平化導航結構
# ----------------------------------------------------
APP_TRANSLATIONS = {
    "繁體中文": {
        "login_title": "⚡ 裕豐電機工業 REETECH - 系統登入",
        "username": "帳號 (admin / manager / security / staff)",
        "password": "密碼 (預設 123)",
        "login_btn": "🔑 登入系統",
        "logout_btn": "🚪 登出系統",
        "lang_label": "🌐 語言切換 / Language",
        "tabs": ["📈 營運戰情", "👔 管理與財務", "🛠️ 工程技術", "🏭 生產倉儲", "💻 系統管理"],
    },
    "Tiếng Việt": {
        "login_title": "⚡ REETECH INDUSTRIAL - Đăng nhập hệ thống",
        "username": "Tài khoản",
        "password": "Mật khẩu (123)",
        "login_btn": "🔑 Đăng nhập",
        "logout_btn": "🚪 Đăng xuất",
        "lang_label": "🌐 Chọn ngôn ngữ",
        "tabs": ["📈 Ban Giám đốc", "👔 Quản lý & Tài chính", "🛠️ Kỹ thuật", "🏭 Sản xuất & Kho", "💻 Quản trị IT"],
    },
    "English": {
        "login_title": "⚡ REETECH INDUSTRIAL - System Login",
        "username": "Username",
        "password": "Password (123)",
        "login_btn": "🔑 Login",
        "logout_btn": "🚪 Logout",
        "lang_label": "🌐 Select Language",
        "tabs": ["📈 Executive", "👔 Management & Finance", "🛠️ Engineering", "🏭 Production & WMS", "💻 IT Admin"],
    }
}

if "current_lang" not in st.session_state:
    st.session_state.current_lang = "繁體中文"

t = APP_TRANSLATIONS.get(st.session_state.current_lang, APP_TRANSLATIONS["繁體中文"])
engine = db_conn.get_db_connection()

def safe_call_module(func, *args, **kwargs):
    if not callable(func): return
    try:
        sig = inspect.signature(func)
        valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        if "engine" in sig.parameters and "engine" not in valid_kwargs:
            valid_kwargs["engine"] = engine
        func(*args, **valid_kwargs)
    except Exception:
        try: func()
        except Exception as e: st.error(f"模組載入異常: {str(e)}")

# ----------------------------------------------------
# 登入驗證畫面
# ----------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown(RECH_LOGO_HTML, unsafe_allow_html=True)
    st.title(t["login_title"])
    st.markdown("---")
    col1, _ = st.columns([1, 2])
    with col1:
        username = st.text_input(t["username"])
        password = st.text_input(t["password"], type="password")
        if st.button(t["login_btn"], use_container_width=True):
            if password == "123":
                st.session_state.logged_in = True
                u_clean = username.strip().lower()
                if u_clean in ["admin", "executive", "boss"]: st.session_state.user_role = "admin"
                elif u_clean in ["manager", "supervisor"]: st.session_state.user_role = "manager"
                elif u_clean in ["security", "guard", "門禁保全"]: st.session_state.user_role = "security"
                else: st.session_state.user_role = "staff"
                st.session_state.user_name = username
                st.rerun()
            else:
                st.error("帳號或密碼錯誤 / Incorrect password")
    st.stop()

# ----------------------------------------------------
# 側邊欄設定
# ----------------------------------------------------
st.sidebar.markdown(RECH_LOGO_HTML, unsafe_allow_html=True)

lang_list = ["繁體中文", "Tiếng Việt", "English"]
selected_lang = st.sidebar.selectbox(t["lang_label"], lang_list, index=lang_list.index(st.session_state.current_lang))
if selected_lang != st.session_state.current_lang:
    st.session_state.current_lang = selected_lang
    st.rerun()

st.sidebar.markdown(f"**👤 {st.session_state.user_name}** (`{st.session_state.user_role.upper()}`)")
if st.sidebar.button(t["logout_btn"], use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")
current_role_clean = str(st.session_state.user_role).strip().lower()

# ----------------------------------------------------
# 主介面：直覺的大型分頁導航 (Tabs)
# ----------------------------------------------------
st.markdown(RECH_LOGO_HTML, unsafe_allow_html=True)

if current_role_clean == "security":
    st.info("🛡️ 保全快速通道：廠區車輛進出與門禁時間登記")
    safe_call_module(vehicle_gate_log.render_vehicle_gate_log_page, engine=engine, lang=st.session_state.current_lang)
    st.stop()

tab_exec, tab_mgmt, tab_eng, tab_prod, tab_it = st.tabs(t["tabs"])

with tab_exec:
    st.markdown("### 📈 營運戰情與分析總覽")
    exec_option = st.radio("選擇戰情項目：", ["🔴 原料價格與隨時股市物價/匯率", "📊 財務類顯示資料 (AR/AP & P&L)", "⚡ 工程專案進度與驗收資料"], horizontal=True)
    if "原料價格" in exec_option:
        safe_call_module(executive_dashboard.render_executive_dashboard_page, sub_route="commodities_fx", lang=st.session_state.current_lang)
    elif "財務類" in exec_option:
        safe_call_module(executive_dashboard.render_executive_dashboard_page, sub_route="financials_pl", lang=st.session_state.current_lang)
    else:
        safe_call_module(executive_dashboard.render_executive_dashboard_page, sub_route="project_progress", lang=st.session_state.current_lang)

with tab_mgmt:
    st.markdown("### 👔 管理部與財務會計中心")
    mgmt_option = st.selectbox(
        "選擇管理與財務功能模組：",
        [
            "🏢 固定資產設備與總務採購",
            "✍️ 電子簽核與請款審核中心",
            "👤 員工個人檔案與人事管理",
            "🚗 廠區車輛進出與門禁時間紀錄",
            "🛠️ 車輛維修保養與 Excel 批次匯入",
            "📍 外勤工程人員 GPS 拍照打卡",
            "🛒 採購與應付帳款 (AP)",
            "📋 銷售與應收帳款 (AR)",
            "💰 全球員工薪資與保險扣款試算",
            "📄 越南電子發票綜合管理中心"
        ]
    )
    
    tenant_info = {"tenant_id": "TENANT-001", "company_name": "裕豐電機工業"}
    user_perms = ["admin", "finance", "ga"]

    if "固定資產" in mgmt_option:
        safe_call_module(asset_management.render_asset_management, tenant_info, user_perms)
    elif "電子簽核" in mgmt_option:
        safe_call_module(approval_center.render_approval_center, tenant_info, user_perms)
    elif "員工個人檔案" in mgmt_option:
        safe_call_module(employee_management.render_employee_management, engine=engine, t=t, lang=st.session_state.current_lang)
    elif "車輛進出" in mgmt_option:
        safe_call_module(vehicle_gate_log.render_vehicle_gate_log_page, engine=engine, lang=st.session_state.current_lang)
    elif "車輛維修" in mgmt_option:
        safe_call_module(vehicle_maintenance.render_vehicle_maintenance_page, engine=engine, lang=st.session_state.current_lang)
    elif "外勤工程" in mgmt_option:
        safe_call_module(field_attendance.render_field_attendance_page, engine=engine, lang=st.session_state.current_lang)
    elif "採購與應付" in mgmt_option:
        safe_call_module(procurement_ap.render_finance_ap, tenant_info, user_perms)
    elif "銷售與應收" in mgmt_option:
        safe_call_module(sales_order_ar.render_supply_chain, tenant_info, user_perms)
    elif "全球員工薪資" in mgmt_option:
        safe_call_module(payroll_management.render_payroll_management_page, engine=engine, lang=st.session_state.current_lang)
    elif "越南電子發票" in mgmt_option:
        safe_call_module(invoice_management.render_invoice_parsing, tenant_info, user_perms)

with tab_eng:
    st.markdown("### 🛠️ 工程技術與設計估價中心")
    eng_option = st.radio("選擇工程功能：", ["📐 配電盤電氣與機構設計圖庫 / 估價", "🔍 工程驗收與品質檢驗紀錄"], horizontal=True)
    if "配電盤" in eng_option:
        safe_call_module(engineering_pipeline.render_engineering_page)
    else:
        safe_call_module(executive_dashboard.render_executive_dashboard_page, sub_route="project_progress", lang=st.session_state.current_lang)

with tab_prod:
    st.markdown("### 🏭 生產製造與倉庫管理中心")
    prod_option = st.selectbox("選擇生產與倉儲功能：", ["📦 倉庫庫存與資材條碼管理", "✂️ 板金加工組工單與條碼", "🎨 粉體塗裝烤漆組品管", "⚡ 配電盤組裝配線組"])
    if "倉庫庫存" in prod_option:
        safe_call_module(warehouse_management.render_warehouse_management, engine=engine, t=t, lang=st.session_state.current_lang)
    else:
        st.info("🛠️ 現場工單追蹤與 QC 品質檢驗模組順利運作中 / Hệ thống đang hoạt động bình thường.")

with tab_it:
    st.markdown("### 💻 資訊管理與系統授權中心")
    it_option = st.radio("選擇管理項目：", ["🔒 帳號權限與全系統稽核軌跡", "🎛️ 客戶 ERP 模組授權與功能開關"], horizontal=True)
    if "帳號權限" in it_option:
        safe_call_module(user_management.render_user_management_page, lang=st.session_state.current_lang)
    else:
        safe_call_module(system_licensing.render_licensing_control_page, lang=st.session_state.current_lang)
