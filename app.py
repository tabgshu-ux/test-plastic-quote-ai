import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 1. 頁面基本設定 (Mobile-First & 企業級外觀)
st.set_page_config(
    page_title="SaaS Enterprise AI-ERP Control Center",
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

# 3. 初始化全系統資料庫中心 (Data Hub Session State)
if "org_nodes" not in st.session_state:
    st.session_state.org_nodes = [
        {"id": "node_01", "name": "👑 董事長室 / 總經理室", "type": "高階決策層", "parent": "無 (頂層)", "modules": ["全球股市/原物料/匯率", "集團綜合損益(P&L)"]},
        {"id": "node_02", "name": "👥 人力資源與總務行政部", "type": "行政支援", "parent": "👑 董事長室 / 總經理室", "modules": ["AI人臉辨識打卡", "廠區車牌辨識(ANPR)"]},
        {"id": "node_03", "name": "💰 財務會計與應付帳款部", "type": "財務中心", "parent": "👑 董事長室 / 總經理室", "modules": ["越南紅發票自動讀取", "應付帳款(AP)連動"]}
    ]

if "iot_devices" not in st.session_state:
    st.session_state.iot_devices = [
        {"dev_id": "DEV-001", "name": "大門口 AI 人臉辨識打卡機", "type": "人臉辨識", "ip": "192.168.1.110", "status": "🟢 連線中 (自動同步人事)"},
        {"dev_id": "DEV-002", "name": "廠區車道車牌辨識攝影機 (ANPR)", "type": "車牌辨識", "ip": "192.168.1.115", "status": "🟢 運作中 (同步保全與總務)"}
    ]

# 模擬全系統自動串聯的發票與應付帳款資料庫
if "ap_invoices" not in st.session_state:
    st.session_state.ap_invoices = [
        {
            "invoice_no": "00012345", 
            "supplier": "越南平陽水電材料有限公司 (Công ty TNHH Vina Material)", 
            "items": "PVC 電線管 50mm, 銅線 2.0", 
            "qty": "120 卷 / 支", 
            "amount_vnd": "16,500,000", 
            "status": "🔴 待付款 (已自動列入應付帳款與負債表)"
        }
    ]

if "app_store_subscriptions" not in st.session_state:
    st.session_state.app_store_subscriptions = {
        "vn_tax": True,
        "iot_bridge": True,
        "car_wash": False,
        "coffee_pos": False,
        "mfg_mes": True,
        "bi_market": True
    }

# 4. 側邊欄導覽
with st.sidebar:
    st.image("https://img.icons8.com/color/96/company.png", width=64)
    st.markdown("### 🌐 SaaS AI-ERP 總控台")
    
    lang = st.selectbox("選擇語系 / Select Language", ["繁體中文", "English", "Tiếng Việt (越南語)", "简体中文"])
    
    st.markdown("---")
    st.markdown("👤 **目前登入者**: `System Admin` (全系統自動串聯)")
    st.markdown("🏢 **目前租戶**: `SaaS Global Control`")
    
    st.markdown("---")
    st.markdown("### 📌 系統導覽選單")
    menu_choice = st.radio(
        "選擇管理模組",
        [
            "🖱️ 滑鼠流視覺化組織與據點拼圖",
            "🤖 AI 硬體與智慧門禁/車牌辨識掛接 (IoT & Biometrics)",
            "🇻🇳 跨國在地化與越南財稅模組 (VN Localization & AP)",
            "👑 董事長高階戰情室與財務連動預覽 (Executive P&L)",
            "📦 模組市集與功能授權設定 (App Store)",
            "📊 系統運行與跨庫數據監控"
        ]
    )
    
    st.markdown("---")
    if st.button("🚪 登出系統", use_container_width=True):
        st.info("已安全登出系統。")

# 5. 主畫面邏輯路由
if "滑鼠流視覺化組織與據點拼圖" in menu_choice:
    st.markdown("## 🖱️ 滑鼠流視覺化組織與實體據點拼圖 (Mouse-First Org Builder)")
    st.info("💡 *完全免打字！滑鼠點擊按鈕即可一鍵掛載部門或倉庫據點。*")
    
    st.markdown("### ⚡ 滑鼠一鍵快速掛載矩陣 (Click-to-Add)")
    m_c1, m_c2, m_c3, m_c4, m_c5 = st.columns(5)
    with m_c1:
        if st.button("👑 加入：董事長室", use_container_width=True):
            st.session_state.org_nodes.append({"id": f"n_{len(st.session_state.org_nodes)+1}", "name": "👑 董事長室 / 總經理室", "type": "高階決策層", "parent": "無 (頂層)", "modules": ["全球股市/原物料/匯率", "綜合損益表"]})
            st.rerun()
    with m_c2:
        if st.button("💰 加入：財務會計部", use_container_width=True):
            st.session_state.org_nodes.append({"id": f"n_{len(st.session_state.org_nodes)+1}", "name": "💰 財務會計與越南稅務部", "type": "行政支援", "parent": "👑 董事長室 / 總經理室", "modules": ["總帳會計", "越南紅發票自動讀取"]})
            st.rerun()
    with m_c3:
        if st.button("⚙️ 加入：工程設計部", use_container_width=True):
            st.session_state.org_nodes.append({"id": f"n_{len(st.session_state.org_nodes)+1}", "name": "⚙️ 工程與設計中心", "type": "營運部門", "parent": "👑 董事長室 / 總經理室", "modules": ["工程估驗計價", "施工日報表"]})
            st.rerun()
    with m_c4:
        if st.button("🏭 加入：生產製造部", use_container_width=True):
            st.session_state.org_nodes.append({"id": f"n_{len(st.session_state.org_nodes)+1}", "name": "🏭 生產製造廠務部", "type": "製造中心", "parent": "👑 董事長室 / 總經理室", "modules": ["MES現場報工", "BOM表管控"]})
            st.rerun()
    with m_c5:
        if st.button("📦 加入：倉庫(掛生產部)", use_container_width=True):
            st.session_state.org_nodes.append({"id": f"n_{len(st.session_state.org_nodes)+1}", "name": "📦 廠內原物料倉庫", "type": "實體據點/庫位", "parent": "🏭 生產製造廠務部", "modules": ["多倉儲位查詢", "條碼PDA收發貨"]})
            st.rerun()

    st.markdown("---")
    col_picker, col_tree = st.columns([1, 1])
    with col_picker:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🛠️ 自訂模組與據點快速拼裝")
        preset_dept = st.selectbox("選擇要新增的部門或實體據點：", ["👥 人力資源與總務行政部", "🌍 國際貿易與海外業務部", "🛒 供應鏈與全球採購部"])
        existing_parents = [node["name"] for node in st.session_state.org_nodes]
        target_parent = st.selectbox("指定其上級掛載點 (Parent):", existing_parents)
        if st.button("🖱️ 滑鼠一鍵確認掛載", type="primary", use_container_width=True):
            st.session_state.org_nodes.append({"id": f"n_{len(st.session_state.org_nodes)+1}", "name": preset_dept, "type": "營運/行政部門", "parent": target_parent, "modules": ["日常作業"]})
            st.success(f"🎉 成功將 [{preset_dept}] 掛載至 [{target_parent}]！")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_tree:
        st.markdown("### 🌳 目前企業組織樹狀拼圖總覽")
        for node in st.session_state.org_nodes:
            st.markdown(f"""
                <div style="background: white; padding: 10px; border-radius: 6px; margin-bottom: 8px; border-left: 4px solid #3b82f6;">
                    <b>📂 {node['name']}</b> <span style="font-size: 11px; color: gray;">({node['type']})</span><br>
                    <span style="font-size: 11px; color: #0f766e;">📌 上級掛載：{node['parent']}</span>
                </div>
            """, unsafe_allow_html=True)

elif "AI 硬體與智慧門禁/車牌辨識掛接" in menu_choice:
    st.markdown("## 🤖 AI 硬體與智慧門禁/車牌辨識掛接 (IoT & Biometrics Plug & Play)")
    st.info("💡 *車牌辨識 (ANPR) 影像與進出紀錄將自動即時推播至【保全室】與【總務/人事部】。*")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🚗 即時車牌辨識與門禁聯動模擬 (ANPR Live Event Bus)")
        mock_anpr_df = pd.DataFrame([
            {"時間": "2026-10-20 15:30:12", "車牌號碼": "61C-888.66", "車輛類型": "外包工程貨車", "分發狀態": "✅ 已同步推播至保全室門禁系統"},
            {"時間": "2026-10-20 14:15:05", "車牌號碼": "51A-123.45", "車輛類型": "總務公務車", "分發狀態": "✅ 已同步推播至總務/人事考勤記錄"},
            {"時間": "2026-10-20 11:02:40", "車牌號碼": "61B-555.11", "車輛類型": "供應商送貨車", "分發狀態": "✅ 已同步推播至保全與倉庫收貨端"}
        ])
        st.dataframe(mock_anpr_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif "跨國在地化與越南財稅模組" in menu_choice:
    st.markdown("## 🇻🇳 跨國在地化與越南財稅模組 (Vietnam Localization & AP Automation)")
    st.info("💡 *上傳越南紅發票後，系統會【全自動】將品項、數量、金額、供應商與發票號碼寫入財務應付帳款，並即時反映在負債表與董事長戰情室中！*")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 📄 越南電子發票解析與自動上下游串聯")
        uploaded_invoice = st.file_uploader("請上傳越南紅發票 (XML 或 PDF)", type=["xml", "pdf"])
        
        if uploaded_invoice or st.button("⚡ 模擬一鍵上傳並自動解析發票 (測試串聯)", type="primary"):
            st.success("🎉 發票解析成功！系統已自動完成全系統下游串聯：")
            col_iv1, col_iv2 = st.columns(2)
            with col_iv1:
                st.markdown("- **發票號碼**: `00099887`")
                st.markdown("- **開立公司 (供應商)**: `Công ty CP Thiết bị Điện Sài Gòn`")
                st.markdown("- **購買品項**: `工業級不斷電系統 (UPS) 5KVA`")
            with col_iv2:
                st.markdown("- **數量**: `2 台`")
                st.markdown("- **總金額 (含 VAT 10%)**: `35,200,000 VND`")
                st.markdown("- **串聯狀態**: 🟢 已自動寫入應付帳款與負債總額！")
                
            new_inv = {
                "invoice_no": "00099887",
                "supplier": "Công ty CP Thiết bị Điện Sài Gòn",
                "items": "工業級不斷電系統 (UPS) 5KVA",
                "qty": "2 台",
                "amount_vnd": "35,200,000",
                "status": "🔴 待付款 (已連動至負債與董事長戰情)"
            }
            if not any(d['invoice_no'] == '00099887' for d in st.session_state.ap_invoices):
                st.session_state.ap_invoices.append(new_inv)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 📚 目前財務應付帳款總表 (AP Ledger - 跨部門連動即時檢視)")
    st.dataframe(pd.DataFrame(st.session_state.ap_invoices), use_container_width=True)

elif "董事長高階戰情室與財務連動預覽" in menu_choice:
    st.markdown("## 👑 董事長高階戰情室與財務聯動預覽 (Executive Dashboard & P&L)")
    st.info("💡 *此處展示董事長或董事會登入時看到的即時戰情：發票金額自動加總、應付帳款負債水位、綜合損益表 (P&L) 與國際原物料/匯率行情。*")
    
    total_ap_amount = "51,700,000 VND"
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("📊 本月應付帳款總負債 (AP)", total_ap_amount, delta="即時連動發票資料庫", delta_color="inverse")
    with kpi2:
        st.metric("💵 集團現金流水位", "2,450,000,000 VND", delta="+5.2%")
    with kpi3:
        st.metric("💱 美金/越幣即時匯率", "25,400 VND", delta="-15 VND")
    with kpi4:
        st.metric("📈 銅價/原物料指數", "9,850 USD/T", delta="+1.4%")
        
    st.markdown("---")
    st.markdown("### 📑 集團綜合損益表與應付帳款連動摘要 (P&L Summary)")
    mock_pl = pd.DataFrame([
        {"財務科目": "營業收入淨額 (Revenue)", "金額 (VND)": "850,000,000", "狀態": "🟢 正常"},
        {"財務
