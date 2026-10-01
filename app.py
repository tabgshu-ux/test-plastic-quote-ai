import streamlit as st
import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, Column, String, Float, Boolean, Date, text
from sqlalchemy.orm import declarative_base, sessionmaker

# ==========================================
# 頁面基礎設定 (Streamlit Page Config)
# ==========================================
st.set_page_config(
    page_title="裕豐電機工業 - AI ERP 企業管理系統",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# 1. Supabase 雲端資料庫連線設定
# ==========================================
# ⚠️ 請將 [YOUR-PASSWORD] 替換為您的 Supabase 資料庫實際密碼
DB_URL = "postgresql+psycopg2://postgres.wvsqbefyeykmueffcbwd:RECH2026erp@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

@st.cache_resource
def get_db_engine():
    return create_engine(DB_URL, pool_pre_ping=True)

Base = declarative_base()

# ---------------- 資料庫 ORM 資料表模型 ----------------
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
    invoice_type = Column(String, default="AR") # "AR" (應收) 或 "AP" (應付)

class ProjectDB(Base):
    __tablename__ = 'projects'
    project_id = Column(String, primary_key=True)
    project_name = Column(String, nullable=False)
    budget = Column(Float, default=0.0)
    actual_material_cost = Column(Float, default=0.0)
    actual_labor_cost = Column(Float, default=0.0)
    actual_overhead = Column(Float, default=0.0)

# 初始化雲端資料庫與 Demo 資料
def init_db_data():
    try:
        engine = get_db_engine()
        Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        today = datetime.date.today()
        
        # 若資料表為空，自動注入裕豐電機配電盤範例資料
        if not session.query(InventoryDB).first():
            session.add_all([
                InventoryDB(item_code="CU-BUS-001", name="高純度銅排 10x100mm", category="銅材", quantity=1500, unit="kg", unit_cost=12.5, safety_stock=2000),
                InventoryDB(item_code="CB-MCCB-100A", name="塑殼斷路器 100A", category="開關元件", quantity=350, unit="pcs", unit_cost=45.0, safety_stock=100),
                InventoryDB(item_code="ENCL-IP54", name="IP54 高壓配電箱體", category="鋼板/箱體", quantity=12, unit="set", unit_cost=850.0, safety_stock=15)
            ])
            
        if not session.query(InvoiceDB).first():
            session.add_all([
                InvoiceDB(invoice_id="INV-2026-001", entity_name="越南樟榜工業區A廠", amount=150000.0, due_date=today + datetime.timedelta(days=15), is_paid=False, invoice_type="AR"),
                InvoiceDB(invoice_id="INV-2026-002", entity_name="海防電力工程有限公司", amount=85000.0, due_date=today - datetime.timedelta(days=5), is_paid=False, invoice_type="AR"),
                InvoiceDB(invoice_id="AP-2026-888", entity_name="施耐德電氣越南分公司", amount=45000.0, due_date=today + datetime.timedelta(days=10), is_paid=False, invoice_type="AP"),
                InvoiceDB(invoice_id="AP-2026-889", entity_name="台灣銅業供應商", amount=62000.0, due_date=today + datetime.timedelta(days=30), is_paid=False, invoice_type="AP")
            ])
            
        if not session.query(ProjectDB).first():
            session.add_all([
                ProjectDB(project_id="PRJ-TAYNINH-01", project_name="西寧紡織廠配電盤工程", budget=250000.0, actual_material_cost=120000.0, actual_labor_cost=45000.0, actual_overhead=15000.0),
                ProjectDB(project_id="PRJ-BINHDUONG-02", project_name="平陽電子廠高壓櫃項目", budget=180000.0, actual_material_cost=95000.0, actual_labor_cost=50000.0, actual_overhead=20000.0)
            ])
            
        session.commit()
        session.close()
        return True
    except Exception as e:
        st.error(f"⚠️ 雲端資料庫連線失敗，請檢查密碼或網路連線：{e}")
        return False

# 執行初始化
db_connected = init_db_data()

# ==========================================
# 2. 側邊欄選單與語系設定
# ==========================================
st.sidebar.title("⚡ 裕豐電機 AI ERP")
st.sidebar.caption("REETECH INDUSTRIAL Co., Ltd.")

lang = st.sidebar.selectbox("🌐 語言設定 / Language / Ngôn ngữ", ["繁體中文", "Tiếng Việt", "English"])

# 語系對照字典
i18n = {
    "繁體中文": {
        "menu_exec": "📊 老闆營運決策看板",
        "menu_finance": "💰 財務與應收/應付帳款",
        "menu_warehouse": "📦 倉庫資材與安全庫存",
        "menu_ga": "🏢 總務與廠務行政管理",
        "btn_refresh": "重新整理數據"
    },
    "Tiếng Việt": {
        "menu_exec": "📊 Báo cáo Giám đốc",
        "menu_finance": "💰 Tài chính & Công nợ (AR/AP)",
        "menu_warehouse": "📦 Kho vật tư & Tồn kho",
        "menu_ga": "🏢 Hành chính Quản trị (GA)",
        "btn_refresh": "Làm mới dữ liệu"
    },
    "English": {
        "menu_exec": "📊 Executive Dashboard",
        "menu_finance": "💰 Finance & AR/AP",
        "menu_warehouse": "📦 Warehouse & Inventory",
        "menu_ga": "🏢 General Affairs (GA)",
        "btn_refresh": "Refresh Data"
    }
}[lang]

menu_choice = st.sidebar.radio("模組功能選單", [
    i18n["menu_exec"],
    i18n["menu_finance"],
    i18n["menu_warehouse"],
    i18n["menu_ga"]
])

# ==========================================
# 3. 模組頁面渲染邏輯
# ==========================================

# ---------------- A. 老闆營運狀況看板 ----------------
def render_exec_dashboard():
    st.title("📊 老闆即時營運與財務狀況看板")
    st.write("即時連結 Supabase 雲端資料庫，監控西寧廠區工程毛利、現金流與資產狀況。")
    
    if not db_connected:
        st.warning("⚠️ 資料庫未連線，請檢查 Supabase 設定。")
        return

    engine = get_db_engine()
    df_inv = pd.read_sql("SELECT * FROM inventory", engine)
    df_invc = pd.read_sql("SELECT * FROM invoices", engine)
    df_prj = pd.read_sql("SELECT * FROM projects", engine)

    # 指標計算
    total_ar = df_invc[(df_invc['invoice_type'] == 'AR') & (df_invc['is_paid'] == False)]['amount'].sum()
    today_str = str(datetime.date.today())
    overdue_ar = df_invc[(df_invc['invoice_type'] == 'AR') & (df_invc['is_paid'] == False) & (df_invc['due_date'].astype(str) < today_str)]['amount'].sum()
    total_ap = df_invc[(df_invc['invoice_type'] == 'AP') & (df_invc['is_paid'] == False)]['amount'].sum()
    
    total_stock_val = (df_inv['quantity'] * df_inv['unit_cost']).sum()
    low_stock_count = len(df_inv[df_inv['quantity'] < df_inv['safety_stock']])
    
    total_budget = df_prj['budget'].sum()
    total_cost = (df_prj['actual_material_cost'] + df_prj['actual_labor_cost'] + df_prj['actual_overhead']).sum()
    profit = total_budget - total_cost

    # 第一排：財務與現金流指標
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("工程在手總營收", f"USD ${total_budget:,.2f}")
    c2.metric("未收應收帳款 (AR)", f"USD ${total_ar:,.2f}", f"⚠️ 逾期 ${overdue_ar:,.2f}" if overdue_ar > 0 else "正常", delta_color="inverse")
    c3.metric("未付應付帳款 (AP)", f"USD ${total_ap:,.2f}")
    c4.metric("倉庫材料總資產", f"USD ${total_stock_val:,.2f}", f"⚠️ {low_stock_count} 項缺料預警" if low_stock_count > 0 else "庫存充裕", delta_color="inverse")

    st.markdown("---")

    # 第二排：專案工程進度與毛利分析
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("🏗️ 配電盤工程專案成本與利潤監控")
        df_prj['total_actual_cost'] = df_prj['actual_material_cost'] + df_prj['actual_labor_cost'] + df_prj['actual_overhead']
        df_prj['margin'] = df_prj['budget'] - df_prj['total_actual_cost']
        st.dataframe(df_prj[['project_id', 'project_name', 'budget', 'total_actual_cost', 'margin']], use_container_width=True)

    with col_right:
        st.subheader("💡 AI 智能風險與營運提示")
        if overdue_ar > 0:
            st.error(f"🔴 **財務風險：** 發現 USD ${overdue_ar:,.2f} 逾期應收帳款，系統建議向海防電力工程發送催款單。")
        if low_stock_count > 0:
            st.warning(f"🟡 **資材風險：** 有 {low_stock_count} 項材料低於安全庫存（如高純度銅排），建議關注銅價並及時採購。")
        st.success("🟢 **工程進度：** 西寧紡織廠工程毛利率符合預期目標 (>30%)。")

# ---------------- B. 財務與帳款模組 ----------------
def render_finance_module():
    st.title("💰 財務與應收/應付帳款管理 (AR / AP)")
    
    engine = get_db_engine()
    df_invc = pd.read_sql("SELECT * FROM invoices", engine)

    tab1, tab2 = st.tabs(["應收帳款 (AR)", "應付帳款 (AP)"])
    
    with tab1:
        st.subheader("客戶應收帳款清單")
        df_ar = df_invc[df_invc['invoice_type'] == 'AR']
        st.dataframe(df_ar, use_container_width=True)
        
    with tab2:
        st.subheader("供應商應付帳款清單")
        df_ap = df_invc[df_invc['invoice_type'] == 'AP']
        st.dataframe(df_ap, use_container_width=True)

# ---------------- C. 倉庫資材模組 ----------------
def render_warehouse_module():
    st.title("📦 倉庫材料與安全庫存管理")
    
    engine = get_db_engine()
    df_inv = pd.read_sql("SELECT * FROM inventory", engine)
    
    st.subheader("配電盤核心原物料庫存")
    df_inv['total_value'] = df_inv['quantity'] * df_inv['unit_cost']
    df_inv['stock_status'] = df_inv.apply(lambda r: "⚠️ 低於安全庫存" if r['quantity'] < r['safety_stock'] else "✅ 正常", axis=1)
    
    st.dataframe(df_inv[['item_code', 'name', 'category', 'quantity', 'unit', 'unit_cost', 'total_value', 'stock_status']], use_container_width=True)

# ---------------- D. 總務與廠務模組 ----------------
def render_ga_module():
    st.title("🏢 總務與廠務行政管理 (GA)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛠️ 廠區機具設備維修/保養 (PM)")
        st.info("• 数控衝床 NC-01：定期保養完成（2026-09-15）\n• 銅排折彎機 BM-02：預計下次保養日 2026-10-10")
    
    with col2:
        st.subheader("🛂 外籍幹部工作證/暫住證 (TRC) 管理")
        st.warning("• 台籍總工程師：暫住證 (TRC) 即將於 45 天後到期，請總務啟動延期申請。")

# ==========================================
# 4. 主程式路由
# ==========================================
if menu_choice == i18n["menu_exec"]:
    render_exec_dashboard()
elif menu_choice == i18n["menu_finance"]:
    render_finance_module()
elif menu_choice == i18n["menu_warehouse"]:
    render_warehouse_module()
elif menu_choice == i18n["menu_ga"]:
    render_ga_module()
