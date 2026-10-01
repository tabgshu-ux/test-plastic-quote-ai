import streamlit as st
import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, Column, String, Float, Boolean, Date, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# ==========================================
# 頁面基礎設定 (Streamlit Page Config)
# ==========================================
st.set_page_config(
    page_title="裕豐電機 REETECH INDUSTRIAL - AI ERP 系統",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# 1. 瀏覽器與系統語系自動偵測 (Auto Language Detection)
# ==========================================
def detect_user_language():
    try:
        # 從 Streamlit request headers 讀取瀏覽器 Accept-Language
        headers = st.context.headers
        accept_lang = headers.get("Accept-Language", "").lower()
        if "zh" in accept_lang:
            return "繁體中文"
        elif "vi" in accept_lang:
            return "Tiếng Việt"
        else:
            return "English"
    except Exception:
        return "繁體中文"

if "current_lang" not in st.session_state:
    st.session_state.current_lang = detect_user_language()

# ==========================================
# 2. Supabase 雲端資料庫連線設定
# ==========================================
DB_URL = "postgresql+psycopg2://postgres:Reetech2026@db.wvsqbefyeykmueffcbwd.supabase.co:5432/postgres"

@st.cache_resource
def get_db_engine():
    return create_engine(DB_URL, pool_pre_ping=True)

Base = declarative_base()

# ---------------- 資料庫 ORM 模型 ----------------
class UserDB(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False) # 'admin', 'manager', 'staff'
    full_name = Column(String)

class ApprovalDB(Base):
    __tablename__ = 'approval_workflows'
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    applicant = Column(String, nullable=False)
    amount = Column(Float, default=0.0)
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
    safety_stock = Column(Float, default=0.0)

class InvoiceDB(Base):
    __tablename__ = 'invoices'
    invoice_id = Column(String, primary_key=True)
    entity_name = Column(String, nullable=False)
    amount = Column(Float, default=0.0)
    due_date = Column(Date, nullable=False)
    is_paid = Column(Boolean, default=False)
    invoice_type = Column(String, default="AR")

class ProjectDB(Base):
    __tablename__ = 'projects'
    project_id = Column(String, primary_key=True)
    project_name = Column(String, nullable=False)
    budget = Column(Float, default=0.0)
    actual_material_cost = Column(Float, default=0.0)
    actual_labor_cost = Column(Float, default=0.0)
    actual_overhead = Column(Float, default=0.0)

# 初始化雲端資料庫
def init_db_data():
    try:
        engine = get_db_engine()
        Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine)
        session = Session()
        today = datetime.date.today()
        
        if not session.query(UserDB).first():
            session.add_all([
                UserDB(username="admin", password="123", role="admin", full_name="老闆 / 總經理"),
                UserDB(username="manager", password="123", role="manager", full_name="工程部主管"),
                UserDB(username="staff", password="123", role="staff", full_name="廠務採購員")
            ])

        if not session.query(ApprovalDB).first():
            session.add_all([
                ApprovalDB(id="APPR-2026-001", title="西寧專案 銅排採購請款單", applicant="廠務採購員", amount=12500.0, status="待簽核"),
                ApprovalDB(id="APPR-2026-002", title="平陽高壓櫃 施耐德斷路器請款", applicant="工程部主管", amount=8400.0, status="已核准")
            ])
            
        if not session.query(InventoryDB).first():
            session.add_all([
                InventoryDB(item_code="CU-BUS-001", name="高純度銅排 10x100mm", category="銅材", quantity=1500, unit="kg", unit_cost=12.5, safety_stock=2000),
                InventoryDB(item_code="CB-MCCB-100A", name="塑殼斷路器 100A", category="開關元件", quantity=350, unit="pcs", unit_cost=45.0, safety_stock=100)
            ])
            
        if not session.query(InvoiceDB).first():
            session.add_all([
                InvoiceDB(invoice_id="INV-2026-001", entity_name="越南樟榜工業區A廠", amount=150000.0, due_date=today + datetime.timedelta(days=15), is_paid=False, invoice_type="AR"),
                InvoiceDB(invoice_id="AP-2026-888", entity_name="施耐德電氣越南分公司", amount=45000.0, due_date=today + datetime.timedelta(days=10), is_paid=False, invoice_type="AP")
            ])
            
        if not session.query(ProjectDB).first():
            session.add_all([
                ProjectDB(project_id="PRJ-TAYNINH-01", project_name="西寧紡織廠配電盤工程", budget=250000.0, actual_material_cost=120000.0, actual_labor_cost=45000.0, actual_overhead=15000.0)
            ])
            
        session.commit()
        session.close()
        return True
    except Exception as e:
        st.error(f"⚠️ 雲端資料庫連線失敗：{e}")
        return False

db_connected = init_db_data()

