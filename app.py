import streamlit as st

st.set_page_config(
    page_title="跨國塑膠/橡膠射出成型 AI ERP",
    page_icon="🏭",
    layout="wide"
)

# ----------------------------------------------------
# 安全動態載入模組 (具備 Try-Except 容錯保護)
# ----------------------------------------------------

def load_module_function(module_name, func_names):
    """安全載入模組並自動尋找對應的渲染函式"""
    try:
        mod = __import__(f"modules.{module_name}", fromlist=["*"])
        for fname in func_names:
            if hasattr(mod, fname):
                return getattr(mod, fname)
        return lambda: st.error(f"⚠️ 在 modules/{module_name}.py 中找不到以下任何入口函式: {func_names}")
    except Exception as e:
        return lambda: st.error(f"❌ 載入 modules/{module_name}.py 失敗！\n\n**詳細錯誤原因**: `{e}`")

# 載入 6 大核心模組
render_exec_db = load_module_function("executive_dashboard", ["render_executive_dashboard_page", "show", "main"])
render_erp_db = load_module_function("erp_dashboard", ["render_erp_dashboard_page", "show", "main"])
render_sales = load_module_function("sales_quotation", ["render_sales_quotation_page", "render_sales_frontend", "show", "main"])
render_invoice = load_module_function("invoice_management", ["render_invoice_management_page", "show", "main"])
render_payroll = load_module_function("payroll_management", ["render_payroll_management_page", "show", "main"])
render_asset = load_module_function("asset_management", ["render_asset_management_page", "show", "main"])

# ----------------------------------------------------
# 側邊欄與頁面路由
# ----------------------------------------------------
st.sidebar.title("🏭 AI ERP 系統選單")
page = st.sidebar.radio(
    "請選擇功能模組：",
    [
        "營運戰情室 (Executive Dashboard)",
        "廠區營運 KPI (ERP Dashboard)",
        "業務報價 & CAD/3D Pipeline",
        "電子發票讀取 (Invoice Management)",
        "薪資考勤計算 (Payroll Management)",
        "跨國資產與模具管理 (Asset Management)"
    ]
)

if page == "營運戰情室 (Executive Dashboard)":
    render_exec_db()
elif page == "廠區營運 KPI (ERP Dashboard)":
    render_erp_db()
elif page == "業務報價 & CAD/3D Pipeline":
    render_sales()
elif page == "電子發票讀取 (Invoice Management)":
    render_invoice()
elif page == "薪資考勤計算 (Payroll Management)":
    render_payroll()
elif page == "跨國資產與模具管理 (Asset Management)":
    render_asset()
