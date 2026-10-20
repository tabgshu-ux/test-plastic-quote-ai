import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 1. 頁面基本設定 (Mobile-First & 企業級外觀)
st.set_page_config(
    page_title="SaaS Enterprise Multi-Tenant AI-ERP & Custom Billing",
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
        },
        "tenant_taipei_wash": {
            "name": "🇹🇼 台北極速智慧洗車坊",
            "org_nodes": [
                {"id": "w_1", "name": "👑 台北總店長室", "type": "高階決策層", "parent": "無 (頂層)", "modules": ["營收戰情"]},
                {"id": "w_2", "name": "🚗 洗車美容部", "type": "營運部門", "parent": "👑 台北總店長室", "modules": ["會員預約", "水刀聯動"]}
            ],
            "iot_devices": [
                {"dev_id": "W-01", "name": "入口車牌辨識 (ANPR)", "type": "車牌辨識", "ip": "10.0.0.15", "status": "🟢 運作中"}
            ],
            "ap_invoices": [],
            "subscription": {
                "plan": "智慧零售與服務標準版 (Standard)",
                "status": "🟡 即將到期 (剩餘 15 天)",
                "expires": "2026-11-05",
                "extra_departments": 2,
                "maintenance_contract": "標準線上客服維修支援"
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
    # ==================== SaaS 總控台：自訂定價與費率管理 ====================
    if "全球定價策略" in menu_choice:
        st.markdown("## ⚙️ SaaS 平台總控台：全球定價策略與費率自訂中心 (Custom Pricing Engine)")
        st.info("💡 *在此處您可以自由調整全平台的收費規則。所有客戶後台的計費與新增部門加價，都會即時依據您在這裡設定的費率自動計算！*")
        
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            with st.form("pricing_form"):
                st.markdown("### 💵 自訂 SaaS 方案基礎月費與加購費率 (USD)")
                
                p1, p2, p3 = st.columns(3)
                with p1:
                    new_ent_fee = st.number_input("旗艦版基礎月費 (Enterprise)", value=st.session_state.global_pricing["enterprise_base_fee"], step=5)
                with p2:
                    new_std_fee = st.number_input("標準版基礎月費 (Standard)", value=st.session_state.global_pricing["standard_base_fee"], step=5)
                with p3:
                    new_dept_fee = st.number_input("每新增一個部門/據點加收費", value=st.session_state.global_pricing["extra_dept_fee"], step=1)
                
                st.markdown("---")
                if st.form_submit_button("💾 儲存並即時更新全球定價策略", type="primary", use_container_width=True):
                    st.session_state.global_pricing["enterprise_base_fee"] = new_ent_fee
                    st.session_state.global_pricing["standard_base_fee"] = new_std_fee
                    st.session_state.global_pricing["extra_dept_fee"] = new_dept_fee
                    st.success("🎉 全球定價規則已成功更新！所有租戶的計費方式已即時同步生效。")
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("### 📊 目前生效中的費率總覽")
        st.markdown(f"- 企業旗艦版月費：**`$ {st.session_state.global_pricing['enterprise_base_fee']} USD`**")
        st.markdown(f"- 標準版月費：**`$ {st.session_state.global_pricing['standard_base_fee']} USD`**")
        st.markdown(f"- 部門/據點彈性加購價：**`$ {st.session_state.global_pricing['extra_dept_fee']} USD / 個`**")

    else:
        st.markdown("## 📦 SaaS 平台總控台：全租戶營收與模組市集")
        st.info("💡 管理全平台模組市集與租戶營收狀況。")
        st.metric("💰 目前平台總 MRR (月營收)", "230 USD")
        st.dataframe(pd.DataFrame([
            {"公司名稱": "越南平陽水電工程", "方案": "旗艦版", "狀態": "🟢 正常"},
            {"公司名稱": "台北極速智慧洗車坊", "方案": "標準版", "狀態": "🟡 15天後到期"}
        ]), use_container_width=True)

else:
    # ==================== 獨立客戶租戶後台 (依全域定價動態計費) ====================
    pricing = st.session_state.global_pricing
    
    if "組織與據點" in menu_choice:
        st.markdown(f"## 🖱️ {current_tenant['name']}：組織樹與實體據點自助設定 (含自訂計費)")
        
        # 根據方案與部門數量動態計算總費用
        is_ent = "旗艦版" in current_tenant["subscription"]["plan"]
        base_fee = pricing["enterprise_base_fee"] if is_ent else pricing["standard_base_fee"]
        dept_count = len(current_tenant["org_nodes"])
        extra_fee = dept_count * pricing["extra_dept_fee"]
        total_monthly = base_fee + extra_fee
        
        st.warning(f"💳 **目前動態計費**：方案基底 `$ {base_fee} USD` + {dept_count} 個部門/據點 (每個 ${pricing['extra_dept_fee']} USD) = **每月總計 `$ {total_monthly} USD`**")
        
        col_set, col_view = st.columns([1, 1])
        
        with col_set:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown(f"### ➕ 新增部門或實體據點 (每新增一個加收 ${pricing['extra_dept_fee']} USD)")
            new_dept = st.text_input("輸入要新增的部門或倉庫名稱", placeholder="例：越南美福二廠 / 財務部")
            existing_parents = [n["name"] for n in current_tenant["org_nodes"]]
            chosen_parent = st.selectbox("指定上級掛載點", existing_parents)
            
            if st.button("💳 確認加購並新增部門/據點", type="primary", use_container_width=True):
                if new_dept:
                    current_tenant["org_nodes"].append({"id": f"n_{len(current_tenant['org_nodes'])+1}", "name": new_dept, "type": "自訂部門/據點", "parent": chosen_parent, "modules": ["日常作業"]})
                    st.success(f"🎉 成功新增 [{new_dept}]！系統已依據管理員設定的費率自動更新帳單。")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_view:
            st.markdown("### 🌳 貴公司目前的組織與據點樹狀圖")
            for node in current_tenant["org_nodes"]:
                is_loc = "實體據點" in node['type'] or "倉庫" in node['name']
                indent = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;┗ 📦 " if is_loc else ("&nbsp;&nbsp;&nbsp;&nbsp;┗ 📂 " if node["parent"] != "無 (頂層)" else "👑 ")
                st.markdown(f"""
                    <div style="background: white; padding: 10px; border-radius: 6px; margin-bottom: 8px; border-left: 4px solid #3b82f6;">
                        <b>{indent}{node['name']}</b> <span style="font-size: 11px; color: gray;">({node['type']})</span><br>
                        <span style="font-size: 11px; color: #0f766e;">📌 上級掛載：{node['parent']}</span>
                    </div>
                """, unsafe_allow_html=True)

    elif "訂閱方案、維修合約" in menu_choice:
        st.markdown(f"## 💳 {current_tenant['name']}：訂閱方案、維修合約與續約付費中心")
        
        is_ent = "旗艦版" in current_tenant["subscription"]["plan"]
        base_fee = pricing["enterprise_base_fee"] if is_ent else pricing["standard_base_fee"]
        dept_count = len(current_tenant["org_nodes"])
        extra_fee = dept_count * pricing["extra_dept_fee"]
        total_monthly = base_fee + extra_fee
        
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 📦 目前動態計費明細 (即時對應總控台定價)")
            st.markdown(f"- **目前方案**: `{current_tenant['subscription']['plan']}`")
            st.markdown(f"- **方案基礎月費**: `$ {base_fee} USD`")
            st.markdown(f"- **現有部門/據點數**: `{dept_count} 個` (費率: ${pricing['extra_dept_fee']}/個)")
            st.markdown(f"- **額外加收總額**: `$ {extra_fee} USD`")
            st.markdown(f"- **總計每月應繳金額**: **`$ {total_monthly} USD / 月`**")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with sc2:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 🛠️ 維修合約與線上續約")
            st.markdown(f"- **維修等級**: `{current_tenant['subscription']['maintenance_contract']}`")
            st.markdown("- **合約到期日**: `{}`".format(current_tenant['subscription']['expires']))
            st.markdown("---")
            if st.button("🚀 立即線上續約 1 年", type="primary", use_container_width=True):
                st.success("🎉 續約成功！已透過金流閘道完成扣款，合約有效期限已展延一年！")
            st.markdown('</div>', unsafe_allow_html=True)

    elif "AI 硬體與車牌" in menu_choice:
        st.markdown(f"## 🤖 {current_tenant['name']}：AI 硬體與車牌/人臉辨識自助掛接")
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            with st.form("tenant_iot_form"):
                d_name = st.text_input("硬體裝置名稱", placeholder="例：大門口車牌辨識攝影機")
                d_ip = st.text_input("裝置 IP 位址", placeholder="例：192.168.1.200")
                if st.form_submit_button("🔌 註冊硬體並連線", type="primary"):
                    if d_name and d_ip:
                        current_tenant["iot_devices"].append({"dev_id": f"DEV-{len(current_tenant['iot_devices'])+1}", "name": d_name, "type": "智慧感測", "ip": d_ip, "status": "🟢 聯機中"})
                        st.success(f"🎉 成功為貴公司掛接硬體 [{d_name}]！")
            st.markdown('</div>', unsafe_allow_html=True)
            if current_tenant["iot_devices"]:
                st.dataframe(pd.DataFrame(current_tenant["iot_devices"]), use_container_width=True)

    elif "越南紅發票" in menu_choice:
        st.markdown(f"## 🇻🇳 {current_tenant['name']}：越南紅發票與應付帳款 (AP)")
        up_file = st.file_uploader("上傳越南電子發票 (XML / PDF)", type=["xml", "pdf"])
        if up_file or st.button("⚡ 模擬一鍵上傳發票並自動串聯", type="primary"):
            new_inv = {"invoice_no": "999888", "supplier": "越南在地供應商", "items": "辦公耗材與五金", "qty": "10式", "amount_vnd": "8,500,000", "status": "🔴 待付款"}
            if not any(x["invoice_no"] == "999888" for x in current_tenant["ap_invoices"]):
                current_tenant["ap_invoices"].append(new_inv)
            st.success("🎉 發票解析成功，已自動連動至貴公司的應付帳款與負債表！")
        if current_tenant["ap_invoices"]:
            st.dataframe(pd.DataFrame(current_tenant["ap_invoices"]), use_container_width=True)
        else:
            st.info("目前尚無應付帳款紀錄。")

    else:
        st.markdown(f"## 👑 {current_tenant['name']}：高階戰情室與 P&L 預覽")
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("📊 本月應付帳款總額", "23,500,000 VND", delta="自動連動")
        with k2:
            st.metric("💵 公司現金流水位", "1,200,000,000 VND", delta="+3.1%")
        with k3:
            st.metric("💱 匯率與原物料", "25,400 VND / USD", delta="正常")
