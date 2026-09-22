import os
import streamlit as st
import google.generativeai as genai

# 匯入各個獨立模組（包含新建的 erp_dashboard）
from modules import (
    executive_dashboard,
    erp_dashboard,
    sales_quotation,
    employee_management,
    payroll_management,
    invoice_management,
    user_management,
)

# 網頁設定
st.set_page_config(
    page_title="Global Injection AI ERP System", page_icon="🏭", layout="wide"
)

# API Key 設定
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ API Key not configured!")
    st.stop()

# 設定 Gemini SDK
genai.configure(api_key=api_key)

# 🏢 0. 初始化公司與多廠區基本資訊
if "company_profile" not in st.session_state:
    st.session_state.company_profile = {
        "name": "環球塑膠射出工業股份有限公司 (Global Injection Molding Corp.)",
        "tax_id": "88889999",
        "website": "www.global-injection-demo.com",
        "sites": {
            "Taiwan (HQ)": {
                "site_name": "台灣總部與研發中心",
                "phone": "+886-2-2999-8888",
                "fax": "+886-2-2999-7777",
                "email": "hq@global-injection.com",
                "address": "新北市三重區光復路二段 88 號 10 樓",
            },
            "China (Dongguan)": {
                "site_name": "中國東莞華南製造基地",
                "phone": "+86-769-8123-4567",
                "fax": "+86-769-8123-4568",
                "email": "cn_sales@global-injection.com",
                "address": "廣東省東莞市長安鎮樟樹浦工業區 16 號",
            },
            "Vietnam (Binh Duong)": {
                "site_name": "越南平陽東安製造廠",
                "phone": "+84-274-3789-999",
                "fax": "+84-274-3789-888",
                "email": "vn_sales@global-injection.com",
                "address": "KCN Đồng An, Phường Bình Hòa, TP. Thuận An, Tỉnh Bình Dương, Việt Nam",
            },
        },
    }

# 🔐 初始化使用者帳號資料庫
if "user_database" not in st.session_state:
    st.session_state.user_database = {
        "admin": {"password": "admin123", "name": "系統最高主管 (Manager)", "role": "executive"},
        "boss": {"password": "boss123", "name": "陳董事長 (Chairman)", "role": "executive"},
        "gm": {"password": "gm123", "name": "林總經理 (General Manager)", "role": "executive"},
        "hr_manager": {"password": "hr123", "name": "張人事主管 (HR Manager)", "role": "hr"},
        "accountant": {"password": "fin123", "name": "王財務會計 (Accountant)", "role": "finance"},
        "alex": {"password": "alex123", "name": "Alex Chen (S-001)", "role": "sales"},
        "david": {"password": "david123", "name": "David Wang (S-002)", "role": "sales"},
    }

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# ==========================================
# 🔓 登入邏輯
# ==========================================
if not st.session_state.authenticated:
    st.title("🏭 塑膠/橡膠射出成型 — 跨國 AI 報價與分權 ERP 系統")
    st.caption("請輸入您的企業帳號與密碼以進行身份驗證與權限跳轉")

    col_login, _ = st.columns([1, 1])
    with col_login:
        with st.form("login_form"):
            username_input = st.text_input("帳號 / Username").strip().lower()
            password_input = st.text_input("密碼 / Password", type="password").strip()
            submit_button = st.form_submit_button("🔑 登入系統", type="primary")

            if submit_button:
                db = st.session_state.user_database
                if username_input in db and db[username_input]["password"] == password_input:
                    st.session_state.authenticated = True
                    st.session_state.user_info = db[username_input]
                    st.success(f"✅ 登入成功！歡迎，{st.session_state.user_info['name']}")
                    st.rerun()
                else:
                    st.error("❌ 帳號或密碼錯誤，請重新輸入！")

        st.info("""
            💡 **最新可用測試帳號密碼清單：**
            - **董事長**：`boss` / `boss123` (進入高階戰情室 & 跨國股市 AI 分析)
            - **總經理**：`gm` / `gm123`
            - **人事主管**：`hr_manager` / `hr123`
            - **財務會計**：`accountant` / `fin123`
            - **業務專員**：`alex` / `alex123` 或 `david` / `david123`
            """)
    st.stop()

