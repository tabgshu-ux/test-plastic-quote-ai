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

# 引入總經理室戰情室與租戶 IT 授權模組
from modules import executive_office
from modules import system_licensing

st.set_page_config(
    page_title="多租戶 AI ERP 系統 - 拼圖式功能選擇與組織階層總控中心",
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

# 初始化總控登入狀態
if "master_logged_in" not in st.session_state:
    st.session_state.master_logged_in = False
if "selected_tenant" not in st.session_state:
    st.session_state.selected_tenant = None

# 🌟 1. 定義全系統所有的「ERP 功能拼圖清單」(Modular Building Blocks)
ALL_ERP_MODULE_PUZZLES = [
    "📈 總經理室戰情室 (AR/AP, P&L, 全球股市與金屬原物料即時監控)",
    "⚡ 工程與設計管理中心 (雙層報價、BOM 零件自動展開、工程驗收)",
    "👤 管理部 - 人事薪資與考勤打卡 (含越南勞動法加班費/夜班加給)",
    "📊 管理部 - 越南會計準則 (Thông tư 200) 與電子發票管理",
    "✍️ 全方位電子簽核中心 (跨部門呈核、估驗計價追蹤)",
    "📦 生產部 - 倉庫資材庫存與條碼管理",
    "🏭 生產部 - 板金加工組工單與粉體塗裝品管",
    "🚗 廠區車輛維修、門禁保全與派車審核",
    "💻 資訊管理部 - IT 專屬後台、租戶自主模組開關與外部 API 串聯"
]

# 🌟 2. 初始化三大商業授權方案及其「拼圖式功能與費用設定」
if "subscription_plans_db" not in st.session_state:
    st.session_state.subscription_plans_db = {
        "🚀 企業旗艦版 (Enterprise Flagship)": {
            "price_usd_year": 3500.0,
            "max_seats": "無限席位 (Unlimited)",
            "enabled_modules": ALL_ERP_MODULE_PUZZLES.copy() # 旗艦版包含所有拼圖
        },
        "💼 正式商業版 (Standard Official)": {
            "price_usd_year": 1500.0,
            "max_seats": "30 席位",
            "enabled_modules": [
                "⚡ 工程與設計管理中心 (雙層報價、BOM 零件自動展開、工程驗收)",
                "👤 管理部 - 人事薪資與考勤打卡 (含越南勞動法加班費/夜班加給)",
                "✍️ 全方位電子簽核中心 (跨部門呈核、估驗計價追蹤)",
                "📦 生產部 - 倉庫資材庫存與條碼管理"
            ]
        },
        "⏱️ 彈性訂閱版 (Flexible Subscription)": {
            "price_usd_month": 150.0,
            "max_seats": "10 席位",
            "enabled_modules": [
                "📦 生產部 - 倉庫資材庫存與條碼管理",
                "✍️ 全方位電子簽核中心 (跨部門呈核、估驗計價追蹤)"
            ]
        }
    }

# 初始化企業組織架構階層資料庫 (支援 1~4 級部門)
if "org_hierarchy_db" not in st.session_state:
    st.session_state.org_hierarchy_db = [
        {"level_1": "總經理室", "level_2": "經營管理處", "level_3": "資訊管理課", "level_4": "IT 系統維護組"},
        {"level_1": "工程事業群", "level_2": "機電設計部", "level_3": "配電盤設計課", "level_4": "BOM 展開組"},
        {"level_1": "生產製造部", "level_2": "廠務課", "level_3": "板金加工課", "level_4": "塗裝品管組"}
    ]

# 初始化全系統租戶清單
if "tenant_licensing_db" not in st.session_state:
    st.session_state.tenant_licensing_db = [
        {
            "tenant_id": "TENANT-001",
            "company_name": "裕豐電機工業 (Reetech Industrial)",
            "tax_id": "0312345678",
            "plan": "🚀 企業旗艦版 (Enterprise Flagship)",
            "pricing_usd": 3500.0,
            "max_seats": "無限席位 (Unlimited)",
            "expiry_date": "2027-12-31",
            "modules": ALL_ERP_MODULE_PUZZLES.copy(),
            "status": "🟢 正常運行 (Active)"
        }
    ]

# ==================== 側邊欄：總控與租戶切換導覽 ====================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/factory.png", width=64)
    st.markdown("### ⚡ AI ERP 總控台 (Master Portal)")
    st.markdown("---")
    
    if not st.session_state.master_logged_in:
        st.markdown("狀態: 請先登入總控台")
    else:
        st.success("🟢 總控管理員已登入")
        if st.session_state.selected_tenant:
            st.markdown(f"**當前操作租戶**: `{st.session_state.selected_tenant}`")
            if st.button("🔄 返回總控台首頁", use_container_width=True):
                st.session_state.selected_tenant = None
                st.rerun()
        
        if st.button("登出總控系統", use_container_width=True):
            st.session_state.master_logged_in = False
            st.session_state.selected_tenant = None
            st.rerun()

    st.markdown("---")
    
    if st.session_state.master_logged_in and st.session_state.selected_tenant:
        st.markdown("##### 🏢 租戶端部門選單：")
        # 抓取該租戶被指派啟用的拼圖模組
        current_tenant_obj = next((t for t in st.session_state.tenant_licensing_db if t["company_name"] == st.session_state.selected_tenant), None)
        allowed_menu_options = current_tenant_obj["modules"] if current_tenant_obj else []
        
        if allowed_menu_options:
            tenant_menu = st.radio("租戶部門選單", allowed_menu_options, label_visibility="collapsed")
        else:
            tenant_menu = "資訊管理部"
    else:
        tenant_menu = "總控台總覽"

# ==================== 主畫面邏輯 ====================

# 1. 尚未登入總控台
if not st.session_state.master_logged_in:
    st.markdown("## 🔐 AI ERP 系統 - 平台總控管理員登入")
    st.markdown("---")
    with st.form("master_login_form"):
        m_acc = st.text_input("總控管理員帳號", value="admin")
        m_pass = st.text_input("密碼", type="password", value="123")
        if st.form_submit_button("登入總控台", type="primary", use_container_width=True):
            if m_acc == "admin" and m_pass == "123":
                st.session_state.master_logged_in = True
                st.rerun()
            else:
                st.error("總控管理員帳號或密碼錯誤 (預設 admin / 123)")

# 2. 已登入總控台：拼圖式方案與租戶總控中心
elif not st.session_state.selected_tenant:
    st.markdown("### 🏢 平台總控台 - 拼圖式功能模組選擇與商業方案定價中心")
    st.caption("在此處設定「旗艦版、正式版、訂閱版」的拼圖式功能組合與費用，並管理 1~4 級部門組織與租戶合約。")

    master_tab1, master_tab2, master_tab3, master_tab4 = st.tabs([
        "🏢 租戶總覽與快速進入", 
        "🧩 拼圖式方案功能與費用設定 (旗艦/正式/訂閱)",
        "🌳 企業 1~4 級部門組織架構管理",
        "➕ 註冊新租戶與拼圖指派"
    ])

    # Tab 1: 租戶總覽與快速進入
    with master_tab1:
        st.markdown("#### 📋 平台現有企業租戶清單")
        search_query = st.text_input("🔍 快速搜尋租戶（公司名稱、代碼或統編）：", placeholder="例如：裕豐 或 TENANT-001")

        tenants = st.session_state.tenant_licensing_db
        filtered_tenants = [
            t for t in tenants 
            if not search_query or search_query.lower() in t["company_name"].lower() or search_query.lower() in t["tenant_id"].lower()
        ]

        if filtered_tenants:
            df_tenants = pd.DataFrame(filtered_tenants)
            st.dataframe(df_tenants, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("#### 🚀 點擊下方按鈕直接進入對應租戶環境：")
            for t in filtered_tenants:
                col_info, col_btn = st.columns([3, 1])
                with col_info:
                    st.markdown(f"**{t['company_name']}** (`{t['tenant_id']}`) | 方案：{t['plan']} | 定價：${t.get('pricing_usd', 0):,.2f}")
                with col_btn:
                    if st.button(f"🚀 進入", key=f"btn_enter_{t['tenant_id']}", use_container_width=True):
                        st.session_state.selected_tenant = t["company_name"]
                        st.rerun()
        else:
            st.warning("⚠️ 找不到符合條件的租戶。")

    # Tab 2: 拼圖式方案功能與費用設定
    with master_tab2:
        st.markdown("#### 🧩 商業授權方案的「拼圖式功能」與費用設定")
        st.info("💡 銷售時可依據客戶需求，在不同方案中自由勾選要組合的 ERP 功能拼圖與設定售價。")

        plans_db = st.session_state.subscription_plans_db
        p_c1, p_c2, p_c3 = st.columns(3)

        with p_c1:
            st.markdown("### 🚀 企業旗艦版")
            st.markdown(f"**費用**：`${plans_db['🚀 企業旗艦版 (Enterprise Flagship)']['price_usd_year']:,.2f} USD/年`")
            st.markdown("**已配置的功能拼圖**：")
            for f in plans_db['🚀 企業旗艦版 (Enterprise Flagship)']['enabled_modules']:
                st.markdown(f"- ✅ {f}")

        with p_c2:
            st.markdown("### 💼 正式商業版")
            st.markdown(f"**費用**：`${plans_db['💼 正式商業版 (Standard Official)']['price_usd_year']:,.2f} USD/年`")
            st.markdown("**已配置的功能拼圖**：")
            for f in plans_db['💼 正式商業版 (Standard Official)']['enabled_modules']:
                st.markdown(f"- ✅ {f}")

        with p_c3:
            st.markdown("### ⏱️ 彈性訂閱版")
            st.markdown(f"**費用**：`${plans_db['⏱️ 彈性訂閱版 (Flexible Subscription)']['price_usd_month']:,.2f} USD/月`")
            st.markdown("**已配置的功能拼圖**：")
            for f in plans_db['⏱️ 彈性訂閱版 (Flexible Subscription)']['enabled_modules']:
                st.markdown(f"- ✅ {f}")

        st.markdown("---")
        with st.expander("⚙️ 編輯指定方案的拼圖模組與定價"):
            with st.form("form_edit_puzzle_plan"):
                target_p_name = st.selectbox("選擇要調整的方案", list(plans_db.keys()))
                edit_price = st.number_input("設定方案費用 (USD)", value=float(plans_db[target_p_name].get("price_usd_year", 1500.0)))
                
                st.markdown("##### 🧩 勾選該方案包含的功能拼圖：")
                current_enabled = plans_db[target_p_name]["enabled_modules"]
                new_selected_puzzles = []
                for puzzle in ALL_ERP_MODULE_PUZZLES:
                    if st.checkbox(puzzle, value=(puzzle in current_enabled), key=f"edit_puz_{target_p_name}_{puzzle}"):
                        new_selected_puzzles.append(puzzle)

                if st.form_submit_button("💾 儲存方案拼圖配置", type="primary"):
                    plans_db[target_p_name]["price_usd_year"] = edit_price
                    plans_db[target_p_name]["enabled_modules"] = new_selected_puzzles
                    st.success(f"🎉 方案 [{target_p_name}] 的拼圖功能與定價已成功更新！")
                    st.rerun()

    # Tab 3: 企業 1~4 級部門組織架構管理
    with master_tab3:
        st.markdown("#### 🌳 企業 1~4 級部門組織架構管理")
        st.info("💡 定義企業內部的組織層級（1級處/部、2級部/課、3級課、4級組），便於後續部門權限與派工對應。")

        df_org = pd.DataFrame(st.session_state.org_hierarchy_db)
        df_org.columns = ["1級部門 (Division/Dept)", "2級部門 (Department/Section)", "3級部門 (Section/Unit)", "4級部門 (Group/Team)"]
        st.dataframe(df_org, use_container_width=True, hide_index=True)

        with st.form("form_add_org_level"):
            st.markdown("##### ➕ 新增 1~4 級部門組織節點")
            l1 = st.text_input("1級部門名稱", placeholder="例: 工程事業群")
            l2 = st.text_input("2級部門名稱", placeholder="例: 機電設計部")
            l3 = st.text_input("3級部門名稱", placeholder="例: 配電盤設計課")
            l4 = st.text_input("4級部門名稱", placeholder="例: BOM 展開組")

            if st.form_submit_button("💾 新增組織階層", type="primary"):
                if l1:
                    st.session_state.org_hierarchy_db.append({
                        "level_1": l1, "level_2": l2, "level_3": l3, "level_4": l4
                    })
                    st.success("🎉 1~4 級部門組織節點已成功建立！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請至少填寫 1 級部門名稱！")

    # Tab 4: 註冊新租戶與拼圖指派
    with master_tab4:
        st.markdown("#### ➕ 註冊新企業租戶並自訂拼圖模組")
        with st.form("form_add_tenant_puzzle"):
            c1, c2 = st.columns(2)
            with c1:
                t_cname = st.text_input("客戶公司名稱 *", placeholder="例: 越南電力工程股份公司")
                t_tax = st.text_input("統一編號 / 稅號 (MST)", placeholder="例: 0309988776")
                t_plan_choice = st.selectbox("選擇基礎授權方案", list(st.session_state.subscription_plans_db.keys()))
            with c2:
                default_pr = st.session_state.subscription_plans_db[t_plan_choice].get("price_usd_year", 1500.0)
                t_pr = st.number_input("合約定價金額 (USD)", min_value=0.0, value=float(default_pr))
                t_exp = st.date_input("合約到期日", value=datetime.date(2027, 12, 31))

            st.markdown("##### 🧩 針對此客戶客製化勾選啟用的功能拼圖：")
            default_puzzles_for_plan = st.session_state.subscription_plans_db[t_plan_choice]["enabled_modules"]
            custom_tenant_puzzles = []
            for puz in ALL_ERP_MODULE_PUZZLES:
                if st.checkbox(puz, value=(puz in default_puzzles_for_plan), key=f"new_tenant_puz_{puz}"):
                    custom_tenant_puzzles.append(puz)

            if st.form_submit_button("🚀 註冊租戶並派發拼圖功能", type="primary", use_container_width=True):
                if t_cname:
                    new_tid = f"TENANT-{len(st.session_state.tenant_licensing_db)+1:03d}"
                    st.session_state.tenant_licensing_db.append({
                        "tenant_id": new_tid,
                        "company_name": t_cname,
                        "tax_id": t_tax,
                        "plan": t_plan_choice,
                        "pricing_usd": t_pr,
                        "max_seats": "自訂席位",
                        "expiry_date": str(t_exp),
                        "modules": custom_tenant_puzzles,
                        "status": "🟢 正常運行 (Active)"
                    })
                    st.success(f"🎉 成功建立新租戶 [{t_cname}] 並派發專屬拼圖功能！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫客戶公司名稱！")

# 3. 已進入特定租戶環境：渲染該租戶被勾選啟用的拼圖功能模組
else:
    st.markdown(f"### ⚡ 當前操作租戶環境：`{st.session_state.selected_tenant}`")
    st.markdown("---")

    # 依照租戶被派發的拼圖模組進行路由渲染
    if "總經理室戰情室" in tenant_menu:
        executive_office.show({"name": st.session_state.selected_tenant})
    elif "工程與設計管理中心" in tenant_menu:
        render_mes_factory({"name": st.session_state.selected_tenant})
    elif "管理部" in tenant_menu:
        render_pos_retail({"name": st.session_state.selected_tenant})
    elif "全方位電子簽核中心" in tenant_menu:
        render_app_store({"name": st.session_state.selected_tenant}, [])
    elif "生產部" in tenant_menu:
        render_org_chart({"name": st.session_state.selected_tenant})
    elif "資訊管理部" in tenant_menu:
        st.markdown("### 💻 資訊管理部 (IT & System) 專屬後台")
        it_tab1, it_tab2 = st.tabs(["🔒 組織權限與角色管理 (RBAC)", "🧩 本公司拼圖模組與外部 API 設定"])
        with it_tab1:
            render_rbac({"name": st.session_state.selected_tenant})
        with it_tab2:
            system_licensing.show({"name": st.session_state.selected_tenant})
    else:
        st.info(f"正在載入模組：{tenant_menu}")
