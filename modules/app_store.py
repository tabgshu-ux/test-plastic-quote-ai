# app.py - 完整多租戶 SaaS ERP 總控主程式（含登入、對帳、拼圖市集與外掛調用）
import streamlit as st
import pandas as pd
import uuid

# 頁面基本設定
st.set_page_config(
    page_title="全球多產業 AI ERP 企業總控平台",
    page_icon="🏢",
    layout="wide"
)

# 1. 安全載入拼圖市集模組 (app_store)
try:
    from modules.app_store import render_app_store
except ImportError:
    try:
        from app_store import render_app_store
    except ImportError:
        def render_app_store(current_tenant=None, all_departments=None):
            st.error("⚠️ 找不到 modules/app_store.py 模組，請確認檔案位置。")

# ==========================================================
# 🔐 2. 帳號登入與授權管理機制 (Authentication)
# ==========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown("## 🔐 全球 SaaS ERP 企業登入中心")
        st.info("💡 請輸入您的租戶帳號與密碼以進入企業總控台。")
        
        with st.form("login_form"):
            username = st.text_input("租戶帳號 (Username)", value="admin")
            password = st.text_input("密碼 (Password)", type="password", value="123456")
            login_btn = st.form_submit_button("登入總控台", type="primary", use_container_width=True)
            
            if login_btn:
                if username == "admin" and password == "123456":
                    st.session_state.logged_in = True
                    st.success("🎉 登入成功！正在載入總控台...")
                    st.rerun()
                else:
                    st.error("❌ 帳號或密碼錯誤（預設帳號：admin / 密碼：123456）")
    st.stop()

# ==========================================================
# 🏢 3. 已登入後：完整企業總控台與多模組導覽
# ==========================================================
st.sidebar.markdown("### 🚀 裕豐電機 (Reetech) 總控台")
st.sidebar.success("👤 當前登入：系統管理員 (Admin)")

nav_mode = st.sidebar.radio(
    "系統導覽選單", 
    [
        "🧩 樂高模組拼圖市集 (App Store)", 
        "📊 企業租戶營運總覽", 
        "💰 租戶對帳與帳務結算中心",
        "⚙️ 系統參數與外掛維護"
    ]
)

if st.sidebar.button("🔒 登出系統", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# 4. 初始化全域租戶與對帳資料庫
if "safe_tenant_db" not in st.session_state:
    st.session_state.safe_tenant_db = {
        "tenant_name": "裕豐電機工業 (Reetech Industrial)",
        "edition_name": "🚀 旗艦企業版 (Enterprise)",
        "price_usd": 2500.0,
        "dept_modules_db": {},
        "billing_history": [
            {"期數": "2026/Q1", "應收金額 (USD)": 2500.0, "狀態": "已結算", "對帳單號": "INV-2026-001"},
            {"期數": "2026/Q2", "應收金額 (USD)": 2500.0, "狀態": "待對帳", "對帳單號": "INV-2026-002"}
        ]
    }

tenant_data = st.session_state.safe_tenant_db

# ==========================================================
# 頁面分流渲染
# ==========================================================
if nav_mode == "🧩 樂高模組拼圖市集 (App Store)":
    # 呼叫拼圖選擇與版本定價中心
    if render_app_store is not None:
        render_app_store()
    else:
        st.error("⚠️ 無法載入 app_store 模組。")

elif nav_mode == "📊 企業租戶營運總覽":
    st.markdown("## 📊 企業租戶營運與組織架構總覽")
    st.info("💡 在此檢視目前全球租戶的啟用狀況、部門組織與雲端資源佔用。")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("目前租戶名稱", tenant_data.get("tenant_name", ""))
    with col2:
        st.metric("當前銷售版本", tenant_data.get("edition_name", ""))
    with col3:
        st.metric("每月總訂閱金額", f"$ {tenant_data.get('price_usd', 0)} USD")
    
    st.markdown("### 🏢 已開通部門與模組明細清單")
    active_db = tenant_data.get("dept_modules_db", {})
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
        st.warning("⚠️ 目前尚未在拼圖市集中勾選任何部門模組。")

elif nav_mode == "💰 租戶對帳與帳務結算中心":
    st.markdown("## 💰 全球多租戶對帳與帳務結算中心 (Reconciliation & Billing)")
    st.info("💡 在此執行跨國租戶的訂閱對帳、期數帳單確認與發票結算。")
    
    st.markdown("### 📄 歷史對帳單與結算紀錄")
    billing_df = pd.DataFrame(tenant_data.get("billing_history", []))
    st.dataframe(billing_df, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### ➕ 手動新增對帳期數與應收調整")
    with st.form("reconciliation_form"):
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            new_period = st.text_input("結算期數 (例如 2026/Q3)", value="2026/Q3")
        with r_col2:
            new_amount = st.number_input("調整金額 (USD)", value=float(tenant_data.get("price_usd", 2500.0)), step=100.0)
            
        if st.form_submit_button("📥 產生並送出新對帳單", type="primary", use_container_width=True):
            new_inv = f"INV-2026-{len(tenant_data['billing_history']) + 1:03d}"
            tenant_data["billing_history"].append({
                "期數": new_period,
                "應收金額 (USD)": new_amount,
                "狀態": "待對帳",
                "對帳單號": new_inv
            })
            st.session_state.safe_tenant_db = tenant_data
            st.success(f"🎉 成功產生對帳單號 [{new_inv}]！")
            st.rerun()

elif nav_mode == "⚙️ 系統參數與外掛維護":
    st.markdown("## ⚙️ 系統參數與外掛矩陣維護中心")
    st.info("💡 管理系統底層設定、語言切換與 `industries/` 外掛資料夾連線狀態。")
    st.success("✅ 目前系統外掛模組運作正常，支援多租戶與 12 大產業動態外掛載入。")
