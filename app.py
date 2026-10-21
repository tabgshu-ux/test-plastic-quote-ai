import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# 引入自訂模組
from modules.pricing_hub import render_pricing_hub
from modules.app_store import render_app_store
from modules.org_chart import render_org_chart
from modules.rbac import render_rbac

st.set_page_config(
    page_title="SaaS Enterprise Modular AI-ERP",
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
# 🌟 全產業通用企業級 AI-ERP 模組庫 (已擴充「智慧零售與 POS 生態系」)
# ==============================================================================
if "master_module_library" not in st.session_state:
    st.session_state.master_module_library = {
        "☕ 智慧零售、POS 收銀與會員行銷生態系 (Smart Retail & POS)": [
            "POS 收銀機與多幣別實體門市結算", "行動支付、電子發票與跨境金流串接", "VIP 會員咖啡廳免費額度與次數控管", 
            "人臉辨識會員快速識別與自動招呼", "推薦分潤機制與最佳推廣大使評選系統", "環保材質（咖啡絲鞋）履歷與碳足跡展示", 
            "電動車獎勵與行銷競賽積分自動化引擎", "門市現場預約與客製化鞋款顏色挑選"
        ],
        "📈 高階決策、營運戰情與多維度 BI": [
            "全局原物料與市場即時行情看板", "匯率多幣別自動換算與避險中心", "全球主要股市與財經大盤監控", 
            "多公司合併財務報表分析", "企業 KPI 戰情室與 AI 智慧營運健檢", "高階主管簽核流與授權矩陣", 
            "跨部門營運總控台與異常預警", "各國稅務合規與利潤匯出分析", "ESG 永續碳排與能源消耗戰情室"
        ],
        "📦 供應鏈、智慧進銷存與倉儲 (SCM & WMS)": [
            "智能進銷存與批號效期全生命周期管理", "供應商評鑑、自動比價與採購發包(PR/PO)", "智慧倉儲物流與 PDA 條碼掃描(WMS)", 
            "進出口報關、物流追蹤與原產地證明", "條碼/QR Code 全自動資產與物料標籤列印", "安全庫存水位 AI 自動補貨警報", 
            "多倉庫智能調撥、批次與序號追蹤", "供應商交期達標率與品質異常扣款追蹤", "保稅倉庫與免稅品項管理"
        ],
        "💰 財務會計、電子發票與人事法規 (Finance & HR)": [
            "總帳會計、多幣別傳票與會計師報表", "應收(AR)智慧催收與應付(AP)現金流排程", "電子發票與各國稅務勾稽", 
            "人事薪酬、勞健保與考勤排班", "GPS 定位行動打卡、外勤軌跡與排班管理", "AI 智慧履歷篩選、面試與人才庫管理", 
            "電子簽核流程引擎 (BPM) 與委任授權", "固定資產盤點、折舊自動提列與租賃會計", "在地化勞資合規與薪資法規資料庫"
        ],
        "🏭 智慧製造、專案管控與業務維運 (Manufacturing & Projects)": [
            "MES 製造執行系統與車間動態報工", "多階 BOM 表管理、製程工藝與標準SOP", "產線動態排程、瓶頸預警與產能平衡調度", 
            "大型專案管理、里程碑與成本預算管控", "客戶關係管理(CRM)、業務商機與銷售漏斗", "售後服務工單、設備維修履歷與定期保養排程", 
            "外包商工班計價、合約追蹤與驗收請款", "CAD/BIM 工程圖檔雲端協同與版本控制", "IoT 機台稼動率監控與 OEE 設備效率分析"
        ],
        "🤖 AI 語音多模態與智慧硬體整合 (AI & Hardware Integration)": [
            "車牌辨識(ANPR)智慧車道與物流車隊管理", "廠區人臉辨識門禁、訪客預約與考勤對接", "AI 智慧語音助理與多國文件即時翻譯", 
            "AI 智慧工安影像辨識與違規即時預警", "車輛保養、車隊 GPS 定位與外派油耗追蹤", "AI 智慧客服機器人與自動化客戶詢價回覆"
        ]
    }

if "global_plans_db" not in st.session_state:
    st.session_state.global_plans_db = {
        "🚀 旗艦集團版 (Enterprise)": {
            "base_price": 350.0,
            "description": "適合大型集團與製造業，解鎖全產業模組與無限部門掛載",
            "included_modules": [
                "POS 收銀機與多幣別實體門市結算", "全局原物料與市場即時行情看板", "高階主管簽核流與授權矩陣", 
                "智能進銷存與批號效期全生命周期管理", "總帳會計、多幣別傳票與會計師報表"
            ]
        },
        "💼 正式商業版 (Professional)": {
            "base_price": 180.0,
            "description": "適合中型企業與貿易商，支援完整供應鏈、財會核心與多據點管理",
            "included_modules": [
                "POS 收銀機與多幣別實體門市結算", "高階主管簽核流與授權矩陣", 
                "智能進銷存與批號效期全生命周期管理", "總帳會計、多幣別傳票與會計師報表"
            ]
        },
        "📦 標準訂閱版 (Subscription)": {
            "base_price": 90.0,
            "description": "適合小型企業或單一據點，靈活按需勾選樂高模組",
            "included_modules": [
                "POS 收銀機與多幣別實體門市結算", "智能進銷存與批號效期全生命周期管理"
            ]
        }
    }

if "global_fx_rates" not in st.session_state:
    st.session_state.global_fx_rates = {"USD": 1.0, "TWD": 31.50, "VND": 25400.00, "RMB": 7.20}

if "tenants_db" not in st.session_state:
    st.session_state.tenants_db = {
        "tenant_vina_group": {
            "name": "🇻🇳 越南平陽控股集團",
            "region": "越南 (Binh Duong, VN)",
            "plan": "🚀 旗艦集團版 (Enterprise)",
            "price_usd": 350,
            "expiry_date": "2027-10-20",
            "dept_modules_db": {
                "⚙️ 工程與技術服務部 (Engineering & Technical)": ["智能進銷存與批號效期全生命周期管理"]
            },
            "org_nodes": [
                {"id": "node_root", "name": "集團董事長室", "type": "👑 頂層 (Board)", "parent": "無 (頂層)"},
                {"id": "node_eng", "name": "越南平陽廠區", "type": "🏭 製造廠區", "parent": "集團董事長室"}
            ],
            "staff": [
                {"name": "Trần Văn Minh", "email": "minh.tv@vina.com", "role": "Tenant Admin (租戶管理員/老闆)", "dept": "董事長室", "lang": "Tiếng Việt"},
                {"name": "Nguyễn Thị Hạnh", "email": "hanh.nt@vina.com", "role": "Department Manager (部門主管)", "dept": "財務部", "lang": "Tiếng Việt"},
                {"name": "Le Van Hung", "email": "hung.lv@vina.com", "role": "Field Worker (現場作業人員)", "dept": "工程技術部", "lang": "Tiếng Việt"}
            ]
        }
    }

# ==================== 動態帳號資料庫 ====================
if "master_staff_db" not in st.session_state:
    st.session_state.master_staff_db = [
        {"name": "許福村", "account": "admin", "password": "admin123", "role": "👑 平台老闆 (Master Admin)", "status": "啟用中"},
        {"name": "財務部專員", "account": "finance", "password": "finance123", "role": "💰 總控台財務專員 (Master Finance)", "status": "啟用中"}
    ]

if "current_portal" not in st.session_state:
    st.session_state.current_portal = "Master"

if "master_logged_in" not in st.session_state:
    st.session_state.master_logged_in = False

if "master_role" not in st.session_state:
    st.session_state.master_role = None

if "master_current_user" not in st.session_state:
    st.session_state.master_current_user = None

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
    st.markdown("### 🌐 企業級 AI-ERP 平台總控")
    
    selected_lang = st.selectbox(
        "🌍 系統全域語系 / Language (i18n)",
        ["繁體中文 (Traditional Chinese)", "Tiếng Việt (越南語)", "English (英文)"]
    )
    
    if "越南" in selected_lang:
        i18n_portal = "👑 Trở về Tổng đài SaaS"
        i18n_current = "🏢 Đang quản lý Tenant"
        i18n_menu = "📌 Menu Điều hướng"
    elif "English" in selected_lang:
        i18n_portal = "👑 Return to SaaS Master Hub"
        i18n_current = "🏢 Current Tenant"
        i18n_menu = "📌 System Navigation"
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
        if st.session_state.master_logged_in:
            role_title = "👑 平台最高管理者" if st.session_state.master_role == "admin" else "💰 總控台財務專員"
            st.markdown(f"**目前身分**: `{st.session_state.master_current_user} ({role_title})`")
            if st.button("🔒 登出總控台 (Lock Master)", use_container_width=True):
                st.session_state.master_logged_in = False
                st.session_state.master_role = None
                st.session_state.master_current_user = None
                st.rerun()
        else:
            st.markdown("👑 **目前身分**: `未登入`")
    
    st.markdown("---")
    st.markdown(f"### {i18n_menu}")
    
    if st.session_state.current_portal == "Master":
        if st.session_state.master_logged_in:
            if st.session_state.master_role == "admin":
                menu_choice = st.radio(
                    "選擇總控台模組",
                    [
                        "🏢 全球企業租戶總覽", 
                        "⚙️ 全球定價策略與方案模組自訂", 
                        "👥 總控台帳號與權限管理"
                    ]
                )
            else:
                menu_choice = "💰 平台財務營收與租戶帳單清單"
        else:
            menu_choice = "🔒 請先登入"
    else:
        current_t_name = st.session_state.tenants_db[st.session_state.current_portal]["name"]
        menu_choice = st.radio(
            f"內部模組 ({current_t_name})",
            [
                "🧩 樂高積木式模組市集 (App Store)", 
                "🖱️ 組織架構圖與節點管理",
                "👥 員工帳號與權限管理 (RBAC)"
            ]
        )

# ==================== 路由分發與動態帳號驗證邏輯 ====================
if st.session_state.current_portal == "Master":
    if not st.session_state.master_logged_in:
        st.markdown("## 🔐 總控台安全登入")
        
        with st.form("master_login_form"):
            input_account = st.text_input("登入帳號 (Account)", placeholder="請輸入帳號...")
            input_pass = st.text_input("密碼 (Password)", type="password", placeholder="請輸入密碼...")
            
            if st.form_submit_button("🔓 登入總控台", type="primary", use_container_width=True):
                matched_user = None
                for u in st.session_state.master_staff_db:
                    if u["account"] == input_account and u["password"] == input_pass:
                        matched_user = u
                        break
                
                if matched_user:
                    if matched_user["status"] == "已停權 (Disabled)":
                        st.error("❌ 此帳號已被停權，無法登入系統！")
                    else:
                        st.session_state.master_logged_in = True
                        st.session_state.master_current_user = matched_user["name"]
                        if "Master Admin" in matched_user["role"]:
                            st.session_state.master_role = "admin"
                        else:
                            st.session_state.master_role = "finance"
                        st.success(f"🎉 歡迎回來，{matched_user['name']}！")
                        st.rerun()
                else:
                    st.error("❌ 帳號或密碼錯誤！")
    else:
        if st.session_state.master_role == "admin":
            if "全球企業租戶總覽" in menu_choice:
                st.markdown("## 🏢 SaaS 平台總控台：企業租戶動態總覽與快速切換")
                
                for t_id, t_data in st.session_state.tenants_db.items():
                    with st.container():
                        st.markdown('<div class="card-container">', unsafe_allow_html=True)
                        col_info, col_btn = st.columns([3, 1])
                        with col_info:
                            st.markdown(f"### 🏢 {t_data['name']}")
                            st.markdown(f"- **租戶代碼**: `{t_id}` | **地區**: `{t_data['region']}`")
                            st.markdown(f"- **目前訂閱方案**: `{t_data['plan']}` | **每月月費**: `$ {t_data['price_usd']} USD`")
                        with col_btn:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button(f"🚀 進入該租戶後台", key=f"enter_{t_id}", type="primary", use_container_width=True):
                                st.session_state.current_portal = t_id
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
            elif "全球定價策略" in menu_choice:
                render_pricing_hub()
            else:
                st.markdown("## 👥 總控台內部員工與權限管理 (IAM)")
                st.info("💡 *在此管理平台總控台內部的管理者與財務人員帳號。當人員離職時，可直接將狀態切換為【已停權】，系統將立即封鎖其登入權限。*")
                
                with st.container():
                    st.markdown('<div class="card-container">', unsafe_allow_html=True)
                    st.markdown("### ➕ 新增總控台內部帳號")
                    with st.form("add_master_staff"):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_name = st.text_input("姓名 (Name)", placeholder="例：王小明")
                            new_account = st.text_input("登入帳號 (Account)", placeholder="例：finance_02")
                        with col2:
                            new_role = st.selectbox("指派角色 (Role)", ["💰 總控台財務專員 (Master Finance)", "👑 平台最高管理者 (Master Admin)"])
                            new_pass_input = st.text_input("設定密碼 (Password)", type="password", placeholder="請設定初始密碼...")
                        
                        if st.form_submit_button("👤 建立總控台帳號", type="primary", use_container_width=True):
                            if new_name and new_account and new_pass_input:
                                st.session_state.master_staff_db.append({
                                    "name": new_name,
                                    "account": new_account,
                                    "password": new_pass_input,
                                    "role": new_role,
                                    "status": "啟用中"
                                })
                                st.success(f"🎉 成功為 [{new_name}] 建立總控台帳號！")
                                st.rerun()
                            else:
                                st.warning("⚠️ 請完整填寫姓名、帳號與密碼。")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("### 📋 現有總控台帳號與離職停權管理")
                with st.container():
                    st.markdown('<div class="card-container">', unsafe_allow_html=True)
                    for idx, staff in enumerate(st.session_state.master_staff_db):
                        cols = st.columns([2, 2, 2, 2, 1])
                        with cols[0]:
                            st.write(f"**{staff['name']}**")
                        with cols[1]:
                            st.write(f"帳號: `{staff['account']}`")
                        with cols[2]:
                            st.write(staff['role'])
                        with cols[3]:
                            new_status = st.selectbox(
                                "狀態", 
                                ["啟用中", "已停權 (Disabled)"], 
                                index=0 if staff['status'] == "啟用中" else 1,
                                key=f"status_select_{idx}"
                            )
                            if new_status != staff['status']:
                                st.session_state.master_staff_db[idx]['status'] = new_status
                                st.success(f"已更新 [{staff['name']}] 狀態為：{new_status}")
                                st.rerun()
                        with cols[4]:
                            if staff['account'] != "admin":
                                if st.button("🗑️ 刪除", key=f"del_staff_{idx}Y"):
                                    st.session_state.master_staff_db.pop(idx)
                                    st.rerun()
                        st.markdown("---")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("## 💰 總控台：平台財務營收與租戶帳單結算中心")
            total_mrr = sum([v["price_usd"] for v in st.session_state.tenants_db.values()])
            c1, c2 = st.columns(2)
            with c1:
                st.metric("📊 本月總訂閱營收 (MRR)", f"$ {total_mrr:,.2f} USD")
            with c2:
                st.metric("🏢 目前有效付費租戶數", f"{len(st.session_state.tenants_db)} 家")
            
            st.markdown("---")
            st.markdown("### 📋 各租戶訂閱明細與帳款清單 (Billing Ledger)")
            billing_list = []
            for t_id, v in st.session_state.tenants_db.items():
                billing_list.append({
                    "租戶代碼": t_id,
                    "公司名稱": v["name"],
                    "地區": v["region"],
                    "訂閱方案": v["plan"],
                    "每月月費 (USD)": f"$ {v['price_usd']}",
                    "合約到期日": v["expiry_date"],
                    "繳費狀態": "✅ 已付費 (Active)"
                })
            with st.container():
                st.markdown('<div class="card-container">', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(billing_list), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
else:
    current_tenant = st.session_state.tenants_db[st.session_state.current_portal]
    if "樂高積木式模組市集" in menu_choice:
        render_app_store(current_tenant, ALL_ENTERPRISE_DEPARTMENTS)
    elif "組織架構圖" in menu_choice:
        render_org_chart(current_tenant)
    else:
        render_rbac(current_tenant)
