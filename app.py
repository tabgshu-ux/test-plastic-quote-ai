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
            "🏭 廠務/設備 (Plant & IoT)",
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
            "🏭 Quản Lý Nhà Máy & IoT",
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
            "🏭 厂务/设备 (Plant & IoT)",
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
            "🏭 Plant & IoT Engineering",
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
            "🏭 Teknik Pabrik & IoT",
            "🧾 Keuangan",
            "👥 SDM & Administrasi",
            "💻 IT & Admin Sistem"
        ]
    }
}

if "lang" not in st.session_state:
    st.session_state.lang = "繁體中文"

# ----------------------------------------------------
# 安全動態載入模組 (具備自動相容與容錯保護)
# ----------------------------------------------------
def load_module_function(module_name, func_names):
    try:
        mod = __import__(f"modules.{module_name}", fromlist=["*"])
        for fname in func_names:
            if hasattr(mod, fname):
                func = getattr(mod, fname)
                def safe_wrapper(*args, **kwargs):
                    try:
                        return func(*args, **kwargs)
                    except TypeError:
                        try:
                            return func(args[0]) if len(args) > 0 else func()
                        except TypeError:
                            return func()
                return safe_wrapper
        return lambda *args, **kwargs: st.error(f"⚠️ 在 modules/{module_name}.py 中找不到以下任何入口函式: {func_names}")
    except Exception as e:
        return lambda *args, **kwargs: st.error(f"❌ 載入 modules/{module_name}.py 失敗！\n\n**詳細錯誤原因**: `{e}`")

# 載入核心模組
render_exec_db = load_module_function("executive_dashboard", ["render_executive_dashboard_page", "render_dashboard", "show", "main"])
render_erp_db = load_module_function("erp_dashboard", ["render_erp_dashboard_page", "show", "main"])
render_sales = load_module_function("sales_quotation", ["render_sales_quotation_page", "render_sales_frontend", "show", "main"])
render_invoice = load_module_function("invoice_management", ["render_invoice_management_page", "render_invoice", "show", "main"])
render_tax_ai = load_module_function("finance_tax", ["render_finance_tax_page", "show", "main"])
render_payroll = load_module_function("payroll_management", ["render_payroll_management_page", "show", "main"])
render_asset = load_module_function("asset_management", ["render_asset_management_page", "show", "main"])
render_user_mgmt = load_module_function("user_management", ["render_user_management_page", "show", "main"])

# ----------------------------------------------------
# 側邊欄：固定 key 值的語系切換器與部門選單
# ----------------------------------------------------
st.sidebar.title("🏭 AI ERP")

selected_lang = st.sidebar.selectbox(
    "🌐 系統語系 (Language):",
    ["繁體中文", "Tiếng Việt", "简体中文", "English", "Bahasa Indonesia"],
    key="fixed_lang_selector_key"
)
st.session_state.lang = selected_lang
lang_dict = I18N[selected_lang]

st.sidebar.markdown("---")

# 主部門單選鈕
selected_dept = st.sidebar.radio(
    lang_dict["dept_select"],
    options=I18N["繁體中文"]["depts"],
    key="fixed_sidebar_dept_radio_key"
)

st.sidebar.markdown("---")

# ----------------------------------------------------
# 頁面路由與直觀展開的子選單 (使用 radio 取代 selectbox)
# ----------------------------------------------------
if "📈 營運戰情室" in selected_dept:
    sub_option = st.sidebar.radio(
        "選擇觀察市場 (Market):",
        ["🌐 全部市場 (All Markets)", "🇹🇼 台灣 (Taiwan)", "🇨🇳 中國/香港 (China/HK)", "🇺🇸 美國 (USA)", "🇻🇳 越南 (Vietnam)", "🛢️ 原物料與匯率 (Commodities/FX)"],
        key="fixed_sub_exec_market_key"
    )
    render_exec_db(sub_option, selected_lang)

elif "💼 業務/行銷" in selected_dept:
    sub_option = st.sidebar.radio(
        "業務功能清單：",
        ["📝 AI 即時報價 & CAD/3D Pipeline", "📊 歷史報價單據與資料庫"],
        key="fixed_sub_sales_option_key"
    )
    render_sales(sub_option)

elif "🛠️ 研發/技術" in selected_dept:
    sub_option = st.sidebar.radio(
        "研發技術清單：",
        ["📦 跨國資產與模具管理", "🛠️ 試模履歷與 DFM 檢討"],
        key="fixed_sub_rd_option_key"
    )
    render_asset(sub_option)

elif "🏭 廠務/設備" in selected_dept:
    sub_option = st.sidebar.radio(
        "廠務設備清單：",
        ["📡 IoT 射出機/連線設備狀態監控", "⚡ 廠區營運與機台 OEE KPI", "🔧 設備預防性保養與故障告警"],
        key="fixed_sub_plant_iot_option_key"
    )
    render_erp_db(sub_option)

elif "🧾 財務" in selected_dept:
    sub_option = st.sidebar.radio(
        "財務功能清單：",
        [
            "📄 越南電子發票 XML 解析與登錄",
            "📧 通用信箱電子發票讀取 (IMAP)",
            "📊 電子發票張數監控與加購預警",
            "🌐 全球跨國稅務 AI 智慧問答"
        ],
        key="fixed_sub_finance_option_key"
    )
    if "全球跨國稅務" in sub_option:
        render_tax_ai(sub_option)
    else:
        render_invoice(sub_option)

elif "👥 人事/行政" in selected_dept:
    sub_option = st.sidebar.radio(
        "人事行政清單：",
        ["💰 每月薪資與考勤變動扣款", "⏰ 網路打卡機連線對接"],
        key="fixed_sub_hr_option_key"
    )
    render_payroll(sub_option)

elif "💻 資訊/IT" in selected_dept:
    sub_option = st.sidebar.radio(
        "資訊管理清單：",
        ["🏢 跨國廠區與子公司管理", "👥 人員帳號與網頁授權", "🔒 模組權限矩陣 (RBAC)"],
        key="fixed_sub_it_option_key"
    )
    render_user_mgmt(sub_option)
