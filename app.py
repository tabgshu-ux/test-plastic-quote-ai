import streamlit as st

st.set_page_config(
    page_title="跨國塑膠/橡膠射出成型 AI ERP",
    page_icon="🏭",
    layout="wide"
)

# ----------------------------------------------------
# 🌐 跨國多語系字典定義 (i18n Dictionary)
# ----------------------------------------------------
I18N = {
    "繁體中文": {
        "title": "🏭 AI ERP 系統選單",
        "lang_select": "🌐 選擇系統語系 (Language):",
        "dept_select": "請選擇部門/模組分類：",
        "depts": [
            "📈 營運戰情室 (Executive)",
            "💼 業務/行銷 (Sales & Marketing)",
            "🛠️ 研發/技術 (R&D & Engineering)",
            "🧾 財務 (Finance)",
            "👥 人事/行政 (HR & Admin)",
            "💻 資訊/IT (IT & System Admin)"
        ]
    },
    "Tiếng Việt": {
        "title": "🏭 Menu Hệ Thống AI ERP",
        "lang_select": "🌐 Chọn ngôn ngữ (Language):",
        "dept_select": "Vui lòng chọn phòng ban/phân hệ:",
        "depts": [
            "📈 Phòng Điều Hành (Executive)",
            "💼 Kinh Doanh / Marketing",
            "🛠️ R&D / Kỹ Thuật",
            "🧾 Tài Chính / Kế Toán",
            "👥 Nhân Sự / Hành Chính",
            "💻 Công Nghệ Thông Tin (IT)"
        ]
    },
    "简体中文": {
        "title": "🏭 AI ERP 系统菜单",
        "lang_select": "🌐 选择系统语系 (Language):",
        "dept_select": "请选择部门/模块分类：",
        "depts": [
            "📈 营运战情室 (Executive)",
            "💼 业务/营销 (Sales & Marketing)",
            "🛠️ 研发/技术 (R&D & Engineering)",
            "🧾 财务 (Finance)",
            "👥 人事/行政 (HR & Admin)",
            "💻 信息/IT (IT & System Admin)"
        ]
    },
    "English": {
        "title": "🏭 AI ERP System Menu",
        "lang_select": "🌐 System Language:",
        "dept_select": "Select Department / Module:",
        "depts": [
            "📈 Executive Dashboard",
            "💼 Sales & Marketing",
            "🛠️ R&D & Engineering",
            "🧾 Finance",
            "👥 HR & Administration",
            "💻 IT & System Admin"
        ]
    },
    "Bahasa Indonesia": {
        "title": "🏭 Menu Sistem AI ERP",
        "lang_select": "🌐 Pilih Bahasa (Language):",
        "dept_select": "Pilih Departemen / Modul:",
        "depts": [
            "📈 Dasbor Eksekutif",
            "💼 Penjualan & Pemasaran",
            "🛠️ R&D & Teknik",
            "🧾 Keuangan",
            "👥 SDM & Administrasi",
            "💻 IT & Admin Sistem"
        ]
    }
}

# 初始化預設語系
if "lang" not in st.session_state:
    st.session_state.lang = "繁體中文"

# ----------------------------------------------------
# 安全動態載入模組
# ----------------------------------------------------
def load_module_function(module_name, func_names):
    try:
        mod = __import__(f"modules.{module_name}", fromlist=["*"])
        for fname in func_names:
            if hasattr(mod, fname):
                return getattr(mod, fname)
        return lambda *args, **kwargs: st.error(f"⚠️ 在 modules/{module_name}.py 中找不到以下任何入口函式: {func_names}")
    except Exception as e:
        return lambda *args, **kwargs: st.error(f"❌ 載入 modules/{module_name}.py 失敗！\n\n**詳細錯誤原因**: `{e}`")

