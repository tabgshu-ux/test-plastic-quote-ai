import streamlit as st

st.set_page_config(
    page_title="Multinational Injection Molding AI ERP",
    page_icon="🏭",
    layout="wide"
)

# ----------------------------------------------------
# 1. 使用者 Session State 初始化與登入驗證機制
# ----------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # 預設維持登入狀態以利測試

if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "username": "admin",
        "name": "Alex Chen (System Admin)",
        "role": "Super Admin"
    }

if "lang" not in st.session_state:
    st.session_state.lang = "繁體中文"

# ----------------------------------------------------
# 🌐 全球多語系完整字典 (Full i18n Dictionary - 5 Languages)
# ----------------------------------------------------
I18N = {
    "繁體中文": {
        "title": "🏭 AI ERP 系統選單",
        "lang_select": "🌐 選擇系統語系 (Language):",
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
        "title": "🏭 AI ERP System Menu",
        "lang_select": "🌐 System Language:",
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
        "title": "🏭 Menu Hệ Thống AI ERP",
        "lang_select": "🌐 Chọn ngôn ngữ (Language):",
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
    },
    "简体中文": {
        "title": "🏭 AI ERP 系统菜单",
        "lang_select": "🌐 选择系统语系 (Language):",
        "dept_select": "请选择部门/模块分类：",
        "depts": [
            "📈 营运战情室 (Executive)",
            "💼 业务/营销 (Sales & Marketing)",
            "🛠️ 研发/技术 (R&D & Engineering)",
            "🏭 厂务/设备 (Plant & IoT)",
            "🧾 财务 (Finance)",
            "👥 人事/行政 (HR & Admin)",
            "💻 信息/IT (IT & System Admin)"
        ],
        "sub_exec": ["🌐 全部市场 (All Markets)", "🇹🇼 台湾 (Taiwan)", "🇨🇳 中国/香港 (China/HK)", "🇺🇸 美国 (USA)", "🇻🇳 越南 (Vietnam)", "🛢️ 原物料与汇率 (Commodities/FX)"],
        "sub_sales": ["📝 AI 实时报价 & CAD/3D Pipeline", "📊 历史报价单据与数据库"],
        "sub_rd": ["📦 跨国资产与模具管理", "🛠️ 试模履历与 DFM 检讨"],
        "sub_plant": ["📡 IoT 注塑机/连线设备状态监控", "⚡ 厂区营运与机台 OEE KPI", "🔧 设备预防性保养与故障告警"],
        "sub_finance": [
            "🛒 采购与应付账款系统 (Procurement & AP)", 
            "📦 订单与应收账款系统 (Sales Orders & AR)", 
            "📄 越南电子发票 XML 解析与登录",
            "📧 通用邮箱电子发票读取 (IMAP)",
            "📊 电子发票张数监控与加购预警",
            "🌐 全球跨国税务 AI 智慧问答"
        ],
        "sub_hr": ["💰 每月薪资与考勤变动扣款", "⏰ 网络打卡机连线对接"],
        "sub_it": ["🏢 跨国厂区与子公司管理", "👥 人员账号与网页授权", "🔒 模块权限矩阵 (RBAC)"]
    },
    "Bahasa Indonesia": {
        "title": "🏭 Menu Sistem AI ERP",
        "lang_select": "🌐 Pilih Bahasa (Language):",
        "dept_select": "Pilih Departemen / Modul:",
        "depts": [
            "📈 Dasbor Eksekutif",
            "💼 Penjualan & Pemasaran",
            "🛠️ R&D & Teknik",
            "🏭 Teknik Pabrik & IoT",
            "🧾 Keuangan & Akuntansi",
            "👥 SDM & Administrasi",
            "💻 IT & Admin Sistem"
        ],
        "sub_exec": ["🌐 Semua Pasar", "🇹🇼 Taiwan", "🇨🇳 Tiongkok/HK", "🇺🇸 AS", "🇻🇳 Vietnam", "🛢️ Komoditas & Valas"],
        "sub_sales": ["📝 Kutipan AI & Saluran CAD/3D", "📊 Riwayat Kutipan & Basis Data"],
        "sub_rd": ["📦 Aset Global & Manajemen Cetakan", "🛠️ Log Uji Cetakan & Tinjauan DFM"],
        "sub_plant": ["📡 Pemantauan Mesin Cetak IoT", "⚡ OEE Pabrik & KPI Operasional", "🔧 Pemeliharaan Preventif & Peringatan"],
        "sub_finance": [
            "🛒 Pengadaan & Hutang Dagang (AP)", 
            "📦 Pesanan Penjualan & Piutang (AR)", 
            "📄 Parser XML Faktur Elektronik",
            "📧 Ambil Faktur via Email (IMAP)",
            "📊 Peringatan Kuota Faktur & Top-up",
            "🌐 Asisten AI Pajak Global"
        ],
        "sub_hr": ["💰 Gaji Bulanan & Absensi", "⏰ Integrasi Mesin Absensi"],
        "sub_it": ["🏢 Situs Global & Anak Perusahaan", "👥 Otentikasi Pengguna", "🔒 Kontrol Akses Berbasis Peran (RBAC)"]
    }
}

# ----------------------------------------------------
# 安全動態載入模組
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
        return lambda *args, **kwargs: st.error(f"⚠️ 在 modules/{module_name}.py 中找不到以下任何入口函式: {func_names}")
    except Exception as e:
        return lambda *args, **kwargs: st.error(f"❌ 載入 modules/{module_name}.py 失敗！\n\n**詳細錯誤原因**: `{e}`")

