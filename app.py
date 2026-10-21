import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# 引入自訂模組
from modules.pricing_hub import render_pricing_hub
from modules.app_store import render_app_store
from modules.org_chart import render_org_chart

st.set_page_config(
    page_title="SaaS Enterprise Modular AI-ERP Ultimate Master",
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
# 🌟 【全能商業級模組大合集庫】包羅萬象的企業與工程 ERP 功能清單 (Master Library)
# ==============================================================================
if "master_module_library" not in st.session_state:
    st.session_state.master_module_library = {
        "📈 高階決策與戰情室 (Executive & BI)": [
            "全局原物料即時行情看板", "國際匯率多幣別換算中心", "全球股市財經大盤監控", 
            "綜合損益表與資產負債表", "企業 KPI 與多維度 BI 戰情室", "高階決策審核簽核流", 
            "跨部門營運總控台", "多公司合併財務報表分析", "AI 商業智能預測與營運健檢"
        ],
        "📦 供應鏈與進銷存 (SCM & WMS)": [
            "智能進銷存與批號效期管理", "全球供應鏈採購比價系統", "倉儲物流與條碼掃描(WMS)", 
            "供應商交期與品質評鑑系統", "進出口報關與海運物流追蹤", "條碼/QR Code資產標籤列印", 
            "PDA 行動叫料與驗收系統", "安全庫存自動補貨警報", "多倉庫調撥與批次管理"
        ],
        "💰 財會、稅務與人事 (Finance & HR)": [
            "總帳會計、傳票與會計師報表", "應收/應付帳款(AR/AP)管理", "越南紅發票與電子發票勾稽", 
            "人事薪酬、勞健保與考勤排班", "GPS 定位行動打卡與排班管理", "AI 履歷篩選與面試排程助手", 
            "電子簽核流程引擎 (BPM)", "固定資產與折舊自動提列", "各國稅務申報試算與合規管理"
        ],
        "⚙️ 水電工程與專案特化 (Engineering & Project)": [
            "水電工程專案與工項預算編號", "工程估驗與計價請款追蹤", "工地現場點工點料管理", 
            "施工日報表與工時扣減聯動", "外包商工班計價與合約管理", "設備維修履歷與保養排程", 
            "工地物聯網(IoT)設備監控", "CAD/BIM 圖檔雲端協同檢視", "工程超支自動預警與鎖定"
        ],
        "🤖 AI 智慧硬體與其他特化 (AI & Hardware Integration)": [
            "車牌辨識 (ANPR) 智慧車道進出", "廠區人臉辨識門禁與考勤對接", "AI 智慧語音助理與跨國翻譯", 
            "AI 智慧工安影像辨識與違規預警", "車輛保養與車隊 GPS 定位追蹤", "汽車美容 / 車體包膜預約管理", 
            "多語言動態介面切換 (越/英/中/日)"
        ]
    }

if "global_plans_db" not in st.session_state:
    st.session_state.global_plans_db = {
        "🚀 旗艦版 (Enterprise)": {
            "base_price": 250.0,
            "description": "適合大型集團與跨國水電工程企業，解鎖全功能與無限部門掛載",
            "included_modules": [
                "全局原物料即時行情看板", "高階決策審核簽核流", "智能進銷存與批號效期管理", 
                "總帳會計、傳票與會計師報表", "水電工程專案與工項預算編號", "工程估驗與計價請款追蹤"
            ]
        },
        "💼 正式商業版 (Professional)": {
            "base_price": 150.0,
            "description": "適合中型企業與成長中公司，支援完整進銷存與財會核心",
            "included_modules": [
                "高階決策審核簽核流", "智能進銷存與批號效期管理", "總帳會計、傳票與會計師報表", "人事薪酬、勞健保與考勤排班"
            ]
        },
        "📦 標準訂閱版 (Subscription)": {
            "base_price": 80.0,
            "description": "適合小型店家或單一據點，靈活按需勾選樂高模組",
            "included_modules": [
                "智能進銷存與批號效期管理", "人事薪酬、勞健保與考勤排班"
            ]
        }
    }

if "global_fx_rates" not in st.session_state:
    st.session_state.global_fx_rates = {"USD": 1.0, "TWD": 31.50, "VND": 25400.00, "RMB": 7.20}

if "tenants_db" not in st.session_state:
    st.session_state.tenants_db = {
        "tenant_vina_水电": {
            "name": "🇻🇳 越南平陽水電工程有限公司",
            "region": "越南 (Binh Duong, VN)",
            "plan": "🚀 旗艦版 (Enterprise)",
            "price_usd": 250,
            "expiry_date": "2027-10-20",
            "dept_modules_db": {
                "⚙️ 工程與技術服務部 (Engineering & Technical)": ["水電工程專案與工項預算編號", "工程估驗與計價請款追蹤"]
            },
            "org_nodes": [
                {"id": "node_root", "name": "董事長室", "type": "👑 頂層 (Board)", "parent": "無 (頂層)"},
                {"id": "node_eng", "name": "工程技術部", "type": "⚙️ 二級部門", "parent": "董事長室"}
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

# ==================== 側邊欄導覽 ====================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/company.png", width=64)
    st.markdown("### 🌐 SaaS 多租戶 AI-ERP 平台")
    
    if st.session_state.current_portal != "Master":
        if st.button("👑 返回 SaaS 平台總控台", type="primary", use_container_width=True):
            st.session_state.current_portal = "Master"
            st.rerun()
        st.markdown(f"🏢 **目前管理租戶**: `{st.session_state.tenants_db[st.session_state.current_portal]['name']}`")
    else:
        st.markdown("👑 **目前身分**: `SaaS 平台總管理員 (Master)`")
    
    st.markdown("---")
    st.markdown("### 📌 系統導覽選單")
    
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
        st.markdown("## 🏢 SaaS 平台總控台：全球企業租戶動態總覽")
        tenant_list = [{"代碼": k, "公司名稱": v["name"], "方案": v["plan"], "月費(USD)": v["price_usd"]} for k, v in st.session_state.tenants_db.items()]
        st.dataframe(pd.DataFrame(tenant_list), use_container_width=True)
        if st.button("📂 進入越南平陽水電後台"):
            st.session_state.current_portal = "tenant_vina_水电"
            st.rerun()
    else:
        render_pricing_hub()
else:
    current_tenant = st.session_state.tenants_db[st.session_state.current_portal]
    if "樂高積木式模組市集" in menu_choice:
        render_app_store(current_tenant, ALL_ENTERPRISE_DEPARTMENTS)
    else:
        render_org_chart(current_tenant)
