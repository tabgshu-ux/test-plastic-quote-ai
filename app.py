# app.py - 全球多租戶 SaaS ERP 總控台（修正版）
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="全球多產業 AI ERP 雲端總控台",
    page_icon="☁️",
    layout="wide"
)

# 安全載入拼圖市集模組
try:
    from modules.app_store import render_app_store
except ImportError:
    try:
        from app_store import render_app_store
    except ImportError:
        def render_app_store(current_tenant=None, all_departments=None):
            st.error("⚠️ 找不到 modules/app_store.py 模組。")

# 1. 平台管理員登入機制
if "platform_admin_logged" not in st.session_state:
    st.session_state.platform_admin_logged = False

if not st.session_state.platform_admin_logged:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown("## ☁️ 全球 SaaS ERP 平台總控登入")
        st.info("💡 請輸入總控台管理員帳號以管理全球多租戶。")
        
        with st.form("admin_login_form"):
            admin_user = st.text_input("管理員帳號", value="admin")
            admin_pass = st.text_input("管理員密碼", type="password", value="123456")
            login_submit = st.form_submit_button("登入全球總控台", type="primary", use_container_width=True)
            
            if login_submit:
                if admin_user == "admin" and admin_pass == "123456":
                    st.session_state.platform_admin_logged = True
                    st.rerun()
                else:
                    st.error("❌ 帳號或密碼錯誤（預設：admin / 123456）")
    st.stop()

# 2. 全球多租戶資料庫初始化
if "global_tenants_db" not in st.session_state:
    st.session_state.global_tenants_db = {
        "裕豐電機工業 (Reetech Industrial)": {
            "tenant_id": "TENANT-001",
            "edition_name": "🚀 旗艦企業版 (Enterprise)",
            "price_usd": 2500.0,
            "custom_org_chart": ["👑 董事會 / CEO Office", "🛠️ 工程部", "🔬 設計部", "🏭 生產部", "📦 倉庫組", "🔩 板金組"],
            "dept_modules_db": {},
            "billing_history": [
                {"期數": "2026/Q1", "應收金額 (USD)": 2500.0, "狀態": "已結算", "對帳單號": "INV-2026-001"},
                {"期數": "2026/Q2", "應收金額 (USD)": 2500.0, "狀態": "待對帳", "對帳單號": "INV-2026-002"}
            ]
        },
        "全球雲端科技 SaaS (Global Cloud Inc.)": {
            "tenant_id": "TENANT-002",
            "edition_name": "🌟 專業 SaaS 版",
            "price_usd": 1200.0,
            "custom_org_chart": ["👑 董事會", "💻 研發處"],
            "dept_modules_db": {},
            "billing_history": [
                {"期數": "2026/Q1", "應收金額 (USD)": 1200.0, "狀態": "已結算", "對帳單號": "INV-2026-003"}
            ]
        }
    }

# 3. 側邊欄總控導覽與當前租戶切換
st.sidebar.markdown("### ☁️ 全球 SaaS ERP 總控台")
st.sidebar.success("👤 平台總管理者 (Platform Admin)")

tenant_names = list(st.session_state.global_tenants_db.keys())
selected_tenant_name = st.sidebar.selectbox("🌐 切換當前操作租戶", tenant_names, key="tenant_selector_box")

current_tenant_data = st.session_state.global_tenants_db[selected_tenant_name]

st.sidebar.markdown("---")
nav_mode = st.sidebar.radio(
    "平台導覽選單", 
    [
        "🧩 樂高模組拼圖市集 (App Store)", 
        "📊 當前租戶營運總覽", 
        "💰 多租戶對帳與帳務結算",
        "⚙️ 全球租戶管理與新增"
    ],
    key="global_main_nav_radio"
)

if st.sidebar.button("🔒 登出總控台", use_container_width=True):
    st.session_state.platform_admin_logged = False
    st.rerun()

