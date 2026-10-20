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

# 3. 初始化 Session State 模擬動態組織與拼圖資料庫
if "org_nodes" not in st.session_state:
    st.session_state.org_nodes = [
        {"id": "node_01", "name": "董事會 / 總經理室", "type": "高階決策層", "parent": "無 (頂層)", "modules": ["全球股市/原物料/匯率", "集團綜合損益(P&L)", "應收/應付水位"]},
        {"id": "node_02", "name": "工程部", "type": "營運部門", "parent": "董事會 / 總經理室", "modules": ["工程估驗計價", "施工日報表", "點工點料回報"]},
        {"id": "node_03", "name": "管理部", "type": "行政支援", "parent": "董事會 / 總經理室", "modules": ["人事考勤薪資", "電子簽核(BPM)", "資安與合規"]},
        {"id": "node_04", "name": "生產部", "type": "製造中心", "parent": "董事會 / 總經理室", "modules": ["MES現場報工", "BOM表與製程", "OEE設備監控"]},
        {"id": "node_05", "name": "廠內原物料倉庫", "type": "實體據點/庫位", "parent": "生產部", "modules": ["多倉儲位查詢", "條碼PDA收發貨", "安全庫存警示"]}
    ]

# 4. 側邊欄導覽
with st.sidebar:
    st.image("https://img.icons8.com/color/96/company.png", width=64)
    st.markdown("### 🌐 SaaS ERP 總控台")
    
    lang = st.selectbox("選擇語系 / Select Language", ["繁體中文", "English", "Tiếng Việt (越南語)", "简体中文"])
    
    st.markdown("---")
    st.markdown("👤 **目前登入者**: `System Admin`")
    st.markdown("🏢 **目前租戶**: `SaaS Global Control`")
    
    st.markdown("---")
    st.markdown("### 📌 系統導覽選單")
    menu_choice = st.radio(
        "選擇管理模組",
        [
            "🧩 動態組織拼圖與樹狀架構 (Visual Org Builder)",
            "🔌 外部資料庫與 API 串聯 (Database Bridge)", 
            "📦 模組市集與功能授權設定 (App Store)",
            "🇻🇳 跨國在地化與越南財稅模組 (VN Localization)",
            "📊 系統運行與跨庫數據監控"
        ]
    )
    
    st.markdown("---")
    if st.button("🚪 登出系統", use_container_width=True):
        st.info("已安全登出系統。")

