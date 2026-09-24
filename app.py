import streamlit as st

st.set_page_config(
    page_title="Multinational Injection Molding AI ERP",
    page_icon="🏭",
    layout="wide"
)

# ----------------------------------------------------
# 🔐 1. 初始化使用者帳號資料庫與登入驗證狀態
# ----------------------------------------------------
if "user_database" not in st.session_state:
    st.session_state.user_database = {
        "admin": {"password": "admin123", "name": "Alex Chen (System Admin)", "role": "Super Admin"},
        "boss": {"password": "boss123", "name": "陳董事長 (Chairman)", "role": "Executive"},
        "gm": {"password": "gm123", "name": "林總經理 (General Manager)", "role": "Executive"},
        "hr_manager": {"password": "hr123", "name": "張人事主管 (HR Manager)", "role": "HR & Admin"},
        "accountant": {"password": "fin123", "name": "王財務會計 (Accountant)", "role": "Finance"},
        "alex": {"password": "alex123", "name": "Alex Chen (Sales)", "role": "Sales"},
    }

# 預設為未登入（畫面重整即自動要求重新登入）
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_info" not in st.session_state:
    st.session_state.user_info = None

if "lang" not in st.session_state:
    st.session_state.lang = "繁體中文"

# ----------------------------------------------------
# 🔓 2. 未登入身分驗證攔截區（未登入前完全中斷，防止洩漏介面）
# ----------------------------------------------------
if not st.session_state.logged_in:
    st.title("🏭 跨國塑膠/橡膠射出成型 — 企業級 AI ERP 系統")
    st.caption("請輸入您的企業帳號與密碼進行身分驗證（畫面重整將自動要求重新登入）")

    col_login, _ = st.columns([1, 1])
    with col_login:
        with st.form("login_form_main"):
            username_input = st.text_input("帳號 / Username", value="admin").strip().lower()
            password_input = st.text_input("密碼 / Password", type="password", value="admin123").strip()
            submit_button = st.form_submit_button("🔑 登入系統", type="primary")

            if submit_button:
                db = st.session_state.user_database
                if username_input in db and db[username_input]["password"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.user_info = db[username_input]
                    st.success(f"✅ 登入成功！歡迎，{st.session_state.user_info['name']}")
                    st.rerun()
                else:
                    st.error("❌ 帳號或密碼錯誤，請重新輸入！")

        st.info("""
            💡 **測試帳號清單：**
            - **最高主管**：`admin` / `admin123` 或 `boss` / `boss123`
            - **財務會計**：`accountant` / `fin123`
            - **人事主管**：`hr_manager` / `hr123`
            - **業務專員**：`alex` / `alex123`
            """)
    st.stop()  # ⛔ 強制中斷！未登入者完全無法載入與執行下方任何選單與模組程式碼

# ----------------------------------------------------
# 🌐 全球多語系完整字典 (i18n)
# ----------------------------------------------------
I18N = {
    "繁體中文": {
        "dept_select": "請選擇部門/模組分類：",
        "depts": [
            "📈 營運戰情室 (Executive)",
            "💼 業務/行銷 (Sales & Marketing)",
            "🛠️ 研發/技術 (R&D & Engineering)",
            "🏭 廠務/設備 (Plant & IoT)",
            "🧾 財務 (Finance)",
            "👥 人事/行政 (HR & Admin)",
            "💻 資訊/IT (IT & System Admin)"
        ],
        "sub_exec": ["🌐 全部市場 (All Markets)", "🇹🇼 台灣 (Taiwan)", "🇨🇳 中國/香港 (China/HK)", "🇺🇸 美國 (USA)", "🇻🇳 越南 (Vietnam)", "🛢️ 原物料與匯率 (Commodities/FX)"],
        "sub_sales": ["📝 AI 即時報價 & CAD/3D Pipeline", "📊 歷史報價單據與資料庫"],
        "sub_rd": ["📦 跨國資產與模具管理", "🛠️ 試模履歷與 DFM 檢討"],
        "sub_plant": ["📡 IoT 射出機/連線設備狀態監控", "⚡ 廠區營運與機台 OEE KPI", "🔧 設備預防性保養與故障告警"],
        "sub_finance": [
            "🛒 採購與應付帳款系統 (Procurement & AP)", 
            "📦 訂單與應收帳款系統 (Sales Orders & AR)", 
            "📄 越南電子發票 XML 解析與登錄",
            "📧 通用信箱電子發票讀取 (IMAP)",
            "📊 電子發票張數監控與加購預警",
            "🌐 全球跨國稅務 AI 智慧問答"
        ],
        "sub_hr": ["💰 每月薪資與考勤變動扣款", "⏰ 網路打卡機連線對接"],
        "sub_it": ["🏢 跨國廠區與子公司管理", "👥 人員帳號與網頁授權", "🔒 模組權限矩陣 (RBAC)"]
    },
    "English": {
        "dept_select": "Select Department / Module:",
        "depts": [
            "📈 Executive Dashboard",
            "💼 Sales & Marketing",
            "🛠️ R&D & Engineering",
            "🏭 Plant & IoT Engineering",
            "🧾 Finance & Accounting",
            "👥 HR & Administration",
            "💻 IT & System Admin"
        ],
        "sub_exec": ["🌐 All Markets", "🇹🇼 Taiwan", "🇨🇳 China/HK", "🇺🇸 USA", "🇻🇳 Vietnam", "🛢️ Commodities & FX"],
        "sub_sales": ["📝 AI Instant Quote & CAD/3D Pipeline", "📊 Quotation History & Database"],
        "sub_rd": ["📦 Global Assets & Mold Management", "🛠️ Mold Trial Logs & DFM Review"],
        "sub_plant": ["📡 IoT Molding Machine Monitoring", "⚡ Plant OEE & Operational KPIs", "🔧 Preventive Maintenance & Alerts"],
        "sub_finance": [
            "🛒 Procurement & Accounts Payable (AP)", 
            "📦 Sales Orders & Accounts Receivable (AR)", 
            "📄 Vietnam E-Invoice XML Parser",
            "📧 Email Invoice Fetcher (IMAP)",
            "📊 E-Invoice Quota Alert & Top-up",
            "🌐 Global Tax & Compliance AI"
        ],
        "sub_hr": ["💰 Monthly Payroll & Deductions", "⏰ Biometric Clock-in Sync"],
        "sub_it": ["🏢 Global Sites & Subsidiaries", "👥 User Auth & Web Permissions", "🔒 Role-Based Access Control (RBAC)"]
    },
    "Tiếng Việt": {
        "dept_select": "Vui lòng chọn phòng ban/phân hệ:",
        "depts": [
            "📈 Phòng Điều Hành (Executive)",
            "💼 Kinh Doanh / Marketing",
            "🛠️ R&D / Kỹ Thuật",
            "🏭 Quản Lý Nhà Máy & IoT",
            "🧾 Tài Chính / Kế Toán",
            "👥 Nhân Sự / Hành Chính",
            "💻 Công Nghệ Thông Tin (IT)"
        ],
        "sub_exec": ["🌐 Tất cả thị trường", "🇹🇼 Đài Loan", "🇨🇳 Trung Quốc/HK", "🇺🇸 Mỹ", "🇻🇳 Việt Nam", "🛢️ Nguyên liệu & Tỷ giá"],
        "sub_sales": ["📝 Báo giá AI & CAD/3D Pipeline", "📊 Lịch sử báo giá & CSDL"],
        "sub_rd": ["📦 Quản lý Tài sản & Khuôn mẫu", "🛠️ Nhật ký thử khuôn & DFM"],
        "sub_plant": ["📡 Giám sát máy ép phun IoT", "⚡ KPI OEE & Vận hành nhà máy", "🔧 Bảo trì phòng ngừa & Cảnh báo"],
        "sub_finance": [
            "🛒 Quản lý Mua hàng & Phải trả (AP)", 
            "📦 Đơn bán hàng & Phải thu (AR)", 
            "📄 Phân tích Hóa đơn XML Việt Nam",
            "📧 Đọc Hóa đơn qua Email (IMAP)",
            "📊 Giám sát & Báo động số lượng HĐ",
            "🌐 Tư vấn AI Thuế Quốc Tế"
        ],
        "sub_hr": ["💰 Lương hàng tháng & Chấm công", "⏰ Kết nối máy chấm công"],
        "sub_it": ["🏢 Quản lý Chi nhánh & Công ty con", "👥 Phân quyền người dùng", "🔒 Ma trận quyền (RBAC)"]
    }
}

# ----------------------------------------------------
# 🛡️ 安全靜態與動態模組載入器 (您原本的寫法，完全保留)
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
        return lambda *args, **kwargs: st.error(f"⚠️ 在 modules/{module_name}.py 中找不到入口函式: {func_names}")
    except Exception as e:
        return lambda *args, **kwargs: st.error(f"❌ 載入 modules/{module_name}.py 失敗！\n\n**詳細錯誤原因**: `{e}`")

# 載入所有功能模組
render_exec_db = load_module_function("executive_dashboard", ["render_executive_dashboard_page", "show", "main"])
render_sales = load_module_function("sales_quotation", ["render_sales_quotation_page", "show", "main"])
render_invoice = load_module_function("invoice_management", ["render_invoice_management_page", "show", "main"])
render_ap = load_module_function("procurement_ap", ["render_procurement_ap_page", "show", "main"])
render_tax_ai = load_module_function("finance_tax", ["render_finance_tax_page", "show", "main"])
render_asset = load_module_function("asset_management", ["render_asset_management_page", "show", "main"])
render_erp_db = load_module_function("erp_dashboard", ["render_erp_dashboard_page", "show", "main"])
render_payroll = load_module_function("payroll_management", ["render_payroll_management_page", "show", "main"])
render_user_mgmt = load_module_function("user_management", ["render_user_management_page", "show", "main"])

# ----------------------------------------------------
# 側邊欄 (Sidebar) 選單渲染 (登入成功後才會看到此區)
# ----------------------------------------------------
st.sidebar.title("🏭 AI ERP")
st.sidebar.markdown("### 👤 User Status")

st.sidebar.success(f"🟢 **{st.session_state.user_info['name']}**")
if st.sidebar.button("🔒 Logout System", key="btn_global_logout"):
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.rerun()

st.sidebar.markdown("---")

selected_lang = st.sidebar.selectbox(
    "🌐 System Language:",
    ["繁體中文", "Tiếng Việt", "English"],
    key="fixed_lang_selector_key"
)

st.session_state["lang"] = selected_lang
lang_dict = I18N.get(selected_lang, I18N["繁體中文"])
st.sidebar.markdown("---")

dept_options = lang_dict["depts"]
selected_dept = st.sidebar.radio(
    lang_dict["dept_select"],
    options=dept_options,
    key=f"sidebar_dept_radio_{selected_lang}"
)
st.sidebar.markdown("---")

dept_idx = dept_options.index(selected_dept)

# 路由分流
if dept_idx == 0:
    sub_option = st.sidebar.radio("Executive:", lang_dict["sub_exec"], key=f"sub_exec_{selected_lang}")
    render_exec_db(sub_option, selected_lang)

elif dept_idx == 1:
    sub_option = st.sidebar.radio("Sales:", lang_dict["sub_sales"], key=f"sub_sales_{selected_lang}")
    render_sales(sub_option, selected_lang)

elif dept_idx == 2:
    sub_option = st.sidebar.radio("Engineering:", lang_dict["sub_rd"], key=f"sub_rd_{selected_lang}")
    render_asset(sub_option, selected_lang)

elif dept_idx == 3:
    sub_option = st.sidebar.radio("Plant & IoT:", lang_dict["sub_plant"], key=f"sub_plant_{selected_lang}")
    render_erp_db(sub_option, selected_lang)

elif dept_idx == 4:
    sub_option = st.sidebar.radio("Finance:", lang_dict["sub_finance"], key=f"sub_finance_{selected_lang}")
    sub_idx = lang_dict["sub_finance"].index(sub_option)
    
    if sub_idx == 0: # 採購與應付帳款 (Procurement & AP ERP)
        render_ap(sub_option, selected_lang)
    elif sub_idx == 1: # 訂單與應收帳款 (AR)
        st.title("📦 Sales Orders & Accounts Receivable (AR)")
        st.info("此模組正在建置中...")
    elif sub_idx == 5: # 全球稅務 AI
        render_tax_ai(sub_option, selected_lang)
    else: # 電子發票管理
        render_invoice(sub_option, selected_lang)

elif dept_idx == 5:
    sub_option = st.sidebar.radio("HR:", lang_dict["sub_hr"], key=f"sub_hr_{selected_lang}")
    render_payroll(sub_option, selected_lang)

elif dept_idx == 6:
    sub_option = st.sidebar.radio("IT Admin:", lang_dict["sub_it"], key=f"sub_it_{selected_lang}")
    render_user_mgmt(sub_option, selected_lang)
