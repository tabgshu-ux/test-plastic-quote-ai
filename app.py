import streamlit as st
import pandas as pd
import datetime

# 引入各大部門與組織模組
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
    page_title="全球多租戶 SaaS AI ERP 平台 - 全球 1~4 級組織與拼圖總控中心",
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

# 🌟 全球企業標準：完整涵蓋 1~4 級（處 ➔ 部 ➔ 課 ➔ 組）之 ERP 拼圖矩陣
if "all_department_puzzles" not in st.session_state:
    st.session_state.all_department_puzzles = [
        # 【1級：總管理處 / 經營戰情】
        {"level": "1級：總管理處 (Division)", "code": "L1-EXEC", "name": "📈 總經理室戰情室 (AR/AP, P&L, 財務現金流與全球原物料監控)"},
        {"level": "1級：總管理處 (Division)", "code": "L1-IT", "name": "💻 資訊管理部 - 總部 IT 專屬後台、RBAC 與跨國 API 串聯"},
        {"level": "1級：總管理處 (Division)", "code": "L1-ESG", "name": "🌱 永續與 ESG 治理中心 - 範疇一二三碳排與跨國法規合規"},

        # 【2級：核心事業部 / 專業處】
        {"level": "2級：核心事業部 (Department)", "code": "L2-ENG", "name": "⚡ 工程事業群 - 機電設計、BOM 零件自動展開與工程驗收"},
        {"level": "2級：核心事業部 (Department)", "code": "L2-FIN", "name": "🇻🇳 越南在地化會計 (Thông tư 200) 與跨國電子發票管理"},
        {"level": "2級：核心事業部 (Department)", "code": "L2-HR", "name": "👤 管理部 - 全球人事薪資與考勤 (含越南勞動法加班費/夜班加給)"},
        {"level": "2級：核心事業部 (Department)", "code": "L2-SALES", "name": "🌐 業務貿易部 - 全球多幣別雙層報價與客戶關係管理 (CRM)"},

        # 【3級：專屬課 / 營運中心】
        {"level": "3級：營運課/中心 (Section)", "code": "L3-SIGN", "name": "✍️ 跨部門電子簽核中心 (呈核路由、估驗計價與手機端簽核)"},
        {"level": "3級：營運課/中心 (Section)", "code": "L3-WH", "name": "📦 倉儲物流課 - 多倉庫條碼化管理、安全庫存水位與自動補貨"},
        {"level": "3級：營運課/中心 (Section)", "code": "L3-PROD", "name": "🏭 製造生產課 - 板金加工組工單排程、派工與進度回報"},
        {"level": "3級：營運課/中心 (Section)", "code": "L3-QA", "name": "🔍 品質保證課 (QA) - IQC進料檢驗、PQC製程品保與OQC出貨檢驗"},

        # 【4級：現場組 / 班別 / 技術小組】
        {"level": "4級：現場組/班別 (Group)", "code": "L4-ISO", "name": "🛡️ ISO 品質合規組 - CAPA 矯正預防措施與設備校驗履歷管理"},
        {"level": "4級：現場組/班別 (Group)", "code": "L4-MAINT", "name": "🚗 廠區車輛與設備維修組 - 廠車維護、門禁保全與派車審核"},
        {"level": "4級：現場組/班別 (Group)", "code": "L4-PACK", "name": "📦 包裝與出貨組 - 成品條碼貼標、棧板管理與海關出貨文件"}
    ]

# 商業方案與 1~4 級拼圖綁定資料庫
if "subscription_plans_db" not in st.session_state:
    st.session_state.subscription_plans_db = {
        "🚀 企業旗艦版 (Enterprise Flagship)": {
            "price_usd": 3500.0,
            "modules": [p["name"] for p in st.session_state.all_department_puzzles]
        },
        "💼 正式商業版 (Standard Official)": {
            "price_usd": 1500.0,
            "modules": [p["name"] for p in st.session_state.all_department_puzzles[:8]]
        },
        "⏱️ 彈性訂閱版 (Flexible Subscription)": {
            "price_usd": 600.0,
            "modules": [p["name"] for p in st.session_state.all_department_puzzles[:4]]
        }
    }

