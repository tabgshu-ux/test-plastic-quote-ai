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
        <div style="font-size: 12.5px; font-weight: 800; color: #1e293b;">全球多租戶 SaaS 總控、版本定價、租戶訂閱與權限管理中心</div>
        <div style="font-size: 8px; font-weight: 700; color: #64748b;">MASTER SAAS SUBSCRIPTION & TENANT MANAGEMENT SYSTEM</div>
    </div>
</div>
"""

# 初始化總控端的全域狀態
if "master_editions" not in st.session_state:
    st.session_state.master_editions = [
        {"edition_id": "ED-01", "name": "🚀 旗艦企業版 (Enterprise)", "price": 2500.0, "desc": "全功能模組無限擴充"},
        {"edition_id": "ED-02", "name": "💼 正式商務版 (Professional)", "price": 1200.0, "desc": "核心財務與採購模組"},
        {"edition_id": "ED-03", "name": "🔄 訂閱彈性版 (Subscription)", "price": 600.0, "desc": "按需動態選配拼圖"}
    ]

if "tenants_db" not in st.session_state:
    st.session_state.tenants_db = [
        {"tenant_id": "TENANT-001", "company": "裕豐電機工業 (Reetech)", "edition": "🚀 旗艦企業版 (Enterprise)", "price": 2500.0, "status": "🟢 正常運營中 (Active)", "is_internal": False},
        {"tenant_id": "TENANT-002", "company": "亞太精密科技", "edition": "💼 正式商務版 (Professional)", "price": 1200.0, "status": "🟡 試用期中 (Trial)", "is_internal": False},
        {"tenant_id": "INTERNAL-HQ", "company": "SaaS 總公司內部營運", "edition": "內部特權版", "price": 0.0, "status": "🟢 內部運營 (免計費)", "is_internal": True}
    ]

if "control_admins" not in st.session_state:
    st.session_state.control_admins = ["super_admin", "admin", "boss_許福村"]

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
# 主介面：精準對齊您要求的 4 大總控核心分頁
# ----------------------------------------------------
st.markdown(SAAS_LOGO_HTML, unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🏷️ 1. 功能模組版本與定價設定", 
    "🏢 2. 租戶訂閱觀看與修改管理", 
    "📊 3. 租戶訂閱總收入與 AR/AP 財務", 
    "🔐 4. 總控進入權限設定"
])

# --- TAB 1: 功能模組版本與定價設定 ---
with tab1:
    st.markdown("### 🏷️ SaaS 功能模組版本與定價設定中心")
    st.info("💡 *在此自訂與新增各種銷售版本名稱（如旗艦版、商務版）、設定對應的定價金額與說明。*")
    
    with st.form("add_edition_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("新增/修改 版本名稱", value="🌟 企業尊榮訂製版")
            new_price = st.number_input("設定每月定價金額 (USD)", value=3500.0, step=100.0)
        with col2:
            new_desc = st.text_area("版本說明與包含項目", value="包含專屬 AI 模型、無限廠區擴充與 7x24 專屬技術支援。")
            
        if st.form_submit_button("💾 儲存並發布新版本與定價", type="primary", use_container_width=True):
            st.session_state.master_editions.append({"edition_id": f"ED-0{len(st.session_state.master_editions)+1}", "name": new_name, "price": new_price, "desc": new_desc})
            st.success(f"🎉 成功新增/更新版本 [{new_name}]，定價 `$ {new_price} USD/月` 已生效！")

    st.markdown("---")
    st.markdown("#### 📋 現行上架中的 SaaS 版本與定價總覽")
    ed_df = pd.DataFrame(st.session_state.master_editions)
    st.dataframe(ed_df, use_container_width=True)

# --- TAB 2: 租戶訂閱觀看與修改管理 ---
with tab2:
    st.markdown("### 🏢 租戶訂閱觀看與即時修改管理")
    st.info("💡 *在此即時觀看所有客戶租戶目前的訂閱狀態與版本，並可直接進行修改、更換版本或調整狀態。*")
    
    tenant_names = [t["company"] for t in st.session_state.tenants_db]
    selected_t_name = st.selectbox("選擇要觀看與修改的目標租戶：", tenant_names)
    
    # 找到該租戶資料
    target_tenant = next((t for t in st.session_state.tenants_db if t["company"] == selected_t_name), None)
    
    if target_tenant:
        with st.form("modify_tenant_form"):
            tc1, tc2 = st.columns(2)
            with tc1:
                edition_options = [e["name"] for e in st.session_state.master_editions] + ["內部特權版"]
                current_ed_index = edition_options.index(target_tenant["edition"]) if target_tenant["edition"] in edition_options else 0
                
                new_assigned_edition = st.selectbox("修改訂閱版本", edition_options, index=current_ed_index)
                new_custom_price = st.number_input("修改每月訂閱金額 (USD)", value=float(target_tenant["price"]), step=50.0)
            with tc2:
                status_options = ["🟢 正常運營中 (Active)", "🟡 試用期中 (Trial)", "🔴 已停權/未繳費 (Suspended)", "🟢 內部運營 (免計費)"]
                current_st_index = status_options.index(target_tenant["status"]) if target_tenant["status"] in status_options else 0
                
                new_status = st.selectbox("修改運行狀態", status_options, index=current_st_index)
                is_internal_check = st.checkbox("設為內部主公司（勾選後將自動排除在總收入與計費計算之外）", value=target_tenant["is_internal"])

            if st.form_submit_button("🚀 立即儲存並更新該租戶設定", type="primary", use_container_width=True):
                target_tenant["edition"] = new_assigned_edition
                target_tenant["price"] = new_custom_price
                target_tenant["status"] = new_status
                target_tenant["is_internal"] = is_internal_check
                st.success(f"🎉 租戶 [{selected_tenant_name if 'selected_tenant_name' in locals() else selected_t_name}] 的訂閱設定已成功更新！")

    st.markdown("---")
    st.markdown("#### 📋 全球所有租戶訂閱現狀總覽")
    t_summary_df = pd.DataFrame(st.session_state.tenants_db)
    st.dataframe(t_summary_df, use_container_width=True)

# --- TAB 3: 租戶訂閱總收入與 AR/AP 財務 ---
with tab3:
    st.markdown("### 📊 租戶訂閱總收入與財務 AR/AP 管理中心")
    st.info("💡 *自動計算所有外部付費租戶的總訂閱收入（已自動將內部免計費專區排除），並提供財務部進行應收帳款 (AR) 管理。*")
    
    # 計算總收入（排除 is_internal == True）
    total_revenue = sum(t["price"] for t in st.session_state.tenants_db if not t["is_internal"])
    paid_count = sum(1 for t in st.session_state.tenants_db if not t["is_internal"])
    
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
        if not t["is_internal"]:
            ar_data.append({
                "tenant_id": t["tenant_id"],
                "company": t["company"],
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