# 載入核心模組
render_exec_db = load_module_function("executive_dashboard", ["render_executive_dashboard_page", "render_dashboard", "show", "main"])
render_erp_db = load_module_function("erp_dashboard", ["render_erp_dashboard_page", "show", "main"])
render_sales = load_module_function("sales_quotation", ["render_sales_quotation_page", "render_sales_frontend", "show", "main"])
render_invoice = load_module_function("invoice_management", ["render_invoice_management_page", "render_invoice", "show", "main"])
render_tax_ai = load_module_function("finance_tax", ["render_finance_tax_page", "show", "main"])
render_payroll = load_module_function("payroll_management", ["render_payroll_management_page", "show", "main"])
render_asset = load_module_function("asset_management", ["render_asset_management_page", "show", "main"])
render_user_mgmt = load_module_function("user_management", ["render_user_management_page", "show", "main"])

# ----------------------------------------------------
# 側邊欄 1：使用者帳號登入/登出狀態區塊
# ----------------------------------------------------
st.sidebar.title("🏭 AI ERP")
st.sidebar.markdown("### 👤 User Status & Role")

if st.session_state.logged_in:
    st.sidebar.success(f"🟢 **{st.session_state.user_info['name']}**")
    st.sidebar.caption(f"🔑 ID: `{st.session_state.user_info['username']}` | Role: `{st.session_state.user_info['role']}`")
    if st.sidebar.button("🔒 Logout System", key="btn_global_logout"):
        st.session_state.logged_in = False
        st.rerun()
else:
    st.sidebar.warning("🔴 Not Logged In")
    with st.sidebar.form("login_form_sidebar"):
        username_input = st.text_input("Username", value="admin")
        password_input = st.text_input("Password", type="password", value="123456")
        submit_login = st.form_submit_button("🚀 Login")
        if submit_login:
            st.session_state.logged_in = True
            st.session_state.user_info = {
                "username": username_input,
                "name": f"{username_input} (Admin)",
                "role": "Super Admin"
            }
            st.rerun()

st.sidebar.markdown("---")

if not st.session_state.logged_in:
    st.title("🔒 Multinational Injection Molding AI ERP System")
    st.warning("⚠️ Please log in from the left sidebar to access the ERP system.")
    st.stop()

# ----------------------------------------------------
# 側邊欄 2：語系切換器與動態語系部門選單
# ----------------------------------------------------
selected_lang = st.sidebar.selectbox(
    "🌐 System Language:",
    ["繁體中文", "English", "Tiếng Việt", "简体中文", "Bahasa Indonesia"],
    key="fixed_lang_selector_key"
)
st.session_state.lang = selected_lang
lang_dict = I18N[selected_lang]
st.sidebar.markdown("---")

# 動態部門選單
dept_options = lang_dict["depts"]
selected_dept = st.sidebar.radio(
    lang_dict["dept_select"],
    options=dept_options,
    key=f"sidebar_dept_radio_{selected_lang}"
)
st.sidebar.markdown("---")

# 透過位置索引 (0 ~ 6) 進行分發，確保切換語言時完美對應
dept_idx = dept_options.index(selected_dept)

# ----------------------------------------------------
# 頁面路由與動態語系子選單
# ----------------------------------------------------
if dept_idx == 0:  # 營運戰情室
    sub_option = st.sidebar.radio(
        "Executive:",
        lang_dict["sub_exec"],
        key=f"sub_exec_{selected_lang}"
    )
    render_exec_db(sub_option, selected_lang)

elif dept_idx == 1:  # 業務/行銷
    sub_option = st.sidebar.radio(
        "Sales:",
        lang_dict["sub_sales"],
        key=f"sub_sales_{selected_lang}"
    )
    render_sales(sub_option)

elif dept_idx == 2:  # 研發/技術
    sub_option = st.sidebar.radio(
        "Engineering:",
        lang_dict["sub_rd"],
        key=f"sub_rd_{selected_lang}"
    )
    render_asset(sub_option)

elif dept_idx == 3:  # 廠務/設備
    sub_option = st.sidebar.radio(
        "Plant & IoT:",
        lang_dict["sub_plant"],
        key=f"sub_plant_{selected_lang}"
    )
    render_erp_db(sub_option)

elif dept_idx == 4:  # 財務
    sub_option = st.sidebar.radio(
        "Finance:",
        lang_dict["sub_finance"],
        key=f"sub_finance_{selected_lang}"
    )
    
    sub_idx = lang_dict["sub_finance"].index(sub_option)
    
    if sub_idx == 0:  # 採購與應付帳款 (AP)
        st.title("🛒 Procurement & Accounts Payable (AP)")
        st.info("Module under construction: Purchase Orders, Goods Receipt Notes, AP Invoices.")
    elif sub_idx == 1:  # 訂單與應收帳款 (AR)
        st.title("📦 Sales Orders & Accounts Receivable (AR)")
        st.info("Module under construction: Sales Orders, Delivery Orders, AR Settlements.")
    elif sub_idx == 5:  # 跨國稅務 AI
        render_tax_ai(sub_option)
    else:  # 發票 XML 解析、IMAP 信箱讀取、張數預警
        render_invoice(sub_option)

elif dept_idx == 5:  # 人事/行政
    sub_option = st.sidebar.radio(
        "HR:",
        lang_dict["sub_hr"],
        key=f"sub_hr_{selected_lang}"
    )
    render_payroll(sub_option)

elif dept_idx == 6:  # 資訊/IT
    sub_option = st.sidebar.radio(
        "IT Admin:",
        lang_dict["sub_it"],
        key=f"sub_it_{selected_lang}"
    )
    render_user_mgmt(sub_option)