# 4. 頁面功能分流渲染
if nav_mode == "🧩 樂高模組拼圖市集 (App Store)":
    st.markdown(f"### 🧩 App Store 配置中：【{selected_tenant_name}】")
    render_app_store(current_tenant=selected_tenant_name)

elif nav_mode == "📊 當前租戶營運總覽":
    st.markdown(f"## 📊 租戶營運總覽：{selected_tenant_name}")
    st.info("💡 在此檢視該租戶的訂閱版本與已開通部門模組明細。")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("租戶代號", current_tenant_data.get("tenant_id", ""))
    with col2:
        st.metric("當前銷售版本", current_tenant_data.get("edition_name", ""))
    with col3:
        st.metric("每月總訂閱金額", f"$ {current_tenant_data.get('price_usd', 0)} USD")
    
    st.markdown("### 🏢 已開通部門與模組明細")
    active_db = current_tenant_data.get("dept_modules_db", {})
    if active_db:
        overview_list = []
        for dept, mods in active_db.items():
            overview_list.append({
                "部門名稱": dept,
                "開通模組數": len(mods),
                "功能明細": ", ".join(mods)
            })
        st.dataframe(pd.DataFrame(overview_list), use_container_width=True)
    else:
        st.warning("⚠️ 此租戶目前尚未在拼圖市集中勾選任何部門模組。")

elif nav_mode == "💰 多租戶對帳與帳務結算":
    st.markdown(f"## 💰 帳務與對帳中心：{selected_tenant_name}")
    st.info("💡 管理該租戶的歷史帳單、期數結算與應收帳款對帳。")
    
    st.markdown("### 📄 歷史對帳單清單")
    billing_df = pd.DataFrame(current_tenant_data.get("billing_history", []))
    st.dataframe(billing_df, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### ➕ 手動新增該租戶對帳單")
    with st.form("tenant_billing_form"):
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            period_val = st.text_input("結算期數", value="2026/Q3")
        with b_col2:
            amount_val = st.number_input("應收金額 (USD)", value=float(current_tenant_data.get("price_usd", 2500.0)), step=100.0)
            
        if st.form_submit_button("📥 產生新帳單", type="primary", use_container_width=True):
            new_inv_id = f"INV-2026-{len(current_tenant_data['billing_history']) + 1:03d}"
            current_tenant_data["billing_history"].append({
                "期數": period_val,
                "應收金額 (USD)": amount_val,
                "狀態": "待對帳",
                "對帳單號": new_inv_id
            })
            st.success(f"🎉 成功為 {selected_tenant_name} 產生帳單 [{new_inv_id}]！")
            st.rerun()

elif nav_mode == "⚙️ 全球租戶管理與新增":
    st.markdown("## ⚙️ 全球 SaaS 租戶清單與新增中心")
    st.info("💡 在此擴增新的全球企業客戶（租戶）。")
    
    tenant_summary = []
    for t_name, t_info in st.session_state.global_tenants_db.items():
        tenant_summary.append({
            "租戶名稱": t_name,
            "租戶ID": t_info.get("tenant_id"),
            "版本": t_info.get("edition_name"),
            "月費 (USD)": t_info.get("price_usd")
        })
    st.dataframe(pd.DataFrame(tenant_summary), use_container_width=True)
    
    st.markdown("---")
    with st.form("new_tenant_form"):
        new_t_name = st.text_input("新企業租戶名稱")
        new_t_id = st.text_input("租戶代號", value="TENANT-003")
        if st.form_submit_button("🚀 快速開通新租戶", type="primary", use_container_width=True):
            if new_t_name and new_t_name not in st.session_state.global_tenants_db:
                st.session_state.global_tenants_db[new_t_name] = {
                    "tenant_id": new_t_id,
                    "edition_name": "🚀 旗艦企業版 (Enterprise)",
                    "price_usd": 3000.0,
                    "custom_org_chart": ["👑 董事會", "🛠️ 總經理室"],
                    "dept_modules_db": {},
                    "billing_history": []
                }
                st.success(f"🎉 成功開通新租戶 [{new_t_name}]！")
                st.rerun()