# 租戶授權與結構資料庫 (內含多級組織與節點結構)
if "tenant_licensing_db" not in st.session_state:
    st.session_state.tenant_licensing_db = [
        {
            "tenant_id": "TENANT-001",
            "name": "裕豐電機工業 (Reetech Industrial)",
            "company_name": "裕豐電機工業 (Reetech Industrial)",
            "tax_id": "0312345678",
            "plan": "🚀 企業旗艦版 (Enterprise Flagship)",
            "pricing_usd": 3500.0,
            "expiry_date": "2027-12-31",
            "modules": [p["name"] for p in st.session_state.all_department_puzzles],
            "status": "🟢 正常運行 (Active)",
            "hierarchical_org_tree": [
                {
                    "id": "div_01",
                    "level": "1級-事業群/處",
                    "name": "生產製造事業群",
                    "parent": "董事長室",
                    "sub_departments": [
                        {
                            "dept_name": "配電盤製造部 (2級-部)",
                            "sections": [
                                {"sec_name": "高壓盤組裝科 (3級-科)", "groups": ["第一作業班", "第二測試班"]},
                                {"sec_name": "低壓盤配線科 (3級-科)", "groups": ["焊接組", "佈線組"]}
                            ]
                        }
                    ],
                    "assigned_modules": ["MES 電機製造執行與車間排程", "工地師傅手機快速回報"]
                }
            ],
            "org_nodes": [
                {"id": "node_root", "name": "裕豐電機工業", "type": "👑 頂層 (Board / 董事會)", "parent": "無 (頂層)"},
                {"id": "node_hq", "name": "總管理處", "type": "👑 一級部門 (Headquarters)", "parent": "裕豐電機工業"},
                {"id": "node_prod", "name": "生產製造事業群", "type": "⚙️ 二級部門 (Functional Dept)", "parent": "總管理處"}
            ],
            "dept_modules_db": {
                "生產製造事業群": ["MES 電機製造執行與車間排程", "倉庫資材庫存與條碼管理"]
            }
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
    st.markdown("## 🏢 平台總控管理中心 (Master Control Panel)")
    st.markdown("在此檢視所有企業租戶、設定方案定價，並按 **全球標準 1~4 級組織架構（處 ➔ 部 ➔ 課 ➔ 組）** 動態勾選功能拼圖。")
    st.markdown("---")

    master_tab1, master_tab2, master_tab3 = st.tabs([
        "📋 企業租戶總覽與快速進入",
        "🧩 全球 1~4 級組織拼圖與動態價格設定",
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

    # Tab 2: 全球 1~4 級組織拼圖與動態價格設定
    with master_tab2:
        st.markdown("### 🧩 全球企業標準 1~4 級組織架構與拼圖模組設定")
        st.info("💡 完整整合全球跨國製造與企業的處、部、課、組組織階層，供管理者精確配置。")
        
        plans = st.session_state.subscription_plans_db
        target_p = st.selectbox("選擇要編輯的授權方案", list(plans.keys()))
        
        with st.form("edit_plan_form"):
            current_price = plans[target_p]["price_usd"]
            new_price = st.number_input("設定年度授權價格 (USD)", value=float(current_price), step=100.0)
            
            st.markdown("##### 🌳 按全球 1~4 級組織階層勾選功能拼圖：")
            current_mods = plans[target_p]["modules"]
            updated_mods = []
            
            levels_order = [
                "1級：總管理處 (Division)",
                "2級：核心事業部 (Department)",
                "3級：營運課/中心 (Section)",
                "4級：現場組/班別 (Group)"
            ]
            
            for lvl in levels_order:
                st.markdown(f"**📂 【 {lvl} 】相關模組與課級單位：**")
                lvl_puzzles = [p for p in st.session_state.all_department_puzzles if p["level"] == lvl]
                for puz in lvl_puzzles:
                    if st.checkbox(puz["name"], value=(puz["name"] in current_mods), key=f"puz_lvl_{target_p}_{puz['code']}"):
                        updated_mods.append(puz["name"])
                st.markdown("")
            
            if st.form_submit_button("💾 儲存全球 1~4 級拼圖與定價配置", type="primary"):
                plans[target_p]["price_usd"] = new_price
                plans[target_p]["modules"] = updated_mods
                st.success(f"🎉 方案 [{target_p}] 的全球 1~4 級組織拼圖配置已成功更新！")
                st.rerun()

    # Tab 3: 註冊新租戶與拼圖派發
    with master_tab3:
        st.markdown("### ➕ 註冊新企業租戶與全球 1~4 級組織拼圖派發")
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
            
            st.markdown("##### 🌳 針對此租戶客製化勾選全球 1~4 級組織與課級拼圖：")
            default_puzzles = st.session_state.subscription_plans_db[t_plan]["modules"]
            tenant_puzzles = []
            
            levels_order = [
                "1級：總管理處 (Division)",
                "2級：核心事業部 (Department)",
                "3級：營運課/中心 (Section)",
                "4級：現場組/班別 (Group)"
            ]
            
            for lvl in levels_order:
                st.markdown(f"**📂 【 {lvl} 】：**")
                lvl_puzzles = [p for p in st.session_state.all_department_puzzles if p["level"] == lvl]
                for puz in lvl_puzzles:
                    if st.checkbox(puz["name"], value=(puz["name"] in default_puzzles), key=f"new_t_puz_{puz['code']}"):
                        tenant_puzzles.append(puz["name"])
                st.markdown("")
            
            if st.form_submit_button("🚀 確認註冊並開通租戶環境", type="primary", use_container_width=True):
                if t_name:
                    new_id = f"TENANT-{len(st.session_state.tenant_licensing_db)+1:03d}"
                    st.session_state.tenant_licensing_db.append({
                        "tenant_id": new_id,
                        "name": t_name,
                        "company_name": t_name,
                        "tax_id": t_tax,
                        "plan": t_plan,
                        "pricing_usd": t_price,
                        "expiry_date": str(t_exp),
                        "modules": tenant_puzzles,
                        "status": "🟢 正常運行 (Active)",
                        "hierarchical_org_tree": [],
                        "org_nodes": [{"id": "node_root", "name": t_name, "type": "👑 頂層 (Board / 董事會)", "parent": "無 (頂層)"}],
                        "dept_modules_db": {}
                    })
                    st.success(f"🎉 成功建立新租戶：{t_name}！")
                    st.rerun()
                else:
                    st.warning("請填寫公司名稱！")

# 層級三：已進入特定租戶環境 (無縫掛載 departments_manager 與 org_chart 模組)
else:
    current_tenant_obj = next((t for t in st.session_state.tenant_licensing_db if t["company_name"] == st.session_state.selected_tenant), None)
    
    if current_tenant_obj:
        st.sidebar.markdown("---")
        st.sidebar.markdown("##### 📂 租戶專屬營運與模組選單：")
        
        tenant_menu_options = [
            "🌳 多級組織架構維護（部 ➔ 科 ➔ 組）與模組動態對應",
            "🖱️ 組織架構圖與節點管理 (Org Chart)",
            "📈 總經理室戰情室 (Executive Office)",
            "💻 資訊管理與 API 授權設定 (System Licensing)"
        ]
        
        chosen_module = st.sidebar.radio("選擇租戶模組", tenant_menu_options, label_visibility="collapsed")
        
        st.markdown(f"### ⚡ 租戶工作區：`{current_tenant_obj['company_name']}`")
        st.markdown(f"**授權方案**：{current_tenant_obj['plan']} | **合約到期**：{current_tenant_obj['expiry_date']}")
        st.markdown("---")
        
        # 精準呼叫對應的模組檔案函數
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
