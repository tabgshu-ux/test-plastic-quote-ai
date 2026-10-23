import streamlit as st
import pandas as pd
import datetime

# 🌐 採用安全匯入與防呆機制，確保主控台絕對不會因為單一模組未就緒而崩潰
try:
    from modules import executive_office
    from modules import system_licensing
    from modules.departments_manager import render_departments_manager
    from modules.org_chart import render_org_chart
    from modules.rbac import render_rbac
    from modules.executive_bi import render_executive_bi
    from modules.pos_retail import render_pos_retail
    from modules.mes_factory import render_mes_factory
    from modules.app_store import render_app_store
except ImportError:
    pass

st.set_page_config(
    page_title="全球多租戶 SaaS AI ERP 平台 - 產業別與 1~4級組織拼圖總控中心",
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

# 🌐 多國語言字典檔支援
lang_dict = {
    "繁體中文": {
        "title": "全球多租戶 SaaS AI ERP 平台 - 全產業別與 1~4 級組織總控中心",
        "sidebar_title": "⚡ SaaS ERP 總控台",
        "lang_label": "🌐 選擇介面語系 / Select Language",
        "logged_in": "🟢 總控管理員已登入",
        "logout": "🚪 登出系統",
        "tab1": "🏭 全球產業與 1~4 級部門拼圖市集",
        "tab2": "💰 四大商業授權方案定價設定",
        "tab3": "📋 企業租戶總覽與方案綁定",
        "tab4": "➕ 註冊新租戶與方案指派"
    },
    "English": {
        "title": "Global Multi-Tenant SaaS AI ERP - Global Industry & Org Control Center",
        "sidebar_title": "⚡ SaaS ERP Master",
        "lang_label": "🌐 Select Language",
        "logged_in": "🟢 Master Admin Logged In",
        "logout": "🚪 Logout",
        "tab1": "🏭 Industry & 1-4 Level Org Marketplace",
        "tab2": "💰 Commercial Plans Setup",
        "tab3": "📋 Tenant Overview & Licensing",
        "tab4": "➕ Register New Tenant"
    },
    "Tiếng Việt": {
        "title": "Nền tảng SaaS AI ERP Đa người thuê - Trung tâm điều khiển toàn cầu",
        "sidebar_title": "⚡ SaaS ERP Tổng",
        "lang_label": "🌐 Chọn ngôn ngữ",
        "logged_in": "🟢 Quản trị viên đã đăng nhập",
        "logout": "Đăng xuất",
        "tab1": "🏭 Chợ ngành nghề toàn cầu & 1-4 cấp",
        "tab2": "💰 Cài đặt gói thương mại",
        "tab3": "📋 Tổng quan khách hàng",
        "tab4": "➕ Đăng ký khách hàng mới"
    }
}

# ==================== 側邊欄導覽與語系切換 ====================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/factory.png", width=64)
    
    current_lang = st.selectbox(
        "🌐 選擇介面語系 / Select Language", 
        ["繁體中文", "English", "Tiếng Việt"], 
        key="current_lang_selector"
    )
    
    t = lang_dict[current_lang]
    st.markdown(f"### {t['sidebar_title']}")
    st.markdown("---")
    
    if st.session_state.master_logged_in:
        st.success(t["logged_in"])
        if st.session_state.selected_tenant:
            st.markdown(f"**當前檢視租戶**：`{st.session_state.selected_tenant}`")
            if st.button("🔄 返回總控台首頁", use_container_width=True):
                st.session_state.selected_tenant = None
                st.rerun()
        
        if st.button(t["logout"], use_container_width=True):
            st.session_state.master_logged_in = False
            st.session_state.selected_tenant = None
            st.rerun()
    else:
        st.info("狀態：等待總控台登入驗證")

# ==================== 核心資料庫初始化 ====================
if "subscription_plans_db" not in st.session_state:
    st.session_state.subscription_plans_db = {
        "🚀 企業旗艦版 (Enterprise Flagship)": {
            "price_usd": 3500.0, "billing_cycle": "每年計費", "max_seats": "無限席位", "desc": "解鎖全公司所有 1~4 級部門與所有業務拼圖模組。"
        },
        "💼 正式商業版 (Standard Official)": {
            "price_usd": 1500.0, "billing_cycle": "每年計費", "max_seats": "30 席位", "desc": "支援核心生產、供應鏈與財會模組。"
        },
        "⏱️ 彈性訂閱版 (Flexible Subscription)": {
            "price_usd": 150.0, "billing_cycle": "每月計費", "max_seats": "10 席位", "desc": "按月隨選訂閱指定部門拼圖。"
        },
        "👤 個人試用版 (Free Trial)": {
            "price_usd": 0.0, "billing_cycle": "14天免費", "max_seats": "3 席位", "desc": "供單一部門進行功能體驗。"
        }
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

# ==================== 主路由邏輯 ====================

# 1. 總控台登入驗證
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

# 2. 總控中心首頁 (未選定特定租戶時)
elif not st.session_state.selected_tenant:
    st.markdown(f"## 🏢 {t['title']}")
    st.markdown("💡 *請自由選擇全球產業別、檢視完整 1~4 級部門階層、管理商業授權方案與查看所有企業租戶！*")
    st.markdown("---")

    master_tab1, master_tab2, master_tab3, master_tab4 = st.tabs([
        t["tab1"], t["tab2"], t["tab3"], t["tab4"]
    ])

    # Tab 1: 全產業與 1~4 級組織拼圖總控市集
    with master_tab1:
        st.markdown("### 🏭 全球全產業標準市集與 1~4 級組織拼圖總控配置")
        st.info("💡 *請選擇企業所屬的全球產業領域，系統將自動展開完整的 1~4 級部門架構與白話功能拼圖，供總控管理員進行勾選與配置。*")
        
        global_industries_db = {
            "科技資訊業 (Tech & IT Software)": {
                "desc": "專為軟體研發、系統整合、雲端服務與高科技企業設計之多級組織架構",
                "levels": {
                    "1級：最高決策層": {
                        "董事長室 / 總經理室": ["👑 老闆專屬營收與資金看板", "👑 集團即時合併報表與現金流水位", "👑 跨國重大決策電子簽核"],
                        "策略發展委員會": ["📈 長期策略目標 KPI 追蹤儀表板", "📈 市場競爭分析與競品情報庫", "📈 投資併購專案評估模型"]
                    },
                    "2級：處 / 部層級": {
                        "資訊處 (IT Division)": ["💻 SaaS 租戶自主拼圖模組開關與授權管控", "💻 組織權限與角色管理 (RBAC) 核心", "💻 外部第三方 API 串聯與資料庫同步"],
                        "人力資源處": ["👥 全球人事組織與員工生命週期管理", "👥 跨國薪資計算引擎 (含加班費/夜班加給)", "👥 多班別排班考勤與請假打卡系統"],
                        "財務會計處": ["📊 總帳會計系統、傳票登錄與試算表", "📊 跨國多幣別會計帳套與傳票管理", "📊 電子發票開立與申報系統"]
                    },
                    "3級：科 / 營運中心": {
                        "資訊處 - 資訊部": ["💻 企業內部 ERP 系統維運與資料庫備份管理", "💻 總部與各廠區網路架構與 VPN 監控", "💻 使用者端硬體設備與資安派送管理"],
                        "資訊處 - 軟體開發部": ["💻 AI 模組串聯、Function Calling 與工作流程引擎", "💻 跨國多語系自動翻譯快取與前端動態渲染", "💻 客製化 API 開發與 Webhook 整合"],
                        "研發專案課": ["💡 新產品研發專案管理與階段閘門審查", "💡 研發實驗數據記錄與原型機測試追蹤"]
                    },
                    "4級：組 / 班別": {
                        "資訊安全小組": ["🛡️ 資訊安全事件通報與資安軌跡日誌", "🛡️ 權限存取控制稽核 (RBAC Log)"],
                        "系統維運組": ["💻 系統效能監控、容器化部署與資安日誌管理"]
                    }
                }
            },
            "傳統製造與電機機械業 (Traditional Mfg & Machinery)": {
                "desc": "專為機械加工、電機製造、配電盤組裝與勞動密集產業設計之多級組織架構",
                "levels": {
                    "1級：最高決策層": {
                        "董事長室 / 總經理室": ["👑 老闆專屬營收與資金看板", "👑 廠區稼動率與生產成本戰情看板"]
                    },
                    "2級：處 / 部層級": {
                        "生產製造事業群": ["🏭 MES 電機製造執行系統與車間工單排程", "🏭 現場機台設備稼動率與 OEE 即時監控"],
                        "供應鏈與採購處": ["📦 全球供應商詢比議價與合格供應商 (AVL) 評鑑", "📦 採購訂單 (PO) 發包與交期追蹤系統"],
                        "品質保證處 (QA/QC)": ["🔍 IQC 進料檢驗與 AQL 抽樣標準管理", "🔍 PQC 製程品保巡檢與不良率統計分析"]
                    },
                    "3級：科 / 營運中心": {
                        "配電盤製造課": ["⚡ 工程雙層報價與技術規格審查", "⚡ BOM (物料清單) 零件自動展開與版次管理"],
                        "倉儲物流管理課": ["📦 智能多倉庫進銷存與安全庫存水位警示", "📦 PDA 條碼掃描入庫、出庫與盤點作業 (WMS)"]
                    },
                    "4級：組 / 班別": {
                        "高壓盤組裝班": ["📱 現場作業員手機快速回報與拍照上傳", "🛡️ ISO 品質合規與 CAPA 矯正預防措施"],
                        "廠區維修與車輛組": ["🚗 廠區車輛與設備維修組 (派車與保養)", "📦 包裝與出貨組 (成品條碼貼標)"]
                    }
                }
            },
            "營造工程與土木建築業 (Construction & Engineering)": {
                "desc": "專為土木建築、廠房營造、機電工程與工程估驗計價設計之多級組織架構",
                "levels": {
                    "1級：最高決策層": {
                        "董事長室 / 總經理室": ["👑 工程總覽與多專案資金現金流戰情室"]
                    },
                    "2級：處 / 部層級": {
                        "工程事業處": ["🏗️ 營建專案工程進度與甘特圖管理", "🏗️ 分包商合約與估驗計價管理系統"],
                        "工務管理處": ["👷 工地現場人員出勤與安衛稽核管理"]
                    },
                    "3級：科 / 營運中心": {
                        "機電工程課": ["⚡ 機電設備點交與工程驗收管理", "⚡ 施工圖說管理與工程變更 (ECN) 追蹤"]
                    },
                    "4級：組 / 班別": {
                        "工地安全衛生組": ["🛡️ 營造工地安衛環保巡檢與違規矯正"],
                        "材料試驗班": ["🔍 營建建材進場抽驗與試驗報告管理"]
                    }
                }
            },
            "零售流通與餐飲連鎖業 (Retail & F&B Chain)": {
                "desc": "專為連鎖門市、電子商務、餐飲餐敘與批發零售業設計之多級組織架構",
                "levels": {
                    "1級：最高決策層": {
                        "董事長室 / 總經理室": ["👑 全通路營收與會員成長戰情室"]
                    },
                    "2級：處 / 部層級": {
                        "營運與通路事業處": ["🛍️ POS 零售收銀與多門市即時銷售看板", "📦 智慧庫存自動補貨與跨店調撥管理"],
                        "行銷與會員處": ["🎯 會員點數商城與多渠道行銷活動管理"]
                    },
                    "3級：科 / 營運中心": {
                        "直營門市營運科": ["💳 門市交班結帳與零用金管理", "📦 門市盤點與效期商品管理"]
                    },
                    "4級：組 / 班別": {
                        "線上客服組": ["💬 客戶諮詢與退換貨處理快速通道"]
                    }
                }
            },
            "醫療生技與製藥業 (Healthcare & Biotech)": {
                "desc": "專為醫療器材、生技研發與藥廠GMP規範設計之多級組織架構",
                "levels": {
                    "1級：最高決策層": {
                        "董事長室 / 總經理室": ["👑 臨床試驗與研發資金戰情室"]
                    },
                    "2級：處 / 部層級": {
                        "研發與法規事務處": ["🧪 實驗室數據記錄與 GMP 批次履歷追溯", "🛡️ 醫療法規與查驗登記文件管制"],
                        "品管與確效處": ["🔍 儀器校驗與無塵室環境監控管理"]
                    },
                    "3級：科 / 營運中心": {
                        "生技研發科": ["💡 實驗配方版本管制與專案進度追蹤"]
                    },
                    "4級：組 / 班別": {
                        "儀器校驗組": ["📏 精密量測儀器校驗週期與異常鎖定"]
                    }
                }
            }
        }

        all_industries = list(global_industries_db.keys())
        selected_ind = st.selectbox("🌐 選擇全球產業領域類別：", all_industries, key="master_industry_dropdown")
        ind_info = global_industries_db[selected_ind]
        st.info(f"💡 產業架構說明：{ind_info['desc']}")
        st.markdown("---")

        st.markdown(f"### 🌳 【 {selected_ind} 】之完整 1~4 級組織階層與功能拼圖市集")
        
        for lvl_name, dept_dict in ind_info["levels"].items():
            st.markdown(f"## 📌 ── 【 {lvl_name} 】 ──")
            
            for d_name, puz_list in dept_dict.items():
                with st.expander(f"🏢 展開配置【 {d_name} 】專屬部門與作業拼圖", expanded=True):
                    c_cols = st.columns(2)
                    for idx, puz in enumerate(puz_list):
                        with c_cols[idx % 2]:
                            st.checkbox(puz, value=True, key=f"master_chk_{selected_ind}_{d_name}_{puz}")
            st.markdown("<br>", unsafe_allow_html=True)

        if st.button("💾 儲存並發布該產業之 1~4 級組織與拼圖配置至客戶端", type="primary", use_container_width=True):
            st.success(f"🎉 成功儲存【{selected_ind}】的 1~4 級組織與功能拼圖市集設定！客戶登入後即可同步生效。")

    # Tab 2: 四大商業方案設定
    with master_tab2:
        st.markdown("### 💰 四大商業授權方案定價與規格設定")
        plans_db = st.session_state.subscription_plans_db
        cols = st.columns(4)
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
        filtered = [t_item for t_item in tenants if not search or search.lower() in t_item["company_name"].lower() or search.lower() in t_item["tenant_id"].lower()]
        
        if filtered:
            for t_item in filtered:
                with st.container():
                    col_i, col_b = st.columns([3, 1])
                    with col_i:
                        st.markdown(f"#### 🏢 {t_item['company_name']} (`{t_item['tenant_id']}`)")
                        st.write(f"• **綁定商業方案**：{t_item['plan']} | **合約金額**：${t_item['pricing_usd']:,.2f} USD")
                        st.write(f"• **合約到期日**：{t_item['expiry_date']} | **運行狀態**：{t_item['status']}")
                    with col_b:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"🚀 進入租戶工作區", key=f"enter_{t_item['tenant_id']}", use_container_width=True):
                            st.session_state.selected_tenant = t_item["company_name"]
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

# 3. 已進入特定租戶工作區
else:
    current_tenant_obj = next((t_item for t_item in st.session_state.tenant_licensing_db if t_item["company_name"] == st.session_state.selected_tenant), None)
    
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
            if 'render_departments_manager' in globals():
                render_departments_manager(current_tenant_obj)
            else:
                st.info("正在載入：多級組織架構維護模組")
        elif "組織架構圖" in chosen_module:
            if 'render_org_chart' in globals():
                render_org_chart(current_tenant_obj)
            else:
                st.info("正在載入：組織架構圖模組")
        elif "總經理室戰情室" in chosen_module:
            if 'executive_office' in globals() and hasattr(executive_office, 'show'):
                executive_office.show(current_tenant_obj)
            else:
                st.info("正在載入：總經理室戰情室模組")
        elif "資訊管理" in chosen_module:
            it_tab1, it_tab2 = st.tabs(["🔒 組織權限與角色管理 (RBAC)", "🧩 本公司拼圖模組與 API 設定"])
            with it_tab1:
                if 'render_rbac' in globals():
                    render_rbac(current_tenant_obj)
                else:
                    st.info("RBAC 模組載入中")
            with it_tab2:
                if 'system_licensing' in globals() and hasattr(system_licensing, 'show'):
                    system_licensing.show(current_tenant_obj)
                else:
                    st.info("系統授權模組載入中")
        else:
            st.info(f"正在載入模組功能：{chosen_module}")
