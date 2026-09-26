import streamlit as st

st.set_page_config(
    page_title="Multinational Injection Molding AI ERP",
    page_icon="🏭",
    layout="wide"
)

# ----------------------------------------------------
# 🔐 1. 初始化使用者帳號資料庫與細部權限 (RBAC)
# ----------------------------------------------------
if "user_database" not in st.session_state:
    st.session_state.user_database = {
        "admin": {
            "password": "admin123", 
            "name": "Alex Chen (System Admin)", 
            "role": "Super Admin",
            "allowed_depts": "ALL"  # 擁有全系統所有模組存取權
        },
        "boss": {
            "password": "boss123", 
            "name": "陳董事長 (Chairman)", 
            "role": "Executive",
            "allowed_depts": "ALL"
        },
        "gm": {
            "password": "gm123", 
            "name": "林總經理 (General Manager)", 
            "role": "Executive",
            "allowed_depts": "ALL"
        },
        "accountant": {
            "password": "fin123", 
            "name": "王財務會計 (Accountant)", 
            "role": "Finance",
            "allowed_depts": ["🧾 財務 (Finance)"]
        },
        "ga_user": {
            "password": "ga123", 
            "name": "李總務專員 (GA Specialist)", 
            "role": "General Affairs",
            "allowed_depts": ["🏢 總務部 (General Affairs)"],  # 僅限總務部相關模組
            "allowed_subs": [
                "📦 總務用品採購與庫存 (GA Procurement & Supplies)",
                "🏢 公司固定資產與設備管理 (Company Assets)",
                "💵 零用金與行政費用申請 (Petty Cash & Expenses)",
                "📄 行政公文與合同管理 (Admin Documents & Contracts)"
            ]
        },
        "hr_manager": {
            "password": "hr123", 
            "name": "張人事主管 (HR Manager)", 
            "role": "HR & Admin",
            "allowed_depts": ["👥 人事/行政 (HR & Admin)"]
        },
        "alex": {
            "password": "alex123", 
            "name": "Alex Chen (Sales)", 
            "role": "Sales",
            "allowed_depts": ["💼 業務/行銷 (Sales & Marketing)"]
        },
    }

# 預設為未登入
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_info" not in st.session_state:
    st.session_state.user_info = None

if "lang" not in st.session_state:
    st.session_state.lang = "繁體中文"

