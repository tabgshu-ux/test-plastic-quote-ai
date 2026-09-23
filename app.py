import streamlit as st
import os

# 設定 Streamlit 網頁基本配置
st.set_page_config(
    page_title="AI 智能製造 & ERP 報價管理系統",
    page_icon="🏭",
    layout="wide"
)

# 嘗試匯入各功能模組
try:
    from modules import sales_quotation
except ImportError:
    sales_quotation = None

try:
    from modules import finance_tax
except ImportError:
    finance_tax = None

# Sidebar 側邊欄主選單與子選單規劃
st.sidebar.title("🏭 企業 ERP 系統導覽")

main_menu = st.sidebar.radio(
    "請選擇功能模組：",
    [
        "💼 業務/行銷 — 報價與 CAD/3D Pipeline",
        "💰 財務/跨國稅務 AI 智慧顧問",
        "📊 歷史報價與客戶紀錄中心"
    ]
)

sub_option = "預設"

# 依據選擇的主選單導覽至對應分頁
if "業務/行銷" in main_menu:
    sub_option = st.sidebar.selectbox("子功能選擇：", ["📝 AI 即時報價 & CAD/3D Pipeline", "📜 歷史報價紀錄"])
    if sales_quotation:
        sales_quotation.show(sub_option)
    else:
        st.error("❌ 找不到 sales_quotation 模組，請檢查 modules/sales_quotation.py 是否存在。")

elif "財務/跨國稅務" in main_menu:
    sub_option = st.sidebar.selectbox("子功能選擇：", ["🌐 全球稅務 AI 中文問答", "📊 跨境扣繳稅 (WHT/FCT) 試算器"])
    if finance_tax:
        finance_tax.show(sub_option)
    else:
        st.error("❌ 找不到 finance_tax 模組，請檢查 modules/finance_tax.py 是否存在。")

elif "歷史報價" in main_menu:
    if sales_quotation:
        sales_quotation.show("歷史報價紀錄")
    else:
        st.info("📊 歷史報價與客戶資料庫載入中...")
