import streamlit as st

# 1. 匯入各核心模組
from modules.sales_quotation import render_sales_quotation_page
from modules.invoice_management import render_invoice_management_page
from modules.payroll_management import render_payroll_management_page
from modules.erp_dashboard import render_erp_dashboard_page
from modules.executive_dashboard import render_executive_dashboard_page
from modules.asset_management import render_asset_management_page  # <-- 新增匯入資產管理模組

st.set_page_config(
    page_title="跨國塑膠/橡膠射出成型 AI ERP",
    page_icon="🏭",
    layout="wide"
)

# 2. 側邊欄功能選單
st.sidebar.title("🏭 AI ERP 系統選單")
page = st.sidebar.radio(
    "請選擇功能模組：",
    [
        "營運戰情室 (Executive Dashboard)",
        "廠區營運 KPI (ERP Dashboard)",
        "業務報價 & CAD/3D Pipeline",
        "電子發票讀取 (Invoice Management)",
        "薪資考勤計算 (Payroll Management)",
        "跨國資產與模具管理 (Asset Management)"  # <-- 新增選單項目
    ]
)

# 3. 頁面路由分流
if page == "營運戰情室 (Executive Dashboard)":
    render_executive_dashboard_page()
elif page == "廠區營運 KPI (ERP Dashboard)":
    render_erp_dashboard_page()
elif page == "業務報價 & CAD/3D Pipeline":
    render_sales_quotation_page()
elif page == "電子發票讀取 (Invoice Management)":
    render_invoice_management_page()
elif page == "薪資考勤計算 (Payroll Management)":
    render_payroll_management_page()
elif page == "跨國資產與模具管理 (Asset Management)":
    render_asset_management_page()  # <-- 呼叫資產管理模組渲染函式
