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
    st.sidebar.subheader("📌 系統功能功能選單")

    # 1. 根據權限動態組合左側選單選項
    menu_options = []
    if user_role in ["executive"]:
        menu_options.append("📈 全球股市與 AI 戰情室")
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

    # 2. 將選單放在左側邊欄 (Radio Buttons)
    selected_menu = st.sidebar.radio("請選擇要執行的功能：", menu_options, key="main_sidebar_menu")

    st.sidebar.divider()

    # 3. 若為高階主管，在左側額外顯示股市區域篩選
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