# ----------------------------------------------------
# 🔓 2. 未登入身分驗證攔截區
# ----------------------------------------------------
if not st.session_state.logged_in:
    st.title("🏭 跨國塑膠/橡膠射出成型 — 企業級 AI ERP 系統")
    st.caption("請輸入您的企業帳號與密碼進行身分驗證（畫面重整將自動要求重新登入）")

    col_login, _ = st.columns([1, 1])
    with col_login:
        with st.form("login_form_main"):
            username_input = st.text_input("帳號 / Username", value="ga_user").strip().lower()
            password_input = st.text_input("密碼 / Password", type="password", value="ga123").strip()
            submit_button = st.form_submit_button("🔑 登入系統", type="primary")

            if submit_button:
                db = st.session_state.user_database
                if username_input in db and db[username_input]["password"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.user_info = db[username_input]
                    st.success(f"✅ 登入成功！歡迎，{st.session_state.user_info['name']}")
                    try:
                        st.rerun()
                    except Exception:
                        pass
                else:
                    st.error("❌ 帳號或密碼錯誤，請重新輸入！")

        st.info("""
            💡 **測試帳號清單：**
            - **最高主管/系統管理員**：`admin` / `admin123` 或 `boss` / `boss123`
            - **財務會計**：`accountant` / `fin123`
            - **總務專員 (細部權限限制)**：`ga_user` / `ga123`
            - **人事主管**：`hr_manager` / `hr123`
            - **業務專員**：`alex` / `alex123`
            """)
    st.stop()  # 未登入完全阻斷

# ----------------------------------------------------
# 🌐 全球多語系字典 (i18n) — 包含新增的財務部下總務部及子功能
# ----------------------------------------------------
I18N = {
    "繁體中文": {
        "dept_select": "請選擇部門/模組分類：",
        "depts": [
            "📈 營運戰情室 (Executive)",
            "🧾 財務 (Finance)",
            "🏢 總務部 (General Affairs)",  # 新增總務部獨立入口
            "👥 人事/行政 (HR & Admin)",
            "💼 業務/行销 (Sales & Marketing)",
            "🛠️ 研發/技術 (R&D & Engineering)",
            "🏭 廠務/設備 (Plant & IoT)",
            "💻 資訊/IT (IT & System Admin)"
        ],
        "sub_exec": ["🌐 全部市場 (All Markets)", "🇹🇼 台灣 (Taiwan)", "🇨🇳 中國/香港 (China/HK)", "🇺🇸 美國 (USA)", "🇻🇳 越南 (Vietnam)", "🛢️ 原物料與匯率 (Commodities/FX)"],
        "sub_finance": [
            "🛒 採購與應付帳款系統 (Procurement & AP)", 
            "📦 訂單與應收帳款系統 (Sales Orders & AR)", 
            "📄 越南電子發票 XML 解析與登錄",
            "📧 通用信箱電子發票讀取 (IMAP)",
            "📊 電子發票張數監控與加購預警",
            "🌐 全球跨國稅務 AI 智慧問答"
        ],
        "sub_ga": [
            "📦 總務用品採購與庫存 (GA Procurement & Supplies)",
            "🏢 公司固定資產與設備管理 (Company Assets)",
            "💵 零用金與行政費用申請 (Petty Cash & Expenses)",
            "📄 行政公文與合同管理 (Admin Documents & Contracts)"
        ],
        "sub_hr": ["💰 每月薪資與考勤變動扣款", "⏰ 網路打卡機連線對接"],
        "sub_sales": ["📝 AI 即時報價 & CAD/3D Pipeline", "📊 歷史報價單據與資料庫"],
        "sub_rd": ["📦 跨國資產與模具管理", "🛠️ 試模履歷與 DFM 檢討"],
        "sub_plant": ["📡 IoT 射出機/連線設備狀態監控", "⚡ 廠區營運與機台 OEE KPI", "🔧 設備預防性保養與故障告警"],
        "sub_it": ["🏢 跨國廠區與子公司管理", "👥 人員帳號與網頁授權", "🔒 模組權限矩陣 (RBAC)"]
    },
    "English": {
        "dept_select": "Select Department / Module:",
        "depts": [
            "📈 Executive Dashboard",
            "🧾 Finance & Accounting",
            "🏢 General Affairs (GA)",
            "👥 HR & Administration",
            "💼 Sales & Marketing",
            "🛠️ R&D & Engineering",
            "🏭 Plant & IoT Engineering",
            "💻 IT & System Admin"
        ],
        "sub_exec": ["🌐 All Markets", "🇹🇼 Taiwan", "🇨🇳 China/HK", "🇺🇸 USA", "🇻🇳 Vietnam", "🛢️ Commodities & FX"],
        "sub_finance": [
            "🛒 Procurement & Accounts Payable (AP)", 
            "📦 Sales Orders & Accounts Receivable (AR)", 
            "📄 Vietnam E-Invoice XML Parser",
            "📧 Email Invoice Fetcher (IMAP)",
            "📊 E-Invoice Quota Alert & Top-up",
            "🌐 Global Tax & Compliance AI"
        ],
        "sub_ga": [
            "📦 GA Procurement & Supplies",
            "🏢 Company Asset Management",
            "💵 Petty Cash & Expense Claim",
            "📄 Admin Documents & Contracts"
        ],
        "sub_hr": ["💰 Monthly Payroll & Deductions", "⏰ Biometric Clock-in Sync"],
        "sub_sales": ["📝 AI Instant Quote & CAD/3D Pipeline", "📊 Quotation History & Database"],
        "sub_rd": ["📦 Global Assets & Mold Management", "🛠️ Mold Trial Logs & DFM Review"],
        "sub_plant": ["📡 IoT Molding Machine Monitoring", "⚡ Plant OEE & Operational KPIs", "🔧 Preventive Maintenance & Alerts"],
        "sub_it": ["🏢 Global Sites & Subsidiaries", "👥 User Auth & Web Permissions", "🔒 Role-Based Access Control (RBAC)"]
    },
    "Tiếng Việt": {
        "dept_select": "Vui lòng chọn phòng ban/phân hệ:",
        "depts": [
            "📈 Phòng Điều Hành (Executive)",
            "🧾 Tài Chính / Kế Toán",
            "🏢 Phòng Tổng Vụ (General Affairs)",
            "👥 Nhân Sự / Hành Chính",
            "💼 Kinh Doanh / Marketing",
            "🛠️ R&D / Kỹ Thuật",
            "🏭 Quản Lý Nhà Máy & IoT",
            "💻 Công Nghệ Thông Tin (IT)"
        ],
        "sub_exec": ["🌐 Tất cả thị trường", "🇹🇼 Đài Loan", "🇨🇳 Trung Quốc/HK", "🇺🇸 Mỹ", "🇻🇳 Việt Nam", "🛢️ Nguyên liệu & Tỷ giá"],
        "sub_finance": [
            "🛒 Quản lý Mua hàng & Phải trả (AP)", 
            "📦 Đơn bán hàng & Phải thu (AR)", 
            "📄 Phân tích Hóa đơn XML Việt Nam",
            "📧 Đọc Hóa đơn qua Email (IMAP)",
            "📊 Giám sát & Báo động số lượng HĐ",
            "🌐 Tư vấn AI Thuế Quốc Tế"
        ],
        "sub_ga": [
            "📦 Mua sắm & Vật tư Tổng vụ",
            "🏢 Quản lý Tài sản cố định",
            "💵 Quyết toán Tiền mặt & Chi phí",
            "📄 Quản lý Công văn & Hợp đồng"
        ],
        "sub_hr": ["💰 Lương hàng tháng & Chấm công", "⏰ Kết nối máy chấm công"],
        "sub_sales": ["📝 Báo giá AI & CAD/3D Pipeline", "📊 Lịch sử báo giá & CSDL"],
        "sub_rd": ["📦 Quản lý Tài sản & Khuôn mẫu", "🛠️ Nhật ký thử khuôn & DFM"],
        "sub_plant": ["📡 Giám sát máy ép phun IoT", "⚡ KPI OEE & Vận hành nhà máy", "🔧 Bảo trì phòng ngừa & Cảnh báo"],
        "sub_it": ["🏢 Quản lý Chi nhánh & Công ty con", "👥 Phân quyền người dùng", "🔒 Ma trận quyền (RBAC)"]
    }
}

# ----------------------------------------------------
# 🛡️ 模組動態載入器 (加強容錯)
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

# 載入所有功能模組（包含新增的總務部模組）
render_exec_db = load_module_function("executive_dashboard", ["render_executive_dashboard_page", "show", "main"])
render_sales = load_module_function("sales_quotation", ["render_sales_quotation_page", "show", "main"])
render_invoice = load_module_function("invoice_management", ["render_invoice_management_page", "show", "main"])
render_ap = load_module_function("procurement_ap", ["render_procurement_ap_page", "show", "main"])
render_ar = load_module_function("sales_order_ar", ["render_sales_order_ar_page", "show", "main"])
render_tax_ai = load_module_function("finance_tax", ["render_finance_tax_page", "show", "main"])
render_asset = load_module_function("asset_management", ["render_asset_management_page", "show", "main"])
render_erp_db = load_module_function("erp_dashboard", ["render_erp_dashboard_page", "show", "main"])
render_payroll = load_module_function("payroll_management", ["render_payroll_management_page", "show", "main"])
render_user_mgmt = load_module_function("user_management", ["render_user_management_page", "show", "main"])
render_ga = load_module_function("general_affairs", ["render_general_affairs_page", "show", "main"])

# ----------------------------------------------------
# 🔒 3. 細部 RBAC 權限過濾器
# ----------------------------------------------------
user_info = st.session_state.user_info
allowed_depts = user_info.get("allowed_depts", "ALL")

# ----------------------------------------------------
# 側邊欄 (Sidebar) 選單渲染
# ----------------------------------------------------
st.sidebar.title("🏭 AI ERP")
st.sidebar.markdown("### 👤 User Status")

st.sidebar.success(f"🟢 **{user_info['name']}** ({user_info['role']})")
if st.sidebar.button("🔒 Logout System", key="btn_global_logout"):
    st.session_state.logged_in = False
    st.session_state.user_info = None
    try:
        st.rerun()
    except Exception:
        pass

st.sidebar.markdown("---")

selected_lang = st.sidebar.selectbox(
    "🌐 System Language:",
    ["繁體中文", "Tiếng Việt", "English"],
    key="fixed_lang_selector_key"
)

st.session_state["lang"] = selected_lang
lang_dict = I18N.get(selected_lang, I18N["繁體中文"])
st.sidebar.markdown("---")

all_depts = lang_dict["depts"]

# **權限限制處理**：如果使用者有特定部門存取限制，則只顯示該使用者有權限點選的部門
if allowed_depts != "ALL":
    available_depts = [d for d in all_depts if any(a in d for a in allowed_depts)]
    if not available_depts:
        available_depts = [all_depts[2]] # 預設 fallback 到總務部
else:
    available_depts = all_depts

selected_dept = st.sidebar.radio(
    lang_dict["dept_select"],
    options=available_depts,
    key=f"sidebar_dept_radio_{selected_lang}"
)
st.sidebar.markdown("---")

# 找到當前選取部門的全域索引值
dept_idx = all_depts.index(selected_dept)

# ----------------------------------------------------
# 🔀 路由分流与權限控管
# ----------------------------------------------------
if dept_idx == 0:  # 📈 營運戰情室
    sub_option = st.sidebar.radio("Executive:", lang_dict["sub_exec"], key=f"sub_exec_{selected_lang}")
    render_exec_db(sub_option, selected_lang)

elif dept_idx == 1:  # 🧾 財務
    sub_option = st.sidebar.radio("Finance:", lang_dict["sub_finance"], key=f"sub_finance_{selected_lang}")
    sub_idx = lang_dict["sub_finance"].index(sub_option)
    
    if sub_idx == 0:
        render_ap(sub_option, selected_lang)
    elif sub_idx == 1:
        render_ar(sub_option, selected_lang)
    elif sub_idx == 5:
        render_tax_ai(sub_option, selected_lang)
    else:
        render_invoice(sub_option, selected_lang)

elif dept_idx == 2:  # 🏢 總務部 (General Affairs)
    # 若有子功能權限限制，過濾子選單
    user_allowed_subs = user_info.get("allowed_subs", "ALL")
    ga_subs = lang_dict["sub_ga"]
    if user_allowed_subs != "ALL":
        filtered_ga_subs = [s for s in ga_subs if any(uas in s for uas in user_allowed_subs)]
        if not filtered_ga_subs:
            filtered_ga_subs = ga_subs
    else:
        filtered_ga_subs = ga_subs

    sub_option = st.sidebar.radio("General Affairs:", filtered_ga_subs, key=f"sub_ga_{selected_lang}")
    render_ga(sub_option, selected_lang)

elif dept_idx == 3:  # 👥 人事/行政
    sub_option = st.sidebar.radio("HR:", lang_dict["sub_hr"], key=f"sub_hr_{selected_lang}")
    render_payroll(sub_option, selected_lang)

elif dept_idx == 4:  # 💼 業務/行銷
    sub_option = st.sidebar.radio("Sales:", lang_dict["sub_sales"], key=f"sub_sales_{selected_lang}")
    render_sales(sub_option, selected_lang)

elif dept_idx == 5:  # 🛠️ 研發/技術
    sub_option = st.sidebar.radio("Engineering:", lang_dict["sub_rd"], key=f"sub_rd_{selected_lang}")
    render_asset(sub_option, selected_lang)

elif dept_idx == 6:  # 🏭 廠務/設備
    sub_option = st.sidebar.radio("Plant & IoT:", lang_dict["sub_plant"], key=f"sub_plant_{selected_lang}")
    render_erp_db(sub_option, selected_lang)

elif dept_idx == 7:  # 💻 資訊/IT
    sub_option = st.sidebar.radio("IT Admin:", lang_dict["sub_it"], key=f"sub_it_{selected_lang}")
    render_user_mgmt(sub_option, selected_lang)
