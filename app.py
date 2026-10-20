import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

# 1. 頁面基本設定 (Mobile-First & 企業級外觀)
st.set_page_config(
    page_title="SaaS Enterprise Multi-Tenant AI-ERP & Strict RBAC",
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

# 3. 初始化全域定價策略、匯率中樞與多租戶資料庫
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
            "name": "SaaS 總控台 (平台營運商專屬)",
            "type": "Master",
            "platform_stats": {"total_mrr": 230, "active_tenants": 2},
            "audit_logs": [{"time": "2026-10-20 12:00:00", "user": "Platform Master", "action": "更新全平台基準匯率與定價策略", "ip": "127.0.0.1"}]
        },
        "tenant_vina_水电": {
            "name": "🇻🇳 越南平陽水電工程有限公司",
            "type": "Tenant",
            "org_nodes": [
                {"id": "n_1", "name": "👑 總經理室", "type": "高階決策層", "parent": "無 (頂層)", "modules": ["全球戰情室", "P&L"]},
                {"id": "n_2", "name": "⚙️ 工程部", "type": "營運部門", "parent": "👑 總經理室", "modules": ["工程估驗", "施工日報"]},
                {"id": "n_3", "name": "📦 平陽廠原物料倉庫", "type": "實體據點/庫位", "parent": "👑 總經理室", "modules": ["庫存管理"]}
            ],
            "iot_devices": [{"dev_id": "DEV-01", "name": "平陽廠大門人臉辨識機", "type": "人臉辨識", "ip": "192.168.10.50", "status": "🟢 聯機中"}],
            "ap_invoices": [{"invoice_no": "000123", "supplier": "越南材料行", "items": "PVC管", "qty": "50支", "amount_vnd": "15,000,000", "status": "🔴 待付款"}],
            "staff": [
                {"name": "許福村 (公司老闆)", "email": "fuchun@vina.com", "role": "Tenant Admin (最高權限)"},
                {"name": "阮文安 (越籍會計)", "email": "an.nguyen@vina.com", "role": "財務與會計專員"},
                {"name": "林工務主任", "email": "linh.site@vina.com", "role": "現場工地主任"}
            ],
            "audit_logs": [
                {"time": "2026-10-20 14:10:22", "user": "阮文安 (越籍會計)", "action": "上傳並解析越南紅發票 (編號: 000123)", "ip": "192.168.10.15"},
                {"time": "2026-10-20 09:30:05", "user": "許福村 (公司老闆)", "action": "新增實體據點：平陽廠原物料倉庫", "ip": "192.168.10.2"}
            ],
            "subscription": {"plan": "跨國製造與工程旗艦版 (Enterprise)", "status": "🟢 正常訂閱中", "expires": "2027-10-20", "maintenance_contract": "含 24/7 VIP 技術維修"}
        },
        "tenant_taipei_wash": {
            "name": "🇹🇼 台北極速智慧洗車坊",
            "type": "Tenant",
            "org_nodes": [
                {"id": "w_1", "name": "👑 台北總店長室", "type": "高階決策層", "parent": "無 (頂層)", "modules": ["營收戰情"]},
                {"id": "w_2", "name": "🚗 洗車美容部", "type": "營運部門", "parent": "👑 台北總店長室", "modules": ["會員預約", "水刀聯動"]}
            ],
            "iot_devices": [{"dev_id": "W-01", "name": "入口車牌辨識 (ANPR)", "type": "車牌辨識", "ip": "10.0.0.15", "status": "🟢 運作中"}],
            "ap_invoices": [],
            "staff": [
                {"name": "張店長", "email": "manager@wash.com", "role": "Tenant Admin"}
            ],
            "audit_logs": [
                {"time": "2026-10-19 10:00:00", "user": "張店長", "action": "初始化台北洗車坊租戶後台", "ip": "1.2.3.4"}
            ],
            "subscription": {"plan": "智慧零售與服務標準版 (Standard)", "status": "🟡 即將到期", "expires": "2026-11-05", "maintenance_contract": "標準客服"}
        }
    }

