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
    page_title="全球多租戶 SaaS AI ERP 平台 - 拼圖式功能選擇與組織總控中心",
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

# 🌟 完整重現圖片中的全球跨國企業完整部門清單
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

# 🌟 全功能模組市集大合集 (對應圖片右側的三大類別)
if "master_app_store_puzzles" not in st.session_state:
    st.session_state.master_app_store_puzzles = {
        "📊 高階決策與即時行情": [
            "全球原物料即時行情看板",
            "國際匯率與多幣別換算中心",
            "全球股市財經大盤監控",
            "綜合損益表與資產負債表",
            "現金流與應收/應付帳款水位",
            "企業 KPI 與多維度 BI 戰情室"
        ],
        "📦 供應鏈與進銷存 (SCM)": [
            "智能進銷存與批號效期管理",
            "全球供應鏈採購與比價系統",
            "倉儲物流與條碼PDA掃描(WMS)",
            "供應商交期與品質評鑑系統",
            "進出口報關與海運物流追蹤",
            "條碼/QR Code與資產標籤列印"
        ],
        "💰 財會、生產與其他核心": [
            "總帳會計、傳票與會計師報表",
            "生產排程、BOM表與製程考考核",
            "CRM 客戶關係與外貿商機管理",
            "人事薪資、勞健保與考勤排班",
            "電子簽核流程引擎 (BOM)",
            "AI 智慧語音助理與跨國翻譯"
        ]
    }

# 初始化部門與勾選模組的對應資料庫
if "dept_puzzle_mapping" not in st.session_state:
    st.session_state.dept_puzzle_mapping = {
        dept: [item for cat_list in st.session_state.master_app_store_puzzles.values() for item in cat_list[:3]]
        for dept in st.session_state.global_departments_list
    }

# 商業方案與租戶資料庫
if "subscription_plans_db" not in st.session_state:
    st.session_state.subscription_plans_db = {
        "🚀 企業旗艦版 (Enterprise Flagship)": {"price_usd": 3500.0},
        "💼 正式商業版 (Standard Official)": {"price_usd": 1500.0},
        "⏱️ 彈性訂閱版 (Flexible Subscription)": {"price_usd": 600.0}
    }

if "tenant_licensing_db" not in st.session_state:
    st.session_state.tenant_licensing_db = [
        {
            "tenant_id": "TENANT-001",
            "company_name": "裕豐電機工業 (Reetech Industrial)",
            "tax_id": "0312345678",
            "plan": "🚀 企業旗艦版 (Enterprise Flagship)",
            "pricing_usd": 3500.0,
            "expiry_date": "2027-12-31",
            "status": "🟢 正常運行 (Active)"
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

# 層級二：總控管理中心 (完全對齊圖片的雙欄互動介面)
elif not st.session_state.selected_tenant:
    st.markdown("## 🏢 平台總控管理中心 - 企業全功能模組市集與組織架構總控")
    st.markdown("💡 *此展示系統【全功能模組大合集】。您可以點選左側任意部門，並自由勾選或組合市面上所有企業管理、高階決策、財會與供應鏈所需的完整模組拼圖。*")
    st.markdown("---")

    master_tab1, master_tab2, master_tab3 = st.tabs([
        "🧩 選擇目標部門並配置拼圖市集 (App Store)",
        "📋 企業租戶總覽與快速進入",
        "➕ 註冊新租戶與授權方案設定"
    ])

    # Tab 1: 完美對齊圖片的雙欄互動介面 (左側部門選單 ➔ 右側功能市集勾選)
    with master_tab1:
        col_dept_list, col_store_market = st.columns([1.2, 1.8])

        with col_dept_list:
            st.markdown("### 📂 選擇目標部門 / 管理層")
            st.caption("請點選要配置的部門：")
            
            # 讓管理者在左側選擇要設定的部門
            selected_dept = st.radio(
                "部門清單", 
                st.session_state.global_departments_list, 
                label_visibility="collapsed"
            )

        with col_store_market:
            st.markdown(f"### 🧩 【 {selected_dept} 】的企業全功能模組市集 (App Store)")
            st.caption("賴勾選此部門/高階角色可解鎖啟用的所有功能與戰情儀表板：")
            st.markdown("---")

            current_dept_puzzles = st.session_state.dept_puzzle_mapping.get(selected_dept, [])
            updated_dept_puzzles = []

            # 依三大類別呈現勾選方塊（完全對齊圖片的三欄式視覺）
            store_cats = st.session_state.master_app_store_puzzles
            
            for cat_name, items in store_cats.items():
                st.markdown(f"#### {cat_name}")
                for item in items:
                    is_checked = st.checkbox(
                        item, 
                        value=(item in current_dept_puzzles), 
                        key=f"chk_store_{selected_dept}_{item}"
                    )
                    if is_checked:
                        updated_dept_puzzles.append(item)
                st.markdown("")

            st.markdown("---")
            if st.button(f"💾 儲存【{selected_dept}】的全功能拼圖圈定", type="primary", use_container_width=True):
                st.session_state.dept_puzzle_mapping[selected_dept] = updated_dept_puzzles
                st.success(f"🎉 成功儲存！【{selected_dept}】已成功更新其專屬的拼圖市集模組。")
                st.rerun()

    # Tab 2: 租戶總覽與快速進入
    with master_tab2:
        st.markdown("### 📋 現有企業租戶清單")
        search = st.text_input("🔍 快速搜尋租戶 (公司名稱或代號)：", placeholder="例如：裕豐 或 TENANT-001")
        
        tenants = st.session_state.tenant_licensing_db
        filtered = [t for t in tenants if not search or search.lower() in t["company_name"].lower() or search.lower() in t["tenant_id"].lower()]
        
        if filtered:
            for t in filtered:
                with st.container():
                    col_i, col_b = st.columns([3, 1])
                    with col_i:
                        st.markdown(f"#### 🏢 {t['company_name']} (`{t['tenant_id']}`)")
                        st.write(f"• **授權方案**：{t['plan']} | **年費**：${t['pricing_usd']:,.2f} USD")
                        st.write(f"• **合約到期**：{t['expiry_date']}")
                    with col_b:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"🚀 進入租戶工作區", key=f"enter_{t['tenant_id']}", use_container_width=True):
                            st.session_state.selected_tenant = t["company_name"]
                            st.rerun()
                    st.markdown("---")
        else:
            st.warning("查無符合條件的租戶。")

    # Tab 3: 註冊新租戶與定價
    with master_tab3:
        st.markdown("### ➕ 註冊新企業租戶與授權合約")
        with st.form("new_tenant_form"):
            c1, c2 = st.columns(2)
            with c1:
                t_name = st.text_input("客戶公司名稱 *", placeholder="例: 越南精密工業股份公司")
                t_tax = st.text_input("統一編號 / 稅號", placeholder="0312345678")
                t_plan = st.selectbox("基礎授權方案", list(st.session_state.subscription_plans_db.keys()))
            with c2:
                default_pr = st.session_state.subscription_plans_db[t_plan]["price_usd"]
                t_price = st.number_input("合約定價金額 (USD)", value=float(default_pr))
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
                        "status": "🟢 正常運行 (Active)"
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
