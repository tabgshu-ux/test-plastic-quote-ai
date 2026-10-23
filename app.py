import streamlit as st
import pandas as pd
import modules.database as db_conn
import modules.app_store as app_store

st.set_page_config(
    page_title="Global SaaS AI ERP - Master Control Hub",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

SAAS_LOGO_HTML = """
<div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 15px; padding: 10px; background: #f8fafc; border-radius: 8px; border-bottom: 3px solid #2563eb;">
    <div style="font-size: 26px; font-weight: 900; color: #2563eb; letter-spacing: -1px; line-height: 1;">Master Control Hub</div>
    <div style="border-left: 2px solid #cbd5e1; padding-left: 10px; line-height: 1.15;">
        <div style="font-size: 12.5px; font-weight: 800; color: #1e293b;">全球多租戶 SaaS 總控、產業別組織架構、樂高市集與國家地區管理中心</div>
        <div style="font-size: 8px; font-weight: 700; color: #64748b;">MASTER SAAS INDUSTRY-BASED TENANT MANAGEMENT SYSTEM</div>
    </div>
</div>
"""

# 初始化全域狀態（確保所有欄位完整，絕不發生 KeyError）
if "master_editions" not in st.session_state:
    st.session_state.master_editions = [
        {"edition_id": "ED-01", "name": "🚀 旗艦企業版 (Enterprise)", "price": 2500.0, "desc": "全功能模組無限擴充"},
        {"edition_id": "ED-02", "name": "💼 正式商務版 (Professional)", "price": 1200.0, "desc": "核心財務與採購模組"},
        {"edition_id": "ED-03", "name": "🔄 訂閱彈性版 (Subscription)", "price": 600.0, "desc": "按需動態選配拼圖"}
    ]

if "tenants_db" not in st.session_state:
    st.session_state.tenants_db = [
        {
            "tenant_id": "TENANT-001", 
            "company": "裕豐電機工業 (Reetech)", 
            "industry": "⚡ 傳統電機與重工業製造", 
            "country": "台灣 / 越南", 
            "region": "越南平陽廠", 
            "edition": "🚀 旗艦企業版 (Enterprise)", 
            "price": 2500.0, 
            "status": "🟢 正常運營中 (Active)", 
            "is_internal": False, 
            "used_modules": ["MES 生產製造", "電子簽核", "供應鏈報價"]
        },
        {
            "tenant_id": "TENANT-002", 
            "company": "亞太精密科技", 
            "industry": "💻 電子高科技與半導體業", 
            "country": "馬來西亞", 
            "region": "吉隆坡總部", 
            "edition": "💼 正式商務版 (Professional)", 
            "price": 1200.0, 
            "status": "🟡 試用期中 (Trial)", 
            "is_internal": False, 
            "used_modules": ["總務採購", "員工薪資"]
        },
        {
            "tenant_id": "INTERNAL-HQ", 
            "company": "SaaS 總公司內部營運", 
            "industry": "🌐 SaaS 軟體與雲服務業", 
            "country": "台灣", 
            "region": "台北總部", 
            "edition": "內部特權版", 
            "price": 0.0, 
            "status": "🟢 內部運營 (免計費)", 
            "is_internal": True, 
            "used_modules": ["全功能解鎖"]
        }
    ]

if "control_admins" not in st.session_state:
    st.session_state.control_admins = ["super_admin", "admin", "boss_許福村"]

if "master_module_library" not in st.session_state:
    st.session_state.master_module_library = {
        "🌟 核心高階戰情": ["全球原料價格與匯率看板", "跨國總損益與資產負債表", "企業戰情室與跨國 BI 分析"],
        "🏭 生產製造與廠務": ["MES 生產製造與 IoT 稼動率監控", "固定資產與模具防混淆", "全球供應鏈倉儲與條碼 WMS"],
        "📦 業務、行政與財務": ["總務採購與多幣別請購單", "全方位電子簽核中心 (BPM)", "跨國電子發票與稅號解析", "AI 語音與多模態智慧輸入"]
    }

# ----------------------------------------------------
# 1. 總控中心登入與權限檢查
# ----------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""

if not st.session_state.logged_in:
    col_l, col_c, col_r = st.columns([1, 1.5, 1])
    with col_c:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(SAAS_LOGO_HTML, unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #1e293b;'>🔐 總控中心安全登入</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>系統將自動驗證是否具備總控進入權限</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        username = st.text_input("請輸入您的總控帳號", value="super_admin")
        password = st.text_input("密碼", type="password", value="123")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔑 驗證並進入總控中心", use_container_width=True, type="primary"):
            if password == "123" and (username in st.session_state.control_admins or username == "super_admin"):
                st.session_state.logged_in = True
                st.session_state.user_name = username
                st.rerun()
            else:
                st.error("❌ 登入失敗：密碼錯誤，或者您的帳號未被授權進入總控中心！")
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
# 主介面：四大核心分頁
# ----------------------------------------------------
st.markdown(SAAS_LOGO_HTML, unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🏭 1. 依【產業別】設定部門與樂高拼圖 (圖一)", 
    "🏢 2. 租戶訂閱觀看、模組修改與國家地區搜尋 (圖二/三)", 
    "📊 3. 租戶訂閱總收入與 AR/AP 財務", 
    "🔐 4. 總控進入權限設定"
])

# --- TAB 1: 依產業別設定部門與樂高拼圖 (圖一) ---
with tab1:
    st.markdown("### 🏭 依【產業別】進行部門組織架構與樂高拼圖設定")
    st.info("💡 *在此選擇客戶的產業別（例如：傳統電機製造業、電子高科技業），系統會自動載入對應的部門，並透過樂高拼圖市集勾選與解鎖功能。*")
    
    selected_industry = st.selectbox(
        "📂 請選擇目標產業別 (Industry Category)：",
        [
            "⚡ 傳統電機與重工業製造 (Machinery & Heavy Industry)",
            "💻 電子高科技與半導體業 (Electronics & Semiconductor)",
            "🌍 跨國貿易與物流服務業 (Global Trading & Logistics)",
            "🩺 生技醫療與製藥業 (Biotech & Pharmaceuticals)"
        ]
    )
    
    st.markdown(f"#### ⚙️ 當前設定產業：`{selected_industry}` 的部門與樂高拼圖市集")
    
    # 對應呼叫您寫好的 app_store 模組
    all_depts_by_industry = [
        "👑 董事長室 / 經營企劃室 (Executive & Board)",
        "👥 人力資源與行政管理部 (HR & Admin)",
        "💰 財務與資本運作部 (Finance)",
        "🛒 供應鏈與進銷存管理 (SCM)",
        "🏭 生產製造與廠務部 (Manufacturing & Plant)",
        "🛠️ 工程技術與設計部 (Engineering)"
    ]
    
    mock_tenant_industry = {
        "name": f"【產業範本：{selected_industry.split('(')[0]}】",
        "price_usd": 2500.0,
        "dept_modules_db": {},
        "org_nodes": []
    }
    app_store.render_app_store(mock_tenant_industry, all_depts_by_industry)

# --- TAB 2: 租戶訂閱觀看、模組修改與國家地區搜尋 (圖二/三) ---
with tab2:
    st.markdown("### 🏢 租戶訂閱觀看、模組修改與國家/地區搜尋中心")
    st.info("💡 *在此依據【國家】、【地區】、【產業別】或【使用版本】進行搜尋，觀看各租戶目前使用的功能模組，若有問題可隨時修改！*")
    
    # 搜尋與過濾條件區 (符合圖三需求)
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        search_country = st.selectbox("🌍 依國家篩選", ["全部", "台灣 / 越南", "馬來西亞", "台灣"])
    with s_col2:
        search_industry = st.selectbox("🏭 依產業別篩選", ["全部", "傳統電機", "電子高科技", "SaaS 軟體"])
    with s_col3:
        search_region = st.text_input("📍 依廠區關鍵字", placeholder="例: 平陽廠...")
    with s_col4:
        search_edition = st.selectbox("🏷️ 依版本篩選", ["全部", "🚀 旗艦企業版 (Enterprise)", "💼 正式商務版 (Professional)"])

    # 過濾租戶資料
    filtered_tenants = st.session_state.tenants_db
    if search_country != "全部":
        filtered_tenants = [t for t in filtered_tenants if search_country in t.get("country", "")]
    if search_industry != "全部":
        filtered_tenants = [t for t in filtered_tenants if search_industry in t.get("industry", "")]
    if search_region:
        filtered_tenants = [t for t in filtered_tenants if search_region.lower() in t.get("region", "").lower()]
    if search_edition != "全部":
        filtered_tenants = [t for t in filtered_tenants if search_edition in t.get("edition", "")]

    st.markdown("---")
    st.markdown(f"#### 🔍 搜尋結果（共找到 {len(filtered_tenants)} 家租戶）")
    
    display_df = pd.DataFrame(filtered_tenants)
    st.dataframe(display_df, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🛠️ 租戶功能模組檢視與即時修改 (符合圖二需求)")
    tenant_names = [t["company"] for t in st.session_state.tenants_db]
    selected_t_name = st.selectbox("選擇要檢視與修改的目標租戶：", tenant_names)
    
    target_tenant = next((t for t in st.session_state.tenants_db if t["company"] == selected_t_name), None)
    
    if target_tenant:
        st.markdown(f"**當前租戶產業別**：`{target_tenant.get('industry', '未設定')}`")
        st.markdown(f"**當前租戶使用中的模組清單**：`{', '.join(target_tenant.get('used_modules', []))}`")
        
        with st.form("modify_tenant_form_detailed"):
            tc1, tc2 = st.columns(2)
            with tc1:
                edition_options = [e["name"] for e in st.session_state.master_editions] + ["內部特權版"]
                current_ed_index = edition_options.index(target_tenant["edition"]) if target_tenant["edition"] in edition_options else 0
                
                new_assigned_edition = st.selectbox("修改訂閱版本", edition_options, index=current_ed_index)
                new_custom_price = st.number_input("修改每月訂閱金額 (USD)", value=float(target_tenant["price"]), step=50.0)
                new_country = st.text_input("修改國家", value=target_tenant.get("country", ""))
            with tc2:
                status_options = ["🟢 正常運營中 (Active)", "🟡 試用期中 (Trial)", "🔴 已停權/未繳費 (Suspended)", "🟢 內部運營 (免計費)"]
                current_st_index = status_options.index(target_tenant["status"]) if target_tenant["status"] in status_options else 0
                
                new_status = st.selectbox("修改運行狀態", status_options, index=current_st_index)
                new_region = st.text_input("修改廠區/地區", value=target_tenant.get("region", ""))
                is_internal_check = st.checkbox("設為內部主公司（勾選後將自動排除在總收入與計費計算之外）", value=target_tenant.get("is_internal", False))

            st.markdown("##### 🧩 該租戶專屬樂高拼圖模組開關調整")
            mod_options_all = ["MES 生產製造", "電子簽核", "供應鏈報價", "總務採購", "員工薪資", "固定資產與模具", "AI 多模態輸入"]
            current_mods = target_tenant.get("used_modules", [])
            selected_mods_updated = []
            
            um_cols = st.columns(3)
            for idx, m_item in enumerate(mod_options_all):
                with um_cols[idx % 3]:
                    if st.checkbox(m_item, value=m_item in current_mods, key=f"tenant_mod_{target_tenant['tenant_id']}_{m_item}"):
                        selected_mods_updated.append(m_item)

            if st.form_submit_button("🚀 立即儲存並更新該租戶的所有設定與模組權限", type="primary", use_container_width=True):
                target_tenant["edition"] = new_assigned_edition
                target_tenant["price"] = new_custom_price
                target_tenant["status"] = new_status
                target_tenant["country"] = new_country
                target_tenant["region"] = new_region
                target_tenant["is_internal"] = is_internal_check
                target_tenant["used_modules"] = selected_mods_updated
                st.success(f"🎉 租戶 [{selected_t_name}] 的版本、產業別、國家地區與樂高拼圖模組權限已成功更新！")

# --- TAB 3: 租戶訂閱總收入與 AR/AP 財務 ---
with tab3:
    st.markdown("### 📊 租戶訂閱總收入與財務 AR/AP 管理中心")
    st.info("💡 *自動計算所有外部付費租戶的總訂閱收入（已自動將內部免計費專區排除），並提供財務部進行應收帳款 (AR) 管理。*")
    
    total_revenue = sum(t["price"] for t in st.session_state.tenants_db if not t.get("is_internal", False))
    paid_count = sum(1 for t in st.session_state.tenants_db if not t.get("is_internal", False))
    
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        st.metric(label="💰 外部付費租戶總月收 (USD)", value=f"$ {total_revenue:,.2f} USD", delta="排除內部免計費公司")
    with mc2:
        st.metric(label="🌐 實際計費付費租戶數", value=f"{paid_count} 家")
    with mc3:
        st.metric(label="📋 財務對帳狀態", value="🟢 帳務平衡正常")

    st.markdown("---")
    st.markdown("#### 💳 租戶應收帳款 (AR) 財務清單")
    ar_data = []
    for t in st.session_state.tenants_db:
        if not t.get("is_internal", False):
            ar_data.append({
                "tenant_id": t["tenant_id"],
                "company": t["company"],
                "industry": t.get("industry", ""),
                "country": t.get("country", ""),
                "edition": t["edition"],
                "monthly_fee_usd": t["price"],
                "ar_status": "🟢 已收訖 (Paid)" if "正常" in t["status"] else "🟡 待催收 (Pending)"
            })
    st.dataframe(pd.DataFrame(ar_data), use_container_width=True)

# --- TAB 4: 總控進入權限設定 ---
with tab4:
    st.markdown("### 🔐 總控中心進入權限與管理者帳號設定")
    st.info("💡 *設定哪些內部人員的帳號具備權限可以開啟與進入這套「SaaS 總控中心」。未授權的帳號將無法登入。*")
    
    with st.form("admin_auth_form"):
        new_admin_acc = st.text_input("新增具備總控進入權限的帳號", placeholder="輸入員工帳號...")
        
        if st.form_submit_button("🛡️ 授權並加入總控白名單", type="primary", use_container_width=True):
            if new_admin_acc and new_admin_acc not in st.session_state.control_admins:
                st.session_state.control_admins.append(new_admin_acc)
                st.success(f"🎉 成功授權帳號 [{new_admin_acc}]！該帳號現在可以順利登入總控中心。")
            else:
                st.warning("⚠️ 帳號空白或已在總控白名單中。")

    st.markdown("---")
    st.markdown("#### 👥 當前具備總控進入權限的管理員名單")
    for adm in st.session_state.control_admins:
        st.markdown(f"- 🛡️ `帳號: {adm}` (具備最高總控權限)")
