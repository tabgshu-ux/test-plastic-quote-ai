import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 1. 頁面基本設定 (Mobile-First & 企業級外觀)
st.set_page_config(
    page_title="SaaS Enterprise Multi-Tenant AI-ERP",
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

# 3. 初始化多租戶資料庫中心 (Multi-Tenant Data Hub)
if "tenants_db" not in st.session_state:
    st.session_state.tenants_db = {
        "tenant_master": {
            "name": "SaaS 總控台 (平台運營商)",
            "org_nodes": [],
            "iot_devices": [],
            "ap_invoices": []
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
            ]
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
            "ap_invoices": []
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
    
    # 取得當前切換的租戶資料
    current_tenant = st.session_state.tenants_db[current_tenant_key]
    
    st.markdown(f"👤 **目前身份**: `Tenant Admin`")
    st.markdown(f"🏢 **目前所屬公司**: `{current_tenant['name']}`")
    
    st.markdown("---")
    st.markdown("### 📌 系統導覽選單")
    
    if current_tenant_key == "tenant_master":
        # 總控台只能看平台級設定與模組市集
        menu_choice = st.radio(
            "選擇管理模組 (Master)",
            [
                "📦 SaaS 平台模組市集 (App Store & Licensing)",
                "📊 平台運行狀態與跨租戶監控"
            ]
        )
    else:
        # 客戶自己的獨立租戶後台 (IT 自行設定)
        menu_choice = st.radio(
            "選擇客戶內部模組 (Tenant IT Panel)",
            [
                "🖱️ 本公司組織與實體據點 IT 自行設定",
                "🤖 本公司 AI 硬體與車牌/人臉辨識掛接",
                "🇻🇳 本公司越南紅發票與應付帳款 (AP)",
                "👑 董事長高階戰情室與 P&L 預覽",
                "📊 本公司系統數據監控"
            ]
        )
    
    st.markdown("---")
    if st.button("🚪 登出系統", use_container_width=True):
        st.info("已安全登出系統。")

# 5. 主畫面邏輯路由
if current_tenant_key == "tenant_master":
    # ==================== SaaS 總控台 (我們自己看的) ====================
    st.markdown("## 📦 SaaS 平台總控台：模組市集與全球授權管理 (Master Control)")
    st.info("💡 *此處為總公司平台運營商視角。您可以管理全平台的模組市集，決定哪些行業（製造業、水電、洗車場、咖啡廳）可以使用哪些擴充拼圖。*")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🛒 全球模組市集與訂閱授權總表 (Global App Store)")
        c1, c2 = st.columns(2)
        with c1:
            st.toggle("越南紅發票自動解析與 VAT 稅務模組", value=True)
            st.toggle("製造業 MES 現場報工與 OEE 設備監控", value=True)
            st.toggle("高階董事會戰情室 (股市/原物料/匯率/P&L)", value=True)
        with c2:
            st.toggle("AI 人臉辨識與車牌辨識 (ANPR) 閘道", value=True)
            st.toggle("洗車場專用：會員儲值與水刀聯動模組", value=True)
            st.toggle("連鎖咖啡廳專用：POS 點餐與原料扣減", value=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("### 🏢 目前平台已註冊的獨立租戶 (Tenants List)")
    tenant_summary_df = pd.DataFrame([
        {"租戶代碼": "tenant_vina_水电", "公司名稱": "越南平陽水電工程有限公司", "方案": "跨國製造/工程版", "狀態": "🟢 正常營運"},
        {"租戶代碼": "tenant_taipei_wash", "公司名稱": "台北極速智慧洗車坊", "方案": "智慧零售/服務版", "狀態": "🟢 正常營運"}
    ])
    st.dataframe(tenant_summary_df, use_container_width=True)

else:
    # ==================== 獨立客戶租戶後台 (客戶 IT 自行設定) ====================
    if "組織與實體據點" in menu_choice:
        st.markdown(f"## 🖱️ {current_tenant['name']}：組織樹與實體據點自助設定 (Tenant IT Panel)")
        st.info("💡 *這是客戶自己的 IT 後台。貴公司的 IT 人員可以隨時透過滑鼠新增部門、指定上級（例如將倉庫掛在生產部下方），完全不需要透過我們！*")
        
        # 快速掛載按鈕
        st.markdown("### ⚡ 客戶 IT 自助快速掛載矩陣 (Click-to-Add)")
        c_k1, c_k2, c_k3 = st.columns(3)
        with c_k1:
            if st.button("➕ 新增：財務會計部", use_container_width=True):
                current_tenant["org_nodes"].append({"id": f"n_{len(current_tenant['org_nodes'])+1}", "name": "💰 財務會計部", "type": "行政支援", "parent": "👑 總經理室", "modules": ["總帳", "應付帳款"]})
                st.rerun()
        with c_k2:
            if st.button("➕ 新增：採購部", use_container_width=True):
                current_tenant["org_nodes"].append({"id": f"n_{len(current_tenant['org_nodes'])+1}", "name": "🛒 全球採購部", "type": "營運部門", "parent": "👑 總經理室", "modules": ["請購", "採購單"]})
                st.rerun()
        with c_k3:
            if st.button("➕ 新增：工廠倉庫(掛生產部)", use_container_width=True):
                current_tenant["org_nodes"].append({"id": f"n_{len(current_tenant['org_nodes'])+1}", "name": "📦 廠內零組件倉庫", "type": "實體據點/庫位", "parent": "🏭 生產製造廠務部", "modules": ["庫存", "PDA"]})
                st.rerun()
                
        st.markdown("---")
        col_set, col_view = st.columns([1, 1])
        
        with col_set:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 🛠️ 自訂新增部門或據點")
            new_dept = st.text_input("輸入部門或據點名稱", placeholder="例：越南美福二廠 / 業務部")
            existing_parents = [n["name"] for n in current_tenant["org_nodes"]]
            chosen_parent = st.selectbox("指定上級掛載點", existing_parents)
            
            if st.button("🧱 確認加入公司組織樹", type="primary", use_container_width=True):
                if new_dept:
                    current_tenant["org_nodes"].append({"id": f"n_{len(current_tenant['org_nodes'])+1}", "name": new_dept, "type": "自訂部門", "parent": chosen_parent, "modules": ["日常作業"]})
                    st.success(f"🎉 成功在貴公司組織下新增 [{new_dept}]！")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_view:
            st.markdown("### 🌳 貴公司目前的組織與據點樹狀圖")
            for node in current_tenant["org_nodes"]:
                is_loc = "實體據點" in node['type']
                indent = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;┗ 📦 " if is_loc else ("&nbsp;&nbsp;&nbsp;&nbsp;┗ 📂 " if node["parent"] != "無 (頂層)" else "👑 ")
                st.markdown(f"""
                    <div style="background: white; padding: 10px; border-radius: 6px; margin-bottom: 8px; border-left: 4px solid #3b82f6;">
                        <b>{indent}{node['name']}</b> <span style="font-size: 11px; color: gray;">({node['type']})</span><br>
                        <span style="font-size: 11px; color: #0f766e;">📌 上級掛載：{node['parent']}</span>
                    </div>
                """, unsafe_allow_html=True)

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
                        current_tenant["iot_devices"].append({"dev_id": f"DEV-{len(current_tenant['iot_devices']+1)}", "name": d_name, "type": "智慧感測", "ip": d_ip, "status": "🟢 聯機中"})
                        st.success(f"🎉 成功為貴公司掛接硬體 [{d_name}]！")
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("### 📋 貴公司目前已連線的硬體設備")
        if current_tenant["iot_devices"]:
            st.dataframe(pd.DataFrame(current_tenant["iot_devices"]), use_container_width=True)
        else:
            st.info("目前尚未連線任何硬體裝置。")

    elif "越南紅發票" in menu_choice:
        st.markdown(f"## 🇻🇳 {current_tenant['name']}：越南紅發票與應付帳款 (AP)")
        st.info("💡 *上傳越南發票後，系統自動串聯應付帳款與董事長戰情室。*")
        
        up_file = st.file_uploader("上傳越南電子發票 (XML / PDF)", type=["xml", "pdf"])
        if up_file or st.button("⚡ 模擬一鍵上傳發票並自動串聯", type="primary"):
            new_inv = {"invoice_no": "999888", "supplier": "越南在地供應商", "items": "辦公耗材與五金", "qty": "10式", "amount_vnd": "8,500,000", "status": "🔴 待付款"}
            if not any(x["invoice_no"] == "999888" for x in current_tenant["ap_invoices"]):
                current_tenant["ap_invoices"].append(new_inv)
            st.success("🎉 發票解析成功，已自動連動至貴公司的應付帳款與負債表！")
            
        st.markdown("### 📚 貴公司目前的應付帳款總表 (AP Ledger)")
        if current_tenant["ap_invoices"]:
            st.dataframe(pd.DataFrame(current_tenant["ap_invoices"]), use_container_width=True)
        else:
            st.info("目前尚無應付帳款紀錄。")

    elif "董事長高階戰情室" in menu_choice:
        st.markdown(f"## 👑 {current_tenant['name']}：高階戰情室與 P&L 預覽")
        st.info("💡 *戰情數字即時反映該租戶內部的發票與營運數據。*")
        
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("📊 本月應付帳款總額", "23,500,000 VND", delta="自動連動")
        with k2:
            st.metric("💵 公司現金流水位", "1,200,000,000 VND", delta="+3.1%")
        with k2:
            st.metric("💱 匯率與原物料", "25,400 VND / USD", delta="正常")
            
    else:
        st.markdown(f"## 📊 {current_tenant['name']}：系統運行監控")
        st.info("💡 即時監控貴公司專屬資料庫與 API 連結狀態。")
