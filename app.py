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
    page_title="全球多租戶 SaaS AI ERP 平台 - 1~4級部門架構與方案總控中心",
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

# 🌟 嚴格對標您提供的圖片：標準 1~4 級部門架構與對應名稱
if "strict_4level_departments" not in st.session_state:
    st.session_state.strict_4level_departments = {
        "1級最高決策層": {
            "desc": "集團最高戰略決策與經營監控核心",
            "departments": {
                "董事長室 / 總經理室": ["👑 全球多維度 BI 經營戰情室", "👑 集團即時合併報表與現金流水位", "👑 跨國重大決策電子簽核", "👑 全球原物料與總經理室即時看板"],
                "經營企劃與策略發展部": ["📈 長期策略目標 KPI 追蹤儀表板", "📈 市場競爭分析與競品情報庫", "📈 投資併購專案評估模型", "📈 企業年度預算編列與執行追蹤"]
            }
        },
        "2級部門": {
            "desc": "核心事業處與管理支援部門",
            "departments": {
                "人力資源與行政管理部": ["👥 全球人事組織與員工生命週期管理", "👥 跨國薪資計算引擎 (含越南勞動法加班費/夜班加給)", "👥 多班別排班考勤與請假打卡系統", "👥 招募管理與績效考核 (KPI/OKRs)"],
                "財務與資本運作部": ["💰 應收帳款 (AR) 與應付帳款 (AP) 即時水位", "💰 多幣別資金調度與銀行信用狀 (L/C) 管理", "💰 國際匯率風險避險與即時換算中心"],
                "會計與稅務管理部": ["📊 總帳會計系統、傳票登錄與試算表", "📊 越南會計準則 (Thông tư 200) 專用帳套", "📊 電子發票 (Electronic Invoice) 開立與申報"],
                "國內與國際業務部": ["💼 國內外客戶關係管理 (CRM) 與商機追蹤", "💼 國際多幣別貿易契約與雙層報價管理", "💼 業務績效獎金與佣金自動計算"],
                "法務與資訊安全處": ["⚖️ 跨國合約生命週期管理與電子簽署", "🛡️ 內部控制與 ISO 內稽內控檢核", "🛡️ 資訊安全事件通報與資安軌跡日誌"]
            }
        },
        "3級部門": {
            "desc": "專業營運課室與供應鏈中心",
            "departments": {
                "供應鏈與全球採購部": ["📦 全球供應商詢比議價與合格供應商 (AVL) 評鑑", "📦 採購訂單 (PO) 發包與交期追蹤系統", "📦 原物料價格波動行情看板"],
                "倉儲物流與庫存管理部": ["📦 智能多倉庫進銷存與安全庫存水位警示", "📦 PDA 條碼掃描入庫、出庫與盤點作業 (WMS)", "📦 批號效期管理 (FIFO/LIFO) 與溯源"],
                "生產製造與商務管理部": ["🏭 MES 電機製造執行系統與車間工單排程", "🏭 現場機台設備稼動率與 OEE 即時監控", "🏭 工地師傅與現場作業員手機快速回報"],
                "工程與技術服務部": ["⚡ 工程雙層報價與技術規格審查", "⚡ BOM (物料清單) 零件自動展開與版次管理", "⚡ 配電盤/變壓器設計圖紙與工程驗收"],
                "品質保證與品管中心 (QA/QC)": ["🔍 IQC 進料檢驗與 AQL 抽樣標準管理", "🔍 PQC 製程品保巡檢與不良率統計分析", "🔍 OQC 出貨檢驗與品質證書列印"]
            }
        },
        "4級部門": {
            "desc": "現場作業班組、研發技術小組與IT支援",
            "departments": {
                "研發設計與創新中心": ["💡 新產品研發專案管理與階段閘門審查", "💡 研發實驗數據記錄與原型機測試追蹤", "💡 智慧財產權與研發圖庫管理"],
                "資訊技術與系統開發部 (IT)": ["💻 SaaS 租戶自主拼圖模組開關與授權管控", "💻 組織權限與角色管理 (RBAC) 核心", "💻 外部第三方 API 串聯與資料庫同步"],
                "現場作業班與品保小組": ["🛡️ ISO 品質合規組 (CAPA 矯正預防措施)", "🚗 廠區車輛與設備維修組 (派車與保養)", "📦 包裝與出貨組 (成品條碼貼標與海關文件)"]
            }
        }
    }

# 商業方案與定價設定 (企業旗艦版、正式商業版、彈性訂閱版、個人試用版)
if "subscription_plans_db" not in st.session_state:
    st.session_state.subscription_plans_db = {
        "🚀 企業旗艦版 (Enterprise Flagship)": {
            "price_usd": 3500.0, "billing_cycle": "每年計費", "max_seats": "無限席位", "target": "大型跨國集團", "desc": "解鎖全公司所有 1~4 級部門與所有業務拼圖模組。"
        },
        "💼 正式商業版 (Standard Official)": {
            "price_usd": 1500.0, "billing_cycle": "每年計費", "max_seats": "30 席位", "target": "中型製造業", "desc": "支援核心生產、供應鏈與財會模組。"
        },
        "⏱️ 彈性訂閱版 (Flexible Subscription)": {
            "price_usd": 150.0, "billing_cycle": "每月計費", "max_seats": "10 席位", "target": "新創或彈性專案", "desc": "按月隨選訂閱指定部門拼圖。"
        },
        "👤 個人試用版 (Free Trial)": {
            "price_usd": 0.0, "billing_cycle": "14天免費", "max_seats": "3 席位", "target": "評估與沙盒測試", "desc": "供單一部門進行功能體驗。"
        }
    }