# 5. 主畫面邏輯路由
if "動態組織拼圖與樹狀架構" in menu_choice:
    st.markdown("## 🧩 動態組織拼圖與樹狀架構管理 (Visual Org-Chart Builder)")
    st.info("💡 *無須繁瑣打字！您可以直接點擊下方的【一鍵快選範本】，滑鼠點兩下就能立刻將常用部門與拼圖掛載至組織樹中。*")
    
    # 🌟 亮點功能：一鍵快選拼圖按鈕區 (免打字，點兩下直接加入)
    st.markdown("### ⚡ 一鍵快速拼裝推薦範本 (Quick-Add Presets)")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    
    with q_col1:
        if st.button("👑 一鍵加：董事長室", use_container_width=True):
            st.session_state.org_nodes.append({
                "id": f"node_{len(st.session_state.org_nodes)+1:02d}",
                "name": "董事長室 (戰情中心)",
                "type": "高階決策層",
                "parent": "無 (頂層)",
                "modules": ["全球股市/原物料/匯率", "集團綜合損益(P&L)", "應收/應付水位"]
            })
            st.success("🎉 已成功一鍵拼入【董事長室】！")
            st.rerun()
            
    with q_col2:
        if st.button("⚙️ 一鍵加：工程部", use_container_width=True):
            st.session_state.org_nodes.append({
                "id": f"node_{len(st.session_state.org_nodes)+1:02d}",
                "name": "工程設計中心",
                "type": "營運部門",
                "parent": "董事會 / 總經理室",
                "modules": ["工程估驗計價", "施工日報表", "點工點料回報"]
            })
            st.success("🎉 已成功一鍵拼入【工程設計中心】！")
            st.rerun()
            
    with q_col3:
        if st.button("📦 一鍵加：倉庫據點", use_container_width=True):
            st.session_state.org_nodes.append({
                "id": f"node_{len(st.session_state.org_nodes)+1:02d}",
                "name": "廠內原物料與成品倉庫",
                "type": "實體據點/庫位",
                "parent": "生產部",
                "modules": ["多倉儲位查詢", "條碼PDA收發貨", "安全庫存警示"]
            })
            st.success("🎉 已成功一鍵拼入【倉庫據點】於生產部下方！")
            st.rerun()
            
    with q_col4:
        if st.button("💰 一鍵加：財務會計部", use_container_width=True):
            st.session_state.org_nodes.append({
                "id": f"node_{len(st.session_state.org_nodes)+1:02d}",
                "name": "財務會計與越南稅務部",
                "type": "行政支援",
                "parent": "董事會 / 總經理室",
                "modules": ["總帳會計與傳票", "越南電子發票讀取", "應收/應付帳款"]
            })
            st.success("🎉 已成功一鍵拼入【財務會計部】！")
            st.rerun()

    st.markdown("---")
    
    col_builder, col_preview = st.columns([1, 1])
    
    with col_builder:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🧱 自訂拼裝組織節點 / 實體據點")
        with st.form("org_builder_form"):
            # 提供常見下拉選項免手動打字
            department_presets = [
                "請選擇或自訂部門...", "總經理室 / 執行長辦公室", "經營企劃處", 
                "財務與資本運作部", "會計與稅務管理部", "人力資源部", 
                "國內業務處", "國際貿易與海外業務部", "市場行銷企劃部", 
                "供應鏈與全球採購部", "倉儲物流與庫存管理", "生產製造廠務部", 
                "工程與技術服務部", "品質保證與品管中心 (QA/QC)", "資訊技術與研發部 (IT)"
            ]
            selected_preset = st.selectbox("快速選擇標準部門/倉庫", department_presets)
            custom_name = st.text_input("或自行輸入名稱", placeholder="若上方沒有可在此手動輸入...")
            
            final_name = custom_name if custom_name else (selected_preset if selected_preset != "請選擇或自訂部門..." else "")
            
            new_type = st.selectbox("節點屬性", ["營運/行政部門 (Department)", "高階決策層 (Board/Exec)", "實體據點/倉庫 (Location/Warehouse)", "子公司/分公司 (Branch)"])
            
            existing_names = [node["name"] for node in st.session_state.org_nodes]
            parent_options = ["無 (頂層主節點)"] + existing_names
            new_parent = st.selectbox("指定上級掛載點 (Parent Node)", parent_options)
            
            st.markdown("#### 🧩 勾選此節點要啟用的功能拼圖：")
            feat_c1, feat_c2 = st.columns(2)
            with feat_c1:
                f1 = st.checkbox("📈 股市/原物料/匯率戰情室", value=False)
                f2 = st.checkbox("💰 財務損益與應收付總覽", value=False)
                f3 = st.checkbox("📦 庫存與倉儲條碼掃描", value=True)
            with feat_c2:
                f4 = st.checkbox("⚙️ 工程估驗與施工日報", value=False)
                f5 = st.checkbox("👥 人事考勤與薪酬管理", value=False)
                f6 = st.checkbox("🇻🇳 越南電子發票與稅務", value=False)

            submitted = st.form_submit_button("🧱 確認拼入組織架構", type="primary", use_container_width=True)
            if submitted:
                if not final_name:
                    st.error("❌ 請選擇或輸入名稱！")
                else:
                    selected_feats = []
                    if f1: selected_feats.append("📈 股市/原物料/匯率戰情室")
                    if f2: selected_feats.append("💰 財務損益與應收付總覽")
                    if f3: selected_feats.append("📦 庫存與倉儲條碼掃描")
                    if f4: selected_feats.append("⚙️ 工程估驗與施工日報")
                    if f5: selected_feats.append("👥 人事考勤與薪酬管理")
                    if f6: selected_feats.append("🇻🇳 越南電子發票與稅務")
                    
                    new_node = {
                        "id": f"node_{len(st.session_state.org_nodes)+1:02d}",
                        "name": final_name,
                        "type": new_type,
                        "parent": new_parent,
                        "modules": selected_feats
                    }
                    st.session_state.org_nodes.append(new_node)
                    st.success(f"🎉 成功將 [{final_name}] 拼裝至上級節點：`{new_parent}`！")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_preview:
        st.markdown("### 🌳 目前企業組織樹狀拼圖總覽")
        st.info("💡 視覺化呈現您目前的組織階層與掛載關係：")
        
        for node in st.session_state.org_nodes:
            indent = "&nbsp;&nbsp;&nbsp;&nbsp;┗ 📂 " if node["parent"] != "無 (頂層主節點)" else "👑 "
            st.markdown(f"""
                <div style="background: white; padding: 10px; border-radius: 6px; margin-bottom: 8px; border-left: 4px solid #3b82f6;">
                    <b>{indent}{node['name']}</b> <span style="font-size: 12px; color: gray;">({node['type']})</span><br>
                    <span style="font-size: 12px; color: #0f766e;">📌 上級掛載：{node['parent']}</span><br>
                    <span style="font-size: 12px; color: #6b7280;">🧩 啟用拼圖：{', '.join(node['modules']) if node['modules'] else '無'}</span>
                </div>
            """, unsafe_allow_html=True)

elif "外部資料庫與 API 串聯" in menu_choice:
    st.markdown("## 🔌 外部資料庫與異質資料來源串聯設定 (Database Bridge)")
    st.info("💡 *在此處您可以設定與擴充對外連結的其他客戶資料庫或即時 API 來源，無須修改程式碼。*")

elif "模組市集與功能授權設定" in menu_choice:
    st.markdown("## 📦 模組市集與功能授權設定 (App Store & Feature Toggles)")
    st.info("💡 說明：在此處管理全系統所有可用的企業模組市集。")

elif "跨國在地化與越南財稅模組" in menu_choice:
    st.markdown("## 🇻🇳 跨國在地化與越南財稅模組 (Vietnam Localization & E-Invoice)")
    st.info("💡 說明：越南紅發票自動解析與 VAT 稅額勾稽。")

else:
    st.markdown("## 📊 系統運行與跨庫數據監控")
    st.info("💡 說明：即時監控各個已掛接外部資料庫與 API 來源的同步狀態。")
