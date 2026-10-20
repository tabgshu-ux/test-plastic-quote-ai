import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 1. 頁面基本設定 (Mobile-First & 企業級外觀)
st.set_page_config(
    page_title="SaaS Enterprise Multi-Tenant AI-ERP & Advanced Modules",
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

# 3. 初始化全域定價策略與多租戶資料庫
if "global_pricing" not in st.session_state:
    st.session_state.global_pricing = {
        "enterprise_base_fee": 150,  # 企業旗艦版預設月費 (USD)
        "standard_base_fee": 80,     # 標準版預設月費 (USD)
        "extra_dept_fee": 5          # 每多一個部門/據點加收費率 (USD)
    }

if "tenants_db" not in st.session_state:
    st.session_state.tenants_db = {
        "tenant_master": {
            "name": "SaaS 總控台 (平台運營商)",
            "org_nodes": [],
            "iot_devices": [],
            "ap_invoices": [],
            "subscription": {"plan": "Master Control", "status": "Active", "expires": "N/A", "mrr": 0}
        },
        "tenant_vina_水电": {
            "name": "🇻🇳 越南平陽水電工程有限公司",
            "org_nodes": [
                {"id": "n_1", "name": "👑 總經理室", "type": "高階決策層", "parent": "無 (頂層)", "modules": ["全球戰情室", "P&L"]},
                {"id": "n_2", "name": "⚙️ 工程部", "type": "營運部門", "parent": "👑 總經理室", "modules": ["工程估驗", "施工日報"]},
                {"id": "n_3", "name": "🏭 生產製造廠務部", "type": "製造中心", "parent": "👑 總經理室", "modules": ["MES報工"]},
                {"id": "n_4", "name": "📦 平陽廠原物料倉庫", "type": "實體據點/庫位", "parent": "🏭 生產製造廠務部", "modules": ["PDA收發貨", "庫存管理"]}
            ],
            "iot_devices": [
                {"dev_id": "DEV-01", "name": "平陽廠大門人臉辨識機", "type": "人臉辨識", "ip": "192.168.10.50", "status": "🟢 聯機中"}
            ],
            "ap_invoices": [
                {"invoice_no": "000123", "supplier": "越南材料行", "items": "PVC管", "qty": "50支", "amount_vnd": "15,000,000", "status": "🔴 待付款"}
            ],
            "subscription": {
                "plan": "跨國製造與工程旗艦版 (Enterprise)",
                "status": "🟢 正常訂閱中",
                "expires": "2027-10-20",
                "extra_departments": 4,
                "maintenance_contract": "含 24/7 VIP 技術維修與遠端支援"
            }
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
                "⚙️ 全球定價策略與計費費率自訂 (Custom Pricing)",
                "📦 SaaS 平台模組市集與全租戶營收監控",
                "📊 平台運行狀態與跨租戶數據監控"
            ]
        )
    else:
        menu_choice = st.radio(
            "選擇客戶內部模組 (Tenant IT Panel)",
            [
                "🖱️ 本公司組織與據點 IT 自行設定 (含即時計費)",
                "💳 訂閱方案、維修合約與續約付費 (Billing & Renewal)",
                "💱 多幣別與即時匯率換算引擎 (Multi-Currency FX)",
                "🛒 智慧採購與供應鏈審核管理 (Smart SCM)",
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
    if "全球定價策略" in menu_choice:
        st.markdown("## ⚙️ SaaS 平台總控台：全球定價策略與費率自訂中心")
        st.info("💡 在此處自訂全平台計費費率。")
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            with st.form("pricing_form"):
                p1, p2, p3 = st.columns(3)
                with p1:
                    new_ent_fee = st.number_input("旗艦版基礎月費 (USD)", value=st.session_state.global_pricing["enterprise_base_fee"], step=5)
                with p2:
                    new_std_fee = st.number_input("標準版基礎月費 (USD)", value=st.session_state.global_pricing["standard_base_fee"], step=5)
                with p3:
                    new_dept_fee = st.number_input("每新增部門/據點加收費", value=st.session_state.global_pricing["extra_dept_fee"], step=1)
                if st.form_submit_button("💾 儲存並更新費率", type="primary", use_container_width=True):
                    st.session_state.global_pricing["enterprise_base_fee"] = new_ent_fee
                    st.session_state.global_pricing["standard_base_fee"] = new_std_fee
                    st.session_state.global_pricing["extra_dept_fee"] = new_dept_fee
                    st.success("🎉 全球定價規則已更新！")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("## 📦 SaaS 平台總控台：營收監控")
        st.metric("💰 目前平台總 MRR", "230 USD")

else:
    pricing = st.session_state.global_pricing
    
    if "組織與據點" in menu_choice:
        st.markdown(f"## 🖱️ {current_tenant['name']}：組織樹與實體據點自助設定")
        is_ent = "旗艦版" in current_tenant["subscription"]["plan"]
        base_fee = pricing["enterprise_base_fee"] if is_ent else pricing["standard_base_fee"]
        dept_count = len(current_tenant["org_nodes"])
        extra_fee = dept_count * pricing["extra_dept_fee"]
        total_monthly = base_fee + extra_fee
        
        st.warning(f"💳 **目前動態計費**：方案基底 `$ {base_fee} USD` + {dept_count} 個部門 = **每月總計 `$ {total_monthly} USD`**")
        
        col_set, col_view = st.columns([1, 1])
        with col_set:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            new_dept = st.text_input("輸入要新增的部門或倉庫名稱")
            existing_parents = [n["name"] for n in current_tenant["org_nodes"]]
            chosen_parent = st.selectbox("指定上級掛載點", existing_parents)
            if st.button("💳 確認加購並新增", type="primary", use_container_width=True):
                if new_dept:
                    current_tenant["org_nodes"].append({"id": f"n_{len(current_tenant['org_nodes'])+1}", "name": new_dept, "type": "自訂部門/據點", "parent": chosen_parent, "modules": ["日常作業"]})
                    st.success(f"🎉 成功新增 [{new_dept}]！")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col_view:
            st.markdown("### 🌳 組織與據點樹狀圖")
            for node in current_tenant["org_nodes"]:
                st.markdown(f"- 📂 **{node['name']}** (上級: {node['parent']})")

    elif "訂閱方案、維修合約" in menu_choice:
        st.markdown(f"## 💳 {current_tenant['name']}：訂閱方案與續約中心")
        st.info("💡 檢視合約與線上續約。")
        if st.button("🚀 立即線上續約 1 年", type="primary"):
            st.success("🎉 續約成功！")

    elif "多幣別與即時匯率換算引擎" in menu_choice:
        st.markdown(f"## 💱 {current_tenant['name']}：多幣別與即時匯率換算引擎 (Multi-Currency FX)")
        st.info("💡 跨國企業專用：自動將越盾 (VND)、美元 (USD)、台幣 (TWD) 進行即時換算與匯兌損益結算。")
        
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            c_fx1, c_fx2 = st.columns(2)
            with c_fx1:
                amount_input = st.number_input("輸入金額", value=16500000, step=100000)
                from_curr = st.selectbox("原始幣別", ["VND (越南盾)", "USD (美元)", "TWD (台幣)"])
            with c_fx2:
                to_curr = st.selectbox("目標結算幣別", ["TWD (台幣)", "USD (美元)", "VND (越南盾)"])
                exchange_rate = st.number_input("今日參考匯率 (系統自動連動)", value=0.0013 if "VND" in from_curr else 31.5, format="("%.4f")
            
            converted_amount = amount_input * exchange_rate
            st.success(f"💱 **換算結果**：`{amount_input:,.0f} {from_curr.split()[0]}` = **`{converted_amount:,.2f} {to_curr.split()[0]}`**")
            st.markdown('</div>', unsafe_allow_html=True)

    elif "智慧採購與供應鏈審核管理" in menu_choice:
        st.markdown(f"## 🛒 {current_tenant['name']}：智慧採購與供應鏈審核管理 (Smart SCM & PR)")
        st.info("💡 當倉庫水位過低或工程請購時，自動生成採購單並走 BPM 電子簽核流程。")
        
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 📋 待審核採購單清單 (Purchase Requisitions)")
            mock_pr = pd.DataFrame([
                {"採購單號": "PR-2026-001", "請購部門": "工程部", "品項": "50mm PVC 電線管", "數量": "100 卷", "預估金額": "12,000,000 VND", "簽核狀態": "⏳ 主管審核中"},
                {"採購單號": "PR-2026-002", "請購部門": "生產部", "品項": "工業軸承 6204", "數量": "20 個", "預估金額": "5,400,000 VND", "簽核狀態": "✅ 已核准轉採購單"}
            ])
            st.dataframe(mock_pr, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

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