# 全系統租戶授權資料庫
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

# 層級二：總控管理中心
elif not st.session_state.selected_tenant:
    st.markdown("## 🏢 平台總控管理中心 - 1~4級部門架構與商業授權總控")
    st.markdown("💡 *嚴格對標 1~4 級組織架構（最高決策層 ➔ 2級部門 ➔ 3級部門 ➔ 4級部門），並與商業方案與租戶系統完全連動。*")
    st.markdown("---")

    master_tab1, master_tab2, master_tab3, master_tab4 = st.tabs([
        "🌳 1~4級部門架構與拼圖市集配置",
        "💰 四大商業方案（旗艦/正式/訂閱/試用）設定",
        "📋 企業租戶總覽與方案連動管理",
        "➕ 註冊新租戶與方案指派"
    ])

    # Tab 1: 嚴格對標 1~4 級部門架構與功能市集
    with master_tab1:
        st.markdown("### 🌳 企業組織架構：1~4 級部門與對應模組配置")
        st.info("💡 請在下方選擇對應的級別與部門名稱，系統將自動展開該部門專屬的業務功能拼圖。")

        hierarchy = st.session_state.strict_4level_departments
        
        selected_level = st.selectbox("選擇組織級別", list(hierarchy.keys()))
        level_data = hierarchy[selected_level]
        st.caption(f"級別說明：{level_data['desc']}")
        st.markdown("---")

        col_dept, col_puzzles = st.columns([1.2, 1.8])

        with col_dept:
            st.markdown("#### 📂 該級別對應的部門名稱")
            dept_names = list(level_data["departments"].keys())
            chosen_dept = st.radio("部門選擇", dept_names, label_visibility="collapsed")

        with col_puzzles:
            st.markdown(f"#### 🧩 【 {chosen_dept} 】內含功能與作業拼圖")
            st.caption("以下為該部門標準配置的業務功能模組：")
            st.markdown("---")

            default_puzzles = level_data["departments"][chosen_dept]
            for puz in default_puzzles:
                st.checkbox(puz, value=True, disabled=True, key=f"chk_strict_{chosen_dept}_{puz}")

            st.success("✅ 此部門模組已與企業授權方案及未來前端網頁客戶選購完全連動。")

    # Tab 2: 四大商業方案設定
    with master_tab2:
        st.markdown("### 💰 四大商業授權方案定價與規格設定")
        plans_db = st.session_state.subscription_plans_db
        c1, c2, c3, c4 = st.columns(4)
        cols = [c1, c2, c3, c4]
        for idx, (p_name, p_info) in enumerate(plans_db.items()):
            with cols[idx]:
                st.markdown(f"#### {p_name}")
                st.write(f"• **定價**：`${p_info['price_usd']:,.2f} USD`")
                st.write(f"• **週期**：{p_info['billing_cycle']}")
                st.write(f"• **席位**：{p_info['max_seats']}")
                st.caption(p_info['desc'])

        st.markdown("---")
        with st.form("edit_plan_form"):
            st.markdown("#### ⚙️ 調整指定商業方案定價")
            target_p = st.selectbox("選擇要修改的方案", list(plans_db.keys()))
            p_data = plans_db[target_p]

            new_pr = st.number_input("設定方案價格 (USD)", value=float(p_data["price_usd"]), step=50.0)
            new_cy = st.text_input("計費週期說明", value=p_data["billing_cycle"])
            new_st = st.text_input("席位限制說明", value=p_data["max_seats"])
            new_ds = st.text_area("方案特色描述", value=p_data["desc"])

            if st.form_submit_button("💾 儲存商業方案設定", type="primary", use_container_width=True):
                plans_db[target_p]["price_usd"] = new_pr
                plans_db[target_p]["billing_cycle"] = new_cy
                plans_db[target_p]["max_seats"] = new_st
                plans_db[target_p]["desc"] = new_ds
                st.success(f"🎉 商業方案 [{target_p}] 已成功更新！")
                st.rerun()

    # Tab 3: 企業租戶總覽
    with master_tab3:
        st.markdown("### 📋 現有企業租戶清單與方案綁定檢視")
        search = st.text_input("🔍 快速搜尋租戶 (公司名稱或代號)：", placeholder="例如：裕豐 或 TENANT-001")
        
        tenants = st.session_state.tenant_licensing_db
        filtered = [t for t in tenants if not search or search.lower() in t["company_name"].lower() or search.lower() in t["tenant_id"].lower()]
        
        if filtered:
            for t in filtered:
                with st.container():
                    col_i, col_b = st.columns([3, 1])
                    with col_i:
                        st.markdown(f"#### 🏢 {t['company_name']} (`{t['tenant_id']}`)")
                        st.write(f"• **綁定商業方案**：{t['plan']} | **合約金額**：${t['pricing_usd']:,.2f} USD")
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
        st.markdown("### ➕ 註冊新企業租戶並綁定四大商業方案")
        with st.form("new_tenant_form"):
            c1, c2 = st.columns(2)
            with c1:
                t_name = st.text_input("客戶公司名稱 *", placeholder="例: 裕豐電機工業")
                t_tax = st.text_input("統一編號 / 稅號", placeholder="0312345678")
                t_plan = st.selectbox("選擇綁定商業方案", list(st.session_state.subscription_plans_db.keys()))
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
                    st.success(f"🎉 成功建立新租戶 [{t_name}] 並自動綁定方案 [{t_plan}]！")
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
        st.markdown(f"**綁定授權方案**：{current_tenant_obj['plan']} | **合約到期**：{current_tenant_obj['expiry_date']}")
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
