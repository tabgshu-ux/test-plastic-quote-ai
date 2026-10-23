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
    page_title="Global SaaS AI ERP - Platform Control Center",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

SAAS_LOGO_HTML = """
<div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 15px; padding: 10px; background: #f8fafc; border-radius: 8px; border-bottom: 3px solid #2563eb;">
    <div style="font-size: 26px; font-weight: 900; color: #2563eb; letter-spacing: -1px; line-height: 1;">SaaS Control Hub</div>
    <div style="border-left: 2px solid #cbd5e1; padding-left: 10px; line-height: 1.15;">
        <div style="font-size: 12.5px; font-weight: 800; color: #1e293b;">全球多租戶雲端 SaaS 總控與財務管理中心</div>
        <div style="font-size: 8px; font-weight: 700; color: #64748b;">PLATFORM ADMIN & TENANT MANAGEMENT SYSTEM</div>
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
        st.markdown("<h2 style='text-align: center; color: #1e293b;'>🔐 總控平台安全登入</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>限平台最高管理者與授權總控人員進入</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        username = st.text_input("總控管理員帳號", value="super_admin")
        password = st.text_input("密碼", type="password", value="123")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔑 進入 SaaS 總控中心", use_container_width=True, type="primary"):
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
# 主介面：符合您需求的 4 大總控核心分頁
# ----------------------------------------------------
st.markdown(SAAS_LOGO_HTML, unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🏢 1. 租戶項目監控與修改", 
    "📊 2. SaaS 管理與財務 AR/AP 中心", 
    "🏠 3. 內部主公司 ERP 專區 (免計費)", 
    "🔐 4. 總控中心權限設定"
])

# --- TAB 1: 租戶項目監控與修改 ---
with tab1:
    st.markdown("### 🏢 租戶使用項目觀察與即時修改")
    st.info("💡 *在此檢視各個外部租戶（例如：裕豐電機工業）當前啟用的功能項目與模組，並可直接為其進行增刪修調整。*")
    
    tenant_select = st.selectbox("選擇要檢視與修改的租戶：", ["TENANT-001 | 裕豐電機工業 (Reetech Industrial)", "TENANT-002 | 亞太精密科技 (Vietnam Branch)"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 當前已開通模組項目")
        st.checkbox("🏭 MES 生產製造與 IoT 監控", value=True)
        st.checkbox("📊 供應鏈與業務報價", value=True)
        st.checkbox("✍️ 全方位電子簽核中心", value=True)
        st.checkbox("💰 跨國應付帳款 (Finance AP)", value=True)
    with col2:
        st.markdown("#### 快速調整與修改")
        st.selectbox("調整訂閱等級", ["Enterprise 旗艦版", "Professional 專業版", "Standard 標準版"])
        if st.button("💾 儲存並更新該租戶的模組配置", type="primary"):
            st.success(f"🎉 成功更新 [{tenant_select}] 的模組與使用權限設定！")

# --- TAB 2: SaaS 管理與財務 AR/AP 中心 ---
with tab2:
    st.markdown("### 📊 全球租戶數量、地區分佈與財務 AR/AP 中心")
    st.info("💡 *提供財務部門檢視各租戶數量、營收金額、地區分佈，並直接對接應收帳款 (AR) 與應付帳款 (AP)。*")
    
    mcol1, mcol2, mcol3 = st.columns(3)
    with mcol1:
        st.metric(label="🌐 總付費租戶數", value="12 家", delta="+2 本月新增")
    with mcol2:
        st.metric(label="🌍 活躍覆蓋地區", value="台灣、越南平陽、馬來西亞")
    with mcol3:
        st.metric(label="💰 總預估月營收 (USD)", value="$ 35,400", delta="+8.5%")

    st.markdown("---")
    st.markdown("#### 📋 租戶營收與財務應收帳款 (AR) 清單")
    
    ar_df = pd.DataFrame([
        {"tenant_id": "TENANT-001", "company": "裕豐電機工業", "region": "越南/台灣", "plan": "Enterprise", "monthly_fee_usd": 2500, "ar_status": "🟢 已收款 (Paid)"},
        {"tenant_id": "TENANT-002", "company": "亞太精密科技", "region": "馬來西亞", "plan": "Professional", "monthly_fee_usd": 1200, "ar_status": "🟡 待催收 (Pending)"}
    ])
    st.dataframe(ar_df, use_container_width=True)

# --- TAB 3: 內部主公司 ERP 專區 (免計費) ---
with tab3:
    st.markdown("### 🏠 內部主公司專區（使用租戶功能，但不列入營收計算）")
    st.info("💡 *我們自己的營運團隊可直接在此操作所有 ERP 模組（如人事、採購、庫存等），此專區享有完整功能但會被系統自動排除在應收帳款與計費之外。*")
    
    internal_choice = st.selectbox("選擇內部主公司作業模組：", ["員工與薪資管理", "總務採購與請購", "全球供應鏈倉儲 (WMS)", "企業戰情室"])
    
    tenant_info = {"tenant_id": "INTERNAL-HQ", "company_name": "SaaS 總公司內部營運 (免計費)"}
    user_perms = ["admin", "finance", "mes"]

    st.markdown("---")
    if "員工" in internal_choice:
        safe_call_module(employee_management.render_employee_management, tenant_info)
    elif "採購" in internal_choice:
        safe_call_module(ga_procurements.render_ga_procurements, tenant_info)
    elif "倉儲" in internal_choice:
        safe_call_module(inventory_wms.render_inventory_wms, tenant_info, user_perms)
    else:
        safe_call_module(dashboard_bi.render_dashboard_bi, tenant_info, user_perms)

# --- TAB 4: 總控中心權限設定 ---
with tab4:
    st.markdown("### 🔐 總控中心訪問與操作權限管理")
    st.info("💡 *設定哪些內部管理者帳號具備開啟、修改與操作本「SaaS 總控中心」的最高權限。*")
    
    with st.form("admin_access_form"):
        st.text_input("新增具備總控權限的使用者帳號", placeholder="輸入員工 Email 或帳號...")
        st.multiselect("授權總控管理權限級別", ["超級總控架構師 (Super Admin)", "財務 AR/AP 審核員", "客戶成功與模組配置專員"], default=["超級總控架構師 (Super Admin)"])
        if st.form_submit_button("🛡️ 儲存總控權限變更", type="primary"):
            st.success("🎉 總控中心訪問權限已成功更新！")
