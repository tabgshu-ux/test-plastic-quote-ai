import streamlit as st
import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, Column, String, Float, Boolean, Date, DateTime, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker

# ==========================================
# 頁面基礎設定 (Streamlit Page Config)
# ==========================================
st.set_page_config(
    page_title="裕豐電機工業 REETECH INDUSTRIAL - AI ERP",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# 1. 多國語言字典 (i18n) - 包含左側所有部門選單
# ==========================================
i18n = {
    "繁體中文": {
        "company_name": "⚡ 裕豐電機工業",
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ 裕豐電機工業 REETECH INDUSTRIAL - 系統登入",
        "username": "帳號",
        "password": "密碼",
        "login_btn": "🔑 登入系統",
        "logout_btn": "🚪 登出系統",
        "lang_selector": "🌐 語言設定 / Language",
        "menu_header": "公司組織部門選單",
        "menu_exec": "👑 董事長/總經理 - 營運戰情看板",
        "menu_fin": "🏢 管理部 - 財務會計 (TT200/多幣別/UNC)",
        "menu_hr": "👥 管理部 - 人事與行政管理",
        "menu_ga": "📦 管理部 - 總務與資產管理",
        "menu_sheet_metal": "✂️ 生產部 - 板金加工組",
        "menu_painting": "🎨 生產部 - 烤漆塗裝組",
        "menu_assembly": "⚡ 生產部 - 配電盤組裝與配線組",
        "menu_warehouse": "🏭 生產部 - 倉庫與資材管理",
        "menu_approval": "✍️ 電子簽核與請款流程"
    },
    "English": {
        "company_name": "⚡ REETECH INDUSTRIAL",
        "company_sub": "REETECH INDUSTRIAL Co., Ltd.",
        "login_title": "⚡ REETECH INDUSTRIAL - System Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "🔑 Login",
        "logout_btn": "🚪 Logout",
        "lang_selector": "🌐 Select Language",
        "menu_header": "Department Menu",
        "menu_exec": "👑 Executive Dashboard (Chairman/GM)",
        "menu_fin": "🏢 Admin - Finance & Accounting (TT200/UNC)",
        "menu_hr": "👥 Admin - HR & Administration",
        "menu_ga": "📦 Admin - General Affairs & Assets",
        "menu_sheet_metal": "✂️️ Production - Sheet Metal Dept",
        "menu_painting": "🎨 Production - Powder Coating Dept",
        "menu_assembly": "⚡ Production - Assembly & Wiring Dept",
        "menu_warehouse": "🏭 Production - Warehouse & Materials",
        "menu_approval": "✍️ E-Approval Workflow"
    },
    "Tiếng Việt": {
        "company_name": "⚡ REETECH INDUSTRIAL",
        "company_sub": "Công ty TNHH REETECH INDUSTRIAL",
        "login_title": "⚡ REETECH INDUSTRIAL - Đăng nhập hệ thống",
        "username": "Tài khoản",
        "password": "Mật khẩu",
        "login_btn": "🔑 Đăng nhập",
        "logout_btn": "🚪 Đăng xuất",
        "lang_selector": "🌐 Chọn ngôn ngữ",
        "menu_header": "Danh mục Phòng ban",
        "menu_exec": "👑 Báo cáo Ban Giám đốc (Chủ tịch/GM)",
        "menu_fin": "🏢 Khối Quản lý - Tài chính Kế toán (TT200)",
        "menu_hr": "👥 Khối Quản lý - Nhân sự & Hành chính",
        "menu_ga": "📦 Khối Quản lý - Quản trị Tải sản",
        "menu_sheet_metal": "✂️ Khối Sản xuất - Tổ Gia công Cơ khí",
        "menu_painting": "🎨 Khối Sản xuất - Tổ Sơn tĩnh điện",
        "menu_assembly": "⚡ Khối Sản xuất - Tổ Lắp ráp Tủ điện",
        "menu_warehouse": "🏭 Khối Sản xuất - Quản lý Kho vật tư",
        "menu_approval": "✍️ Hệ thống Phê duyệt Điện tử"
    }
}

# 語系自動偵測 (支援 URL 與瀏覽器首選語系)
def auto_detect_language():
    query_params = st.query_params
    if "lang" in query_params:
        lang_code = query_params["lang"].lower()
        if "en" in lang_code:
            return "English"
        elif "vi" in lang_code:
            return "Tiếng Việt"
        elif "zh" in lang_code:
            return "繁體中文"
            
    try:
        headers = st.context.headers
        accept_lang = headers.get("Accept-Language", "").lower()
        if "en" in accept_lang:
            return "English"
        elif "vi" in accept_lang:
            return "Tiếng Việt"
        elif "zh" in accept_lang:
            return "繁體中文"
    except Exception:
        pass
    return "English"  # 若偵測不到則預設為英文 (針對跨國外商電腦)

if "current_lang" not in st.session_state:
    st.session_state.current_lang = auto_detect_language()

# ==========================================
# 2. Supabase 雲端資料庫快取 (防止卡頓與反白)
# ==========================================
DB_URL = "postgresql+psycopg2://postgres.wvsqbefyeykmueffcbwd:Reetech2026@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"

# 使用 cache_resource 將資料庫連線鎖定快取
@st.cache_resource
def get_db_engine():
    return create_engine(DB_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)

Base = declarative_base()

EXCHANGE_RATES = {"USD": 1.0, "VND": 25400.0, "TWD": 32.0, "CNY": 7.23}

def convert_to_usd(amount, currency):
    rate = EXCHANGE_RATES.get(currency, 1.0)
    return amount / rate if rate > 0 else amount

# ---------------- 資料庫 ORM 模型 ----------------
class UserDB(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    full_name = Column(String)

class ApprovalDB(Base):
    __tablename__ = 'approval_workflows'
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    applicant = Column(String, nullable=False)
    amount = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    status = Column(String, default="待簽核")
    created_at = Column(DateTime, default=datetime.datetime.now)

class InventoryDB(Base):
    __tablename__ = 'inventory'
    item_code = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)
    quantity = Column(Float, default=0.0)
    unit = Column(String)
    unit_cost = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    safety_stock = Column(Float, default=0.0)

class InvoiceDB(Base):
    __tablename__ = 'invoices'
    invoice_id = Column(String, primary_key=True)
    entity_name = Column(String, nullable=False)          
    account_code = Column(String, default="3311")          
    category_type = Column(String, default="資材採購")    
    project_name = Column(String, default="")              
    project_period = Column(String, default="")            
    quoted_amount = Column(Float, default=0.0)             
    quoter_name = Column(String, default="")               
    payment_terms = Column(String, default="")             
    uncollected_reason = Column(Text, default="")          
    contract_file_name = Column(String, default="")        
    amount = Column(Float, default=0.0)                    
    currency = Column(String, default="USD")               
    amount_usd = Column(Float, default=0.0)                
    due_date = Column(Date, nullable=False)
    is_paid = Column(Boolean, default=False)               
    invoice_type = Column(String, default="AR")            
    bank_name = Column(String, default="")                 
    bank_transfer_ref = Column(String, default="")         
    payment_date = Column(Date, nullable=True)             

class ProductionTaskDB(Base):
    __tablename__ = 'production_tasks'
    task_id = Column(String, primary_key=True)
    dept_name = Column(String, nullable=False)             
    project_name = Column(String, nullable=False)          
    drawing_no = Column(String, default="")                
    qty = Column(Float, default=1.0)                       
    operator = Column(String, default="")                  
    status = Column(String, default="生產中")               
    due_date = Column(Date, nullable=False)

class ProjectDB(Base):
    __tablename__ = 'projects'
    project_id = Column(String, primary_key=True)
    project_name = Column(String, nullable=False)
    budget = Column(Float, default=0.0)
    actual_material_cost = Column(Float, default=0.0)
    actual_labor_cost = Column(Float, default=0.0)
    actual_overhead = Column(Float, default=0.0)

# 使用快取避開每次的結構檢查
@st.cache_resource
def init_db_structure():
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    with engine.connect() as conn:
        alter_queries = [
            "ALTER TABLE approval_workflows ADD COLUMN IF NOT EXISTS currency VARCHAR DEFAULT 'USD';",
            "ALTER TABLE inventory ADD COLUMN IF NOT EXISTS currency VARCHAR DEFAULT 'USD';",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS currency VARCHAR DEFAULT 'USD';",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS amount_usd FLOAT DEFAULT 0.0;",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS account_code VARCHAR DEFAULT '3311';",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS category_type VARCHAR DEFAULT '資材採購';",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS project_name VARCHAR DEFAULT '';",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS project_period VARCHAR DEFAULT '';",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS quoted_amount FLOAT DEFAULT 0.0;",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS quoter_name VARCHAR DEFAULT '';",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_terms VARCHAR DEFAULT '';",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS uncollected_reason TEXT DEFAULT '';",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS contract_file_name VARCHAR DEFAULT '';",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS bank_name VARCHAR DEFAULT '';",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS bank_transfer_ref VARCHAR DEFAULT '';",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_date DATE NULL;"
        ]
        for q in alter_queries:
            conn.execute(text(q))
        conn.commit()
    return True

init_db_structure()

# ==========================================
# 3. 登入管理
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_name = ""

def login_page():
    t = i18n[st.session_state.current_lang]
    st.title(t["login_title"])
    st.caption(t["company_sub"])
    st.markdown("---")
    
    col1, _ = st.columns([1, 2])
    with col1:
        username = st.text_input(f"{t['username']} (admin / manager / staff)")
        password = st.text_input(f"{t['password']} (123)", type="password")
        if st.button(t["login_btn"], use_container_width=True):
            engine = get_db_engine()
            Session = sessionmaker(bind=engine)
            session = Session()
            user = session.query(UserDB).filter_by(username=username, password=password).first()
            if user:
                st.session_state.logged_in = True
                st.session_state.user_role = user.role
                st.session_state.user_name = user.full_name
                st.rerun()
            else:
                st.error("帳號或密碼錯誤 / Incorrect login / Sai tài khoản")
            session.close()

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ==========================================
# 4. 側邊欄與動態三語系選單
# ==========================================
t = i18n[st.session_state.current_lang]

st.sidebar.title(t["company_name"])
st.sidebar.caption(t["company_sub"])

lang_list = ["English", "繁體中文", "Tiếng Việt"]
selected_lang = st.sidebar.selectbox(
    t["lang_selector"],
    lang_list,
    index=lang_list.index(st.session_state.current_lang)
)

if selected_lang != st.session_state.current_lang:
    st.session_state.current_lang = selected_lang
    st.rerun()

st.sidebar.markdown(f"**👤 {st.session_state.user_name}** ({st.session_state.user_role.upper()})")
if st.sidebar.button(t["logout_btn"]):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

# 動態依據語系建立選單對照
menu_mapping = {}
if st.session_state.user_role == "admin":
    menu_mapping[t["menu_exec"]] = "exec"

menu_mapping[t["menu_fin"]] = "fin"
menu_mapping[t["menu_hr"]] = "hr"
menu_mapping[t["menu_ga"]] = "ga"
menu_mapping[t["menu_sheet_metal"]] = "sheet_metal"
menu_mapping[t["menu_painting"]] = "painting"
menu_mapping[t["menu_assembly"]] = "assembly"
menu_mapping[t["menu_warehouse"]] = "warehouse"
menu_mapping[t["menu_approval"]] = "approval"

selected_menu_label = st.sidebar.radio(t["menu_header"], list(menu_mapping.keys()))
menu_choice = menu_mapping[selected_menu_label]

# ==========================================
# 5. 模組渲染邏輯
# ==========================================

def format_currency_display(amount, curr):
    if curr == "VND":
        return f"₫ {amount:,.0f} VND"
    elif curr == "USD":
        return f"$ {amount:,.2f} USD"
    elif curr == "TWD":
        return f"NT$ {amount:,.0f} TWD"
    elif curr == "CNY":
        return f"¥ {amount:,.2f} CNY"
    return f"{amount:,.2f} {curr}"

# 1. 董事長 / 總經理 戰情
def render_exec_dashboard():
    st.title(t["menu_exec"])
    engine = get_db_engine()
    df_invc = pd.read_sql("SELECT * FROM invoices", engine)
    df_prj = pd.read_sql("SELECT * FROM projects", engine)

    total_ar = df_invc[df_invc['invoice_type'] == 'AR']['amount_usd'].sum() if 'amount_usd' in df_invc.columns else 0.0
    total_ap = df_invc[df_invc['invoice_type'] == 'AP']['amount_usd'].sum() if 'amount_usd' in df_invc.columns else 0.0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total AR (應收折合 USD)", f"USD ${total_ar:,.2f}")
    c2.metric("Total AP (應付折合 USD)", f"USD ${total_ap:,.2f}")
    c3.metric("Active Projects (工程數)", f"{len(df_prj)}")
    
    st.markdown("---")
    st.subheader("🏗️ Project Profitability & Cost Control")
    st.dataframe(df_prj, use_container_width=True)

# 2. 財務模組
def render_finance_module():
    st.title(t["menu_fin"])
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    tab_ar, tab_ap, tab_pay, tab_add = st.tabs([
        "📋 TK 131 Accounts Receivable (AR)", 
        "💳 TK 331 Accounts Payable (AP)", 
        "🏦 Bank Transfer (UNC)",
        "➕ New Invoice Entry"
    ])

    with tab_ar:
        ar_invoices = session.query(InvoiceDB).filter_by(invoice_type="AR").all()
        df_ar = pd.DataFrame([{
            "ID": i.invoice_id,
            "Account": i.account_code or "1311",
            "Customer": i.entity_name,
            "Project": i.project_name or "-",
            "Currency": i.currency or "USD",
            "Amount": format_currency_display(i.amount or 0.0, i.currency or "USD"),
            "USD Equivalent": f"${(i.amount_usd or convert_to_usd(i.amount, i.currency)):,.2f}",
            "Status": "Paid" if i.is_paid else "Pending"
        } for i in ar_invoices])
        st.dataframe(df_ar, use_container_width=True)

    with tab_ap:
        ap_invoices = session.query(InvoiceDB).filter_by(invoice_type="AP").all()
        df_ap = pd.DataFrame([{
            "ID": i.invoice_id,
            "Account": i.account_code or "3311",
            "Supplier": i.entity_name,
            "Item/Spec": i.project_name or "-",
            "Currency": i.currency or "USD",
            "Amount": format_currency_display(i.amount or 0.0, i.currency or "USD"),
            "USD Equivalent": f"${(i.amount_usd or convert_to_usd(i.amount, i.currency)):,.2f}",
            "Status": "Paid" if i.is_paid else "Pending"
        } for i in ap_invoices])
        st.dataframe(df_ap, use_container_width=True)

    with tab_pay:
        st.subheader("🏦 Bank Payment Voucher (Ủy Nhiệm Chi - UNC)")
        ap_unpaid = session.query(InvoiceDB).filter_by(invoice_type="AP", is_paid=False).all()
        ap_options = {f"{i.invoice_id} - {i.entity_name} ({format_currency_display(i.amount, i.currency)})": i.invoice_id for i in ap_unpaid}

        if ap_options:
            selected_ap_label = st.selectbox("Select Invoice to Pay", list(ap_options.keys()))
            target_ap_id = ap_options[selected_ap_label]
            target_ap = session.query(InvoiceDB).filter_by(invoice_id=target_ap_id).first()

            with st.form("bank_pay_form"):
                bank_name = st.selectbox("Bank", ["Vietcombank (VCB)", "BIDV", "MB Bank", "First Bank", "Mega Bank"])
                bank_transfer_ref = st.text_input("UNC Ref Number *")
                payment_date = st.date_input("Transfer Date", datetime.date.today())
                if st.form_submit_button("Save UNC Record"):
                    if bank_transfer_ref:
                        target_ap.is_paid = True
                        target_ap.bank_name = bank_name
                        target_ap.bank_transfer_ref = bank_transfer_ref
                        target_ap.payment_date = payment_date
                        session.commit()
                        st.success("UNC Saved!")
                        st.rerun()
        else:
            st.info("All AP invoices are paid!")

    with tab_add:
        st.subheader("➕ Add New Invoice")
        with st.form("add_invoice_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                inv_type = st.selectbox("Type", ["AR - Accounts Receivable", "AP - Accounts Payable"])
                entity_name = st.text_input("Customer / Supplier Name *")
                project_name = st.text_input("Project / Item Name *")
            with col_b:
                currency = st.selectbox("Currency *", ["VND", "USD", "TWD", "CNY"])
                amount = st.number_input("Amount *", min_value=0.0)
                due_date = st.date_input("Due Date", datetime.date.today() + datetime.timedelta(days=30))

            if st.form_submit_button("Save Invoice"):
                if entity_name and project_name:
                    type_code = "AR" if "AR" in inv_type else "AP"
                    new_inv_id = f"{type_code}-2026-{datetime.datetime.now().strftime('%m%d%H%M')}"
                    calc_usd = convert_to_usd(amount, currency)
                    new_inv = InvoiceDB(invoice_id=new_inv_id, entity_name=entity_name, project_name=project_name, amount=amount, currency=currency, amount_usd=calc_usd, due_date=due_date, invoice_type=type_code)
                    session.add(new_inv)
                    session.commit()
                    st.success("Saved successfully!")
                    st.rerun()

    session.close()

# 3. 生產線模组
def render_production_module(dept_title, dept_key):
    st.title(dept_title)
    engine = get_db_engine()
    df_task = pd.read_sql(f"SELECT * FROM production_tasks WHERE dept_name='{dept_key}'", engine)
    st.dataframe(df_task, use_container_width=True)

# 路由選擇
if menu_choice == "exec":
    render_exec_dashboard()
elif menu_choice == "fin":
    render_finance_module()
elif menu_choice == "hr":
    st.title(t["menu_hr"])
    st.info("HR Management & Vietnamese Labor Contracts.")
elif menu_choice == "ga":
    st.title(t["menu_ga"])
    st.info("General Affairs & Asset Management.")
elif menu_choice == "sheet_metal":
    render_production_module(t["menu_sheet_metal"], "板金加工組")
elif menu_choice == "painting":
    render_production_module(t["menu_painting"], "烤漆塗裝組")
elif menu_choice == "assembly":
    render_production_module(t["menu_assembly"], "配電盤組裝與配線組")
elif menu_choice == "warehouse":
    st.title(t["menu_warehouse"])
    st.dataframe(pd.read_sql("SELECT * FROM inventory", get_db_engine()), use_container_width=True)
elif menu_choice == "approval":
    st.title(t["menu_approval"])
    st.dataframe(pd.read_sql("SELECT * FROM approval_workflows", get_db_engine()), use_container_width=True)
