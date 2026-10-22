import streamlit as st
import pandas as pd
import datetime

# 引入各大部門模組
from modules.executive_bi import render_executive_bi
from modules.pos_retail import render_pos_retail
from modules.mes_factory import render_mes_factory
from modules.app_store import render_app_store
from modules.org_chart import render_org_chart
from modules.rbac import render_rbac
from modules.departments_manager import render_departments_manager
from modules import executive_office
from modules import system_licensing

st.set_page_config(
    page_title="全球多租戶 SaaS AI ERP 平台 - 部門專屬拼圖市集總控中心",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card-container { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); margin-bottom: 20px; }
    h1, h2, h3 { color: #1e293b; }
    .stButton>button { border-radius: 6px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ==================== Session State 初始化 ====================
if "master_logged_in" not in st.session_state:
    st.session_state.master_logged_in = False
if "selected_tenant" not in st.session_state:
    st.session_state.selected_tenant = None

# 1. 全球跨國企業完整部門清單
if "global_departments_list" not in st.session_state:
    st.session_state.global_departments_list = [
        "董事長室 / 總經理室 (Executive & Board Room)",
        "經營企劃與策略發展部 (Corporate Strategy)",
        "人力資源與行政管理部 (HR & Admin Dept)",
        "法務與合規遵循部 (Legal & Compliance)",
        "資訊安全與稽核中心 (Audit & Info Security)",
        "財務與資本運作部 (Finance Dept)",
        "會計與稅務管理部 (Accounting & Tax)",
        "國內業務與通路發展部 (Domestic Sales)",
        "國際貿易與海外業務部 (Global Export Sales)",
        "市場行銷與品牌企劃部 (Marketing Dept)",
        "客戶成功與售後服務部 (Customer Success / CS)",
        "供應鏈與全球採購部 (Supply Chain & Procurement)",
        "倉儲物流與庫存管理部 (Warehouse & Logistics)",
        "生產製造與商務管理部 (Manufacturing & Plant)",
        "工程與技術服務部 (Engineering & Technical)",
        "生產管制與物料控制部 (PMC / Production Control)",
        "品質保證與品管中心 (QA / QC Dept)",
        "研發設計與創新中心 (R&D / Design Center)",
        "資訊技術與系統開發部 (IT & Software Development)"
    ]

# 2. 為每個部門量身打造的相對應專屬功能拼圖清單
if "department_specific_puzzles_db" not in st.session_state:
    st.session_state.department_specific_puzzles_db = {
        "董事長室 / 總經理室 (Executive & Board Room)": [
            "👑 全球多維度 BI 經營戰情室", "👑 集團即時合併報表與現金流水位", "👑 跨國重大決策電子簽核", "👑 全球原物料與總經理室即時看板"
        ],
        "經營企劃與策略發展部 (Corporate Strategy)": [
            "📈 長期策略目標 KPI 追蹤儀表板", "📈 市場競爭分析與競品情報庫", "📈 投資併購專案評估模型", "📈 企業年度預算編列與執行追蹤"
        ],
        "人力資源與行政管理部 (HR & Admin Dept)": [
            "👥 全球人事組織與員工生命週期管理", "👥 跨國薪資計算引擎 (含越南勞動法加班費/夜班加給)", 
            "👥 多班別排班考勤與請假打卡系統", "👥 招募管理、面試評核與績效考核 (KPI/OKRs)", "👥 勞健保、社會保險與福委會管理"
        ],
        "法務與合規遵循部 (Legal & Compliance)": [
            "⚖️ 跨國合約生命週期管理與電子簽署", "⚖️ 企業法規遵循風險評估與稽核", "⚖️ 智財權與專利證照管家", "⚖️ 訴訟案件追蹤與法律文件庫"
        ],
        "資訊安全與稽核中心 (Audit & Info Security)": [
            "🛡️ 內部控制與 ISO 內稽內控檢核", "🛡️ 資訊安全事件通報與資安軌跡日誌", "🛡️ 權限存取控制稽核 (RBAC Log)", "🛡️ 廠區門禁與個資保護合規檢查"
        ],
        "財務與資本運作部 (Finance Dept)": [
            "💰 應收帳款 (AR) 與應付帳款 (AP) 即時水位", "💰 多幣別資金調度與銀行信用狀 (L/C) 管理", 
            "💰 資本支出 (CapEx) 審核與 ROI 評估", "💰 國際匯率風險避險與即時換算中心"
        ],
        "會計與稅務管理部 (Accounting & Tax)": [
            "📊 總帳會計系統、傳票登錄與試算表", "📊 越南會計準則 (Thông tư 200) 專用帳套", 
            "📊 電子發票 (Electronic Invoice) 開立與申報", "📊 各國動態稅制引擎與營業稅計算"
        ],
        "國內業務與通路發展部 (Domestic Sales)": [
            "💼 國內客戶關係管理 (CRM) 與商機追蹤", "💼 國內多層級經銷商與通路授信管理", "💼 國內銷貨合約、雙層報價與出貨單開立", "💼 業務績效獎金與佣金自動計算"
        ],
        "國際貿易與海外業務部 (Global Export Sales)": [
            "🌐 海外客戶外貿商機與詢報價管理", "🌐 國際多幣別貿易契約與信用狀 (L/C)", 
            "🌐 國外海運、空運物流與出貨排程追蹤", "🌐 國貿出口報關文件與海關申報連線"
        ],
        "市場行銷與品牌企劃部 (Marketing Dept)": [
            "🎯 數位行銷活動 ROI 追蹤與潛客開發", "🎯 品牌數位資產 (DAM) 與行銷素材管理", "🎯 參展專案管理與展覽經費核銷", "🎯 客戶滿意度與市場問卷調查系統"
        ],
        "客戶成功與售後服務部 (Customer Success / CS)": [
            "🎧 客戶服務工單 (Service Ticket) 派工系統", "🎧 售後維修保固履歷與客訴追蹤", "🎧 客戶健康度評分與續約提醒機制", "🎧 智能客服機器人與語音紀錄歸檔"
        ],
        "供應鏈與全球採購部 (Supply Chain & Procurement)": [
            "📦 全球供應商詢比議價與合格供應商 (AVL) 評鑑", "📦 採購訂單 (PO) 發包與交期追蹤系統", 
            "📦 原物料價格波動與大宗物料行情看板", "📦 供應鏈交期準確率與品質績效評分"
        ],
        "倉儲物流與庫存管理部 (Warehouse & Logistics)": [
            "📦 智能多倉庫進銷存與安全庫存水位警示", "📦 PDA 條碼掃描入庫、出庫與盤點作業 (WMS)", 
            "📦 批號效期管理 (FIFO/LIFO) 與安全溯源", "📦 棧板管理、貨位優化與海關保稅倉庫管理"
        ],
        "生產製造與商務管理部 (Manufacturing & Plant)": [
            "🏭 MES 電機製造執行系統與車間工單排程", "🏭 現場機台設備稼動率與 OEE 即時監控", 
            "🏭 工地師傅與現場作業員手機快速回報", "🏭 模具/治具壽命管理與預防性保養維護"
        ],
        "工程與技術服務部 (Engineering & Technical)": [
            "⚡ 工程雙層報價與技術規格審查", "⚡ BOM (物料清單) 零件自動展開與版次管理", 
            "⚡ 配電盤/變壓器設計圖紙與工程驗收管理", "⚡ 現場技術支援工時與工程變更 (ECN) 追蹤"
        ],
        "生產管制與物料控制部 (PMC / Production Control)": [
            "📅 主生產排程 (MPS) 與物料需求規劃 (MRP)", "📅 產能負荷分析與瓶頸工序即時調度", 
            "📅 缺料預警機制與急單插入模擬試算", "📅 生產進度甘特圖與交期即時預測"
        ],
        "品質保證與品管中心 (QA / QC Dept)": [
            "🔍 IQC 進料檢驗與 AQL 抽樣標準管理", "🔍 PQC 製程品保巡檢與不良率統計分析", 
            "🔍 OQC 出貨檢驗與品質合格證書列印", "🔍 ISO 品質合規與 CAPA 矯正預防措施追蹤"
        ],
        "研發設計與創新中心 (R&D / Design Center)": [
            "💡 新產品研發專案管理與階段閘門審查", "💡 研發實驗數據記錄與原型機測試追蹤", 
            "💡 智慧財產權與研發圖庫管理", "💡 產品碳足跡與綠色設計 (Eco-Design) 評估"
        ],
        "資訊技術與系統開發部 (IT & Software Development)": [
            "💻 SaaS 租戶自主拼圖模組開關與授權管控", "💻 組織權限與角色管理 (RBAC) 核心", 
            "💻 外部第三方 API 串聯、Webhook 與資料庫同步", "💻 系統效能監控、容器化部署與資安日誌管理"
        ]
    }

# 初始化部門與勾選模組的對應資料庫
if "dept_puzzle_mapping" not in st.session_state:
    st.session_state.dept_puzzle_mapping = {
        dept: st.session_state.department_specific_puzzles_db.get(dept, [])[:3]
        for dept in st.session_state.global_departments_list
    }

# 3. 三大商業授權方案與定價設定
if "subscription_plans_db" not in st.session_state:
    st.session_state.subscription_plans_db = {
        "🚀 企業旗艦版 (Enterprise Flagship)": {
            "type": "年度旗艦買斷/授權", "price_usd": 3500.0, "billing_cycle": "每年計費", "max_seats": "無限席位 (Unlimited)", "desc": "適合大型集團，解鎖全公司所有 1~4 級部門與模組市集權限。"
        },
        "💼 正式商業版 (Standard Official)": {
            "type": "正式商業授權", "price_usd": 1500.0, "billing_cycle": "每年計費", "max_seats": "30 席位", "desc": "適合中型製造業，支援核心生產、供應鏈與財會模組。"
        },
        "⏱️ 彈性訂閱版 (Flexible Subscription)": {
            "type": "SaaS 月租訂閱制", "price_usd": 150.0, "billing_cycle": "每月計費 (Monthly)", "max_seats": "10 席位", "desc": "適合新創或彈性專案，按月隨選訂閱指定部門拼圖。"
        }
    }

# 4. 租戶授權資料庫
if "tenant_licensing_db" not in st.session_state:
    st.session_state.tenant_licensing_db = [
        {
            "tenant_id": "TENANT-001",
            "company_name": "裕豐電機工業 (Reetech Industrial)",
            "tax_id": "0312345678",
            "plan": "🚀 企業旗艦版 (Enterprise Flagship)",
            "pricing_usd": 3500.0,
            "expiry_date": "2027-12-31",
            "status": "🟢 正常運行 (Active)",
            "hierarchical_org_tree": [],
            "org_nodes": [{"id": "node_root", "name": "裕豐電機工業", "type": "👑 頂層 (Board / 董事會)", "parent": "無 (頂層)"}],
            "dept_modules_db": {}
        }
    ]

# ==================== 側邊欄導覽 ====================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/factory.png", width=64)
    st.markdown("### ⚡ SaaS ERP 總控台")
    st.markdown("---")
    
    if st.session_state.master_logged_in:
        st.success("🟢 總控管理員已登入")
        if st.session_state.selected_tenant:
            st.markdown(f"**當前租戶**：`{st.session_state.selected_tenant}`")
            if st.button("🔄 返回總控台首頁", use_container_width=True):
                st.session_state.selected_tenant = None
                st.rerun()
        
        if st.button("🚪 登出系統", use_container_width=True):
            st.session_state.master_logged_in = False
            st.session_state.selected_tenant = None
            st.rerun()
    else:
        st.info("狀態：等待登入驗證")

# ==================== 主路由邏輯 ====================

# 層級一：總控登入
if not st.session_state.master_logged_in:
    st.markdown("## 🔐 全球多租戶 SaaS AI ERP - 平台總控登入")
    st.markdown("請輸入總控管理員帳號密碼以進入 SaaS 核心管理中心。")
    st.markdown("---")
    
    with st.form("login_form"):
        acc = st.text_input("管理員帳號", value="admin")
        pwd = st.text_input("密碼", type="password", value="123")
        if st.form_submit_button("安全登入總控台", type="primary", use_container_width=True):
            if acc == "admin" and pwd == "123":
                st.session_state.master_logged_in = True
                st.success("登入成功！")
                st.rerun()
            else:
                st.error("帳號或密碼錯誤 (預設 admin / 123)")

# 層級二：總控管理中心
elif not st.session_state.selected_tenant:
    st.markdown("## 🏢 平台總控管理中心 - 部門專屬拼圖市集與方案定價總控")
    st.markdown("💡 *在此點選左側任意部門，右側將即時載入該部門「相對應的專屬功能模組」供您自由勾選配置。*")
    st.markdown("---")

    master_tab1, master_tab2, master_tab3, master_tab4 = st.tabs([
        "🧩 選擇部門並配置專屬拼圖市集",
        "💰 商業方案與訂閱制/正式版費用設定",
        "📋 企業租戶總覽與快速進入",
        "➕ 註冊新租戶與方案指派"
    ])

    # Tab 1: 雙欄互動介面 (左側部門選單 ➔ 右側加載該部門專屬功能)
    with master_tab1:
        col_dept_list, col_store_market = st.columns([1.2, 1.8])

        with col_dept_list:
            st.markdown("### 📂 選擇目標部門 / 管理層")
            st.caption("請點選要配置的部門：")
            selected_dept = st.radio(
                "部門清單", 
                st.session_state.global_departments_list, 
                label_visibility="collapsed"
            )

        with col_store_market:
            st.markdown(f"### 🧩 【 {selected_dept} 】專屬功能模組市集")
            st.caption("勾選此部門相對應的專屬業務模組與戰情儀表板：")
            st.markdown("---")

            current_dept_puzzles = st.session_state.dept_puzzle_mapping.get(selected_dept, [])
            updated_dept_puzzles = []

            # 抓取該部門專屬的模組清單
            specific_puzzles = st.session_state.department_specific_puzzles_db.get(selected_dept, [])

            st.markdown(f"#### 📌 {selected_dept} 核心業務模組")
            for item in specific_puzzles:
                is_checked = st.checkbox(
                    item, 
                    value=(item in current_dept_puzzles), 
                    key=f"chk_specific_{selected_dept}_{item}"
                )
                if is_checked:
                    updated_dept_puzzles.append(item)

            st.markdown("---")
            if st.button(f"💾 儲存【{selected_dept}】的專屬拼圖配置", type="primary", use_container_width=True):
                st.session_state.dept_puzzle_mapping[selected_dept] = updated_dept_puzzles
                st.success(f"🎉 成功儲存！【{selected_dept}】已成功更新其相對應的專屬功能模組。")
                st.rerun()

    # Tab 2: 商業方案與訂閱制/正式版費用設定
    with master_tab2:
        st.markdown("### 💰 商業授權方案、正式版與訂閱制費用設定")
        st.info("💡 在此設定全球 SaaS 平台的各級方案定價、計費週期（年費/月租訂閱）與席位限制。")

        plans_db = st.session_state.subscription_plans_db
        c1, c2, c3 = st.columns(3)
        cols = [c1, c2, c3]
        for idx, (p_name, p_info) in enumerate(plans_db.items()):
            with cols[idx]:
                st.markdown(f"#### {p_name}")
                st.write(f"• **方案屬性**：{p_info['type']}")
                st.write(f"• **定價金額**：`${p_info['price_usd']:,.2f} USD`")
                st.write(f"• **計費週期**：{p_info['billing_cycle']}")
                st.write(f"• **席位限制**：{p_info['max_seats']}")
                st.caption(p_info['desc'])

        st.markdown("---")
        st.markdown("#### ⚙️ 調整指定方案之定價與規範")
        with st.form("edit_subscription_plan_form"):
            target_plan = st.selectbox("選擇要編輯的授權方案", list(plans_db.keys()))
            current_info = plans_db[target_plan]
            
            new_price = st.number_input("設定方案價格 (USD)", value=float(current_info["price_usd"]), step=50.0)
            new_cycle = st.text_input("計費週期說明", value=current_info["billing_cycle"])
            new_seats = st.text_input("席位限制說明", value=current_info["max_seats"])
            new_desc = st.text_area("方案特色描述", value=current_info["desc"])

            if st.form_submit_button("💾 儲存方案定價與設定", type="primary", use_container_width=True):
                plans_db[target_plan]["price_usd"] = new_price
                plans_db[target_plan]["billing_cycle"] = new_cycle
                plans_db[target_plan]["max_seats"] = new_seats
                plans_db[target_plan]["desc"] = new_desc
                st.success(f"🎉 方案 [{target_plan}] 的財務定價與規範已成功更新！")
                st.rerun()

    # Tab 3: 企業租戶總覽與快速進入
    with master_tab3:
        st.markdown("### 📋 現有企業租戶清單與方案檢視")
        search = st.text_input("🔍 快速搜尋租戶 (公司名稱或代號)：", placeholder="例如：裕豐 或 TENANT-001")
        
        tenants = st.session_state.tenant_licensing_db
        filtered = [t for t in tenants if not search or search.lower() in t["company_name"].lower() or search.lower() in t["tenant_id"].lower()]
        
        if filtered:
            for t in filtered:
                with st.container():
                    col_i, col_b = st.columns([3, 1])
                    with col_i:
                        st.markdown(f"#### 🏢 {t['company_name']} (`{t['tenant_id']}`)")
                        st.write(f"• **採購方案**：{t['plan']} | **合約金額**：${t.get('pricing_usd', 0):,.2f} USD")
                        st.write(f"• **合約到期日**：{t['expiry_date']} | **運行狀態**：{t['status']}")
                    with col_b:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"🚀 進入租戶工作區", key=f"enter_{t['tenant_id']}", use_container_width=True):
                            st.session_state.selected_tenant = t["company_name"]
                            st.rerun()
                    st.markdown("---")
        else:
            st.warning("查無符合條件的租戶。")

    # Tab 4: 註冊新租戶與方案指派
    with master_tab4:
        st.markdown("### ➕ 註冊新企業租戶並綁定授權方案")
        with st.form("new_tenant_form"):
            c1, c2 = st.columns(2)
            with c1:
                t_name = st.text_input("客戶公司名稱 *", placeholder="例: 越南精密工業股份公司")
                t_tax = st.text_input("統一編號 / 稅號", placeholder="0312345678")
                t_plan = st.selectbox("選擇商業授權方案 (旗艦/正式/訂閱)", list(st.session_state.subscription_plans_db.keys()))
            with c2:
                default_pr = st.session_state.subscription_plans_db[t_plan]["price_usd"]
                t_price = st.number_input("客製合約定價金額 (USD)", value=float(default_pr))
                t_exp = st.date_input("合約到期日", value=datetime.date(2027, 12, 31))
            
            if st.form_submit_button("🚀 確認註冊並開通租戶環境", type="primary", use_container_width=True):
                if t_name:
                    new_id = f"TENANT-{len(st.session_state.tenant_licensing_db)+1:03d}"
                    st.session_state.tenant_licensing_db.append({
                        "tenant_id": new_id,
                        "company_name": t_name,
                        "tax_id": t_tax,
                        "plan": t_plan,
                        "pricing_usd": t_price,
                        "expiry_date": str(t_exp),
                        "status": "🟢 正常運行 (Active)",
                        "hierarchical_org_tree": [],
                        "org_nodes": [{"id": "node_root", "name": t_name, "type": "👑 頂層 (Board / 董事會)", "parent": "無 (頂層)"}],
                        "dept_modules_db": {}
                    })
                    st.success(f"🎉 成功建立新租戶：{t_name}！")
                    st.rerun()
                else:
                    st.warning("請填寫公司名稱！")

# 層級三：已進入特定租戶環境
else:
    current_tenant_obj = next((t for t in st.session_state.tenant_licensing_db if t["company_name"] == st.session_state.selected_tenant), None)
    
    if current_tenant_obj:
        st.sidebar.markdown("---")
        st.sidebar.markdown("##### 📂 租戶專屬功能選單：")
        
        tenant_menu_options = [
            "🌳 多級組織架構維護（部 ➔ 科 ➔ 組）",
            "🖱️ 組織架構圖與節點管理 (Org Chart)",
            "📈 總經理室戰情室 (Executive Office)",
            "💻 資訊管理與 API 授權設定 (System Licensing)"
        ]
        
        chosen_module = st.sidebar.radio("選擇租戶模組", tenant_menu_options, label_visibility="collapsed")
        
        st.markdown(f"### ⚡ 租戶工作區：`{current_tenant_obj['company_name']}`")
        st.markdown(f"**授權方案**：{current_tenant_obj['plan']} | **合約到期**：{current_tenant_obj['expiry_date']}")
        st.markdown("---")
        
        if "多級組織架構維護" in chosen_module:
            render_departments_manager(current_tenant_obj)
        elif "組織架構圖" in chosen_module:
            render_org_chart(current_tenant_obj)
        elif "總經理室戰情室" in chosen_module:
            executive_office.show(current_tenant_obj)
        elif "資訊管理" in chosen_module:
            it_tab1, it_tab2 = st.tabs(["🔒 組織權限與角色管理 (RBAC)", "🧩 本公司拼圖模組與 API 設定"])
            with it_tab1:
                render_rbac(current_tenant_obj)
            with it_tab2:
                system_licensing.show(current_tenant_obj)
        else:
            st.info(f"正在載入模組功能：{chosen_module}")