# 載入 7 大核心模組
render_exec_db = load_module_function("executive_dashboard", ["render_executive_dashboard_page", "render_dashboard", "show", "main"])
render_erp_db = load_module_function("erp_dashboard", ["render_erp_dashboard_page", "show", "main"])
render_sales = load_module_function("sales_quotation", ["render_sales_quotation_page", "render_sales_frontend", "show", "main"])
render_invoice = load_module_function("invoice_management", ["render_invoice_management_page", "show", "main"])
render_payroll = load_module_function("payroll_management", ["render_payroll_management_page", "show", "main"])
render_asset = load_module_function("asset_management", ["render_asset_management_page", "show", "main"])
render_user_mgmt = load_module_function("user_management", ["render_user_management_page", "show", "main"])

# ----------------------------------------------------
# 側邊欄：語言切換器 & 部門選單
# ----------------------------------------------------
st.sidebar.title("🏭 AI ERP")

# 語系切換下拉選單 (放置於最頂端)
selected_lang = st.sidebar.selectbox(
    "🌐 系統語系 (Language):",
    ["繁體中文", "Tiếng Việt", "简体中文", "English", "Bahasa Indonesia"],
    index=["繁體中文", "Tiếng Việt", "简体中文", "English", "Bahasa Indonesia"].index(st.session_state.lang),
    key="lang_selector"
)
st.session_state.lang = selected_lang
lang_dict = I18N[selected_lang]

st.sidebar.markdown("---")

# 根據選擇的語系顯示部門選單
department_idx = st.sidebar.radio(
    lang_dict["dept_select"],
    options=list(range(len(lang_dict["depts"]))),
    format_func=lambda x: lang_dict["depts"][x]
)

st.sidebar.markdown("---")

# ----------------------------------------------------
# 頁面路由分流 (將目前語系傳入各模組)
# ----------------------------------------------------
if department_idx == 0:  # 營運戰情室
    sub_option = st.sidebar.selectbox(
        "選擇觀察市場 (Market):",
        ["🌐 全部市場 (All Markets)", "🇹🇼 台灣 (Taiwan)", "🇨🇳 中國/香港 (China/HK)", "🇺🇸 美國 (USA)", "🇻🇳 越南 (Vietnam)", "🛢️ 原物料與匯率 (Commodities/FX)"],
        key="sub_exec_market"
    )
    render_exec_db(sub_option, selected_lang)

elif department_idx == 1:  # 業務/行銷
    sub_option = st.sidebar.selectbox(
        "業務項目 (Sales Items):",
        ["📝 AI 即時報價 & CAD/3D Pipeline", "📊 歷史報價單據與資料庫"],
        key="sub_sales_option"
    )
    render_sales(sub_option)

elif department_idx == 2:  # 研發/技術
    sub_option = st.sidebar.selectbox(
        "技術項目 (Engineering Items):",
        ["📦 跨國資產與模具管理", "⚡ 廠區營運與機台 OEE KPI"],
        key="sub_rd_option"
    )
    if "資產" in sub_option or "Asset" in sub_option:
        render_asset()
    else:
        render_erp_db()

elif department_idx == 3:  # 財務
    sub_option = st.sidebar.selectbox(
        "財務項目 (Finance Items):",
        ["📧 通用信箱電子發票讀取 (IMAP)", "🇻🇳 越南 XML 電子發票解析"],
        key="sub_finance_option"
    )
    render_invoice(sub_option)

elif department_idx == 4:  # 人事/行政
    sub_option = st.sidebar.selectbox(
        "人事項目 (HR Items):",
        ["💰 每月薪資與考勤變動扣款", "⏰ 網路打卡機連線對接"],
        key="sub_hr_option"
    )
    render_payroll(sub_option)

elif department_idx == 5:  # 資訊/IT
    sub_option = st.sidebar.selectbox(
        "管理項目 (IT Items):",
        ["🏢 跨國廠區與子公司管理", "👥 人員帳號與網頁授權", "🔒 模組權限矩陣 (RBAC)"],
        key="sub_it_option"
    )
    render_user_mgmt(sub_option)
