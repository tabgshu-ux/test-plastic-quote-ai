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
    page_title="裕豐電機工業 REETECH INDUSTRIAL - AI ERP 企業管理系統",
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
# 2. 瀏覽器與系統語系自動偵測
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
DB_URL = "postgresql+psycopg2://postgres.wvsqbefyeykmueffcbwd:Reetech2026@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"

def get_db_engine():
    return create_engine(DB_URL, pool_pre_ping=True)

Base = declarative_base()

EXCHANGE_RATES = {
    "USD": 1.0,
    "VND": 25400.0,
    "TWD": 32.0,
    "CNY": 7.23
}

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

def init_db_data():
    try:
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

        Session = sessionmaker(bind=engine)
        session = Session()
        today = datetime.date.today()
        
        if not session.query(UserDB).first():
            session.add_all([
                UserDB(username="admin", password="123", role="admin", full_name="董事長 / 總經理"),
                UserDB(username="manager", password="123", role="manager", full_name="管理部主管"),
                UserDB(username="staff", password="123", role="staff", full_name="廠務生產線班長")
            ])

        if not session.query(ApprovalDB).first():
            session.add_all([
                ApprovalDB(id="APPR-2026-001", title="西寧專案 銅排採購請款單", applicant="廠務採購員", amount=12500.0, currency="USD", status="待簽核"),
                ApprovalDB(id="APPR-2026-002", title="平陽高壓櫃 施耐德斷路器請款", applicant="工程部主管", amount=213360000.0, currency="VND", status="已核准")
            ])
            
        if not session.query(InventoryDB).first():
            session.add_all([
                InventoryDB(item_code="CU-BUS-001", name="高純度導電銅排 10x100mm", category="銅材資材", quantity=1500, unit="kg", unit_cost=12.5, currency="USD", safety_stock=2000),
                InventoryDB(item_code="CB-MCCB-100A", name="塑殼斷路器 100A (Schneider)", category="開關元件", quantity=350, unit="pcs", unit_cost=1143000.0, currency="VND", safety_stock=100)
            ])
            
        if not session.query(InvoiceDB).first():
            session.add_all([
                InvoiceDB(
                    invoice_id="INV-2026-001",
                    entity_name="CÔNG TY TNHH A-Z TÂY NINH",
                    account_code="1311 - TK 1311 (Hợp đồng thi công)",
                    category_type="專案工程合約款",
                    project_name="西寧紡織廠配電盤新建工程",
                    project_period="HD-2026-TN01",
                    quoted_amount=6350000000.0,
                    quoter_name="張經理 (工程部)",
                    payment_terms="30% 訂金 / 60% 進場 / 10% 驗收",
                    uncollected_reason="客戶建廠進度延遲，等待第二期驗收文件簽核中",
                    contract_file_name="Hop_Dong_TayNinh_2026.pdf",
                    amount=3810000000.0,
                    currency="VND",
                    amount_usd=150000.0,
                    due_date=today + datetime.timedelta(days=15),
                    is_paid=False,
                    invoice_type="AR"
                ),
                InvoiceDB(
                    invoice_id="AP-2026-001",
                    entity_name="正泰電器股份有限公司 (CHINT)",
                    account_code="3311 - TK 3311 (Mua NVL/Linh kiện)",
                    category_type="原材料與零組件採購",
                    project_name="高壓斷路器 (MCCB 100A / ACB 2000A) 批次進貨",
                    project_period="PO-2026-0315",
                    quoted_amount=325350.0,
                    quoter_name="李採購員",
                    payment_terms="月結 30 天 (Net 30)",
                    uncollected_reason="已於 2026/03/25 經 VCB 完成全額匯款",
                    contract_file_name="UNC_Chint_VCB_20260325.pdf",
                    amount=325350.0,
                    currency="CNY",
                    amount_usd=45000.0,
                    due_date=today - datetime.timedelta(days=5),
                    is_paid=True,
                    invoice_type="AP",
                    bank_name="Vietcombank (VCB)",
                    bank_transfer_ref="UNC-20260325-88921",
                    payment_date=today - datetime.timedelta(days=5)
                )
            ])

        if not session.query(ProductionTaskDB).first():
            session.add_all([
                ProductionTaskDB(task_id="TSK-CUT-01", dept_name="板金加工組", project_name="西寧紡織廠 2000A 高壓主配電櫃", drawing_no="DWG-TN-2026-A01", qty=6.0, operator="Nguyễn Văn A (阿安)", status="生產中", due_date=today + datetime.timedelta(days=3))
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

i18n = {
    "繁體中文": {"login_title": "⚡ 裕豐電機工業 REETECH INDUSTRIAL - 系統登入", "username": "帳號", "password": "密碼", "login_btn": "🔑 登入系統", "logout_btn": "🚪 登出系統"},
    "Tiếng Việt": {"login_title": "⚡ REETECH INDUSTRIAL - Đăng nhập", "username": "Tài khoản", "password": "Mật khẩu", "login_btn": "🔑 Đăng nhập", "logout_btn": "🚪 Đăng xuất"},
    "English": {"login_title": "⚡ REETECH INDUSTRIAL - Login", "username": "Username", "password": "Password", "login_btn": "🔑 Login", "logout_btn": "🚪 Logout"}
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_name = ""

def login_page():
    t = i18n[st.session_state.current_lang]
    st.title("⚡ 裕豐電機工業 - AI ERP 企業管理系統")
    st.caption("REETECH INDUSTRIAL Co., Ltd.")
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
                st.error("帳號或密碼錯誤 / Incorrect login")
            session.close()

if not st.session_state.logged_in:
    login_page()
    st.stop()

st.sidebar.title("⚡ 裕豐電機工業")
st.sidebar.caption("REETECH INDUSTRIAL Co., Ltd.")

lang_list = ["繁體中文", "Tiếng Việt", "English"]
selected_lang = st.sidebar.selectbox("🌐 語言設定 / Language", lang_list, index=lang_list.index(st.session_state.current_lang))
st.session_state.current_lang = selected_lang
t = i18n[selected_lang]

st.sidebar.markdown(f"**👤 {st.session_state.user_name}** ({st.session_state.user_role.upper()})")
if st.sidebar.button(t["logout_btn"]):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

menu_options = []
if st.session_state.user_role == "admin":
    menu_options.append("👑 董事長/總經理 - 營運戰情看板")

menu_options.extend([
    "🏢 管理部 - 財務會計 (TT200/多幣別/UNC)",
    "👥 管理部 - 人事與行政管理",
    "📦 管理部 - 總務與資產管理",
    "✂️ 生產部 - 板金加工組",
    "🎨 生產部 - 烤漆塗裝組",
    "⚡ 生產部 - 配電盤組裝與配線組",
    "🏭 生產部 - 倉庫與資材管理",
    "✍️️ 電子簽核與請款流程"
])

menu_choice = st.sidebar.radio("公司組織部門選單", menu_options)

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

def translate_vi_to_zh(text_content):
    if not text_content:
        return "請輸入或貼上越南文內容。"
    dictionary = {"Hợp đồng": "合約", "Ủy nhiệm chi": "銀行轉帳單 (UNC)", "Thanh toán": "付款", "Tạm ứng": "預付/訂金", "Nghiệm thu": "驗收"}
    translated = text_content
    for vi, zh in dictionary.items():
        translated = translated.replace(vi, f"**{zh} ({vi})**")
    return translated

def render_exec_dashboard():
    st.title("👑 裕豐電機工業 - 董事長 / 總經理 營運戰情看板")
    st.caption("REETECH INDUSTRIAL Co., Ltd.")
    engine = get_db_engine()
    df_invc = pd.read_sql("SELECT * FROM invoices", engine)
    df_prj = pd.read_sql("SELECT * FROM projects", engine)

    total_ar = df_invc[df_invc['invoice_type'] == 'AR']['amount_usd'].sum() if 'amount_usd' in df_invc.columns else 0.0
    total_ap = df_invc[df_invc['invoice_type'] == 'AP']['amount_usd'].sum() if 'amount_usd' in df_invc.columns else 0.0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("應收帳款 (折合 USD)", f"USD ${total_ar:,.2f}")
    c2.metric("應付貨款 (折合 USD)", f"USD ${total_ap:,.2f}")
    c3.metric("在手工程專案數", f"{len(df_prj)} 項")
    
    st.markdown("---")
    st.subheader("🏗️ 配電盤工程項目成本與利潤監控")
    st.dataframe(df_prj, use_container_width=True)

def render_finance_module():
    st.title("💰 裕豐電機工業 - 管理部 財務會計管理")
    st.caption("符合越南 Thông tư 200/2014/TT-BTC 會計制度標準 & 多幣別與銀行 UNC 審計。")
    
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    tab_ar, tab_ap, tab_pay, tab_add, tab_translate = st.tabs([
        "📋 TK 131 應收帳款 (AR)", 
        "💳 TK 331 應付帳款 (AP) 明細", 
        "🏦 銀行轉帳 (UNC)",
        "會計帳款與單據登記", 
        "🌐 越南合約/UNC AI 翻譯對照"
    ])

    with tab_ar:
        ar_invoices = session.query(InvoiceDB).filter_by(invoice_type="AR").all()
        total_unpaid_usd = sum(i.amount_usd or convert_to_usd(i.amount, i.currency) for i in ar_invoices if not i.is_paid)
        
        c1, c2 = st.columns(2)
        c1.metric("TK 131 待收總額 (折合美金 USD)", f"${total_unpaid_usd:,.2f}", delta="-待收金額")
        c2.metric("應收筆數", f"{len(ar_invoices)} 筆")
        
        st.markdown("---")
        st.subheader("📑 TK 131 應收帳款 (AR) 多幣別明細表")
        
        df_ar = pd.DataFrame([{
            "單號": i.invoice_id,
            "會計科目": i.account_code or "1311",
            "客戶名稱": i.entity_name,
            "工程/項目": i.project_name or "-",
            "交易幣別": i.currency or "USD",
            "當期應收金額": format_currency_display(i.amount or 0.0, i.currency or "USD"),
            "折合美金 (USD)": f"${(i.amount_usd or convert_to_usd(i.amount, i.currency)):,.2f}",
            "經辦員": i.quoter_name or "-",
            "合約/單據": i.contract_file_name or "未上傳",
            "約定到期日": i.due_date,
            "狀態": "已收款" if i.is_paid else "⏳ 未收款",
            "未能收款原因": i.uncollected_reason or "-"
        } for i in ar_invoices])

        st.dataframe(df_ar, use_container_width=True)

    with tab_ap:
        ap_invoices = session.query(InvoiceDB).filter_by(invoice_type="AP").all()
        total_ap_usd = sum(i.amount_usd or convert_to_usd(i.amount, i.currency) for i in ap_invoices if not i.is_paid)
        
        c1, c2 = st.columns(2)
        c1.metric("TK 331 待付採購總額 (折合美金 USD)", f"${total_ap_usd:,.2f}", delta="-待付金額")
        c2.metric("應付筆數", f"{len(ap_invoices)} 筆")

        st.markdown("---")
        st.subheader("🛒 TK 331 採購資材應付帳款 (AP) 明細表")
        
        df_ap = pd.DataFrame([{
            "請款單號": i.invoice_id,
            "會計科目": i.account_code or "3311",
            "供應商名稱": i.entity_name,
            "採購品名規格": i.project_name or "-",
            "交易幣別": i.currency or "USD",
            "應付金額": format_currency_display(i.amount or 0.0, i.currency or "USD"),
            "折合美金 (USD)": f"${(i.amount_usd or convert_to_usd(i.amount, i.currency)):,.2f}",
            "付款狀態": "✅ 已轉帳付清" if i.is_paid else "⏳ 待轉帳",
            "實際轉帳日期": i.payment_date or "-",
            "付款銀行": i.bank_name or "-",
            "轉帳單號 (UNC)": i.bank_transfer_ref or "-",
            "水單/單據": i.contract_file_name or "未上傳",
            "備註": i.uncollected_reason or "-"
        } for i in ap_invoices])
        
        st.dataframe(df_ap, use_container_width=True)

    with tab_pay:
        st.subheader("🏦 銀行轉帳與水單登記 (Ủy Nhiệm Chi)")
        ap_unpaid = session.query(InvoiceDB).filter_by(invoice_type="AP", is_paid=False).all()
        ap_options = {f"{i.invoice_id} - {i.entity_name} ({format_currency_display(i.amount, i.currency)})": i.invoice_id for i in ap_unpaid}

        if ap_options:
            selected_ap_label = st.selectbox("選擇要核銷付款的應付單號", list(ap_options.keys()))
            target_ap_id = ap_options[selected_ap_label]
            target_ap = session.query(InvoiceDB).filter_by(invoice_id=target_ap_id).first()

            with st.form("bank_pay_form"):
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    bank_name = st.selectbox("付款銀行", ["Vietcombank (VCB)", "BIDV", "MB Bank", "ViettinBank", "ACB", "第一銀行 (First Bank)", "兆豐銀行", "其他 Bank"])
                    bank_transfer_ref = st.text_input("銀行轉帳水單單號 (Số UNC) *", placeholder="例: UNC-20260326-9901")
                with col_p2:
                    payment_date = st.date_input("實際轉帳日期", datetime.date.today())
                    unc_file = st.file_uploader("📎 上傳銀行轉帳水單 (UNC)", type=["pdf", "png", "jpg"])

                pay_notes = st.text_area("付款備註", value=f"已於 {payment_date} 經 {bank_name} 完成匯款 {format_currency_display(target_ap.amount, target_ap.currency)}。")

                submit_pay = st.form_submit_button("💾 儲存轉帳紀錄並標記為已付清", use_container_width=True)

                if submit_pay:
                    if not bank_transfer_ref:
                        st.error("請輸入銀行轉帳水單單號 (UNC)！")
                    else:
                        target_ap.is_paid = True
                        target_ap.bank_name = bank_name
                        target_ap.bank_transfer_ref = bank_transfer_ref
                        target_ap.payment_date = payment_date
                        target_ap.uncollected_reason = pay_notes
                        if unc_file:
                            target_ap.contract_file_name = unc_file.name
                        session.commit()
                        st.success(f"單號 {target_ap_id} 之轉帳水單 {bank_transfer_ref} 已順利寫入！")
                        st.rerun()
        else:
            st.info("目前所有應付帳款皆已付款結清！")

    with tab_add:
        st.subheader("會計帳款與單據登記")
        
        with st.form("add_invoice_form"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                inv_type = st.selectbox("帳款性質", ["AR - 應收帳款 (TK 131)", "AP - 應付帳款 (TK 331)"])
                account_code = st.selectbox(
                    "越南 TT200 標準會計科目",
                    [
                        "3311 - Mua nguyên vật liệu/linh kiện (資材與零組件採購)",
                        "3312 - Chi phí gia công/thầu phụ (外包工程與加工費)",
                        "3313 - Mua sắm máy móc/TSCĐ (機器設備與固定資產)",
                        "3318 - Chi phí vận chuyển/điện nước (運費/水電/廠務雜支)",
                        "1311 - Hợp đồng thi công (專案工程合約款)",
                        "1312 - Bán hàng thiết bị/tủ điện (配電盤/設備銷售款)",
                        "1318 - Phải thu khác (其他應收款)"
                    ]
                )
                entity_name = st.text_input("客戶名稱 (AR) 或 供應商名稱 (AP) *")
                project_name = st.text_input("工程名稱 (AR) 或 採購品名規格 (AP) *")
                project_period = st.text_input("合約編號 (AR) 或 採購 PO 單號 (AP)")

            with col_b:
                currency = st.selectbox("💱 交易幣別 *", ["VND (越南盾)", "USD (美金)", "TWD (台幣)", "CNY (人民幣)"])
                curr_code = currency.split(" ")[0]
                
                amount = st.number_input(f"當期金額 ({curr_code}) *", min_value=0.0)
                quoted_amount = st.number_input(f"總報價 / 總採購金額 ({curr_code})", min_value=0.0)
                
                quoter_name = st.text_input("經辦人員 / 業務員")
                payment_terms = st.text_input("付款條件 (例: Net 30 / 30% 預付)")
                due_date = st.date_input("約定到期日期", datetime.date.today() + datetime.timedelta(days=30))
                uncollected_reason = st.text_area("未收款原因 (AR) 或 付款備註說明 (AP)")
                uploaded_file = st.file_uploader("📎 上傳工程合約 / 採購 PO / 銀行水單", type=["pdf", "txt", "png", "jpg"])

            submit_btn = st.form_submit_button("💾 儲存並寫入 Supabase 雲端資料庫", use_container_width=True)

            if submit_btn:
                if not entity_name or not project_name:
                    st.error("請填寫對象名稱與工程/採購品名！")
                else:
                    type_code = "AR" if "AR" in inv_type else "AP"
                    new_inv_id = f"{type_code}-2026-{datetime.datetime.now().strftime('%m%d%H%M')}"
                    file_name = uploaded_file.name if uploaded_file else ""
                    
                    calc_usd = convert_to_usd(amount, curr_code)

                    new_invoice = InvoiceDB(
                        invoice_id=new_inv_id,
                        entity_name=entity_name,
                        account_code=account_code,
                        category_type=account_code.split(" - ")[1] if " - " in account_code else account_code,
                        project_name=project_name,
                        project_period=project_period,
                        quoted_amount=quoted_amount,
                        quoter_name=quoter_name,
                        payment_terms=payment_terms,
                        uncollected_reason=uncollected_reason,
                        contract_file_name=file_name,
                        amount=amount,
                        currency=curr_code,
                        amount_usd=calc_usd,
                        due_date=due_date,
                        is_paid=False,
                        invoice_type=type_code
                    )
                    session.add(new_invoice)
                    session.commit()
                    st.success(f"帳款單號 {new_inv_id} ({curr_code}) 已成功建立並同步至雲端資料庫！")
                    st.rerun()

    with tab_translate:
        st.subheader("🌐 越南文合約 / 銀行水單 (UNC) AI 翻譯對照")
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("#### 🇻🇳 越南文內文 (Input)")
            vi_contract_text = st.text_area("貼上越南文條款或 UNC 內容：", value="Ủy nhiệm chi (UNC): Bên A chuyển khoản thanh toán 381,000,000 VND cho Bên B qua ngân hàng Vietcombank. Số GD: UNC-20260325-88921.", height=220)

        with col_right:
            st.markdown("#### 🇹🇼 中文條款即時對照 (Translation)")
            translated_result = translate_vi_to_zh(vi_contract_text)
            st.markdown(translated_result)

    session.close()

def render_production_module(dept_name):
    st.title(f"🏭 裕豐電機工業 - 生產部 ({dept_name})")
    st.caption("配電盤生產製造進度、派工單管理與現場 QC 檢查")
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    st.subheader(f"📋 {dept_name} 現有派工單與生產進度")
    tasks = session.query(ProductionTaskDB).filter_by(dept_name=dept_name).all()
    if tasks:
        df_task = pd.DataFrame([{"派工單號": t.task_id, "專案名稱": t.project_name, "圖號": t.drawing_no, "數量": t.qty, "負責師傅/班長": t.operator, "交期": t.due_date, "當前狀態": t.status} for t in tasks])
        st.dataframe(df_task, use_container_width=True)
    else:
        st.info(f"目前 {dept_name} 無進行中的派工單。")

    st.markdown("---")
    st.subheader(f"➕ 新增 {dept_name} 派工單")
    with st.form(f"add_task_{dept_name}"):
        col1, col2 = st.columns(2)
        with col1:
            prj_name = st.text_input("工程專案名稱 *")
            dwg_no = st.text_input("施工圖號 (DWG No.)")
        with col2:
            qty = st.number_input("派工數量 (台/套)", min_value=1.0, value=1.0)
            operator = st.text_input("負責師傅 / 班長姓名")
            due_date = st.date_input("預計完工日期", datetime.date.today() + datetime.timedelta(days=5))

        if st.form_submit_button("💾 建立派工單"):
            if not prj_name:
                st.error("請輸入專案名稱！")
            else:
                new_tsk_id = f"TSK-{datetime.datetime.now().strftime('%m%d%H%M')}"
                new_task = ProductionTaskDB(task_id=new_tsk_id, dept_name=dept_name, project_name=prj_name, drawing_no=dwg_no, qty=qty, operator=operator, status="生產中", due_date=due_date)
                session.add(new_task)
                session.commit()
                st.success(f"派工單 {new_tsk_id} 建立成功！")
                st.rerun()
    session.close()

def render_warehouse_module():
    st.title("🏭 裕豐電機工業 - 生產部 (倉庫與資材管理)")
    st.caption("即時控管配電盤用銅排、斷路器與機構件庫存水準與安全庫存預警。")
    engine = get_db_engine()
    df_inv = pd.read_sql("SELECT * FROM inventory", engine)
    st.dataframe(df_inv, use_container_width=True)

def render_approval_module():
    st.title("✍️ 裕豐電機工業 - 電子簽核與請款流程")
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    approvals = session.query(ApprovalDB).all()
    df_appr = pd.DataFrame([{"ID": a.id, "主題": a.title, "申請人": a.applicant, "金額": format_currency_display(a.amount, a.currency or "USD"), "狀態": a.status, "申請日期": a.created_at} for a in approvals])
    st.dataframe(df_appr, use_container_width=True)

if menu_choice == "👑 董事長/總經理 - 營運戰情看板":
    render_exec_dashboard()
elif menu_choice == "🏢 管理部 - 財務會計":
    render_finance_module()
elif menu_choice == "👥 管理部 - 人事與行政管理":
    st.title("👥 裕豐電機工業 - 管理部 (人事與行政管理)")
    st.info("出勤統計、越南員工勞動合約管理與薪資試算。")
elif menu_choice == "📦 管理部 - 總務與資產管理":
    st.title("📦 裕豐電機工業 - 管理部 (總務與資產管理)")
    st.info("廠房固定資產、公務車輛管理與日常總務採購。")
elif menu_choice == "✂️ 生產部 - 板金加工組":
    render_production_module("板金加工組")
elif menu_choice == "🎨 生產部 - 烤漆塗裝組":
    render_production_module("烤漆塗裝组")
elif menu_choice == "⚡ 生產部 - 配電盤組裝與配線組":
    render_production_module("配電盤組裝與配線組")
elif menu_choice == "🏭 生產部 - 倉庫與資材管理":
    render_warehouse_module()
elif menu_choice == "✍️ 電子簽核與請款流程":
    render_approval_module()
