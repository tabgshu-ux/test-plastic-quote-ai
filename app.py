import streamlit as st
import pandas as pd
import modules.database as db_conn
# 直接調用您已經寫好的現有樂高模組市集檔案！
import modules.app_store as app_store  

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
        <div style="font-size: 12.5px; font-weight: 800; color: #1e293b;">全球多租戶 SaaS 總控與樂高模組市集管理中心</div>
        <div style="font-size: 8px; font-weight: 700; color: #64748b;">MULTI-TENANT SAAS APP STORE & CONTROL CENTER</div>
    </div>
</div>
"""

# ----------------------------------------------------
# 1. 總控安全登入
# ----------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_name = ""

# 初始化全平台獨立模組庫與測試租戶資料 (供 app_store 使用)
if "master_module_library" not in st.session_state:
    st.session_state.master_module_library = {
        "🌟 核心高階戰情": ["全球原料價格與匯率看板", "跨國總損益與資產負債表", "企業戰情室與跨國 BI 分析"],
        "🏭 生產製造與廠務": ["MES 生產製造與 IoT 稼動率監控", "固定資產與模具防混淆", "全球供應鏈倉儲與條碼 WMS"],
        "📦 業務、行政與財務": ["總務採購與多幣別請購單", "全方位電子簽核中心 (BPM)", "跨國電子發票與稅號解析", "AI 語音與多模態智慧輸入"]
    }

if "current_tenant_mock" not in st.session_state:
    st.session_state.current_tenant_mock = {
        "name": "裕豐電機工業 (Reetech Industrial)",
        "price_usd": 2500.0,
        "dept_modules_db": {},
        "org_nodes": []
    }

if not st.session_state.logged_in:
    col_l, col_c, col_r = st.columns([1, 1.5, 1])
    with col_c:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(SAAS_LOGO_HTML, unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #1e293b;'>🔐 總控平台安全登入</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        username = st.text_input("總控管理員帳號", value="admin")
        password = st.text_input("密碼", type="password", value="123")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔑 進入總控平台", use_container_width=True, type="primary"):
            if password == "123":
                st.session_state.logged_in = True
                st.session_state.user_role = "admin"
                st.session_state.user_name = username
                st.rerun()
            else:
                st.error("❌ 密碼錯誤")
    st.stop()

# ----------------------------------------------------
# 側邊欄控制
# ----------------------------------------------------
st.sidebar.markdown("### 🌐 SaaS 總控後台")
st.sidebar.markdown(f"**👤 管理員: {st.session_state.user_name}**")
st.sidebar.success("🟢 總控存取權限：已授權")
if st.sidebar.button("🚪 登出總控中心", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

# ----------------------------------------------------
# 主介面：串連現有的 app_store 模組
# ----------------------------------------------------
st.markdown(SAAS_LOGO_HTML, unsafe_allow_html=True)

tab1, tab2 = st.tabs([
    "🧩 1. 樂高積木模組市集 (App Store)", 
    "📊 2. 財務 AR/AP 與租戶營收管理"
])

with tab1:
    # 定義部門清單，直接傳入您寫好的 app_store 渲染函式[cite: 12]
    all_departments = [
        "👑 董事長室 / 經營企劃室 (Executive & Board)",
        "👥 人力資源與行政管理部 (HR & Admin)",
        "💰 財務與資本運作部 (Finance)",
        "🛒 供應鏈與進銷存管理 (SCM)",
        "🏭 生產製造與廠務部 (Manufacturing)",
        "🛠️ 工程技術與設計部 (Engineering)",
        "💻 資訊技術與系統開發部 (IT)"
    ]
    app_store.render_app_store(st.session_state.current_tenant_mock, all_departments)

with tab2:
    st.markdown("### 📊 財務 AR/AP 與租戶營收管理中心")
    st.metric(label="🌐 當前租戶預估月訂閱費 (USD)", value=f"$ {st.session_state.current_tenant_mock['price_usd']} USD")
    st.info("💡 *在此檢視各租戶的應收帳款 (AR) 狀況，並進行催收與財務對帳。*")
    
    ar_df = pd.DataFrame([
        {"tenant_id": "TENANT-001", "company": "裕豐電機工業", "plan": "樂高動態自訂版", "fee_usd": st.session_state.current_tenant_mock['price_usd'], "status": "🟢 正常運營中"}
    ])
    st.dataframe(ar_df, use_container_width=True)
