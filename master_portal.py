import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="SaaS Master Control Hub",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #f1f5f9; }
    .card-container { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); margin-bottom: 20px; }
    h1, h2, h3 { color: #0f172a; }
    </style>
""", unsafe_allow_html=True)

# 初始化 Master 專屬全域狀態
if "master_logged_in" not in st.session_state:
    st.session_state.master_logged_in = False
if "master_role" not in st.session_state:
    st.session_state.master_role = None
if "master_current_user" not in st.session_state:
    st.session_state.master_current_user = None

if "master_staff_db" not in st.session_state:
    st.session_state.master_staff_db = [
        {"name": "許福村", "account": "admin", "password": "admin123", "role": "👑 平台老闆 (Master Admin)", "status": "啟用中"},
        {"name": "財務部專員", "account": "finance", "password": "finance123", "role": "💰 總控台財務專員 (Master Finance)", "status": "啟用中"}
    ]

if "tenants_db" not in st.session_state:
    st.session_state.tenants_db = {
        "tenant_vina_group": {
            "name": "🇻🇳 越南平陽控股集團",
            "region": "越南 (Binh Duong, VN)",
            "plan": "🚀 旗艦集團版 (Enterprise)",
            "price_usd": 350,
            "expiry_date": "2027-10-20"
        }
    }

# ==================== 總控台側邊欄導覽 ====================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/company.png", width=64)
    st.markdown("### 👑 SaaS 平台總控台 (Master)")
    st.markdown("---")
    
    if st.session_state.master_logged_in:
        role_title = "平台老闆" if st.session_state.master_role == "admin" else "財務專員"
        st.markdown(f"**目前身分**: `{st.session_state.master_current_user} ({role_title})`")
        if st.button("🔒 登出總控台", use_container_width=True):
            st.session_state.master_logged_in = False
            st.session_state.master_role = None
            st.session_state.master_current_user = None
            st.rerun()
    else:
        st.markdown("👑 **目前身分**: `未登入`")
        
    st.markdown("---")
    if st.session_state.master_logged_in:
        if st.session_state.master_role == "admin":
            master_menu = st.radio("總控台選單", ["🏢 全球企業租戶總覽", "👥 總控台帳號與權限管理 (IAM)"])
        else:
            master_menu = "💰 平台財務營收與帳單清單"
    else:
        master_menu = "🔒 請先登入"

# ==================== 總控台主畫面邏輯 ====================
if not st.session_state.master_logged_in:
    st.markdown("## 🔐 平台總控台安全登入 (Master Portal)")
    st.info("💡 *此為獨立加密之總控台，與租戶 ERP 資料完全實體隔離。*")
    
    with st.form("master_login_form"):
        input_account = st.text_input("登入帳號 (Account)", placeholder="請輸入總控台帳號...")
        input_pass = st.text_input("密碼 (Password)", type="password", placeholder="請輸入密碼...")
        
        if st.form_submit_button("🔓 登入總控台", type="primary", use_container_width=True):
            matched_user = None
            for u in st.session_state.master_staff_db:
                if u["account"] == input_account and u["password"] == input_pass:
                    matched_user = u
                    break
            
            if matched_user:
                if matched_user["status"] == "已停權 (Disabled)":
                    st.error("❌ 此帳號已被停權，無法登入！")
                else:
                    st.session_state.master_logged_in = True
                    st.session_state.master_current_user = matched_user["name"]
                    st.session_state.master_role = "admin" if "Master Admin" in matched_user["role"] else "finance"
                    st.success(f"🎉 歡迎回來，{matched_user['name']}！")
                    st.rerun()
            else:
                st.error("❌ 帳號或密碼錯誤！")
else:
    if st.session_state.master_role == "admin":
        if "全球企業租戶總覽" in master_menu:
            st.markdown("## 🏢 SaaS 平台總控台：企業租戶動態總覽")
            for t_id, t_data in st.session_state.tenants_db.items():
                with st.container():
                    st.markdown('<div class="card-container">', unsafe_allow_html=True)
                    st.markdown(f"### 🏢 {t_data['name']}")
                    st.markdown(f"- **租戶代碼**: `{t_id}` | **地區**: `{t_data['region']}`")
                    st.markdown(f"- **目前訂閱方案**: `{t_data['plan']}` | **每月月費**: `$ {t_data['price_usd']} USD`")
                    st.markdown(f"- **合約到期日**: `{t_data['expiry_date']}`")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("## 👥 總控台內部員工與權限管理 (IAM)")
            st.info("💡 *在此管理總控台帳號。離職人員可直接設定為【已停權】，無需修改程式碼。*")
            
            with st.container():
                st.markdown('<div class="card-container">', unsafe_allow_html=True)
                st.markdown("### 📋 現有總控台帳號清單")
                for idx, staff in enumerate(st.session_state.master_staff_db):
                    cols = st.columns([2, 2, 2, 2, 1])
                    with cols[0]:
                        st.write(f"**{staff['name']}**")
                    with cols[1]:
                        st.write(f"帳號: `{staff['account']}`")
                    with cols[2]:
                        st.write(staff['role'])
                    with cols[3]:
                        new_status = st.selectbox(
                            "狀態", ["啟用中", "已停權 (Disabled)"], 
                            index=0 if staff['status'] == "啟用中" else 1,
                            key=f"m_status_{idx}"
                        )
                        if new_status != staff['status']:
                            st.session_state.master_staff_db[idx]['status'] = new_status
                            st.rerun()
                    with cols[4]:
                        if staff['account'] != "admin":
                            if st.button("🗑️", key=f"del_m_{idx}"):
                                st.session_state.master_staff_db.pop(idx)
                                st.rerun()
                    st.markdown("---")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("## 💰 總控台：平台財務營收與租戶帳單結算中心")
        total_mrr = sum([v["price_usd"] for v in st.session_state.tenants_db.values()])
        st.metric("📊 本月總訂閱營收 (MRR)", f"$ {total_mrr:,.2f} USD")
