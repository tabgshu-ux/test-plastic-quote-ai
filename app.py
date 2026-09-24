import os
import streamlit as st
import google.generativeai as genai

# 匯入各個獨立模組
try:
    from modules import (
        executive_dashboard,
        sales_quotation,
        employee_management,
        payroll_management,
        invoice_management,
        user_management,
        procurement_ap,  # 採購與應付帳款模組
    )
except ImportError as e:
    st.error(f"⚠️ 模組載入提示：請確認 modules 資料夾中檔案齊全 ({e})")

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

# 預設為未登入（每次畫面重整 session 清空即自動要求登入）
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# ==========================================
# 🔓 登入邏輯（未登入前嚴格防護，絕不暴露內部頁面）
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
    st.stop()  # ⛔ 強制中斷！未登入者無法執行下方任何模組與功能

# ==========================================
# 🔒 主系統 UI & 路由分發
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
    st.header(f"⚙️ 後台管理中心 — [{ROLE_NAME_MAP.get(user_role)}]")

    selected_stock_market = "🌐 全部市場 (All Markets)"
    if user_role == "executive":
        st.sidebar.subheader("📈 股市市場選擇 (Market Filter)")
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
        st.sidebar.divider()

    # 動態建構符合角色的頁籤 (Tabs)
    tabs_to_show = []
    if user_role in ["executive"]:
        tabs_to_show.append("📈 全球股市與 AI 財經動態戰情室")
        tabs_to_show.append("📊 業務報價總覽與資料庫")
        tabs_to_show.append("🏢 跨國多廠區/公司資訊設定")

    if user_role in ["executive", "finance"]:
        tabs_to_show.append("🛒 採購與應付帳款 ERP (Procurement & AP)")

    if user_role in ["executive", "hr"]:
        tabs_to_show.append("📋 人事檔案 (Employee Profiles)")

    if user_role in ["executive", "hr", "finance"]:
        tabs_to_show.append("💵 每月薪資發放與變動扣款 (Monthly Payroll)")

    if user_role in ["executive", "finance"]:
        tabs_to_show.append("🧾 越南電子發票登記 (Hóa đơn điện tử)")

    if user_role in ["executive"]:
        tabs_to_show.append("👥 系統使用者與權限管理 (User Management)")

    active_tabs = st.tabs(tabs_to_show)

    for i, tab_name in enumerate(tabs_to_show):
        with active_tabs[i]:
            if tab_name == "📈 全球股市與 AI 財經動態戰情室":
                if hasattr(executive_dashboard, "render_executive_dashboard_page"):
                    executive_dashboard.render_executive_dashboard_page(selected_stock_market)
                elif hasattr(executive_dashboard, "render_dashboard"):
                    executive_dashboard.render_dashboard(selected_stock_market)
                else:
                    executive_dashboard.show(selected_stock_market)

            elif tab_name == "🛒 採購與應付帳款 ERP (Procurement & AP)":
                if hasattr(procurement_ap, "render_procurement_ap_page"):
                    procurement_ap.render_procurement_ap_page()
                else:
                    procurement_ap.show()

            elif tab_name == "📊 業務報價總覽與資料庫":
                sales_quotation.render_sales_overview()

            elif tab_name == "🏢 跨國多廠區/公司資訊設定":
                user_management.render_company_profile_setting()

            elif tab_name == "📋 人事檔案 (Employee Profiles)":
                employee_management.render_employee_management()

            elif tab_name == "💵 每月薪資發放與變動扣款 (Monthly Payroll)":
                payroll_management.render_payroll_management()

            elif tab_name == "🧾 越南電子發票登記 (Hóa đơn điện tử)":
                invoice_management.render_invoice_management()

            elif tab_name == "👥 系統使用者與權限管理 (User Management)":
                user_management.render_user_management(ROLE_NAME_MAP)

# 業務專用前台 (Sales)
else:
    sales_quotation.render_sales_frontend()
