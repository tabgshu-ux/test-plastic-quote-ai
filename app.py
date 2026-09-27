import traceback
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
            "allowed_depts": "ALL"
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
            "allowed_depts": ["🏢 總務與倉儲 (General Affairs & WH)"]
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
            username_input = st.text_input("帳號 / Username", value="admin").strip().lower()
            password_input = st.text_input("密碼 / Password", type="password", value="admin123").strip()
            submit_button = st.form_submit_button("🔑 登入系統", type="primary")

            if submit_button:
                db = st.session_state.user_database
                if username_input in db and db[username_input]["password"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.user_info = db[username_input]
                    st.success("✅ 登入成功！歡迎，" + str(st.session_state.user_info['name']))
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
            - **總務/倉儲專員**：`ga_user` / `ga123`
            - **人事主管**：`hr_manager` / `hr123`
            - **業務專員**：`alex` / `alex123`
            """)
    st.stop()

# ----------------------------------------------------
# 🌐 全球多語系完整字典 (i18n) - 左下角選單已整合為單一名稱
# ----------------------------------------------------
I18N = {
    "繁體中文": {
        "dept_select": "請選擇部門/模組分類：",
        "depts": [
            "📈 營運戰情室 (Executive)",
            "🧾 財務 (Finance)",
            "🏢 總務與倉儲 (General Affairs & WH)",
            "👥 人事/行政 (HR & Admin)",
            "💼 業務/行銷 (Sales & Marketing)",
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
            "📦 倉儲進出庫與物料管理 (Warehouse)",
            "🏢 總務用品採購與庫存 (GA Procurement)",
            "💵 零用金與行政費用申請 (Petty Cash & Expenses)",
            "📄 行政公文與合同管理 (Contracts)",
            "📑 總務與簽核審核中心 (Approval Center)"
        ],
        "sub_hr": [
            "📋 員工人事資料表", 
            "💰 每月薪資與考勤變動扣款", 
            "⏰ 網路打卡機連線對接"
        ],
        "sub_sales": ["📝 AI 即時報價 & CAD/3D Pipeline", "📊 歷史報價單據與資料庫"],
        "sub_rd": ["📦 跨國資產與模具管理", "🛠️ 試模履歷與 DFM 檢討"],
        "sub_plant": ["📡 IoT 射出機/連線設備狀態監控", "⚡ 廠區營運與機台 OEE KPI", "🔧 設備預防性保養與故障告警"],
        "sub_it": [
            "💻 系統管理與稽核中心"
        ]
    },
    "English": {
        "dept_select": "Select Department / Module:",
        "depts": [
            "📈 Executive Dashboard",
            "🧾 Finance & Accounting",
            "🏢 General Affairs & WH",
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
            "📦 Warehouse Management System",
            "🏢 GA Procurement & Supplies",
            "💵 Petty Cash & Expense Claim",
            "📄 Admin Documents & Contracts",
            "📑 Approval & Workflow Center"
        ],
        "sub_hr": [
            "📋 Global Employee Profiles", 
            "💰 Monthly Payroll & Deductions", 
            "⏰ Biometric Clock-in Sync"
        ],
        "sub_sales": ["📝 AI Instant Quote & CAD/3D Pipeline", "📊 Quotation History & Database"],
        "sub_rd": ["📦 Global Assets & Mold Management", "🛠️ Mold Trial Logs & DFM Review"],
        "sub_plant": ["📡 IoT Molding Machine Monitoring", "⚡ Plant OEE & Operational KPIs", "🔧 Preventive Maintenance & Alerts"],
        "sub_it": [
            "💻 System Admin & Audit Center"
        ]
    },
    "Tiếng Việt": {
        "dept_select": "Vui lòng chọn phòng ban/phân hệ:",
        "depts": [
            "📈 Phòng Điều Hành (Executive)",
            "🧾 Tài Chính / Kế Toán",
            "🏢 Phòng Tổng Vụ & Kho (GA & WH)",
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
            "📦 Quản lý Kho & Nhập xuất kho",
            "🏢 Mua sắm & Vật tư Tổng vụ",
            "💵 Quyết toán Tiền mặt & Chi phí",
            "📄 Quản lý Công văn & Hợp đồng",
            "📑 Trung tâm Phê duyệt & Ký duyệt"
        ],
        "sub_hr": [
            "📋 Hồ sơ nhân sự toàn cầu", 
            "💰 Lương hàng tháng & Chấm công", 
            "⏰ Kết nối máy chấm công"
        ],
        "sub_sales": ["📝 Báo giá AI & CAD/3D Pipeline", "📊 Lịch sử báo giá & CSDL"],
        "sub_rd": ["📦 Quản lý Tài sản & Khuôn mẫu", "🛠️ Nhật ký thử khuôn & DFM"],
        "sub_plant": ["📡 Giám sát máy ép phun IoT", "⚡ KPI OEE & Vận hành nhà máy", "🔧 Bảo trì phòng ngừa & Cảnh báo"],
        "sub_it": [
            "💻 Quản trị Hệ thống & Kiểm toán"
        ]
    }
}

# ----------------------------------------------------
# 🛡️ 安全動態模組載入器 (萬用無錯包裝)
# ----------------------------------------------------
def load_module_function(module_name, func_names):
    try:
        mod = __import__("modules." + str(module_name), fromlist=["*"])
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
                            try:
                                return func()
                            except Exception:
                                st.error("❌ 執行 modules/" + str(module_name) + ".py 內部錯誤：\n```python\n" + str(traceback.format_exc()) + "\n```")
                    except Exception:
                        st.error("❌ 執行 modules/" + str(module_name) + ".py 例外錯誤：\n```python\n" + str(traceback.format_exc()) + "\n```")
                return safe_wrapper
        return lambda *args, **kwargs: st.error("⚠️ 在 modules/" + str(module_name) + ".py 中找不到入口函式: " + str(func_names))
    except Exception:
        err_detail = traceback.format_exc()
        return lambda *args, **kwargs: st.error("❌ 載入 modules/" + str(module_name) + ".py 失敗！\n\n**詳細錯誤追蹤**:\n```python\n" + str(err_detail) + "\n```")

# 載入所有功能模組
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
render_emp_mgmt = load_module_function("employee_management", ["render_employee_management", "show", "main"])
render_wh_mgmt = load_module_function("warehouse_management", ["render_warehouse_management", "show", "main"])

# ----------------------------------------------------
# 🔒 RBAC 權限過濾與側邊欄選單
# ----------------------------------------------------
user_info = st.session_state.user_info
allowed_depts = user_info.get("allowed_depts", "ALL")

st.sidebar.title("🏭 AI ERP")
st.sidebar.markdown("### 👤 User Status")
st.sidebar.success("🟢 **" + str(user_info['name']) + "** (" + str(user_info['role']) + ")")

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

if allowed_depts != "ALL":
    available_depts = [d for d in all_depts if any(a in d for a in allowed_depts)]
    if not available_depts:
        available_depts = [all_depts[2]]
else:
    available_depts = all_depts

selected_dept = st.sidebar.radio(
    lang_dict["dept_select"],
    options=available_depts,
    key="sidebar_dept_radio_" + str(selected_lang)
)
st.sidebar.markdown("---")

dept_idx = all_depts.index(selected_dept)

# ----------------------------------------------------
# 🔀 路由分流
# ----------------------------------------------------
if dept_idx == 0:
    sub_option = st.sidebar.radio("Executive:", lang_dict["sub_exec"], key="sub_exec_" + str(selected_lang))
    render_exec_db(sub_option, selected_lang)

elif dept_idx == 1:
    sub_option = st.sidebar.radio("Finance:", lang_dict["sub_finance"], key="sub_finance_" + str(selected_lang))
    sub_idx = lang_dict["sub_finance"].index(sub_option)
    if sub_idx == 0:
        render_ap(sub_option, selected_lang)
    elif sub_idx == 1:
        render_ar(sub_option, selected_lang)
    elif sub_idx == 5:
        render_tax_ai(sub_option, selected_lang)
    else:
        render_invoice(sub_option, selected_lang)

elif dept_idx == 2:
    sub_option = st.sidebar.radio("General Affairs & WH:", lang_dict["sub_ga"], key="sub_ga_" + str(selected_lang))
    sub_idx = lang_dict["sub_ga"].index(sub_option)
    if sub_idx == 0:
        render_wh_mgmt(sub_option, selected_lang)
    else:
        render_ga(sub_option, selected_lang)

elif dept_idx == 3:
    sub_option = st.sidebar.radio("HR:", lang_dict["sub_hr"], key="sub_hr_" + str(selected_lang))
    sub_idx = lang_dict["sub_hr"].index(sub_option)
    if sub_idx == 0:
        render_emp_mgmt(sub_option, selected_lang)
    else:
        render_payroll(sub_option, selected_lang)

elif dept_idx == 4:
    sub_option = st.sidebar.radio("Sales:", lang_dict["sub_sales"], key="sub_sales_" + str(selected_lang))
    render_sales(sub_option, selected_lang)

elif dept_idx == 5:
    sub_option = st.sidebar.radio("Engineering:", lang_dict["sub_rd"], key="sub_rd_" + str(selected_lang))
    render_asset(sub_option, selected_lang)

elif dept_idx == 6:
    sub_option = st.sidebar.radio("Plant & IoT:", lang_dict["sub_plant"], key="sub_plant_" + str(selected_lang))
    render_erp_db(sub_option, selected_lang)

elif dept_idx == 7:  # 💻 資訊/IT
    sub_option = st.sidebar.radio("IT Admin:", lang_dict["sub_it"], key="sub_it_" + str(selected_lang))
    render_user_mgmt(sub_option, selected_lang)
