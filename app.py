import inspect
import modules.database as db_conn
import modules.org_management as org_management
import modules.employee_management as employee_management
import modules.leave_attendance as leave_attendance
import modules.ga_procurements as ga_procurements
import modules.approval_center as approval_center
import modules.finance_ap as finance_ap
import modules.asset_management as asset_management
import modules.mes_production as mes_production
import modules.supply_chain as supply_chain
import modules.invoice_parsing as invoice_parsing
import modules.ga_contracts as ga_contracts
import modules.ai_multimodal as ai_multimodal
import modules.tax_ledger as tax_ledger
import modules.inventory_wms as inventory_wms
import modules.dashboard_bi as dashboard_bi
import modules.api_gateway_config as api_gateway_config
import pandas as pd
import streamlit as st

# 📱 移動優先與全螢幕佈局設定
st.set_page_config(
    page_title="Global SaaS AI ERP - Control Center",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

SAAS_LOGO_HTML = """
<div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 15px; padding: 10px; background: #f8fafc; border-radius: 8px; border-bottom: 3px solid #2563eb;">
    <div style="font-size: 26px; font-weight: 900; color: #2563eb; letter-spacing: -1px; line-height: 1;">SaaS Control Hub</div>
    <div style="border-left: 2px solid #cbd5e1; padding-left: 10px; line-height: 1.15;">
        <div style="font-size: 12.5px; font-weight: 800; color: #1e293b;">全球多租戶 SaaS 總控、版本銷售與模組拼圖管理中心</div>
        <div style="font-size: 8px; font-weight: 700; color: #64748b;">GLOBAL SAAS MULTI-TENANT ENTERPRISE PLATFORM</div>
    </div>
</div>
"""

def safe_call_module(func, *args, **kwargs):
    if not callable(func): return
    try:
        sig = inspect.signature(func)
        valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        func(*args, **valid_kwargs)
    except Exception as e:
        try: func()
        except Exception as err: st.error(f"模組載入異常: {str(err)}")

# ----------------------------------------------------
# 1. 登入驗證畫面（置中對齊）
# ----------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_name = ""

if not st.session_state.logged_in:
    col_l, col_c, col_r = st.columns([1, 1.5, 1])
    with col_c:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(SAAS_LOGO_HTML, unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #1e293b;'>🔐 SaaS 總控中心安全登入</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>限平台最高管理者與授權總控人員進入</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        username = st.text_input("總控管理員帳號", value="super_admin")
        password = st.text_input("密碼", type="password", value="123")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔑 進入 SaaS 總控平台", use_container_width=True, type="primary"):
            if password == "123":
                st.session_state.logged_in = True
                st.session_state.user_role = "super_admin"
                st.session_state.user_name = username
                st.rerun()
            else:
                st.error("❌ 密碼錯誤")
    st.stop()

# ----------------------------------------------------
# 側邊欄狀態
# ----------------------------------------------------
st.sidebar.markdown("### 🌐 SaaS 總控後台")
st.sidebar.markdown(f"**👤 管理員: {st.session_state.user_name}**")
st.sidebar.success("🟢 總控中心存取權限：已授權")
if st.sidebar.button("🚪 登出總控中心", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

# ----------------------------------------------------
# 主介面：四大核心分頁
# ----------------------------------------------------
st.markdown(SAAS_LOGO_HTML, unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🏢 1. 租戶版本、銷售與定價管理", 
    "🧩 2. 各部門層級與模組拼圖勾選 (App Store)", 
    "📊 3. 財務 AR/AP 與內部免計費專區", 
    "🔐 4. 總控權限與存取設定"
])

# --- TAB 1: 租戶版本、銷售與定價管理 ---
with tab1:
    st.markdown("### 🏢 租戶銷售版本、方案定價與狀態管理")
    st.info("💡 *在此管理各個客戶租戶的銷售方案（旗艦企業版、正式商務版、訂閱彈性版、個人微型版）與自訂訂閱金額。*")
    
    tenant_list = st.selectbox("選擇要設定的目標租戶：", [
        "TENANT-001 | 裕豐電機工業 (Reetech Industrial) - 越南/台灣",
        "TENANT-002 | 亞太精密科技 - 馬來西亞分公司"
    ])
    
    c1, c2 = st.columns(2)
    with c1:
        edition_type = st.selectbox(
            "選擇 SaaS 銷售版本 (Edition)",
            ["🚀 旗艦企業版 (Enterprise Edition)", "💼 正式商務版 (Professional Edition)", "🔄 訂閱彈性版 (Subscription Edition)", "👤 個人微型版 (Personal Edition)"],
            index=0
        )
        custom_price = st.number_input("自訂月訂閱金額 (USD / 月)", value=2500.0, step=100.0)
    with c2:
        billing_cycle = st.selectbox("計費週期", ["月繳 (Monthly)", "季繳 (Quarterly)", "年繳 (Annually - 9折優惠)"])
        tenant_status = st.selectbox("租戶運行狀態", ["🟢 正式運營中 (Active)", "🟡 試用期中 (Trial)", "🔴 已停權/未繳費 (Suspended)"])

    if st.button("💾 儲存該租戶的版本與定價設定", type="primary"):
        st.success(f"🎉 成功更新租戶方案為 [{edition_type}]，月費設定：`$ {custom_price} USD`！")

    st.markdown("---")
    st.markdown("#### 📋 全球租戶方案與定價總覽表")
    tenant_df = pd.DataFrame([
        {"tenant_id": "TENANT-001", "company": "裕豐電機工業", "edition": "旗艦企業版", "monthly_fee_usd": 2500, "status": "🟢 運營中"},
        {"tenant_id": "TENANT-002", "company": "亞太精密科技", "edition": "正式商務版", "monthly_fee_usd": 1200, "status": "🟡 試用期"}
    ])
    st.dataframe(tenant_df, use_container_width=True)

# --- TAB 2: 各部門層級與模組拼圖勾選 (App Store) ---
with tab2:
    st.markdown("### 🧩 依部門層級與模組拼圖勾選 (App Store 模式)")
    st.info("💡 *勾選目標部門與對應的高階/基礎模組拼圖，為選定的租戶動態配置與解鎖功能。*")
    
    selected_dept = st.selectbox(
        "請選擇要配置的目標部門 / 管理層：",
        [
            "📈 董事長室 / 經營企劃室 (Executive & Board)",
            "👔 人力資源與行政管理部 (HR & Admin Dept)",
            "💰 財務與資本運作部 (Finance Dept)",
            "🛒 供應鏈與進銷存管理 (SCM & Procurement)",
            "🏭 生產製造與廠務部 (Manufacturing & Plant)",
            "🛠️ 工程技術與設計服務部 (Engineering & Technical)",
            "💻 資訊技術與系統開發部 (IT & Software Development)"
        ]
    )
    
    st.markdown("---")
    st.markdown(f"#### ⚙️ 配置部門：`{selected_dept}` 的可用模組拼圖")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("##### 🌟 核心與高階戰情模組")
        m1 = st.checkbox("🔴 全球原料與即時匯率看板", value=True)
        m2 = st.checkbox("📈 跨國總損益與資產負債表", value=True)
        m3 = st.checkbox("⚡ MES 生產製造與 IoT 稼動率監控", value=True)
        m4 = st.checkbox("🤖 AI 語音與多模態智慧輸入", value=True)
    with col_b:
        st.markdown("##### 📦 業務、行政與供應鏈模組")
        m5 = st.checkbox("🛒 總務採購與多幣別請購單", value=True)
        m6 = st.checkbox("✍️ 全方位電子簽核中心 (BPM)", value=True)
        m7 = st.checkbox("🧾 跨國電子發票與稅號 MST 解析", value=True)
        m8 = st.checkbox("📦 全球供應鏈倉儲與條碼 (WMS)", value=True)

    if st.button("💾 儲存並套用此部門的模組拼圖權限", type="primary"):
        st.success(f"🎉 成功為部門 [{selected_dept}] 更新模組拼圖配置！")

# --- TAB 3: 財務 AR/AP 與內部免計費專區 ---
with tab3:
    st.markdown("### 📊 SaaS 財務 AR/AP 中心與內部免計費專區")
    tab_f1, tab_f2 = st.tabs(["💰 財務應收/應付帳款 (AR/AP)", "🏠 內部主公司營運專區 (免計費)"])
    
    with tab_f1:
        st.markdown("#### 💳 全球租戶應收帳款 (AR) 與營收統計")
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            st.metric(label="🌐 總預估月營收 (USD)", value="$ 3,700", delta="+12%")
        with fcol2:
            st.metric(label="📋 本月待收帳款 (AR)", value="$ 1,200", delta="1 筆待催收")
            
        ar_table = pd.DataFrame([
            {"tenant_id": "TENANT-001", "company": "裕豐電機工業", "version": "旗艦企業版", "amount_usd": 2500, "ar_status": "🟢 已收款 (Paid)"},
            {"tenant_id": "TENANT-002", "company": "亞太精密科技", "version": "正式商務版", "amount_usd": 1200, "ar_status": "🟡 待收款 (Pending)"}
        ])
        st.dataframe(ar_table, use_container_width=True)
        
    with tab_f2:
        st.markdown("#### 🏠 內部總公司專區（使用 ERP 功能，但不列入營收與 AR 計算）")
        st.info("💡 *我們自己的團隊可在此完整操作所有 ERP 模組，系統會自動在財會計費中將本區排除。*")
        internal_mod = st.selectbox("選擇內部作業模組：", ["員工與薪資管理", "總務採購", "全球供應鏈倉儲 (WMS)", "企業戰情室"])
        
        internal_tenant = {"tenant_id": "INTERNAL-HQ", "company_name": "SaaS 內部營運公司 (免計費)"}
        if "員工" in internal_mod:
            safe_call_module(employee_management.render_employee_management, internal_tenant)
        elif "採購" in internal_mod:
            safe_call_module(ga_procurements.render_ga_procurements, internal_tenant)
        elif "倉儲" in internal_mod:
            safe_call_module(inventory_wms.render_inventory_wms, internal_tenant, ["admin"])
        else:
            safe_call_module(dashboard_bi.render_dashboard_bi, internal_tenant, ["admin"])

# --- TAB 4: 總控權限與存取設定 ---
with tab4:
    st.markdown("### 🔐 總控中心存取權限與人員設定")
    st.info("💡 *嚴格控管哪些內部管理員具備開啟、修改與操作本「SaaS 總控中心」的最高權限。*")
    
    with st.form("control_access_form"):
        st.text_input("授權管理員帳號 / Email", placeholder="輸入總控人員帳號...")
        st.multiselect("授權管理級別", ["超級總控架構師 (Super Admin)", "財務 AR/AP 審核員", "銷售與租戶配置專員"], default=["超級總控架構師 (Super Admin)"])
        if st.form_submit_button("🛡️ 儲存總控存取權限", type="primary"):
            st.success("🎉 總控存取權限已成功儲存！")
