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
    page_title="Global Multi-Tenant SaaS AI ERP",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------
# 🏢 SaaS 總控平台品牌 Logo 橫幅
# ----------------------------------------------------
SAAS_LOGO_HTML = """
<div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 15px; padding: 10px; background: #f8fafc; border-radius: 8px; border-bottom: 3px solid #2563eb;">
    <div style="font-size: 28px; font-weight: 900; color: #2563eb; letter-spacing: -1px; line-height: 1;">SaaS AI ERP</div>
    <div style="border-left: 2px solid #cbd5e1; padding-left: 10px; line-height: 1.15;">
        <div style="font-size: 13px; font-weight: 800; color: #1e293b;">全球多租戶雲端 SaaS 總控平台</div>
        <div style="font-size: 8.5px; font-weight: 700; color: #64748b;">GLOBAL MULTI-TENANT SAAS CLOUD PLATFORM • (當前測試租戶：裕豐電機工業)</div>
    </div>
</div>
"""

t = {
    "login_title": "🌐 SaaS AI ERP 雲端平台登入",
    "subtitle": "Global Multi-Tenant SaaS Platform Control Center",
    "username": "平台管理員帳號 (admin)",
    "password": "密碼 (預設 123)",
    "login_btn": "🔑 安全登入系統",
    "logout_btn": "🚪 登出系統",
    "tabs": ["📈 企業戰情", "👔 行政人事", "💰 財務會計", "🏭 生產與資產", "📦 供應鏈與系統"],
}

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
# 登入驗證畫面（置中對齊優化）
# ----------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_name = ""

if not st.session_state.logged_in:
    # 完美置中配置：使用三欄式版面，將登入卡片置於中間
    col_left, col_center, col_right = st.columns([1, 1.5, 1])
    
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(SAAS_LOGO_HTML, unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #1e293b;'>{t['login_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>{t['subtitle']}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        username = st.text_input(t["username"], value="admin")
        password = st.text_input(t["password"], type="password", value="123")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(t["login_btn"], use_container_width=True, type="primary"):
            if password == "123":
                st.session_state.logged_in = True
                st.session_state.user_role = "admin"
                st.session_state.user_name = username
                st.rerun()
            else:
                st.error("❌ 帳號或密碼錯誤 / Incorrect password")
        st.markdown("<br><br>", unsafe_allow_html=True)
    st.stop()

# ----------------------------------------------------
# 側邊欄設定
# ----------------------------------------------------
st.sidebar.markdown("### 🌐 SaaS 總控平台")
st.sidebar.markdown(f"**👤 {st.session_state.user_name}** (`{st.session_state.user_role.upper()}`)")
st.sidebar.info("🏢 當前依附測試租戶：\n**裕豐電機工業 (Reetech)**")
if st.sidebar.button(t["logout_btn"], use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

# ----------------------------------------------------
# 主介面：直覺的大型分頁導航 (Tabs)
# ----------------------------------------------------
st.markdown(SAAS_LOGO_HTML, unsafe_allow_html=True)

tenant_info = {"tenant_id": "TENANT-001", "company_name": "裕豐電機工業 (Reetech Industrial)"}
user_perms = ["admin", "finance", "mes", "ga"]

tab1, tab2, tab3, tab4, tab5 = st.tabs(t["tabs"])

with tab1:
    st.markdown("### 📈 企業戰情室與 BI 分析")
    safe_call_module(dashboard_bi.render_dashboard_bi, tenant_info, user_perms)

with tab2:
    st.markdown("### 👔 行政管理與人事差勤中心")
    sub_choice = st.selectbox("選擇管理功能：", ["員工與薪資管理", "請假與差勤管理", "總務採購與請購", "電子簽核中心", "組織架構與匯率"])
    if "員工" in sub_choice:
        safe_call_module(employee_management.render_employee_management, tenant_info)
    elif "請假" in sub_choice:
        safe_call_module(leave_attendance.render_leave_attendance, tenant_info)
    elif "總務採購" in sub_choice:
        safe_call_module(ga_procurements.render_ga_procurements, tenant_info)
    elif "電子簽核" in sub_choice:
        safe_call_module(approval_center.render_approval_center, tenant_info, user_perms)
    else:
        safe_call_module(org_management.render_org_management, tenant_info, user_perms)

with tab3:
    st.markdown("### 💰 財務會計與稅務中心")
    sub_choice = st.selectbox("選擇財務功能：", ["跨國應付帳款 (Finance AP)", "跨國電子發票解析", "多國動態稅制與總帳"])
    if "應付帳款" in sub_choice:
        safe_call_module(finance_ap.render_finance_ap, tenant_info, user_perms)
    elif "電子發票" in sub_choice:
        safe_call_module(invoice_parsing.render_invoice_parsing, tenant_info, user_perms)
    else:
        safe_call_module(tax_ledger.render_tax_ledger, tenant_info, user_perms)

with tab4:
    st.markdown("### 🏭 生產製造、資產與合約中心")
    sub_choice = st.selectbox("選擇廠務功能：", ["MES 生產製造與 IoT 監控", "固定資產與模具管理", "行政公文與合約列管", "AI 多模態無門檻輸入"])
    if "MES" in sub_choice:
        safe_call_module(mes_production.render_mes_production, tenant_info, user_perms)
    elif "固定資產" in sub_choice:
        safe_call_module(asset_management.render_asset_management, tenant_info, user_perms)
    elif "行政公文" in sub_choice:
        safe_call_module(ga_contracts.render_ga_contracts, tenant_info, user_perms)
    else:
        safe_call_module(ai_multimodal.render_ai_multimodal, tenant_info, user_perms)

with tab5:
    st.markdown("### 📦 供應鏈、倉儲與 API 閘道器")
    sub_choice = st.selectbox("選擇供應鏈與系統功能：", ["供應鏈與業務報價", "全球供應鏈倉儲 (WMS)", "第三方 API 閘道器配置"])
    if "供應鏈與業務報價" in sub_choice:
        safe_call_module(supply_chain.render_supply_chain, tenant_info, user_perms)
    elif "倉儲" in sub_choice:
        safe_call_module(inventory_wms.render_inventory_wms, tenant_info, user_perms)
    else:
        safe_call_module(api_gateway_config.render_api_gateway_config, tenant_info, user_perms)
