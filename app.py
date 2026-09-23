import streamlit as st

st.set_page_config(
    page_title="跨國塑膠/橡膠射出成型 AI ERP",
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
        "name": "Alex Chen (系統管理者)",
        "role": "Super Admin"
    }

if "lang" not in st.session_state:
    st.session_state.lang = "繁體中文"

# ----------------------------------------------------
# 🌐 跨國多語系字典定義 (i18n Dictionary)
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
        "sub_sales": ["📝 AI 即時報價 & CAD/3D Pipeline", "📊 歷史報價單據與資料庫"],
        "sub_finance": [
            "🛒 採購與應付帳款系統 (Procurement & AP)", 
            "📦 訂單與應收帳款系統 (Sales Orders & AR)", 
            "📄 越南電子發票 XML 解析與登錄",
            "📧 通用信箱電子發票讀取 (IMAP)",
            "📊 電子發票張數監控與加購預警",
            "🌐 全球跨國稅務 AI 智慧問答"
        ]
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
        "sub_sales": ["📝 Báo giá AI & CAD/3D Pipeline", "📊 Lịch sử báo giá & CSDL"],
        "sub_finance": [
            "🛒 Quản lý Mua hàng & Phải trả (AP)", 
            "📦 Đơn bán hàng & Phải thu (AR)", 
            "📄 Phân tích Hóa đơn điện tử XML",
            "📧 Đọc Hóa đơn qua Email (IMAP)",
            "📊 Giám sát & Báo động số lượng HĐ",
            "🌐 Tư vấn AI Thuế quốc tế"
        ]
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
        "sub_sales": ["📝 AI 实时报价 & CAD/3D Pipeline", "📊 历史报价单据与数据库"],
        "sub_finance": [
            "🛒 采购与应付账款系统 (Procurement & AP)", 
            "📦 订单与应收账款系统 (Sales Orders & AR)", 
            "📄 越南电子发票 XML 解析与登录",
            "📧 通用邮箱电子发票读取 (IMAP)",
            "📊 电子发票张数监控与加购预警",
            "🌐 全球跨国税务 AI 智慧问答"
        ]
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
            "🧾 Finance",
            "👥 HR & Administration",
            "💻 IT & System Admin"
        ],
        "sub_sales": ["📝 AI Quotation & CAD/3D Pipeline", "📊 Quotation History & DB"],
        "sub_finance": [
            "🛒 Procurement & Accounts Payable (AP)", 
            "📦 Sales Orders & Accounts Receivable (AR)", 
            "📄 Vietnam E-Invoice XML Parser",
            "📧 Fetch Invoices via Email (IMAP)",
            "📊 E-Invoice Quota Alert & Top-up",
            "🌐 Global Tax AI Assistant"
        ]
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
            "🧾 Keuangan",
            "👥 SDM & Administrasi",
            "💻 IT & Admin Sistem"
        ],
        "sub_sales": ["📝 Kutipan AI & Saluran CAD/3D", "📊 Riwayat Kutipan & Basis Data"],
        "sub_finance": [
            "🛒 Pengadaan & Hutang Dagang (AP)", 
            "📦 Pesanan Penjualan & Piutang (AR)", 
            "📄 Parser XML Faktur Elektronik",
            "📧 Ambil Faktur via Email (IMAP)",
            "📊 Peringatan Kuota Faktur & Top-up",
            "🌐 Asisten AI Pajak Global"
        ]
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
st.sidebar.markdown("### 👤 使用者狀態與權限")

if st.session_state.logged_in:
    st.sidebar.success(f"🟢 **{st.session_state.user_info['name']}**")
    st.sidebar.caption(f"🔑 帳號: `{st.session_state.user_info['username']}` | 角色: `{st.session_state.user_info['role']}`")
    if st.sidebar.button("🔒 登出系統", key="btn_global_logout"):
        st.session_state.logged_in = False
        st.rerun()
