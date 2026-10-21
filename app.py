import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# 引入自訂模組
from modules.pricing_hub import render_pricing_hub
from modules.app_store import render_app_store
from modules.org_chart import render_org_chart

st.set_page_config(
    page_title="SaaS Global Cross-Border AI-ERP Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card-container { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); margin-bottom: 20px; }
    h1, h2, h3 { color: #1e293b; }
    .stButton>button { border-radius: 6px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 🌟 全球跨國通用 AI-ERP 模組庫 (已將多語系/AI翻譯抽離為全域基礎設施)
# ==============================================================================
if "master_module_library" not in st.session_state:
    st.session_state.master_module_library = {
        "📈 高階決策、跨國戰情與多維度 BI": [
            "全局原物料與市場即時行情看板", "國際匯率多幣別自動換算與避險中心", "全球主要股市與財經大盤監控", 
            "跨國多公司合併財務報表分析", "企業 KPI 戰情室與 AI 智慧營運健檢", "高階主管簽核流與授權矩陣", 
            "跨部門營運總控台與異常預警", "多國稅務合規與利潤匯出分析", "ESG 永續碳排與能源消耗戰情室"
        ],
        "📦 全球供應鏈、智慧進銷存與倉儲 (SCM & WMS)": [
            "智能進銷存與批號效期全生命周期管理", "全球供應商評鑑、自動比價與採購發包(PR/PO)", "智慧倉儲物流與 PDA 條碼掃描(WMS)", 
            "進出口報關、海運物流追蹤與原產地證明", "條碼/QR Code 全自動資產與物料標籤列印", "安全庫存水位 AI 自動補貨警報", 
            "多倉庫智能調撥、批次與序號追蹤", "供應商交期達標率與品質異常扣款追蹤", "全球保稅倉庫與免稅品項管理"
        ],
        "💰 跨國財會、電子發票與人事法規 (Finance & HR)": [
            "總帳會計、多幣別傳票與會計師國際報表", "全球應收(AR)智慧催收與應付(AP)現金流排程", "越南紅發票/電子發票與各國稅務勾稽", 
            "多國人事薪酬、外派人員勞健保與考勤排班", "GPS 定位行動打卡、外勤軌跡與排班管理", "AI 智慧履歷篩選、跨國面試與人才庫管理", 
            "全球電子簽核流程引擎 (BPM) 與委任授權", "固定資產盤點、多國折舊自動提列與租賃會計", "跨國勞資合規與在地化薪資法規資料庫"
        ],
        "🏭 智慧製造、專案管控與業務維運 (Manufacturing & Projects)": [
            "MES 製造執行系統與車間動態報工", "多階 BOM 表管理、製程工藝與標準SOP", "產線動態排程、瓶頸預警與產能平衡調度", 
            "大型跨國專案管理、里程碑與成本預算管控", "客戶關係管理(CRM)、全球商機與外貿銷售漏斗", "售後服務工單、設備維修履歷與定期保養排程", 
            "外包商工班計價、合約追蹤與驗收請款", "CAD/BIM 工程圖檔雲端協同與版本控制", "IoT 機台稼動率監控與 OEE 設備效率分析"
        ],
        "🤖 AI 語音多模態與智慧硬體整合 (AI & Hardware Integration)": [
            "車牌辨識(ANPR)智慧車道與物流車隊管理", "廠區人臉辨識門禁、訪客預約與考勤對接", "AI 智慧語音助理與多國文件即時跨語系翻譯", 
            "AI 智慧工安影像辨識與違規即時預警", "車輛保養、車隊 GPS 定位與外派油耗追蹤", "AI 智慧客服機器人與自動化客戶詢價回覆"
        ]
    }

if "global_plans_db" not in st.session_state:
    st.session_state.global_plans_db = {
        "🚀 跨國旗艦集團版 (Enterprise)": {
            "base_price": 350.0,
            "description": "適合跨國集團、製造業與大型企業，解鎖全產業模組與無限部門掛載",
            "included_modules": [
                "全局原物料與市場即時行情看板", "高階主管簽核流與授權矩陣", "智能進銷存與批號效期全生命周期管理", 
                "總帳會計、多幣別傳票與會計師國際報表", "跨部門營運總控台與異常預警"
            ]
        },
        "💼 正式商業版 (Professional)": {
            "base_price": 180.0,
            "description": "適合中型企業與貿易商，支援完整供應鏈、財會核心與多據點管理",
            "included_modules": [
                "高階主管簽核流與授權矩陣", "智能進銷存與批號效期全生命周期管理", 
                "總帳會計、多幣別傳票與會計師國際報表", "多國人事薪酬、外派人員勞健保與考勤排班"
            ]
        },
        "📦 標準訂閱版 (Subscription)": {
            "base_price": 90.0,
            "description": "適合小型企業或單一據點，靈活按需勾選樂高模組",
            "included_modules": [
                "智能進銷存與批號效期全生命周期管理", "多國人事薪酬、外派人員勞健保與考勤排班"
            ]
        }
    }

if "global_fx_rates" not in st.session_state:
    st.session_state.global_fx_rates = {"USD": 1.0, "TWD": 31.50, "VND": 25400.00, "RMB": 7.20}

if "tenants_db" not in st.session_state:
    st.session_state.tenants_db = {
        "tenant_vina_group": {
            "name": "🇻🇳 越南平陽跨國控股集團",
            "region": "越南 (Binh Duong, VN)",
            "plan": "🚀 跨國旗艦集團版 (Enterprise)",
            "price_usd": 350,
            "expiry_date": "2027-10-20",
            "dept_modules_db": {
                "⚙️ 工程與技術服務部 (Engineering & Technical)": ["智能進銷存與批號效期全生命周期管理"]
            },
            "org_nodes": [
                {"id": "node_root", "name": "集團董事長室", "type": "👑 頂層 (Board)", "parent": "無 (頂層)"},
                {"id": "node_eng", "name": "越南平陽廠區", "type": "🏭 製造廠區", "parent": "集團董事長室"}
            ]
        }
    }

if "current_portal" not in st.session_state:
    st.session_state.current_portal = "Master"

ALL_ENTERPRISE_DEPARTMENTS = [
    "👑 董事長室 / 總經理室 (Executive & Board Room)",
    "📈 經營企劃與策略發展部 (Corporate Strategy)",
    "👥 人力資源與行政管理部 (HR & Admin Dept)",
    "⚖️ 法務與合規遵循部 (Legal & Compliance)",
    "🔒 資訊安全與稽核中心 (Audit & Info Security)",
    "💰 財務與資本運作部 (Finance Dept)",
    "📊 會計與稅務管理部 (Accounting & Tax)",
    "🌍 國內業務與通路發展部 (Domestic Sales)",
    "🌐 國際貿易與海外業務部 (Global Export Sales)",
    "📢 市場行銷與品牌企劃部 (Marketing Dept)",
    "🤝 客戶成功與售後服務部 (Customer Success / CS)",
    "🛒 供應鏈與全球採購部 (Supply Chain & Procurement)",
    "📦 倉儲物流與庫存管理部 (Warehouse & Logistics)",
    "🏭 生產製造與廠務管理部 (Manufacturing & Plant)",
    "⚙️ 工程與技術服務部 (Engineering & Technical)",
    "📊 生產管制與物料控制部 (PMC / Production Control)",
    "🛡️ 品質保證與品管中心 (QA / QC Dept)",
    "💡 研發設計與創新中心 (R&D / Design Center)",
    "💻 資訊技術與系統開發部 (IT & Software Development)"
]

# ==================== 側邊欄導覽 (含全域多語言動態切換) ====================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/company.png", width=64)
    st.markdown("### 🌐 跨國 AI-ERP 平台總控台")
    
    # 全域內建的語系切換核心引擎
    selected_lang = st.selectbox(
        "🌍 系統全域語系 / Global Language (i18n)",
        ["繁體中文 (Traditional Chinese)", "Tiếng Việt (越南語)", "English (英文)"]
    )
    
    # 根據語系動態對應介面提示文字
    if "越南" in selected_lang:
        i18n_portal = "👑 Trở về Tổng đài SaaS"
        i18n_current = "🏢 Đang quản lý Tenant"
        i18n_menu = "📌 Menu Điều hướng Hệ thống"
    elif "English" in selected_lang:
        i18n_portal = "👑 Return to SaaS Master Hub"
        i18n_current = "🏢 Current Tenant"
        i18n_menu = "📌 System Navigation Menu"
    else:
        i18n_portal = "👑 返回 SaaS 平台總控台"
        i18n_current = "🏢 目前管理租戶"
        i18n_menu = "📌 系統導覽選單"
    
    st.markdown("---")
    
    if st.session_state.current_portal != "Master":
        if st.button(i18n_portal, type="primary", use_container_width=True):
            st.session_state.current_portal = "Master"
            st.rerun()
        st.markdown(f"{i18n_current}: `{st.session_state.tenants_db[st.session_state.current_portal]['name']}`")
    else:
        st.markdown("👑 **目前身分**: `AI ERP 首席架構師 / Master`")
    
    st.markdown("---")
    st.markdown(f"### {i18n_menu}")
    
    if st.session_state.current_portal == "Master":
        menu_choice = st.radio(
            "選擇總控台模組",
            ["🏢 全球企業租戶總覽", "⚙️ 全球定價策略與方案模組自訂 (Pricing App Store)"]
        )
    else:
        current_t_name = st.session_state.tenants_db[st.session_state.current_portal]["name"]
        menu_choice = st.radio(
            f"內部模組 ({current_t_name})",
            ["🧩 樂高積木式模組市集 (App Store)", "🖱️ ProcessOn 組織架構圖與節點管理"]
        )

# ==================== 路由分發邏輯 ====================
if st.session_state.current_portal == "Master":
    if "全球企業租戶總覽" in menu_choice:
        st.markdown("## 🏢 SaaS 平台總控台：全球跨國企業租戶動態總覽")
        tenant_list = [{"代碼": k, "公司名稱": v["name"], "方案": v["plan"], "月費(USD)": v["price_usd"]} for k, v in st.session_state.tenants_db.items()]
        st.dataframe(pd.DataFrame(tenant_list), use_container_width=True)
        if st.button("📂 進入越南平陽控股集團後台"):
            st.session_state.current_portal = "tenant_vina_group"
            st.rerun()
    else:
        render_pricing_hub()
else:
    current_tenant = st.session_state.tenants_db[st.session_state.current_portal]
    if "樂高積木式模組市集" in menu_choice:
        render_app_store(current_tenant, ALL_ENTERPRISE_DEPARTMENTS)
    else:
        render_org_chart(current_tenant)
