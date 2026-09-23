import streamlit as st

st.set_page_config(
    page_title="跨國塑膠/橡膠射出成型 AI ERP",
    page_icon="🏭",
    layout="wide"
)

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
# 一級選單：側邊欄部門分類 (含 💻 資訊/IT 部門)
# ----------------------------------------------------
st.sidebar.title("🏭 AI ERP 系統選單")

department = st.sidebar.radio(
    "請選擇部門/模組分類：",
    [
        "📈 營運戰情室 (Executive)",
        "💼 業務/行銷 (Sales & Marketing)",
        "🛠️ 研發/技術 (R&D & Engineering)",
        "🧾 財務 (Finance)",
        "👥 人事/行政 (HR & Admin)",
        "💻 資訊/IT (IT & System Admin)"
    ]
)

st.sidebar.markdown("---")

# ----------------------------------------------------
# 二級動態選單：依據選擇的部門，在側邊欄下方展開對應業務
# ----------------------------------------------------
if department == "📈 營運戰情室 (Executive)":
    st.sidebar.subheader("📈 股市與匯率觀測區域")
    sub_option = st.sidebar.selectbox(
        "選擇觀察市場：",
        [
            "🌐 全部市場 (All Markets)",
            "🇹🇼 台灣 (Taiwan)",
            "🇨🇳 中國/香港 (China/HK)",
            "🇺🇸 美國 (USA)",
            "🇻🇳 越南 (Vietnam)",
            "🛢️ 原物料與匯率 (Commodities/FX)"
        ],
        key="sub_exec_market"
    )
    render_exec_db(sub_option)

elif department == "💼 業務/行銷 (Sales & Marketing)":
    st.sidebar.subheader("💼 業務功能選單")
    sub_option = st.sidebar.selectbox(
        "選擇業務項目：",
        ["📝 AI 即時報價 & CAD/3D Pipeline", "📊 歷史報價單據與資料庫"],
        key="sub_sales_option"
    )
    render_sales(sub_option)

elif department == "🛠️ 研發/技術 (R&D & Engineering)":
    st.sidebar.subheader("🛠️ 研發與技術功能選單")
    sub_option = st.sidebar.selectbox(
        "選擇技術項目：",
        ["📦 跨國資產與模具管理", "⚡ 廠區營運與機台 OEE KPI"],
        key="sub_rd_option"
    )
    if sub_option == "📦 跨國資產與模具管理":
        render_asset()
    else:
        render_erp_db()

elif department == "🧾 財務 (Finance)":
    st.sidebar.subheader("🧾 財務功能選單")
    sub_option = st.sidebar.selectbox(
        "選擇財務項目：",
        ["📧 通用信箱電子發票讀取 (IMAP)", "🇻🇳 越南 XML 電子發票解析"],
        key="sub_finance_option"
    )
    render_invoice(sub_option)

elif department == "👥 人事/行政 (HR & Admin)":
    st.sidebar.subheader("👥 人事行政功能選單")
    sub_option = st.sidebar.selectbox(
        "選擇人事項目：",
        ["💰 每月薪資與考勤變動扣款", "⏰ 網路打卡機連線對接"],
        key="sub_hr_option"
    )
    render_payroll(sub_option)

elif department == "💻 資訊/IT (IT & System Admin)":
    st.sidebar.subheader("💻 資訊系統管理選單")
    sub_option = st.sidebar.selectbox(
        "選擇管理項目：",
        ["👥 人員帳號與網頁授權", "🏢 跨國部門架構管理", "🔒 模組權限矩陣 (RBAC)"],
        key="sub_it_option"
    )
    render_user_mgmt(sub_option)
