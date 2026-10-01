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
    page_title="裕豐電機 REETECH INDUSTRIAL - AI ERP 系統",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# 1. 強制清除快取機制
# ==========================================
st.sidebar.markdown("### ⚙️ 系統快取維護")
if st.sidebar.button("🧹 清除舊連線快取 (Clear Cache)"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.sidebar.success("快取已重置！系統重新連線中...")
    st.rerun()

# ==========================================
# 2. 瀏覽器與系統語系自動偵測 (Auto Language Detection)
# ==========================================
def detect_user_language():
    try:
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
# 3. Supabase 雲端資料庫連線設定
# ==========================================
# ⚠️ 請將 Reetech2026 替換為您在 Supabase 設定的新密碼
DB_URL = "postgresql+psycopg2://postgres.wvsqbefyeykmueffcbwd:Reetech2026@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"

def get_db_engine():
    return create_engine(DB_URL, pool_pre_ping=True)

Base = declarative_base()

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
    entity_name = Column(String, nullable=False)          # 客戶/廠商名稱
    project_name = Column(String, default="")              # 工程名稱
    project_period = Column(String, default="")            # 工程時間
    quoted_amount = Column(Float, default=0.0)             # 工程報價
    quoter_name = Column(String, default="")               # 報價人姓名
    payment_terms = Column(String, default="")             # 收款條件
    uncollected_reason = Column(Text, default="")          # 未能收款的原因
    amount = Column(Float, default=0.0)                    # 當期應收金額
    due_date = Column(Date, nullable=False)
    is_paid = Column(Boolean, default=False)               # 是否已收款
    invoice_type = Column(String, default="AR")            # AR 或 AP

class ProjectDB(Base):
    __tablename__ = 'projects'
    project_id = Column(String, primary_key=True)
    project_name = Column(String, nullable=False)
    budget = Column(Float, default=0.0)
    actual_material_cost = Column(Float, default=0.0)
    actual_labor_cost = Column(Float, default=0.0)
    actual_overhead = Column(Float, default=0.0)

# 初始化雲端資料庫並自動自動補齊缺失欄位
def init_db_data():
    try:
        engine = get_db_engine()
        Base.metadata.create_all(engine)
        
        # 自動補充舊資料表缺少的欄位 (Migration Helper)
        with engine.connect() as conn:
            alter_queries = [
                "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS project_name VARCHAR DEFAULT '';",
                "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS project_period VARCHAR DEFAULT '';",
                "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS quoted_amount FLOAT DEFAULT 0.0;",
                "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS quoter_name VARCHAR DEFAULT '';",
                "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_terms VARCHAR DEFAULT '';",
                "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS uncollected_reason TEXT DEFAULT '';"
            ]
            for q in alter_queries:
                conn.execute(text(q))
            conn.commit()

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
                InvoiceDB(
                    invoice_id="INV-2026-001",
                    entity_name="越南樟榜工業區 A 廠",
                    project_name="西寧紡織廠配電盤新建工程",
                    project_period="2026/01 - 2026/05",
                    quoted_amount=250000.0,
                    quoter_name="張經理 (工程部)",
                    payment_terms="30% 訂金 / 60% 進場 / 10% 驗收",
                    uncollected_reason="客戶建廠進度延遲，等待第二期驗收文件簽核中",
                    amount=150000.0,
                    due_date=today + datetime.timedelta(days=15),
                    is_paid=False,
                    invoice_type="AR"
                ),
                InvoiceDB(
                    invoice_id="INV-2026-002",
                    entity_name="平陽神浪工業區 B 廠",
                    project_name="高壓變壓器櫃擴建工程",
                    project_period="2026/02 - 2026/04",
                    quoted_amount=88000.0,
                    quoter_name="陳工程師",
                    payment_terms="50% 訂金 / 50% 完工",
                    uncollected_reason="業主財務審核發票中，預計下週撥款",
                    amount=44000.0,
                    due_date=today + datetime.timedelta(days=5),
                    is_paid=False,
                    invoice_type="AR"
                ),
                InvoiceDB(
                    invoice_id="AP-2026-888",
                    entity_name="施耐德電氣越南分公司",
                    project_name="資材採購 - 高壓斷路器批次進貨",
                    project_period="2026/03",
                    quoted_amount=45000.0,
                    quoter_name="李採購",
                    payment_terms="月結 30 天",
                    uncollected_reason="-",
                    amount=45000.0,
                    due_date=today + datetime.timedelta(days=10),
                    is_paid=False,
                    invoice_type="AP"
                )
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
# 4. 多國語言字典 (i18n)
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
        "menu_approval": "✍️️ Hệ thống Phê duyệt",
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
# 5. 登入管理
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
# 6. 側邊欄與選單
# ==========================================
st.sidebar.title("⚡ 裕豐電機 AI ERP")
st.sidebar.caption("REETECH INDUSTRIAL")

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
# 7. 模組渲染邏輯
# ==========================================
def render_finance_module():
    st.title("💰 財務 – 應收 (AR) 與 應付 (AP) 帳款管理")
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    tab_ar, tab_ap, tab_edit = st.tabs(["📋 應收帳款 (AR) 監控", "💳 應付帳款 (AP) 明細", "✏️ 填寫 / 更新未收款原因"])

    with tab_ar:
        ar_invoices = session.query(InvoiceDB).filter_by(invoice_type="AR").all()
        total_quoted = sum(i.quoted_amount or 0.0 for i in ar_invoices)
        total_unpaid = sum(i.amount or 0.0 for i in ar_invoices if not i.is_paid)
        
        c1, c2 = st.columns(2)
        c1.metric("工程報價總額 (USD)", f"${total_quoted:,.2f}")
        c2.metric("未收應收帳款餘額 (USD)", f"${total_unpaid:,.2f}", delta="-待收金額")
        
        st.markdown("---")
        st.subheader("📑 工程應收帳款明細表")
        
        df_ar = pd.DataFrame([{
            "發票/單號": i.invoice_id,
            "客戶名稱": i.entity_name,
            "工程名稱": i.project_name or "-",
            "工程時間": i.project_period or "-",
            "工程報價 (USD)": i.quoted_amount or 0.0,
            "當期應收 (USD)": i.amount or 0.0,
            "報價人姓名": i.quoter_name or "-",
            "收款條件": i.payment_terms or "-",
            "到期日": i.due_date,
            "狀態": "已收款" if i.is_paid else "⏳ 未收款",
            "未能收款的原因 (備註)": i.uncollected_reason or "-"
        } for i in ar_invoices])

        st.dataframe(df_ar, use_container_width=True)

    with tab_ap:
        ap_invoices = session.query(InvoiceDB).filter_by(invoice_type="AP").all()
        df_ap = pd.DataFrame([{
            "請款單號": i.invoice_id,
            "供應商名稱": i.entity_name,
            "採購項目": i.project_name or "-",
            "應付金額 (USD)": i.amount or 0.0,
            "付款條件": i.payment_terms or "-",
            "到期日": i.due_date,
            "狀態": "已付款" if i.is_paid else "⏳ 待付款"
        } for i in ap_invoices])
        st.dataframe(df_ap, use_container_width=True)

    with tab_edit:
        st.subheader("✍️ 填寫與維護應收帳款未收款原因")
        ar_pending = session.query(InvoiceDB).filter_by(invoice_type="AR").all()
        pending_options = {f"{i.invoice_id} - {i.entity_name} ({i.project_name or '無工程名'})": i.invoice_id for i in ar_pending}
        
        if pending_options:
            selected_label = st.selectbox("選擇工程應收單號", list(pending_options.keys()))
            target_id = pending_options[selected_label]
            target_inv = session.query(InvoiceDB).filter_by(invoice_id=target_id).first()
            
            st.info(f"**當前工程：** {target_inv.project_name or '-'} | **當期應收：** USD ${target_inv.amount:,.2f}")
            
            new_reason = st.text_area("輸入未能收款的原因：", value=target_inv.uncollected_reason or "", height=120)
            is_paid_status = st.checkbox("標記為已完成收款", value=target_inv.is_paid)

            if st.button("💾 儲存並更新至 Supabase 雲端", use_container_width=True):
                target_inv.uncollected_reason = new_reason
                target_inv.is_paid = is_paid_status
                session.commit()
                st.success(f"單號 {target_id} 之未收款原因已順利更新！")
                st.rerun()
        else:
            st.info("目前沒有應收帳款單號。")

    session.close()

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

    total_ar = df_invc[df_invc['invoice_type'] == 'AR']['amount'].sum() if 'invoice_type' in df_invc.columns else 0.0
    total_ap = df_invc[df_invc['invoice_type'] == 'AP']['amount'].sum() if 'invoice_type' in df_invc.columns else 0.0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("AR (應收帳款)", f"USD ${total_ar:,.2f}")
    c2.metric("AP (應付帳款)", f"USD ${total_ap:,.2f}")
    c3.metric("Projects (工程數)", f"{len(df_prj)}")
    
    st.markdown("---")
    st.subheader("🏗️ 配電盤工程項目監控 / Project Monitoring")
    st.dataframe(df_prj, use_container_width=True)

# 路由控制
if menu_choice == t.get("menu_exec"):
    render_exec_dashboard()
elif menu_choice == t["menu_approval"]:
    render_approval_module()
elif menu_choice == t["menu_finance"]:
    render_finance_module()
elif menu_choice == t["menu_warehouse"]:
    st.title(t["menu_warehouse"])
    st.dataframe(pd.read_sql("SELECT * FROM inventory", get_db_engine()), use_container_width=True)
