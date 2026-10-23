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
    page_title="Global SaaS AI ERP - Department Lego Control Hub",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

SAAS_LOGO_HTML = """
<div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 15px; padding: 10px; background: #f8fafc; border-radius: 8px; border-bottom: 3px solid #2563eb;">
    <div style="font-size: 26px; font-weight: 900; color: #2563eb; letter-spacing: -1px; line-height: 1;">LEGO ERP Control Hub</div>
    <div style="border-left: 2px solid #cbd5e1; padding-left: 10px; line-height: 1.15;">
        <div style="font-size: 12.5px; font-weight: 800; color: #1e293b;">全球 SaaS 企業部門架構、樂高拼圖模組與版本定價總控中心</div>
        <div style="font-size: 8px; font-weight: 700; color: #64748b;">DEPARTMENT-BASED LEGO APP STORE & TENANT LICENSING SYSTEM</div>
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
        st.markdown("<h2 style='text-align: center; color: #1e293b;'>🔐 總控平台安全登入</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>限平台最高架構師與總控管理員進入</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        username = st.text_input("總控帳號", value="super_admin")
        password = st.text_input("密碼", type="password", value="123")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔑 進入總控平台", use_container_width=True, type="primary"):
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
st.sidebar.markdown("### 🧩 SaaS 總控台")
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
    "🧩 1. 企業部門架構與樂高拼圖模組市集", 
    "🏷️ 2. SaaS 版本定義與定價策略管理", 
    "🏢 3. 客戶租戶開通與模組動態串連", 
    "📊 4. 財務 AR/AP 與內部免計費專區"
])

# --- TAB 1: 企業部門架構與樂高拼圖模組市集 ---
with tab1:
    st.markdown("### 🏢 依標準企業部門勾選樂高拼圖模組 (App Store)")
    st.info("💡 *在此選擇您要設定的目標部門，並勾選該部門所包含的功能拼圖，作為後續版本打包與租戶串連的基礎。*")
    
    # 依照使用者提供的完整企業部門組織架構分類
    department_category = st.selectbox(
        "選擇部門大類：",
        [
            "📈 核心營運與商務部門 (Core Business & Operations)",
            "🛠️ 研發與技術部門 (Research & Technology)",
            "🏭 供應鏈與生產部門 (Supply Chain & Production)",
            "📋 行政與後勤支援部門 (Administration & Support)"
        ]
    )
    
    if "核心營運" in department_category:
        sub_dept = st.selectbox("選擇子部門", ["Sales Department / 業務部", "Marketing Department / 行銷部", "Business Development (BD) / 商務拓展部", "Operations Department / 營運部", "Customer Support (CS) / 客戶服務部"])
    elif "研發與技術" in department_category:
        sub_dept = st.selectbox("選擇子部門", ["Research & Development (R&D) / 研發部", "Information Technology (IT) / 資訊技術部", "Product Management / 產品管理部"])
    elif "供應鏈與生產" in department_category:
        sub_dept = st.selectbox("選擇子部門", ["Procurement / Purchasing / 採購部", "Supply Chain Department / 供應鏈管理部", "Production / Manufacturing / 生產/製造部", "Quality Assurance / QC / 品質保證管制部"])
    else:
        sub_dept = st.selectbox("選擇子部門", ["Human Resources (HR) / 人力資源部", "Finance & Accounting / 財務與會計部", "Legal Department / 法務部", "Administration / 總務部 (行政部)"])
        
    st.markdown("---")
    st.markdown(f"#### ⚙️ 配置部門：`{sub_dept}` 的樂高拼圖功能")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("##### 🌟 核心營運與戰情拼圖")
        b1 = st.checkbox("📊 全球原料價格與即時匯率看板", value=True)
        b2 = st.checkbox("📈 企業戰情室與跨國 BI 分析", value=True)
        b3 = st.checkbox("🏭 MES 生產製造與 IoT 稼動率監控", value=True)
        b4 = st.checkbox("🤖 AI 語音與多模態智慧輸入", value=True)
    with col_m2:
        st.markdown("##### 📦 業務、行政與供應鏈拼圖")
        b5 = st.checkbox("🛒 總務採購與多幣別請購單", value=True)
        b6 = st.checkbox("✍️ 全方位電子簽核中心 (BPM)", value=True)
        b7 = st.checkbox("🧾 跨國電子發票與稅號 MST 解析", value=True)
        b8 = st.checkbox("📦 全球供應鏈倉儲與條碼 WMS", value=True)

    if st.button("💾 儲存此部門的樂高拼圖模組對應", type="primary"):
        st.success(f"🎉 成功為部門 [{sub_dept}] 綁定所選的樂高拼圖模組！")

# --- TAB 2: SaaS 版本定義與定價策略管理 ---
with tab2:
    st.markdown("### 🏷️ SaaS 銷售版本定義與定價管理中心")
    st.info("💡 *在此設定不同的銷售版本（如旗艦企業版、正式商務版、訂閱彈性版、個人微型版），並定義其包含哪些部門拼圖與對應月費金額。*")
    
    ed1, ed2 = st.columns(2)
    with ed1:
        edition_name = st.selectbox(
            "選擇要定義的 SaaS 版本",
            ["🚀 旗艦企業版 (Enterprise Edition)", "💼 正式商務版 (Professional Edition)", "🔄 訂閱彈性版 (Subscription Edition)", "👤 個人微型版 (Personal Edition)"]
        )
        base_price = st.number_input("設定基準月訂閱金額 (USD / 月)", value=2500.0, step=100.0)
    with ed2:
        edition_desc = st.text_area("版本功能說明與備註", value="包含全功能模組、多廠區無限擴充、專屬 AI 語音與 IoT 聯網支援。")
        
    st.markdown("#### 🔗 勾選此版本包含的部門與拼圖模組")
    inc1, inc2 = st.columns(2)
    with inc1:
        st.checkbox("✅ 包含：核心商務與業務/行銷模組", value=True)
        st.checkbox("✅ 包含：研發與 IT 資訊管理模組", value=True)
    with inc2:
        st.checkbox("✅ 包含：供應鏈與 MES 生產製造模組", value=True)
        st.checkbox("✅ 包含：人資、財務與法務後勤模組", value=True)

    if st.button("💾 儲存版本定義與定價規則", type="primary"):
        st.success(f"🎉 成功儲存 [{edition_name}] 的定價規則：`$ {base_price} USD/月`！")

    st.markdown("---")
    st.markdown("#### 📋 目前已定義的 SaaS 版本與定價總覽")
    edition_df = pd.DataFrame([
        {"edition": "旗艦企業版 (Enterprise)", "price_usd": 2500, "included_modules": "全功能 (16個模組全開)", "status": "🟢 上架販售中"},
        {"edition": "正式商務版 (Professional)", "price_usd": 1200, "included_modules": "財務、採購、銷售、人資 (8個模組)", "status": "🟢 上架販售中"},
        {"edition": "訂閱彈性版 (Subscription)", "price_usd": 600, "included_modules": "按需單模組動態訂閱", "status": "🟢 上架販售中"},
        {"edition": "個人微型版 (Personal)", "price_usd": 150, "included_modules": "基礎辦公與筆記報價", "status": "🟢 上架販售中"}
    ])
    st.dataframe(edition_df, use_container_width=True)

# --- TAB 3: 客戶租戶開通與模組動態串連 ---
with tab3:
    st.markdown("### 🏢 客戶租戶開通與樂高拼圖模組動態串連")
    st.info("💡 *選擇您的客戶租戶（例如：裕豐電機工業），为其指派銷售版本。系統將依據版本定義，自動為其串連並解鎖對應的部門與模組拼圖功能。*")
    
    tenant_target = st.selectbox(
        "選擇目標客戶租戶：",
        ["TENANT-001 | 裕豐電機工業 (Reetech Industrial) - 越南/台灣", "TENANT-002 | 亞太精密科技 - 馬來西亞分公司"]
    )
    
    tc1, tc2 = st.columns(2)
    with tc1:
        assigned_edition = st.selectbox("指派販售版本", ["🚀 旗艦企業版 (Enterprise Edition)", "💼 正式商務版 (Professional Edition)", "🔄 訂閱彈性版 (Subscription Edition)", "👤 個人微型版 (Personal Edition)"])
        actual_price = st.number_input("確認該租戶成交月費 (USD)", value=2500.0, step=100.0)
    with tc2:
        run_status = st.selectbox("租戶狀態", ["🟢 正式運營中 (Active)", "🟡 試用期中 (Trial)", "🔴 已停權 (Suspended)"])
        st.markdown("**🔗 樂高自動串連狀態**：已依據版本定義自動開通對應部門模組。")

    if st.button("🚀 確認開通租戶並啟動樂高模組串連", type="primary"):
        st.success(f"🎉 租戶 [{tenant_target}] 已成功套用 [{assigned_edition}]，所有樂高拼圖模組已即時為其串連開通！")

    st.markdown("---")
    st.markdown("#### 📋 全球租戶與樂高串連狀態總覽")
    tenant_summary = pd.DataFrame([
        {"tenant_id": "TENANT-001", "company": "裕豐電機工業", "edition": "旗艦企業版", "monthly_fee_usd": 2500, "status": "🟢 運營中", "lego_status": "16個部門拼圖全串連"},
        {"tenant_id": "TENANT-002", "company": "亞太精密科技", "edition": "正式商務版", "monthly_fee_usd": 1200, "status": "🟡 試用期", "lego_status": "8個部門拼圖已串連"}
    ])
    st.dataframe(tenant_summary, use_container_width=True)

# --- TAB 4: 財務 AR/AP 與內部免計費專區 ---
with tab4:
    st.markdown("### 📊 SaaS 財務 AR/AP 中心與內部主公司專區")
    f_tab1, f_tab2 = st.tabs(["💰 財務應收/應付帳款 (AR/AP)", "🏠 內部主公司營運專區 (免計費)"])
    
    with f_tab1:
        st.markdown("#### 💳 全球租戶應收帳款 (AR) 與營收統計")
        mc1, mc2 = st.columns(2)
        with mc1:
            st.metric(label="🌐 總預估月營收 (USD)", value="$ 3,700", delta="+12%")
        with mc2:
            st.metric(label="📋 本月待收帳款 (AR)", value="$ 1,200", delta="1 筆待催收")
            
        ar_table = pd.DataFrame([
            {"tenant_id": "TENANT-001", "company": "裕豐電機工業", "version": "旗艦企業版", "amount_usd": 2500, "ar_status": "🟢 已收款 (Paid)"},
            {"tenant_id": "TENANT-002", "company": "亞太精密科技", "version": "正式商務版", "amount_usd": 1200, "ar_status": "🟡 待收款 (Pending)"}
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