else:
    st.sidebar.warning("🔴 未登入系統")
    with st.sidebar.form("login_form_sidebar"):
        username_input = st.text_input("帳號 (Username)", value="admin")
        password_input = st.text_input("密碼 (Password)", type="password", value="123456")
        submit_login = st.form_submit_button("🚀 登入系統")
        if submit_login:
            st.session_state.logged_in = True
            st.session_state.user_info = {
                "username": username_input,
                "name": f"{username_input} (管理者)",
                "role": "Super Admin"
            }
            st.rerun()

st.sidebar.markdown("---")

if not st.session_state.logged_in:
    st.title("🔒 跨國塑膠/橡膠射出成型 AI ERP 系統")
    st.warning("⚠️ 請先於左側邊欄輸入帳號密碼進行登入，以存取各部門管理模組與權限功能。")
    st.stop()

# ----------------------------------------------------
# 側邊欄 2：語系切換器與動態語系部門選單
# ----------------------------------------------------
selected_lang = st.sidebar.selectbox(
    "🌐 系統語系 (Language):",
    ["繁體中文", "Tiếng Việt", "简体中文", "English", "Bahasa Indonesia"],
    key="fixed_lang_selector_key"
)
st.session_state.lang = selected_lang
lang_dict = I18N[selected_lang]
st.sidebar.markdown("---")

# 動態選單：根據當前 selected_lang 載入對應語言列表
dept_options = lang_dict["depts"]
selected_dept = st.sidebar.radio(
    lang_dict["dept_select"],
    options=dept_options,
    key=f"sidebar_dept_radio_{selected_lang}"
)
st.sidebar.markdown("---")

# 獲取選中的部門索引 (0 到 6)，確保模組判斷不受語系切換影響
dept_idx = dept_options.index(selected_dept)

# ----------------------------------------------------
# 頁面路由與動態語系子選單
# ----------------------------------------------------
if dept_idx == 0:  # 營運戰情室
    sub_option = st.sidebar.radio(
        "Market:",
        ["🌐 All Markets", "🇹🇼 Taiwan", "🇨🇳 China/HK", "🇺🇸 USA", "🇻🇳 Vietnam", "🛢️ Commodities/FX"],
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
        ["📦 Assets & Mold Mgmt", "🛠️ Mold Trial & DFM"],
        key=f"sub_rd_{selected_lang}"
    )
    render_asset(sub_option)

elif dept_idx == 3:  # 廠務/設備
    sub_option = st.sidebar.radio(
        "Plant & IoT:",
        ["📡 IoT Machine Monitor", "⚡ Plant OEE KPI", "🔧 Maintenance & Alerts"],
        key=f"sub_plant_{selected_lang}"
    )
    render_erp_db(sub_option)

elif dept_idx == 4:  # 財務
    sub_option = st.sidebar.radio(
        "Finance:",
        lang_dict["sub_finance"],
        key=f"sub_finance_{selected_lang}"
    )
    
    if "Tax" in sub_option or "Thuế" in sub_option or "税务" in sub_option or "Pajak" in sub_option:
        render_tax_ai(sub_option)
    elif "Procurement" in sub_option or "Mua hàng" in sub_option or "采购" in sub_option or "Pengadaan" in sub_option:
        st.title("🛒 Procurement & AP System")
        st.info("Phân hệ Quản lý Mua hàng & Phải trả (AP) đang được khởi tạo...")
    elif "Sales Orders" in sub_option or "Đơn bán hàng" in sub_option or "订单" in sub_option or "Pesanan" in sub_option:
        st.title("📦 Sales Orders & AR System")
        st.info("Phân hệ Đơn bán hàng & Phải thu (AR) đang được khởi tạo...")
    else:
        render_invoice(sub_option)

elif dept_idx == 5:  # 人事/行政
    sub_option = st.sidebar.radio(
        "HR:",
        ["💰 Payroll & Attendance", "⏰ Clock-in Integration"],
        key=f"sub_hr_{selected_lang}"
    )
    render_payroll(sub_option)

elif dept_idx == 6:  # 資訊/IT
    sub_option = st.sidebar.radio(
        "IT Admin:",
        ["🏢 Multi-site Mgmt", "👥 User Auth", "🔒 RBAC Matrix"],
        key=f"sub_it_{selected_lang}"
    )
    render_user_mgmt(sub_option)
