import streamlit as st
import pandas as pd
import datetime

# 🌟 完整引入 modules/ 資料夾底下的所有實戰模組資產
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
    page_title="全球多租戶 SaaS AI ERP 平台 - 總控與拼圖式租戶管理中心",
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

# 全系統定義的 ERP 功能拼圖清單
if "all_puzzles" not in st.session_state:
    st.session_state.all_puzzles = [
        "📊 總經理室戰情室 (AR/AP, P&L, 財務現金流)",
        "⚡ 工程與設計中心 (雙層報價、BOM 零件自動展開)",
        "👤 管理部 - 人事薪資與考勤 (含越南勞動法加班費)",
        "🇻🇳 越南在地化稅務 (Thông tư 200 與電子發票)",
        "✍️ 全方位電子簽核中心 (跨部門呈核、手機簽核)",
        "📦 生產部 - 倉庫資材庫存與條碼管理",
        "🛡️ ISO與ESG合規 (CAPA 矯正預防與碳足跡盤查)",
        "💻 資訊管理部 - IT 專屬後台與 API 串聯"
    ]

# 商業方案與拼圖配置資料庫
if "subscription_plans_db" not in st.session_state:
    st.session_state.subscription_plans_db = {
        "🚀 企業旗艦版 (Enterprise Flagship)": {
            "price_usd": 3500.0,
            "modules": st.session_state.all_puzzles.copy()
        },
        "💼 正式商業版 (Standard Official)": {
            "price_usd": 1500.0,
            "modules": st.session_state.all_puzzles[:4]
        },
        "⏱️ 彈性訂閱版 (Flexible Subscription)": {
            "price_usd": 600.0,
            "modules": st.session_state.all_puzzles[:2]
        }
    }

# 租戶授權與拼圖綁定資料庫
if "tenant_licensing_db" not in st.session_state:
    st.session_state.tenant_licensing_db = [
        {
            "tenant_id": "TENANT-001",
            "company_name": "裕豐電機工業 (Reetech Industrial)",
            "tax_id": "0312345678",
            "plan": "🚀 企業旗艦版 (Enterprise Flagship)",
            "pricing_usd": 3500.0,
            "expiry_date": "2027-12-31",
            "modules": st.session_state.all_puzzles.copy(),
            "status": "🟢 正常運行 (Active)"
        }
    ]

# ==================== 側邊欄導覽 ====================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/factory.png", width=64)
    st.markdown("### ⚡ AI ERP 總控台")
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

# 層級一：總控管理員登入驗證
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

