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

st.set_page_config(
    page_title="Global SaaS AI ERP - Lego Brick Control Hub",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

SAAS_LOGO_HTML = """
<div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 15px; padding: 10px; background: #f8fafc; border-radius: 8px; border-bottom: 3px solid #2563eb;">
    <div style="font-size: 26px; font-weight: 900; color: #2563eb; letter-spacing: -1px; line-height: 1;">LEGO ERP Control Hub</div>
    <div style="border-left: 2px solid #cbd5e1; padding-left: 10px; line-height: 1.15;">
        <div style="font-size: 12.5px; font-weight: 800; color: #1e293b;">全球 SaaS 樂高拼圖模組串連、版本定義與租戶授權總控中心</div>
        <div style="font-size: 8px; font-weight: 700; color: #64748b;">MODULAR LEGO APP STORE & TENANT LICENSING SYSTEM</div>
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
# 1. 總控安全登入
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
        st.markdown("<h2 style='text-align: center; color: #1e293b;'>🔐 樂高總控中心安全登入</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>限平台最高架構師與總控管理員進入</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        username = st.text_input("總控帳號", value="super_admin")
        password = st.text_input("密碼", type="password", value="123")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔑 進入樂高總控平台", use_container_width=True, type="primary"):
            if password == "123":
                st.session_state.logged_in = True
                st.session_state.user_role = "super_admin"
                st.session_state.user_name = username
                st.rerun()
            else:
                st.error("❌ 密碼錯誤")
    st.stop()

# ----------------------------------------------------
# 側邊欄控制
# ----------------------------------------------------
st.sidebar.markdown("### 🧩 SaaS 樂高總控台")
st.sidebar.markdown(f"**👤 管理員: {st.session_state.user_name}**")
st.sidebar.success("🟢 總控存取權限：已授權")
if st.sidebar.button("🚪 登出總控中心", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

# ----------------------------------------------------
# 主介面：四大核心分頁
# ----------------------------------------------------
st.markdown(SAAS_LOGO_HTML, unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🧩 1. 樂高拼圖模組市集與版本定價定義", 
    "🏢 2. 客戶租戶方案指派與動態串連", 
    "📊 3. 財務 AR/AP 與內部免計費專區", 
    "🔐 4. 總控權限與人員設定"
])

# --- TAB 1: 樂高拼圖模組市集與版本定價定義 ---
with tab1:
    st.markdown("### 🧩 樂高拼圖模組選擇、部門歸屬與版本定價設定")
    st.info("💡 *在此選擇部門並透過 App Store 勾選拼圖模組，設定各版本的包含項目與價格，作為後續租戶開通與功能串連的依據。*")
    
    # 選擇目標部門
    target_dept = st.selectbox(
        "選擇要配置的企業部門層級：",
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
    st.markdown(f"#### 📦 定義 `{target_dept}` 的樂高拼圖模組與定價")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("##### 🌟 高階與戰情模組拼圖")
        p1 = st.checkbox("🔴 全球原料價格與即時匯率看板 ($20/月)", value=True)
        p2 = st.checkbox("📊 跨國總損益與資產負債表 ($30/月)", value=True)
        p3 = st.checkbox("⚡ MES 生產製造與 IoT 稼動率監控 ($80/月)", value=True)
        p4 = st.checkbox("🤖 AI 語音與多模態智慧輸入 ($50/月)", value=True)
    with col_p2:
        st.markdown("##### 📦 業務、行政與供應鏈模組拼圖")
        p5 = st.checkbox("🛒 總務採購與多幣別請購單 ($30/月)", value=True)
        p6 = st.checkbox("✍️ 全方位電子簽核中心 (BPM) ($40/月)", value=True)
        p7 = st.checkbox("🧾 跨國電子發票與稅號 MST 解析 ($30/月)", value=True)
        p8 = st.checkbox("📦 全球供應鏈倉儲與條碼 WMS ($50/月)", value=True)

    edition_mapping = st.selectbox(
        "將此部門拼圖組合對應至 SaaS 銷售版本：",
        ["🚀 旗艦企業版 (Enterprise - 全功能打包)", "💼 正式商務版 (Professional)", "🔄 訂閱彈性版 (Subscription)", "👤 個人微型版 (Personal)"]
    )
    
    if st.button("💾 儲存該部門的樂高拼圖與版本定價規則", type="primary"):
        st.success(f"🎉 成功將所選拼圖模組綁定至 [{edition_type if 'edition_type' in locals() else edition_mapping}]！租戶勾選此版本後將自動串連並解鎖對應功能。")

# --- TAB 2: 客戶租戶方案指派與動態串連 ---
with tab2:
    st.markdown("### 🏢 客戶租戶方案指派與樂高功能串連開關")
    st.info("💡 *在此選擇您的客戶（例如：裕豐電機工業），為其指派銷售版本。系統會自動串連並開啟對應的樂高拼圖模組功能。*")
    
    tenant_name = st.selectbox("選擇目標客戶租戶：", ["TENANT-001 | 裕豐電機工業 (Reetech Industrial) - 越南/台灣", "TENANT-002 | 亞太精密科技 - 馬來西亞分公司"])
    
    tc1, tc2 = st.columns(2)
    with tc1:
        assigned_edition = st.selectbox("指派 SaaS 銷售版本", ["🚀 旗艦企業版 (Enterprise)", "💼 正式商務版 (Professional)", "🔄 訂閱彈性版 (Subscription)", "👤 個人微型版 (Personal)"])
        tenant_fee = st.number_input("確認每月訂閱金額 (USD / 月)", value=2500.0, step=100.0)
    with tc2:
        tenant_run_status = st.selectbox("租戶運行狀態", ["🟢 正式運營中 (Active)", "🟡 試用期中 (Trial)", "🔴 已停權 (Suspended)"])
        st.markdown("**🔗 樂高拼圖串連狀態**：已根據版本自動解鎖 16 個核心模組。")

    if st.button("🚀 儲存租戶授權並連動開通樂高模組", type="primary"):
        st.success(f"🎉 租戶 [{tenant_name}] 已成功套用 [{assigned_edition}]，所有選定的樂高拼圖功能已為其即時串連開通！")

    st.markdown("---")
    st.markdown("#### 📋 全球租戶版本與樂高授權總覽")
    summary_df = pd.DataFrame([
        {"tenant_id": "TENANT-001", "company": "裕豐電機工業", "edition": "旗艦企業版", "monthly_fee_usd": 2500, "status": "🟢 運營中", "linked_modules": "16 模組已串連"},
        {"tenant_id": "TENANT-002", "company": "亞太精密科技", "edition": "正式商務版", "monthly_fee_usd": 1200, "status": "🟡 試用", "linked_modules": "8 模組已串連"}
    ])
    st.dataframe(summary_df, use_container_width=True)

# --- TAB 3: 財務 AR/AP 與內部免計費專區 ---
with tab3:
    st.markdown("### 📊 SaaS 財務 AR/AP 中心與內部主公司專區")
    f_tab1, f_tab2 = st.tabs(["💰 財務應收/應付帳款 (AR/AP)", "🏠 內部主公司營運專區 (免計費)"])
    
    with f_tab1:
        st.markdown("#### 💳 全球租戶應收帳款 (AR) 與營收總覽")
        mc1, mc2 = st.columns(2)
        with mc1:
            st.metric(label="🌐 總預估月營收 (USD)", value="$ 3,700", delta="+12%")
        with mc2:
            st.metric(label="📋 本月待收帳款 (AR)", value="$ 1,200", delta="1 筆待催收")
            
        ar_table = pd.DataFrame([
            {"tenant_id": "TENANT-001", "company": "裕豐電機工業", "edition": "旗艦企業版", "amount_usd": 2500, "ar_status": "🟢 已收款 (Paid)"},
            {"tenant_id": "TENANT-002", "company": "亞太精密科技", "edition": "正式商務版", "amount_usd": 1200, "ar_status": "🟡 待收款 (Pending)"}
        ])
        st.dataframe(ar_table, use_container_width=True)
        
    with f_tab2:
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

# --- TAB 4: 總控權限與人員設定 ---
with tab4:
    st.markdown("### 🔐 總控中心存取權限與人員設定")
    st.info("💡 *嚴格控管哪些內部管理員具備開啟、修改與操作本「SaaS 樂高總控中心」的最高權限。*")
    
    with st.form("control_access_form"):
        st.text_input("授權管理員帳號 / Email", placeholder="輸入總控人員帳號...")
        st.multiselect("授權管理級別", ["超級總控架構師 (Super Admin)", "財務 AR/AP 審核員", "銷售與樂高拼圖配置專員"], default=["超級總控架構師 (Super Admin)"])
        if st.form_submit_button("🛡️ 儲存總控存取權限", type="primary"):
            st.success("🎉 總控存取權限已成功儲存！")