# ==========================================
# 🔒 主系統 UI & 路由分發 (左側導覽選單版)
# ==========================================
ROLE_NAME_MAP = {
    "executive": "👑 董事長/總經理 (全權限)",
    "hr": "👥 人事主管/HR",
    "finance": "💰 財務會計",
    "sales": "💼 業務人員",
}

st.sidebar.title("👤 使用者資訊")
st.sidebar.write(f"**當前使用者**：{st.session_state.user_info['name']}")
st.sidebar.write(f"**權限角色**： {ROLE_NAME_MAP.get(st.session_state.user_info['role'], '一般權限')}")

if st.sidebar.button("🚪 登出系統", key="btn_logout_main"):
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.rerun()

st.sidebar.divider()
user_role = st.session_state.user_info["role"]

# 後台管理中心 (非 Sales)
if user_role in ["executive", "hr", "finance"]:
    st.sidebar.subheader("📌 系統功能選單")

    # 1. 根據權限動態組合左側選單選項
    menu_options = []
    if user_role in ["executive"]:
        menu_options.append("📈 全球股市與 AI 戰情室")
        menu_options.append("📊 企業 ERP 營運與財務 KPI")  # 💡 獨立分頁新增於此！
        menu_options.append("📊 業務報價總覽與資料庫")
        menu_options.append("🏢 跨國多廠區/公司設定")

    if user_role in ["executive", "hr"]:
        menu_options.append("📋 人事檔案管理")

    if user_role in ["executive", "hr", "finance"]:
        menu_options.append("💵 每月薪資與變動扣款")

    if user_role in ["executive", "finance"]:
        menu_options.append("🧾 越南電子發票登記")

    if user_role in ["executive"]:
        menu_options.append("👥 系統使用者與權限管理")

    # 2. 將選單放在左側邊欄
    selected_menu = st.sidebar.radio("請選擇要執行的功能：", menu_options, key="main_sidebar_menu")

    st.sidebar.divider()

    # 3. 若為高階主管且選擇「全球股市與 AI 戰情室」，在左側額外顯示股市區域篩選
    selected_stock_market = "🌐 全部市場 (All Markets)"
    if user_role == "executive" and selected_menu == "📈 全球股市與 AI 戰情室":
        st.sidebar.subheader("📈 股市市場選擇")
        selected_stock_market = st.sidebar.radio(
            "切換檢視區域",
            [
                "🌐 全部市場 (All Markets)",
                "🇹🇼 台灣 (Taiwan)",
                "🇨🇳 中國/香港 (China/HK)",
                "🇺🇸 美國 (USA)",
                "🇻🇳 越南 (Vietnam)",
                "🛢️ 原物料與匯率 (Commodities/FX)"
            ],
            key="sidebar_market_choice"
        )

    # 4. 主畫面內容展示（根據左側選單進行切換）
    st.header(f"⚙️ {selected_menu}")

    if selected_menu == "📈 全球股市與 AI 戰情室":
        executive_dashboard.render_dashboard(selected_stock_market)
    elif selected_menu == "📊 企業 ERP 營運與財務 KPI":
        erp_dashboard.render_erp_dashboard()  # 💡 呼叫獨立 ERP 看板！
    elif selected_menu == "📊 業務報價總覽與資料庫":
        sales_quotation.render_sales_overview()
    elif selected_menu == "🏢 跨國多廠區/公司設定":
        user_management.render_company_profile_setting()
    elif selected_menu == "📋 人事檔案管理":
        employee_management.render_employee_management()
    elif selected_menu == "💵 每月薪資與變動扣款":
        payroll_management.render_payroll_management()
    elif selected_menu == "🧾 越南電子發票登記":
        invoice_management.render_invoice_management()
    elif selected_menu == "👥 系統使用者與權限管理":
        user_management.render_user_management(ROLE_NAME_MAP)

# 業務專用前台 (Sales)
else:
    sales_quotation.render_sales_frontend()