# 4. 側邊欄：嚴格權限隔離切換器
with st.sidebar:
    st.image("https://img.icons8.com/color/96/company.png", width=64)
    st.markdown("### 🌐 SaaS 多租戶 AI-ERP 平台")
    
    lang = st.selectbox("選擇語系 / Select Language", ["繁體中文", "English", "Tiếng Việt (越南語)", "简体中文"])
    
    st.markdown("---")
    st.markdown("🔒 **[嚴格權限隔離與視角切換]**")
    current_tenant_key = st.selectbox(
        "選擇登入身分與視角 (Context Switcher)",
        options=list(st.session_state.tenants_db.keys()),
        format_func=lambda x: st.session_state.tenants_db[x]["name"]
    )
    
    current_tenant = st.session_state.tenants_db[current_tenant_key]
    is_master = (current_tenant["type"] == "Master")
    
    st.markdown(f"👤 **目前身分**: `{'平台總管理員 (Master)' if is_master else '租戶公司管理員 (Tenant Admin)'}`")
    st.markdown(f"🏢 **目前所屬環境**: `{current_tenant['name']}`")
    
    st.markdown("---")
    st.markdown("### 📌 系統導覽選單")
    
    if is_master:
        # ==================== 平台總控台選單（絕對管不到租戶內部資料） ====================
        menu_choice = st.radio(
            "選擇平台總控模組 (Master Control)",
            [
                "💱 全球多幣別與即時匯率中樞 (Global FX)",
                "⚙️ 全球定價策略與計費費率自訂 (Pricing)",
                "📦 全平台租戶營收與訂閱總覽 (MRR)",
                "🔒 平台總控台資安稽核日誌 (Platform Audit Trail)"
            ]
        )
    else:
        # ==================== 個別租戶內部選單（完全屬於該公司私有） ====================
        menu_choice = st.radio(
            "選擇客戶內部模組 (Tenant IT Panel)",
            [
                "🖱️ 本公司組織與據點自助設定",
                "👥 本公司員工帳號與權限角色管理 (RBAC)",
                "🔒 本公司系統資安稽核日誌 (Audit Trail)",
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
if is_master:
    # ==================== 平台總控台 (Master View) ====================
    if "全球多幣別與即時匯率引擎" in menu_choice or "全球多幣別" in menu_choice:
        st.markdown("## 💱 SaaS 平台總控台：全球多幣別與即時匯率引擎 (Global FX Engine)")
        st.info("💡 *此處為平台總管理員專屬。您可以維護全平台的基準匯率，供所有跨國租戶自動調用。*")
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
                    st.success("🎉 全平台基準匯率已更新！")
            st.markdown('</div>', unsafe_allow_html=True)

    elif "全球定價策略" in menu_choice:
        st.markdown("## ⚙️ SaaS 平台總控台：全球定價策略與費率自訂中心")
        st.info("💡 設定全平台的訂閱月費與部門加購價。")
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            with st.form("pricing_form"):
                p1, p2, p3 = st.columns(3)
                with p1: new_ent = st.number_input("旗艦版基礎月費 (USD)", value=st.session_state.global_pricing["enterprise_base_fee"], step=5)
                with p2: new_std = st.number_input("標準版基礎月費 (USD)", value=st.session_state.global_pricing["standard_base_fee"], step=5)
                with p3: new_dep = st.number_input("每新增部門加收費", value=st.session_state.global_pricing["extra_dept_fee"], step=1)
                if st.form_submit_button("💾 儲存並更新費率", type="primary", use_container_width=True):
                    st.session_state.global_pricing["enterprise_base_fee"] = new_ent
                    st.session_state.global_pricing["standard_base_fee"] = new_std
                    st.session_state.global_pricing["extra_dept_fee"] = new_dep
                    st.success("🎉 全球定價規則已更新！")
            st.markdown('</div>', unsafe_allow_html=True)

    elif "全平台租戶營收" in menu_choice or "全平台" in menu_choice:
        st.markdown("## 📦 SaaS 平台總控台：全平台租戶營收與訂閱總覽 (MRR)")
        st.info("💡 總覽所有註冊企業租戶的方案與營收狀況（無法檢視客戶內部發票或員工隱私資料）。")
        st.metric("💰 平台總 MRR (月營收)", "230 USD")
        st.dataframe(pd.DataFrame([
            {"租戶代碼": "tenant_vina_水电", "公司名稱": "越南平陽水電工程", "方案": "旗艦版", "狀態": "🟢 正常"},
            {"租戶代碼": "tenant_taipei_wash", "公司名稱": "台北極速智慧洗車坊", "方案": "標準版", "狀態": "🟡 15天後到期"}
        ]), use_container_width=True)

    else:
        st.markdown("## 🔒 平台總控台資安稽核日誌 (Platform Audit Trail)")
        st.info("💡 記錄平台管理員自身的系統層級操作。")
        st.dataframe(pd.DataFrame(current_tenant["audit_logs"]), use_container_width=True)

else:
    # ==================== 獨立客戶租戶後台 (Tenant View - 完全與外界隔離) ====================
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
                    current_tenant["audit_logs"].insert(0, {
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "user": current_tenant["staff"][0]["name"],
                        "action": f"新增部門/據點：{new_dept} (掛載於 {chosen_parent})",
                        "ip": "192.168.10.5"
                    })
                    st.success(f"🎉 成功新增 [{new_dept}]！已自動寫入貴公司專屬的資安稽核日誌。")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col_view:
            st.markdown("### 🌳 貴公司組織與據點樹狀圖")
            for node in current_tenant["org_nodes"]:
                st.markdown(f"- 📂 **{node['name']}** (上級: {node['parent']})")

    elif "員工帳號與權限角色管理" in menu_choice:
        st.markdown(f"## 👥 {current_tenant['name']}：企業內部員工帳號與權限角色管理 (RBAC)")
        st.info("💡 *在此處您可以建立貴公司內部的員工帳號與指派職務，落實內部權限分工。*")
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            with st.form("staff_form"):
                s_name = st.text_input("員工姓名*", placeholder="例：陳大為")
                s_email = st.text_input("電子郵件 (登入帳號)*", placeholder="例：david@company.com")
                s_role = st.selectbox("指派權限角色", ["財務與會計專員", "現場工地主任", "總務與人事專員", "採購專員", "租戶系統管理員"])
                if st.form_submit_button("👤 建立員工帳號", type="primary", use_container_width=True):
                    if s_name and s_email:
                        current_tenant["staff"].append({"name": s_name, "email": s_email, "role": s_role})
                        current_tenant["audit_logs"].insert(0, {
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "user": current_tenant["staff"][0]["name"],
                            "action": f"新增員工帳號：{s_name} ({s_role})",
                            "ip": "192.168.10.2"
                        })
                        st.success(f"🎉 成功建立員工 [{s_name}]！")
            st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(current_tenant["staff"]), use_container_width=True)

    elif "資安稽核日誌" in menu_choice:
        st.markdown(f"## 🔒 {current_tenant['name']}：系統資安稽核日誌與操作軌跡追蹤")
        st.info("💡 記錄貴公司內部所有員工的操作軌跡，確保資安合規。")
        st.dataframe(pd.DataFrame(current_tenant["audit_logs"]), use_container_width=True)

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
