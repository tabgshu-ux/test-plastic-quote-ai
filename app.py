import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 1. 頁面基本設定 (Mobile-First & 企業級外觀)
st.set_page_config(
    page_title="SaaS Enterprise ERP Control Center",
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

# 3. 初始化 Session State 模擬動態組織樹、硬體裝置與租戶訂閱模組
if "org_nodes" not in st.session_state:
    st.session_state.org_nodes = [
        {"id": "node_01", "name": "👑 董事長室 / 總經理室", "type": "高階決策層", "parent": "無 (頂層)", "modules": ["全球股市/原物料/匯率", "集團綜合損益(P&L)"]},
        {"id": "node_02", "name": "👥 人力資源與行政管理部", "type": "行政支援", "parent": "👑 董事長室 / 總經理室", "modules": ["AI人臉辨識打卡", "指紋機與門禁管理"]},
        {"id": "node_03", "name": "🏭 生產製造廠務部", "type": "製造中心", "parent": "👑 董事長室 / 總經理室", "modules": ["MES現場報工", "廠區車牌辨識(ANPR)"]},
        {"id": "node_04", "name": "📦 廠內原物料倉庫 (生產部附屬)", "type": "實體據點/庫位", "parent": "🏭 生產製造廠務部", "modules": ["多倉儲位查詢", "條碼PDA收發貨"]}
    ]

if "iot_devices" not in st.session_state:
    st.session_state.iot_devices = [
        {"dev_id": "DEV-001", "name": "大門口 AI 人臉辨識打卡機", "type": "人臉辨識 (Face Recognition)", "ip": "192.168.1.110", "status": "🟢 連線中 (自動同步考勤)"},
        {"dev_id": "DEV-002", "name": "廠區車道車牌辨識攝影機 (ANPR)", "type": "車牌辨識 (License Plate)", "ip": "192.168.1.115", "status": "🟢 運作中 (自動放行與記錄)"}
    ]

# 模擬模組市集的訂閱開關狀態
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
    st.markdown("### 🌐 SaaS ERP 總控台")
    
    lang = st.selectbox("選擇語系 / Select Language", ["繁體中文", "English", "Tiếng Việt (越南語)", "简体中文"])
    
    st.markdown("---")
    st.markdown("👤 **目前登入者**: `System Admin` (極致懶人滑鼠流)")
    st.markdown("🏢 **目前租戶**: `SaaS Global Control`")
    
    st.markdown("---")
    st.markdown("### 📌 系統導覽選單")
    menu_choice = st.radio(
        "選擇管理模組",
        [
            "🖱️ 滑鼠流視覺化組織與據點拼圖",
            "🤖 AI 硬體與智慧門禁/車牌辨識掛接 (IoT & Biometrics)",
            "🔌 外部資料庫與 API 快速掛接 (Database Bridge)", 
            "📦 模組市集與功能授權設定 (App Store)",
            "🇻🇳 跨國在地化與越南財稅模組 (VN Localization)",
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
        preset_dept = st.selectbox("選擇要新增的部門或實體據點：", [
            "👥 人力資源與行政管理部",
            "🌍 國際貿易與海外業務部",
            "🛒 供應鏈與全球採購部",
            "🚚 廠外物流轉運倉 (掛採購部)",
            "🔍 品質保證與品管中心 (QA/QC)",
            "💻 資訊技術與系統開發部 (IT)"
        ])
        
        existing_parents = [node["name"] for node in st.session_state.org_nodes]
        target_parent = st.selectbox("指定其上級掛載點 (Parent):", existing_parents)
        
        st.markdown("#### 🧩 快速勾選功能拼圖：")
        p1, p2 = st.columns(2)
        with p1:
            chk_1 = st.checkbox("📈 股市/原物料/匯率戰情室", value=False)
            chk_2 = st.checkbox("💰 財務損益與應收付總覽", value=False)
            chk_3 = st.checkbox("📦 庫存與倉儲條碼掃描", value=True)
        with p2:
            chk_4 = st.checkbox("⚙️ 工程估驗與施工日報", value=False)
            chk_5 = st.checkbox("👥 人事考勤與薪酬管理", value=False)
            chk_6 = st.checkbox("🇻🇳 越南電子發票與稅務", value=False)
            
        if st.button("🖱️ 滑鼠一鍵確認掛載", type="primary", use_container_width=True):
            mods = []
            if chk_1: mods.append("📈 股市/原物料/匯率戰情室")
            if chk_2: mods.append("💰 財務損益與應收付總覽")
            if chk_3: mods.append("📦 庫存與倉儲條碼掃描")
            if chk_4: mods.append("⚙️ 工程估驗與施工日報")
            if chk_5: mods.append("👥 人事考勤與薪酬管理")
            if chk_6: mods.append("🇻🇳 越南電子發票與稅務")
            
            node_type = "實體據點/庫位" if "倉" in preset_dept else "營運/行政部門"
            st.session_state.org_nodes.append({
                "id": f"n_{len(st.session_state.org_nodes)+1}",
                "name": preset_dept,
                "type": node_type,
                "parent": target_parent,
                "modules": mods
            })
            st.success(f"🎉 成功將 [{preset_dept}] 掛載至 [{target_parent}] 下方！")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_tree:
        st.markdown("### 🌳 目前企業組織樹狀拼圖總覽")
        st.info("💡 滑鼠點選即時生成的組織與實體據點掛載關係：")
        
        for node in st.session_state.org_nodes:
            is_loc = "實體據點" in node['type']
            indent = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;┗ 📦 " if is_loc else ("&nbsp;&nbsp;&nbsp;&nbsp;┗ 📂 " if node["parent"] != "無 (頂層主節點)" else "👑 ")
            border_color = "#10b981" if is_loc else "#3b82f6"
            
            st.markdown(f"""
                <div style="background: white; padding: 10px; border-radius: 6px; margin-bottom: 8px; border-left: 4px solid {border_color};">
                    <b>{indent}{node['name']}</b> <span style="font-size: 11px; color: gray;">({node['type']})</span><br>
                    <span style="font-size: 11px; color: #0f766e;">📌 上級掛載：{node['parent']}</span><br>
                    <span style="font-size: 11px; color: #6b7280;">🧩 啟用拼圖：{', '.join(node['modules']) if node['modules'] else '無'}</span>
                </div>
            """, unsafe_allow_html=True)

elif "AI 硬體與智慧門禁/車牌辨識掛接" in menu_choice:
    st.markdown("## 🤖 AI 硬體與智慧門禁/車牌辨識掛接 (IoT & Biometrics Plug & Play)")
    st.info("💡 *零設定、滑鼠流！在此處您可以一鍵掛接各種硬體裝置。*")

elif "外部資料庫與 API 快速掛接" in menu_choice:
    st.markdown("## 🔌 外部資料庫與 API 快速掛接 (Database Bridge)")
    st.info("💡 說明：透過滑鼠點選與參數填寫，輕鬆對接外部資料庫與 API。")

elif "模組市集與功能授權設定" in menu_choice:
    st.markdown("## 📦 模組市集與功能授權設定 (App Store & Feature Toggles)")
    st.info("💡 *歡迎來到 SaaS 萬能模組市集！在此處您可以像逛 App Store 一樣，用滑鼠隨選隨開，為您的企業或跨界業務（製造業、越南財稅、物聯網、洗車場、咖啡廳等）即時解鎖強大功能。*")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🛒 跨業態與核心模組雲端市集")
        st.markdown("您可以透過下方的滑鼠開關，即時為本租戶（公司）訂閱或關閉對應的垂直模組：")
        
        c_app1, c_app2 = st.columns(2)
        
        with c_app1:
            st.markdown("#### 🇻🇳 跨國在地化與財稅解決方案")
            sub_vn = st.toggle("越南紅發票自動解析與 VAT 稅務模組", value=st.session_state.app_store_subscriptions["vn_tax"])
            sub_mfg = st.toggle("製造業 MES 現場報工與 OEE 設備監控", value=st.session_state.app_store_subscriptions["mfg_mes"])
            sub_bi = st.toggle("高階董事會戰情室 (股市/原物料/匯率/P&L)", value=st.session_state.app_store_subscriptions["bi_market"])
            
        with c_app2:
            st.markdown("#### 🚀 跨界與物聯網 (IoT) 擴充模組")
            sub_iot = st.toggle("AI 人臉辨識、指紋與車牌辨識 (ANPR) 閘道", value=st.session_state.app_store_subscriptions["iot_bridge"])
            sub_wash = st.toggle("洗車場專用：會員儲值、預約與水刀聯動模組", value=st.session_state.app_store_subscriptions["car_wash"])
            sub_cafe = st.toggle("連鎖咖啡廳專用：POS 點餐與原料自動扣減", value=st.session_state.app_store_subscriptions["coffee_pos"])
            
        st.markdown("---")
        if st.button("💾 儲存並即時更新本租戶模組授權", type="primary", use_container_width=True):
            st.session_state.app_store_subscriptions["vn_tax"] = sub_vn
            st.session_state.app_store_subscriptions["mfg_mes"] = sub_mfg
            st.session_state.app_store_subscriptions["bi_market"] = sub_bi
            st.session_state.app_store_subscriptions["iot_bridge"] = sub_iot
            st.session_state.app_store_subscriptions["car_wash"] = sub_wash
            st.session_state.app_store_subscriptions["coffee_pos"] = sub_cafe
            st.success("🎉 模組市集授權已即時更新！系統側邊欄與功能權限已動態重構完畢。")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 顯示目前已開通的強大模組清單預覽
        st.markdown("### 📋 本租戶目前已解鎖啟用的模組總覽")
        active_modules_list = [k for k, v in st.session_state.app_store_subscriptions.items() if v]
        st.info(f"✨ 目前本公司已啟用的核心與跨界模組代碼：`{', '.join(active_modules_list)}`")

elif "跨國在地化與越南財稅模組" in menu_choice:
    st.markdown("## 🇻🇳 跨國在地化與越南財稅模組 (Vietnam Localization & E-Invoice)")
    st.info("💡 說明：越南紅發票自動解析與 VAT 稅額勾稽。")

else:
    st.markdown("## 📊 系統運行與跨庫數據監控")
    st.info("💡 說明：即時監控各個已掛接外部資料庫與 API 來源的同步狀態。")
