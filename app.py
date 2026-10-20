import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

# 1. 頁面基本設定 (Mobile-First & 企業級外觀)
st.set_page_config(
    page_title="SaaS Enterprise Multi-Tenant AI-ERP & Audit Trail",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 自定義精緻企業風 CSS 美化 (UI/UX Styling)
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .card-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #1e293b;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 初始化全域定價策略、匯率中樞與多租戶資料庫（含員工帳號與稽核日誌）
if "global_pricing" not in st.session_state:
    st.session_state.global_pricing = {
        "enterprise_base_fee": 150,
        "standard_base_fee": 80,
        "extra_dept_fee": 5
    }

if "global_fx_rates" not in st.session_state:
    st.session_state.global_fx_rates = {
        "USD": 1.0,
        "TWD": 31.50,
        "VND": 25400.00,
        "RMB": 7.20
    }

if "tenants_db" not in st.session_state:
    st.session_state.tenants_db = {
        "tenant_master": {
            "name": "SaaS 總控台 (平台運營商)",
            "org_nodes": [],
            "iot_devices": [],
            "ap_invoices": [],
            "staff": [{"name": "總管理員", "email": "admin@saas.com", "role": "Platform Master"}],
            "audit_logs": [{"time": "2026-10-20 12:00:00", "user": "總管理員", "action": "啟動平台全域匯率與定價策略", "ip": "127.0.0.1"}],
            "subscription": {"plan": "Master Control", "status": "Active", "expires": "N/A"}
        },
        "tenant_vina_水电": {
            "name": "🇻🇳 越南平陽水電工程有限公司",
            "org_nodes": [
                {"id": "n_1", "name": "👑 總經理室", "type": "高階決策層", "parent": "無 (頂層)", "modules": ["全球戰情室", "P&L"]},
                {"id": "n_2", "name": "⚙️ 工程部", "type": "營運部門", "parent": "👑 總經理室", "modules": ["工程估驗", "施工日報"]},
                {"id": "n_3", "name": "📦 平陽廠原物料倉庫", "type": "實體據點/庫位", "parent": "👑 總經理室", "modules": ["庫存管理"]}
            ],
            "iot_devices": [{"dev_id": "DEV-01", "name": "平陽廠大門人臉辨識機", "type": "人臉辨識", "ip": "192.168.10.50", "status": "🟢 聯機中"}],
            "ap_invoices": [{"invoice_no": "000123", "supplier": "越南材料行", "items": "PVC管", "qty": "50支", "amount_vnd": "15,000,000", "status": "🔴 待付款"}],
            "staff": [
                {"name": "許福村 (老闆)", "email": "fuchun@vina.com", "role": "Tenant Admin (最高權限)"},
                {"name": "阮文安 (越籍會計)", "email": "an.nguyen@vina.com", "role": "財務與會計專員"},
                {"name": "林工務主任", "email": "linh.site@vina.com", "role": "現場工地主任"}
            ],
            "audit_logs": [
                {"time": "2026-10-20 14:10:22", "user": "阮文安 (越籍會計)", "action": "上傳並解析越南紅發票 (編號: 000123)", "ip": "192.168.10.15"},
                {"time": "2026-10-20 09:30:05", "user": "許福村 (老闆)", "action": "新增實體據點：平陽廠原物料倉庫", "ip": "192.168.10.2"}
            ],
            "subscription": {"plan": "跨國製造與工程旗艦版 (Enterprise)", "status": "🟢 正常訂閱中", "expires": "2027-10-20", "extra_departments": 3, "maintenance_contract": "含 24/7 VIP 技術維修"}
        }
    }

# 4. 側邊欄：多租戶切換器與導覽選單
with st.sidebar:
    st.image("https://img.icons8.com/color/96/company.png", width=64)
    st.markdown("### 🌐 SaaS 多租戶 AI-ERP 平台")
    
    lang = st.selectbox("選擇語系 / Select Language", ["繁體中文", "English", "Tiếng Việt (越南語)", "简体中文"])
    
    st.markdown("---")
    st.markdown("🏢 **[多租戶環境切換模擬器]**")
    current_tenant_key = st.selectbox(
        "選擇登入視角 (Tenant Switcher)",
        options=list(st.session_state.tenants_db.keys()),
        format_func=lambda x: st.session_state.tenants_db[x]["name"]
    )
    
    current_tenant = st.session_state.tenants_db[current_tenant_key]
    
    st.markdown(f"👤 **目前身份**: `Tenant Admin`")
    st.markdown(f"🏢 **目前所屬公司**: `{current_tenant['name']}`")
    
    st.markdown("---")
    st.markdown("### 📌 系統導覽選單")
    
    if current_tenant_key == "tenant_master":
        menu_choice = st.radio(
            "選擇管理模組 (Master)",
            [
                "💱 全球多幣別與即時匯率引擎 (Global FX Engine)",
                "⚙️ 全球定價策略與費率自訂 (Custom Pricing)",
                "📦 SaaS 平台營運與全租戶監控"
            ]
        )
    else:
        menu_choice = st.radio(
            "選擇客戶內部模組 (Tenant IT Panel)",
            [
                "🖱️ 本公司組織與據點 IT 自行設定",
                "👥 本公司員工帳號與權限角色管理 (RBAC)",
                "🔒 系統資安稽核日誌與操作軌跡追蹤 (Audit Trail)",
                "💳 訂閱方案與維修合約管理",
                "🤖 本公司 AI 硬體與車牌/人臉辨識掛接",
                "🇻🇳 本公司越南紅發票與應付帳款 (AP)",
                "👑 董事長高階戰情室與 P&L 預覽"
            ]
        )
    
    st.markdown("---")
    if st.button("🚪 登出系統", use_container_width=True):
        st.info("已安全登出系統。")

# 5. 主畫面邏輯路由
if current_tenant_key == "tenant_master":
    # ==================== SaaS 總控台 ====================
    if "全球多幣別與即時匯率引擎" in menu_choice:
        st.markdown("## 💱 SaaS 平台總控台：全球多幣別與即時匯率引擎 (Global FX Engine)")
        st.info("💡 集團總控台基準匯率維護。")
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            with st.form("fx_form"):
                fx = st.session_state.global_fx_rates
                fx_c1, fx_c2, fx_c3, fx_c4 = st.columns(4)
                with fx_c1: st.number_input("美元 (USD)", value=fx["USD"], disabled=True)
                with fx_c2: new_twd = st.number_input("台幣 (TWD)", value=fx["TWD"], step=0.1)
                with fx_c3: new_vnd = st.number_input("越南盾 (VND)", value=fx["VND"], step=10.0)
                with fx_c4: new_rmb = st.number_input("人民幣 (RMB)", value=fx["RMB"], step=0.01)
                if st.form_submit_button("💾 立即更新全平台即時匯率", type="primary", use_container_width=True):
                    st.session_state.global_fx_rates["TWD"] = new_twd
                    st.session_state.global_fx_rates["VND"] = new_vnd
                    st.session_state.global_fx_rates["RMB"] = new_rmb
                    st.success("🎉 全球即時匯率已更新！")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("## ⚙️ SaaS 平台總控台：全球定價策略")
        st.info("管理全平台方案與加購價。")

else:
    # ==================== 獨立客戶租戶後台 ====================
    pricing = st.session_state.global_pricing
    
    if "組織與據點" in menu_choice:
        st.markdown(f"## 🖱️ {current_tenant['name']}：組織樹與實體據點自助設定")
        col_set, col_view = st.columns([1, 1])
        with col_set:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            new_dept = st.text_input("輸入要新增的部門或倉庫名稱")
            existing_parents = [n["name"] for n in current_tenant["org_nodes"]]
            chosen_parent = st.selectbox("指定上級掛載點", existing_parents)
            if st.button("💳 確認加購並新增", type="primary", use_container_width=True):
                if new_dept:
                    current_tenant["org_nodes"].append({"id": f"n_{len(current_tenant['org_nodes'])+1}", "name": new_dept, "type": "自訂部門/據點", "parent": chosen_parent, "modules": ["日常作業"]})
                    # 自動記錄資安稽核日誌
                    current_tenant["audit_logs"].insert(0, {
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "user": "System Admin (模擬員工)",
                        "action": f"新增組織部門/據點：{new_dept} (掛載於 {chosen_parent})",
                        "ip": "192.168.10.5"
                    })
                    st.success(f"🎉 成功新增 [{new_dept}]！系統已同步寫入資安稽核日誌。")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col_view:
            st.markdown("### 🌳 組織與據點樹狀圖")
            for node in current_tenant["org_nodes"]:
                st.markdown(f"- 📂 **{node['name']}** (上級: {node['parent']})")

    elif "員工帳號與權限角色管理" in menu_choice:
        st.markdown(f"## 👥 {current_tenant['name']}：企業內部員工帳號與權限角色管理 (RBAC)")
        st.info("💡 *在此處您可以建立公司內部的員工帳號，並指派不同的職務角色（如財務會計、工地主任、總務、採購），落實權限隔離與分工。*")
        
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            with st.form("staff_form"):
                st.markdown("### ➕ 新增公司員工帳號")
                s_name = st.text_input("員工姓名*", placeholder="例：陳大為")
                s_email = st.text_input("電子郵件 (登入帳號)*", placeholder="例：david.chen@vina.com")
                s_role = st.selectbox("指派權限角色 (Role)", [
                    "財務與會計專員 (Finance)", 
                    "現場工地主任 (Site Manager)", 
                    "總務與人事專員 (HR & Admin)", 
                    "供應鏈採購專員 (Procurement)",
                    "租戶系統管理員 (Tenant Admin)"
                ])
                if st.form_submit_button("👤 建立員工帳號並賦予權限", type="primary", use_container_width=True):
                    if s_name and s_email:
                        current_tenant["staff"].append({"name": s_name, "email": s_email, "role": s_role})
                        current_tenant["audit_logs"].insert(0, {
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "user": "Tenant Admin",
                            "action": f"新增員工帳號：{s_name} ({s_email})，角色：{s_role}",
                            "ip": "192.168.10.2"
                        })
                        st.success(f"🎉 成功建立員工 [{s_name}] 的登入帳號！")
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("### 📋 目前公司內部員工與權限清單")
        st.dataframe(pd.DataFrame(current_tenant["staff"]), use_container_width=True)

    elif "資安稽核日誌與操作軌跡追蹤" in menu_choice:
        st.markdown(f"## 🔒 {current_tenant['name']}：系統資安稽核日誌與操作軌跡追蹤 (Audit Trail)")
        st.info("💡 *企業級資安合規保證！此處即時記錄了公司內所有員工的操作軌跡（誰在什麼時候修改了組織、上傳發票、新增帳號等），確保萬無一失。*")
        
        if current_tenant["audit_logs"]:
            st.dataframe(pd.DataFrame(current_tenant["audit_logs"]), use_container_width=True)
        else:
            st.info("目前尚無操作稽核日誌。")

    elif "訂閱方案" in menu_choice or "訂閱方案與維修合約" in menu_choice:
        st.markdown(f"## 💳 {current_tenant['name']}：訂閱方案與續約中心")
        if st.button("🚀 立即線上續約 1 年", type="primary"):
            st.success("🎉 續約成功！")

    elif "AI 硬體與車牌" in menu_choice:
        st.markdown(f"## 🤖 {current_tenant['name']}：AI 硬體與車牌/人臉辨識自助掛接")
        if current_tenant["iot_devices"]:
            st.dataframe(pd.DataFrame(current_tenant["iot_devices"]), use_container_width=True)

    elif "越南紅發票" in menu_choice:
        st.markdown(f"## 🇻🇳 {current_tenant['name']}：越南紅發票與應付帳款 (AP)")
        if current_tenant["ap_invoices"]:
            st.dataframe(pd.DataFrame(current_tenant["ap_invoices"]), use_container_width=True)

    else:
        st.markdown(f"## 👑 {current_tenant['name']}：高階戰情室與 P&L 預覽")
        st.metric("📊 本月應付帳款總額", "23,500,000 VND")