# ==========================================
# 3. 多國語言字典 (i18n)
# ==========================================
i18n = {
    "繁體中文": {
        "title": "⚡ 裕豐電機 AI ERP",
        "login_title": "⚡ 裕豐電機 - 系統登入",
        "username": "帳號",
        "password": "密碼",
        "login_btn": "🔑 登入系統",
        "logout_btn": "🚪 登出系統",
        "menu_exec": "📊 老闆營運決策看板",
        "menu_approval": "✍️ 電子請款與簽核系統",
        "menu_finance": "💰 財務與應收/應付帳款",
        "menu_warehouse": "📦 倉庫資材管理",
        "company_sub": "REETECH INDUSTRIAL"
    },
    "Tiếng Việt": {
        "title": "⚡ REETECH INDUSTRIAL AI ERP",
        "login_title": "⚡ REETECH INDUSTRIAL - Đăng nhập",
        "username": "Tài khoản",
        "password": "Mật khẩu",
        "login_btn": "🔑 Đăng nhập",
        "logout_btn": "🚪 Đăng xuất",
        "menu_exec": "📊 Báo cáo Giám đốc",
        "menu_approval": "✍️ Hệ thống Phê duyệt",
        "menu_finance": "💰 Tài chính & Công nợ (AR/AP)",
        "menu_warehouse": "📦 Quản lý Kho vật tư",
        "company_sub": "REETECH INDUSTRIAL"
    },
    "English": {
        "title": "⚡ REETECH INDUSTRIAL AI ERP",
        "login_title": "⚡ REETECH INDUSTRIAL - Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "🔑 Login",
        "logout_btn": "🚪 Logout",
        "menu_exec": "📊 Executive Dashboard",
        "menu_approval": "✍️ Approval Workflow",
        "menu_finance": "💰 Finance & AR/AP",
        "menu_warehouse": "📦 Warehouse & Inventory",
        "company_sub": "REETECH INDUSTRIAL"
    }
}

# ==========================================
# 4. 登入管理
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_name = ""

def login_page():
    t = i18n[st.session_state.current_lang]
    st.title(t["login_title"])
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
                st.error("帳號或密碼錯誤 / Incorrect login")
            session.close()

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ==========================================
# 5. 側邊欄與選單
# ==========================================
st.sidebar.title("⚡ 裕豐電機 AI ERP")
st.sidebar.caption("REETECH INDUSTRIAL")

# 語系切換 (自動選擇預設語系，並支援手動切換)
lang_list = ["繁體中文", "Tiếng Việt", "English"]
selected_lang = st.sidebar.selectbox(
    "🌐 語言設定 / Language / Ngôn ngữ",
    lang_list,
    index=lang_list.index(st.session_state.current_lang)
)
st.session_state.current_lang = selected_lang
t = i18n[selected_lang]

st.sidebar.markdown(f"**👤 {st.session_state.user_name}** ({st.session_state.user_role.upper()})")
if st.sidebar.button(t["logout_btn"]):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

menu_options = []
if st.session_state.user_role == "admin":
    menu_options.append(t["menu_exec"])

menu_options.extend([
    t["menu_approval"],
    t["menu_finance"],
    t["menu_warehouse"]
])

menu_choice = st.sidebar.radio("Menu", menu_options)

# ==========================================
# 6. 模組渲染邏輯
# ==========================================
def render_approval_module():
    st.title(t["menu_approval"])
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    approvals = session.query(ApprovalDB).all()
    df_appr = pd.DataFrame([{
        "ID": a.id, "Title": a.title, "Applicant": a.applicant, 
        "Amount (USD)": a.amount, "Status": a.status, "Date": a.created_at
    } for a in approvals])
    st.dataframe(df_appr, use_container_width=True)

def render_exec_dashboard():
    st.title(t["menu_exec"])
    engine = get_db_engine()
    df_invc = pd.read_sql("SELECT * FROM invoices", engine)
    df_prj = pd.read_sql("SELECT * FROM projects", engine)

    total_ar = df_invc[df_invc['invoice_type'] == 'AR']['amount'].sum()
    total_ap = df_invc[df_invc['invoice_type'] == 'AP']['amount'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("AR (應收帳款)", f"USD ${total_ar:,.2f}")
    c2.metric("AP (應付帳款)", f"USD ${total_ap:,.2f}")
    c3.metric("Projects (工程數)", f"{len(df_prj)}")
    
    st.markdown("---")
    st.subheader("🏗️ 配電盤工程項目監控 / Project Monitoring")
    st.dataframe(df_prj, use_container_width=True)

if menu_choice == t.get("menu_exec"):
    render_exec_dashboard()
elif menu_choice == t["menu_approval"]:
    render_approval_module()
elif menu_choice == t["menu_finance"]:
    st.title(t["menu_finance"])
    st.dataframe(pd.read_sql("SELECT * FROM invoices", get_db_engine()), use_container_width=True)
elif menu_choice == t["menu_warehouse"]:
    st.title(t["menu_warehouse"])
    st.dataframe(pd.read_sql("SELECT * FROM inventory", get_db_engine()), use_container_width=True)
