import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 1. 頁面基本設定 (Mobile-First & 企業級外觀)
st.set_page_config(
    page_title="SaaS Enterprise Multi-Tenant AI-ERP & Billing",
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

# 3. 初始化多租戶資料庫與商業計費中心 (Billing & Tenants Hub)
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
                "monthly_fee_usd": 150,
                "extra_departments": 4,
                "extra_fee_usd": 20, # 每多一個部門 +5 USD
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
                "monthly_fee_usd": 80,
                "extra_departments": 2,
                "extra_fee_usd": 0,
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
                "📦 SaaS 平台模組市集與全租戶營收監控 (Master Billing)",
                "📊 平台運行狀態與跨租戶數據監控"
            ]
        )
    else:
        menu_choice = st.radio(
            "選擇客戶內部模組 (Tenant IT Panel)",
            [
                "🖱️ 本公司組織與據點 IT 自行設定 (含計費)",
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
    # ==================== SaaS 總控台 (我們自己看的營收與續約管理) ====================
    st.markdown("## 📦 SaaS 平台總控台：全租戶營收、訂閱與續約管理 (Master Billing)")
    st.info("💡 *此處為平台運營商視角。您可以總覽所有客戶的訂閱方案、每月經常性收入 (MRR)、部門擴充計費與維修合約到期狀況。*")
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("💰 平台總 MRR (月營收)", "230 USD", delta="+15% MoM")
    with m2:
        st.metric("🏢 活躍企業租戶數", "2 家", delta="成長中")
    with m3:
        st.metric("⚠️ 30天內即將到期合約", "1 家 (台北洗車坊)", delta="需發送續約提醒", delta_color="inverse")
    with m4:
        st.metric("💳 自動續約扣款成功率", "100%", delta="Stripe Gateway")
        
    st.markdown("---")
    st.markdown("### 📋 所有企業租戶訂閱與計費總表")
    billing_summary_data = [
        {"租戶代碼": "tenant_vina_水电", "公司名稱": "越南平陽水電工程", "訂閱方案": "企業旗艦版 ($150)", "部門數": 4, "額外加收": "$20", "合約到期日": "2027-10-20", "狀態": "🟢 正常"},
        {"租戶代碼": "tenant_taipei_wash", "公司名稱": "台北極速智慧洗車坊", "訂閱方案": "標準版 ($80)", "部門數": 2, "額外加收": "$0", "合約到期日": "2026-11-05", "狀態": "🟡 15天後到期"}
    ]
    st.dataframe(pd.DataFrame(billing_summary_data), use_container_width=True)

else:
    # ==================== 獨立客戶租戶後台 (含部門新增付費與續約管理) ====================
    if "組織與據點" in menu_choice:
        st.markdown(f"## 🖱️ {current_tenant['name']}：組織樹與實體據點自助設定 (含按量計費)")
        st.info("💡 *貴公司的 IT 可以隨時新增部門或倉庫。注意：系統採彈性計費，每新增一個部門或實體據點將自動加收 5 USD/月。*")
        
        # 顯示當前計費提示
        sub_info = current_tenant["subscription"]
        st.warning(f"💳 **目前計費方案**：`{sub_info['plan']}` | 現有部門/據點數：`{len(current_tenant['org_nodes'])}` 個 (每月額外加收：`$ {sub_info['extra_fee_usd']} USD`)")
        
        col_set, col_view = st.columns([1, 1])
        
        with col_set:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### ➕ 新增部門或實體據點 (付費確認)")
            new_dept = st.text_input("輸入要新增的部門或倉庫名稱", placeholder="例：越南美福二廠 / 財務部")
            existing_parents = [n["name"] for n in current_tenant["org_nodes"]]
            chosen_parent = st.selectbox("指定上級掛載點", existing_parents)
            
            st.markdown("ℹ️ *新增此據點將使您的每月訂閱費自動增加 5 USD。*")
            if st.button("💳 確認加購並新增部門/據點", type="primary", use_container_width=True):
                if new_dept:
                    current_tenant["org_nodes"].append({"id": f"n_{len(current_tenant['org_nodes'])+1}", "name": new_dept, "type": "自訂部門/據點", "parent": chosen_parent, "modules": ["日常作業"]})
                    current_tenant["subscription"]["extra_fee_usd"] += 5
                    st.success(f"🎉 成功新增 [{new_dept}]！已自動更新每月帳單（增加 5 USD）。")
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
        st.info("💡 *在此處您可以檢視貴公司的軟體訂閱狀態、維修合約等級，並透過線上金流隨時進行續約或升級方案。*")
        
        sub = current_tenant["subscription"]
        
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 📦 目前訂閱與帳單明細")
            st.markdown(f"- **目前方案**: `{sub['plan']}`")
            st.markdown(f"- **訂閱狀態**: `{sub['status']}`")
            st.markdown(f"- **合約到期日**: `{sub['expires']}`")
            st.markdown(f"- **基本月租費**: `$ {sub['monthly_fee_usd']} USD`")
            st.markdown(f"- **額外部門/據點加收**: `$ {sub['extra_fee_usd']} USD`")
            st.markdown(f"- **總計每月應繳金額**: **`$ {sub['monthly_fee_usd'] + sub['extra_fee_usd']} USD / 月`**")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with sc2:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 🛠️ 維修合約與技術支援 (Maintenance)")
            st.markdown(f"- **維修等級**: `{sub['maintenance_contract']}`")
            st.markdown("- **硬體遠端保固**: `包含 (人臉機/車牌機/IoT 設備)`")
            st.markdown("- **專屬技術顧問**: `線上 7x24 即時支援`")
            
            st.markdown("---")
            if st.button("🚀 立即線上續約 1 年 (享有 9 折優惠)", type="primary", use_container_width=True):
                st.success("🎉 續約成功！系統已透過金流閘道完成扣款，合約有效期限已自動展延一年！")
            st.markdown('</div>', unsafe_allow_html=True)

    elif "AI 硬體與車牌" in menu_choice:
        st.markdown(f"## 🤖 {current_tenant['name']}：AI 硬體與車牌/人臉辨識自助掛接")
        st.info("💡 *貴公司的 IT 可以在此自行輸入硬體 IP，將人臉辨識機或車牌辨識攝影機直接連進公司系統。*")
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
        st.info("💡 *上傳越南發票後，系統自動串聯應付帳款與董事長戰情室。*")
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
        st.info("💡 *戰情數字即時反映該租戶內部的發票與營運數據。*")
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("📊 本月應付帳款總額", "23,500,000 VND", delta="自動連動")
        with k2:
            st.metric("💵 公司現金流水位", "1,200,000,000 VND", delta="+3.1%")
        with k3:
            st.metric("💱 匯率與原物料", "25,400 VND / USD", delta="正常")