# 層級二：總控管理中心 (含拼圖設定、定價、租戶總覽)
elif not st.session_state.selected_tenant:
    st.markdown("## 🏢 平台總控管理中心 (Master Control Panel)")
    st.markdown("在此檢視所有企業租戶、設定方案定價、動態勾選拼圖模組，並管控各客戶合約與組織。")
    st.markdown("---")

    master_tab1, master_tab2, master_tab3 = st.tabs([
        "📋 企業租戶總覽與快速進入",
        "🧩 拼圖式方案與動態價格設定",
        "➕ 註冊新租戶與拼圖派發"
    ])

    # Tab 1: 租戶總覽
    with master_tab1:
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
                        st.write(f"• **合約到期**：{t['expiry_date']} | **已開通拼圖數**：{len(t['modules'])} 個模組")
                    with col_b:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"🚀 進入租戶工作區", key=f"enter_{t['tenant_id']}", use_container_width=True):
                            st.session_state.selected_tenant = t["company_name"]
                            st.rerun()
                    st.markdown("---")
        else:
            st.warning("查無符合條件的租戶。")

    # Tab 2: 拼圖式方案與動態價格設定
    with master_tab2:
        st.markdown("### 🧩 商業方案拼圖與動態價格管理")
        st.info("💡 管理者可在此自由調整標準方案的價格，並動態勾選要組合進該方案的功能拼圖。")
        
        plans = st.session_state.subscription_plans_db
        target_p = st.selectbox("選擇要編輯的授權方案", list(plans.keys()))
        
        with st.form("edit_plan_form"):
            current_price = plans[target_p]["price_usd"]
            new_price = st.number_input("設定年度授權價格 (USD)", value=float(current_price), step=100.0)
            
            st.markdown("##### 🧩 勾選該方案內含的 ERP 功能拼圖：")
            current_mods = plans[target_p]["modules"]
            updated_mods = []
            for puz in st.session_state.all_puzzles:
                if st.checkbox(puz, value=(puz in current_mods), key=f"puz_chk_{target_p}_{puz}"):
                    updated_mods.append(puz)
            
            if st.form_submit_button("💾 儲存方案拼圖與定價配置", type="primary"):
                plans[target_p]["price_usd"] = new_price
                plans[target_p]["modules"] = updated_mods
                st.success(f"🎉 方案 [{target_p}] 已成功更新！")
                st.rerun()

    # Tab 3: 註冊新租戶與拼圖指派
    with master_tab3:
        st.markdown("### ➕ 註冊新企業租戶與客製化拼圖派發")
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
            
            st.markdown("##### 🧩 針對此客戶客製化勾選啟用的功能拼圖：")
            default_puzzles = st.session_state.subscription_plans_db[t_plan]["modules"]
            tenant_puzzles = []
            for puz in st.session_state.all_puzzles:
                if st.checkbox(puz, value=(puz in default_puzzles), key=f"new_t_puz_{puz}"):
                    tenant_puzzles.append(puz)
            
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
                        "modules": tenant_puzzles,
                        "status": "🟢 正常運行 (Active)"
                    })
                    st.success(f"🎉 成功建立新租戶：{t_name}！")
                    st.rerun()
                else:
                    st.warning("請填寫公司名稱！")

# 層級三：已進入特定租戶環境 (無縫串接 modules/ 底下的強大模組)
else:
    # 取得當前租戶物件
    current_tenant_obj = next((t for t in st.session_state.tenant_licensing_db if t["company_name"] == st.session_state.selected_tenant), None)
    
    if current_tenant_obj:
        st.sidebar.markdown("---")
        st.sidebar.markdown("##### 📂 租戶功能模組選單：")
        allowed_modules = current_tenant_obj["modules"]
        
        # 側邊欄選單切換該租戶被授權的拼圖
        chosen_module = st.sidebar.radio("選擇模組", allowed_modules, label_visibility="collapsed")
        
        st.markdown(f"### ⚡ 租戶工作區：`{current_tenant_obj['company_name']}`")
        st.markdown(f"**授權方案**：{current_tenant_obj['plan']} | **合約到期**：{current_tenant_obj['expiry_date']}")
        st.markdown("---")
        
        # 🔗 資深工程師級路由分派：精準呼叫 modules/ 底下的實作檔案
        if "總經理室戰情室" in chosen_module:
            executive_office.show({"name": current_tenant_obj['company_name']})
        elif "工程與設計中心" in chosen_module:
            render_mes_factory({"name": current_tenant_obj['company_name']})
        elif "管理部" in chosen_module or "越南在地化稅務" in chosen_module:
            render_pos_retail({"name": current_tenant_obj['company_name']})
        elif "電子簽核" in chosen_module:
            render_app_store({"name": current_tenant_obj['company_name']}, [])
        elif "生產部" in chosen_module or "ISO與ESG" in chosen_module:
            render_org_chart({"name": current_tenant_obj['company_name']})
        elif "資訊管理部" in chosen_module:
            st.markdown("### 💻 資訊管理部 (IT & System) 專屬後台")
            it_tab1, it_tab2 = st.tabs(["🔒 組織權限與角色管理 (RBAC)", "🧩 本公司拼圖模組與 API 設定"])
            with it_tab1:
                render_rbac({"name": current_tenant_obj['company_name']})
            with it_tab2:
                system_licensing.show({"name": current_tenant_obj['company_name']})
        else:
            st.info(f"正在載入模組功能：{chosen_module}")
