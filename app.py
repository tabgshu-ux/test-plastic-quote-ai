import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# ==============================================================================
# 🧩 SaaS 企業級多租戶 AI-ERP 系統 (總控台方案定價樂高市集 + 資料庫持久化)
# ==============================================================================

st.set_page_config(
    page_title="SaaS Enterprise Modular AI-ERP Pricing Hub",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .card-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #1e293b;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
    .org-root-card {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        font-size: 15px;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
        display: inline-block;
        margin-bottom: 10px;
    }
    .org-level1-card {
        background: #ffffff;
        border: 2px solid #2563eb;
        color: #1e293b;
        padding: 10px 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 4px;
        min-width: 160px;
    }
    .org-level2-card {
        background: #f0fdf4;
        border: 2px solid #10b981;
        color: #065f46;
        padding: 8px 12px;
        border-radius: 6px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin: 3px;
        min-width: 140px;
        font-size: 12px;
    }
    .tree-connector {
        width: 2px;
        height: 20px;
        background-color: #94a3b8;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 初始化全域資料與方案定價資料庫 (Master Pricing & Plans DB)
if "global_plans_db" not in st.session_state:
    st.session_state.global_plans_db = {
        "🚀 旗艦版 (Enterprise)": {
            "base_price": 250.0,
            "description": "適合大型集團與跨國水電工程企業，解鎖全功能與無限部門掛載",
            "included_modules": ["全局戰情室與BI分析", "高階決策審核", "水電工程專案與預算", "工程估驗與計價請款", "全局資金水位管理"]
        },
        "💼 正式商業版 (Professional)": {
            "base_price": 150.0,
            "description": "適合中型企業與成長中公司，支援完整進銷存與財會核心",
            "included_modules": ["高階決策審核", "智能進銷存管理", "總帳會計與報表", "人事組織架構管理"]
        },
        "📦 標準訂閱版 (Subscription)": {
            "base_price": 80.0,
            "description": "適合小型店家或單一據點，靈活按需勾選樂高模組",
            "included_modules": ["智能進銷存管理", "人事組織架構管理"]
        }
    }

if "global_fx_rates" not in st.session_state:
    st.session_state.global_fx_rates = {"USD": 1.0, "TWD": 31.50, "VND": 25400.00, "RMB": 7.20}

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

DEPARTMENT_MODULE_CATALOG = {
    "👑 董事長室 / 總經理室 (Executive & Board Room)": {
        "col1": ["全局戰情室與BI分析", "高階決策審核", "營運總控台", "跨部門協調"],
        "col2": ["智能進銷存管理", "供應鏈採購比價", "倉儲物流與WMS", "供應商交期評鑑"],
        "col3": ["總帳會計與報表", "生產排程與BOM管理", "CRM客戶關係管理", "人事考勤與薪資計算"]
    },
    "👥 人力資源與行政管理部 (HR & Admin Dept)": {
        "col1": ["人事組織架構管理", "員工考勤打卡與GPS", "多國薪資與勞健保", "教育訓練與考核"],
        "col2": ["內部公告與公文簽核", "訪客預約與門禁對接", "會議室與車輛預約", "辦公用品請購申領"],
        "col3": ["AI 履歷篩選助手", "員工滿意度調查", "勞資合規資料庫", "多語言員工App"]
    },
    "💰 財務與資本運作部 (Finance Dept)": {
        "col1": ["全球資金水位管理", "應收帳款(AR)催收", "應付帳款(AP)排程", "銀行融資與LC管理"],
        "col2": ["子公司合併報表", "稅務申報與發票勾稽", "預算編列與費用控管", "資本支出(CAPEX)追蹤"],
        "col3": ["AI 異常交易預警", "電子發票與越南紅發票", "自動化傳票生成", "跨國利潤匯出分析"]
    },
    "⚙️ 工程與技術服務部 (Engineering & Technical)": {
        "col1": ["水電工程專案與預算", "工程估驗與計價請款", "工地現場點工點料", "施工日報表與工時扣減"],
        "col2": ["設備維修履歷保養", "CAD/BIM圖檔協同", "工地現場安衛查核", "外包商工班計價"],
        "col3": ["AI 工程預算超支預警", "PDA現場叫料系統", "工地物聯網(IoT)監控", "智能施工甘特圖"]
    },
    "🏭 生產製造與廠務管理部 (Manufacturing & Plant)": {
        "col1": ["MES製造執行與報工", "BOM表與用料清單", "產線排程與產能規劃", "製程SOP管理"],
        "col2": ["設備OEE稼動率預警", "模具壽命與保養維護", "產線計件薪資計算", "車間碳排與能源監控"],
        "col3": ["AI 產能瓶頸優化", "機器視覺(AI)瑕疵檢測", "AGV無人搬運車派工", "智慧產線看板"]
    }
}

if "tenants_db" not in st.session_state:
    st.session_state.tenants_db = {
        "tenant_vina_水电": {
            "name": "🇻🇳 越南平陽水電工程有限公司",
            "region": "越南 (Binh Duong, VN)",
            "plan": "🚀 旗艦版 (Enterprise)",
            "price_usd": 250,
            "expiry_date": "2027-10-20",
            "dept_modules_db": {
                "👑 董事長室 / 總經理室 (Executive & Board Room)": ["全局戰情室與BI分析", "高階決策審核"],
                "⚙️ 工程技術服務部 (Engineering & Technical)": ["水電工程專案與預算", "工程估驗與計價請款"]
            },
            "org_nodes": [
                {"id": "node_root", "name": "董事長室", "type": "👑 頂層 (Board)", "parent": "無 (頂層)"},
                {"id": "node_eng", "name": "工程技術部", "type": "⚙️ 二級部門", "parent": "董事長室"}
            ],
            "iot_devices": [{"dev_id": "DEV-01", "name": "平陽廠人臉辨識機", "type": "人臉辨識", "ip": "192.168.10.50", "status": "🟢 聯機中"}],
            "ap_invoices": [{"invoice_no": "000123", "supplier": "越南材料行", "items": "PVC管", "amount_vnd": "15,000,000", "status": "🔴 待付款"}],
            "staff": [{"name": "許福村", "email": "fuchun@vina.com", "role": "Tenant Admin"}],
            "audit_logs": [{"time": "2026-10-20 14:10:22", "user": "許福村", "action": "初始化系統", "ip": "192.168.10.2"}]
        }
    }

if "current_portal" not in st.session_state:
    st.session_state.current_portal = "Master"

# 4. 側邊欄導覽
with st.sidebar:
    st.image("https://img.icons8.com/color/96/company.png", width=64)
    st.markdown("### 🌐 SaaS 多租戶 AI-ERP 平台")
    
    lang = st.selectbox("選擇語系 / Select Language", ["繁體中文", "English", "Tiếng Việt (越南語)", "简体中文"])
    
    st.markdown("---")
    
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
            "選擇總控台模組 (Master Hub)",
            [
                "🏢 全球企業租戶動態總覽與管理 (Tenants Hub)",
                "💱 全球多幣別與即時匯率中樞 (Global FX)",
                "⚙️ 全球定價策略與方案模組自訂 (Pricing App Store)"
            ]
        )
    else:
        current_t_name = st.session_state.tenants_db[st.session_state.current_portal]["name"]
        menu_choice = st.radio(
            f"內部模組 ({current_t_name})",
            [
                "🧩 樂高積木式模組市集與功能開關 (App Store)",
                "🖱️ ProcessOn 標準組織架構圖與節點 CRUD",
                "👥 員工帳號與權限角色管理 (RBAC)",
                "🔒 系統資安稽核日誌 (Audit Trail)",
                "🤖 AI 硬體與車牌/人臉辨識掛接",
                "🇻🇳 越南紅發票與應付帳款 (AP)"
            ]
        )
    
    st.markdown("---")
    if st.button("🚪 登出系統", use_container_width=True):
        st.info("已安全登出系統。")

# 5. 主畫面邏輯路由
if st.session_state.current_portal == "Master":
    if "全球企業租戶動態總覽" in menu_choice:
        st.markdown("## 🏢 SaaS 平台總控台：全球企業租戶動態總覽與管理中心")
        st.info("💡 *在此處檢視所有企業客戶，並可直接點擊進入該公司後台協助核對組織圖！*")
        
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                search_keyword = st.text_input("🔍 搜尋公司名稱", placeholder="輸入關鍵字...")
            with s2:
                region_filter = st.selectbox("🌍 依地區位置過濾", ["全部地區", "越南 (Binh Duong, VN)", "台灣 (Taipei, TW)"])
            with s3:
                sort_by = st.selectbox("📊 排序依據", ["價格由高到低", "使用到期日最近", "公司名稱筆畫"])
            with s4:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("➕ 新增企業客戶租戶", type="primary", use_container_width=True):
                    st.success("🎉 請引導客戶透過模組市集自助註冊！")
            st.markdown('</div>', unsafe_allow_html=True)

        tenant_list_data = []
        for t_key, t_val in st.session_state.tenants_db.items():
            total_active_mods = sum(len(mods) for mods in t_val.get("dept_modules_db", {}).values())
            tenant_list_data.append({
                "租戶代碼": t_key,
                "公司名稱": t_val["name"],
                "地區位置": t_val["region"],
                "訂閱方案": t_val["plan"],
                "每月價格 (USD)": t_val["price_usd"],
                "已啟用功能數": total_active_mods,
                "狀態": "🟢 正常營運"
            })
        df_tenants = pd.DataFrame(tenant_list_data)

        if search_keyword:
            df_tenants = df_tenants[df_tenants.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False)).any(axis=1)]
        if region_filter != "全部地區":
            df_tenants = df_tenants[df_tenants["地區位置"] == region_filter]

        st.markdown("### 📋 企業租戶列表")
        st.dataframe(df_tenants, use_container_width=True)
        
        st.markdown("### 🚀 快速進入指定客戶租戶後台與組織圖核對")
        quick_cols = st.columns(len(st.session_state.tenants_db))
        for idx, (t_key, t_val) in enumerate(st.session_state.tenants_db.items()):
            with quick_cols[idx]:
                st.markdown(f"""
                    <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; margin-bottom: 10px;">
                        <b>{t_val['name']}</b><br>
                        <span style="font-size: 12px; color: gray;">{t_val['region']} | ${t_val['price_usd']}/月</span>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"📂 進入後台", key=f"btn_{t_key}", use_container_width=True):
                    st.session_state.current_portal = t_key
                    st.rerun()

    elif "全球多幣別與即時匯率引擎" in menu_choice:
        st.markdown("## 💱 SaaS 平台總控台：全球多幣別與即時匯率引擎")
        st.info("💡 維護全平台的基準匯率。")
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            with st.form("fx_form"):
                fx = st.session_state.global_fx_rates
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.number_input("美元 (USD)", value=fx["USD"], disabled=True)
                with c2: nt = st.number_input("台幣 (TWD)", value=fx["TWD"], step=0.1)
                with c3: nv = st.number_input("越南盾 (VND)", value=fx["VND"], step=10.0)
                with c4: nr = st.number_input("人民幣 (RMB)", value=fx["RMB"], step=0.01)
                if st.form_submit_button("💾 立即更新全平台即時匯率", type="primary", use_container_width=True):
                    st.session_state.global_fx_rates["TWD"] = nt
                    st.session_state.global_fx_rates["VND"] = nv
                    st.session_state.global_fx_rates["RMB"] = nr
                    st.success("🎉 匯率更新成功！")
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        # ==================== 總控台全新模組：全球定價策略與方案模組自訂 (Pricing App Store) ====================
        st.markdown("## ⚙️ SaaS 平台總控台：全球定價策略與方案模組自訂 (Pricing App Store)")
        st.info("💡 *在此處自由自訂【旗艦版】、【正式商業版】與【標準訂閱版】所包含的預設樂高模組，並直接在下方填入並鎖定方案的每月基本訂閱金額！*")
        
        plan_tabs = st.tabs(list(st.session_state.global_plans_db.keys()))
        
        all_possible_all_modules = [
            "全局戰情室與BI分析", "高階決策審核", "營運總控台", "跨部門協調",
            "智能進銷存管理", "供應鏈採購比價", "倉儲物流與WMS", "供應商交期評鑑",
            "總帳會計與報表", "生產排程與BOM管理", "CRM客戶關係管理", "人事考勤與薪資計算",
            "水電工程專案與預算", "工程估驗與計價請款", "全方位資金水位管理"
        ]
        
        for idx, (plan_name, plan_data) in enumerate(st.session_state.global_plans_db.items()):
            with plan_tabs[idx]:
                with st.form(f"form_plan_{plan_name}"):
                    st.markdown(f"### 📦 編輯方案：{plan_name}")
                    
                    p_desc = st.text_input("方案描述說明", value=plan_data["description"], key=f"desc_{plan_name}")
                    p_price = st.number_input("每月基本訂閱金額 (USD $)", value=float(plan_data["base_price"]), step=10.0, key=f"price_{plan_name}")
                    
                    st.markdown("#### 🧱 選擇此方案預設解鎖的樂高模組 (App Store 組合)")
                    
                    c_m1, c_m2 = st.columns(2)
                    selected_plan_mods = []
                    
                    half_len = len(all_possible_all_modules) // 2
                    with c_m1:
                        for mod in all_possible_all_modules[:half_len]:
                            if st.checkbox(mod, value=mod in plan_data["included_modules"], key=f"p_mod_{plan_name}_{mod}"):
                                selected_plan_mods.append(mod)
                    with c_m2:
                        for mod in all_possible_all_modules[half_len:]:
                            if st.checkbox(mod, value=mod in plan_data["included_modules"], key=f"p_mod_{plan_name}_{mod}"):
                                selected_plan_mods.append(mod)
                                
                    st.markdown("---")
                    if st.form_submit_button(f"💾 儲存【{plan_name}】定價與模組配置", type="primary", use_container_width=True):
                        st.session_state.global_plans_db[plan_name]["description"] = p_desc
                        st.session_state.global_plans_db[plan_name]["base_price"] = p_price
                        st.session_state.global_plans_db[plan_name]["included_modules"] = selected_plan_mods
                        st.success(f"🎉 成功更新 [{plan_name}] 的方案定價與模組規則！")
                        st.rerun()

else:
    # ==================== 個別租戶後台：資料庫持久化串聯模組市集與組織樹 ====================
    current_tenant = st.session_state.tenants_db[st.session_state.current_portal]
    
    if "dept_modules_db" not in current_tenant:
        current_tenant["dept_modules_db"] = {}
        
    if "樂高積木式模組市集與功能開關" in menu_choice:
        st.markdown(f"## 🧩 {current_tenant['name']}：樂高積木式模組市集與功能開關 (App Store)")
        st.info("💡 *說明：點選左側任意部門，右側會即時讀取與寫入資料庫，讓您自由勾選或組合該部門專屬的 ERP 功能模組，並即時計費！*")
        
        col_left, col_right = st.columns([1, 2.5])
        
        with col_left:
            st.markdown("### 🏢 選擇目標部門 / 管理層")
            selected_dept = st.radio(
                "部門選擇",
                ALL_ENTERPRISE_DEPARTMENTS,
                index=0,
                label_visibility="collapsed"
            )
            
        with col_right:
            clean_dept_name = selected_dept.split('(')[0].strip()
            st.markdown(f"### 🛒 【{clean_dept_name}】的資料庫模組市集 (App Store)")
            
            cat_data = DEPARTMENT_MODULE_CATALOG.get(selected_dept, {
                "col1": ["全局戰情室", "高階決策審核", "營運總控台", "跨部門協調"],
                "col2": ["智能進銷存管理", "供應鏈採購比價", "倉儲物流與WMS", "供應商交期評鑑"],
                "col3": ["總帳會計與報表", "生產排程與BOM", "CRM客戶關係管理", "人事考勤與薪資"]
            })
            
            saved_dept_mods = current_tenant["dept_modules_db"].get(selected_dept, [])
            
            with st.form(f"form_store_{selected_dept}"):
                mc1, mc2, mc3 = st.columns(3)
                curr_selected = []
                
                with mc1:
                    st.markdown("#### 📈 高階決策與行情")
                    for mod in cat_data["col1"]:
                        if st.checkbox(mod, value=mod in saved_dept_mods, key=f"m1_{selected_dept}_{mod}"):
                            curr_selected.append(mod)
                with mc2:
                    st.markdown("#### 📦 供應鏈與進銷存")
                    for mod in cat_data["col2"]:
                        if st.checkbox(mod, value=mod in saved_dept_mods, key=f"m2_{selected_dept}_{mod}"):
                            curr_selected.append(mod)
                with mc3:
                    st.markdown("#### 💰 財會與生產核心")
                    for mod in cat_data["col3"]:
                        if st.checkbox(mod, value=mod in saved_dept_mods, key=f"m3_{selected_dept}_{mod}"):
                            curr_selected.append(mod)
                            
                st.markdown("---")
                total_all_mods = sum(len(mods) for mods in current_tenant["dept_modules_db"].values())
                calculated_price = 80 + (total_all_mods * 5)
                current_tenant["price_usd"] = calculated_price
                
                st.markdown(f"### 💳 系統計費試算：當前部門選定 `{len(curr_selected)}` 項模組 ➔ 企業每月總訂閱費用：**`$ {current_tenant['price_usd']} USD`**")
                
                if st.form_submit_button(f"💾 立即寫入資料庫：儲存【{clean_dept_name}】模組配置", type="primary", use_container_width=True):
                    current_tenant["dept_modules_db"][selected_dept] = list(set(curr_selected))
                    
                    node_names = [n["name"] for n in current_tenant["org_nodes"]]
                    short_name = clean_dept_name.replace("👑", "").replace("📈", "").replace("👥", "").replace("⚖️", "").replace("🔒", "").replace("💰", "").replace("📊", "").replace("🌍", "").replace("🌐", "").replace("📢", "").replace("🤝", "").replace("🛒", "").replace("📦", "").replace("🏭", "").replace("⚙️", "").replace("🛡️", "").replace("💡", "").replace("💻", "").strip()
                    
                    if short_name not in node_names:
                        current_tenant["org_nodes"].append({
                            "id": f"node_{uuid.uuid4().hex[:8]}",
                            "name": short_name,
                            "type": selected_dept,
                            "parent": "董事長室" if "董事長室" not in short_name else "無 (頂層)"
                        })
                        
                    st.success(f"🎉 成功寫入資料庫！【{short_name}】部門及其專屬功能已永久紀錄並同步至組織架構圖。")
                    st.rerun()

    elif "ProcessOn 標準組織架構圖與節點 CRUD" in menu_choice:
        st.markdown(f"## 🖱️ {current_tenant['name']}：ProcessOn 標準組織架構圖與節點管理")
        st.info("💡 *在此處自由新增、修改或刪除公司內部組織節點，並可直接檢視每個部門在資料庫中對應啟用的功能！*")
        
        col_set, col_edit = st.columns([1, 1])
        existing_parents = [n["name"] for n in current_tenant["org_nodes"]]
        
        with col_set:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### ➕ 新增組織節點或據點 (寫入資料庫)")
            with st.form("org_add_form"):
                n_name = st.text_input("部門/據點名稱*", placeholder="例：財務部 / 台北旗艦總店")
                n_type = st.selectbox("部門層級屬性", ["👑 頂層 (Board / 董事會)", "👑 一級部門 (Headquarters)", "⚙️ 二級部門 (Functional Dept)", "🏢 三級據點/倉庫 (Branch / Warehouse)"])
                n_parent = st.selectbox("指定上級掛載點", existing_parents)
                
                if st.form_submit_button("🧱 寫入資料庫並新增節點", type="primary", use_container_width=True):
                    if n_name:
                        current_tenant["org_nodes"].append({
                            "id": f"node_{uuid.uuid4().hex[:8]}",
                            "name": n_name,
                            "type": n_type,
                            "parent": n_parent
                        })
                        st.success(f"🎉 成功寫入資料庫：新增 [{n_name}]！")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_edit:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### ✏️ 修改或刪除現有節點 (資料庫同步更新)")
            if current_tenant["org_nodes"]:
                node_options = {f"{n['name']} ({n['type']}) [ID: {n['id']}]": n for n in current_tenant["org_nodes"]}
                selected_label = st.selectbox("選擇要管理的節點", list(node_options.keys()))
                target_node = node_options[selected_label]
                
                if target_node:
                    with st.form("org_edit_form"):
                        up_name = st.text_input("修改名稱", value=target_node["name"])
                        up_parent = st.selectbox("修改上級掛載點", existing_parents, index=existing_parents.index(target_node["parent"]) if target_node["parent"] in existing_parents else 0)
                        
                        cb1, cb2 = st.columns(2)
                        with cb1:
                            sub_u = st.form_submit_button("💾 儲存修改", type="primary", use_container_width=True)
                        with cb2:
                            sub_d = st.form_submit_button("🗑️ 從資料庫刪除", type="primary", use_container_width=True)
                            
                        if sub_u:
                            target_node["name"] = up_name
                            target_node["parent"] = up_parent
                            st.success("🎉 資料庫更新成功！")
                            st.rerun()
                        if sub_d:
                            if target_node["parent"] == "無 (頂層)":
                                st.error("❌ 無法刪除頂層最高決策層！")
                            else:
                                current_tenant["org_nodes"] = [n for n in current_tenant["org_nodes"] if n["id"] != target_node["id"]]
                                st.success("🗑️ 節點已從資料庫刪除！")
                                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📊 資料庫即時組織架構與部門專屬功能總覽")
        st.info("💡 *下方即時呈現資料庫中的組織階層方塊圖，並自動帶出各部門在市集裡勾選啟用的功能模組！*")
        
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            roots = [n for n in current_tenant["org_nodes"] if n["parent"] == "無 (頂層)"]
            others = [n for n in current_tenant["org_nodes"] if n["parent"] != "無 (頂層)"]
            dept_db = current_tenant.get("dept_modules_db", {})
            
            for r in roots:
                r_mods = []
                for k, v in dept_db.items():
                    if r['name'] in k:
                        r_mods = v
                r_mods_str = ", ".join(r_mods) if r_mods else "尚未勾選模組"
                
                st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="org-root-card">
                            👑 {r['name']} <span style="font-size: 12px; font-weight: normal;">({r['type']})</span><br>
                            <span style="font-size: 11px; opacity: 0.9;">📦 啟用功能：{r_mods_str}</span>
                        </div>
                    </div>
                    <div class="tree-connector"></div>
                """, unsafe_allow_html=True)
                
                level1 = [n for n in others if n["parent"] == r["name"]]
                if level1:
                    cols1 = st.columns(len(level1))
                    for idx1, l1 in enumerate(level1):
                        with cols1[idx1]:
                            l1_mods = []
                            for k, v in dept_db.items():
                                if l1['name'] in k:
                                    l1_mods = v
                            l1_mods_str = ", ".join(l1_mods) if l1_mods else "尚未勾選模組"
                            
                            st.markdown(f"""
                                <div style="text-align: center;">
                                    <div class="org-level1-card">
                                        <b>{l1['name']}</b><br>
                                        <span style="font-size: 11px; color: gray;">{l1['type']}</span><br>
                                        <span style="font-size: 10px; color: #2563eb;">📌 功能：{l1_mods_str}</span>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    elif "員工帳號與權限角色管理" in menu_choice:
        st.markdown(f"## 👥 {current_tenant['name']}：員工帳號與權限角色管理 (RBAC)")
        st.info("💡 建立公司內部員工帳號與職務。")
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            with st.form("staff_form"):
                s_name = st.text_input("員工姓名*", placeholder="例：陳大為")
                s_email = st.text_input("電子郵件 (登入帳號)*", placeholder="例：david@company.com")
                s_role = st.selectbox("指派權限角色", ["財務與會計專員", "現場工地主任", "總務與人事專員", "採購專員", "租戶系統管理員"])
                if st.form_submit_button("👤 建立員工帳號", type="primary", use_container_width=True):
                    if s_name and s_email:
                        current_tenant["staff"].append({"name": s_name, "email": s_email, "role": s_role})
                        st.success(f"🎉 成功建立員工 [{s_name}] 並寫入資料庫！")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(current_tenant["staff"]), use_container_width=True)

    elif "資安稽核日誌" in menu_choice:
        st.markdown(f"## 🔒 {current_tenant['name']}：系統資安稽核日誌")
        st.info("💡 記錄公司內部員工操作軌跡。")
        st.dataframe(pd.DataFrame(current_tenant["audit_logs"]), use_container_width=True)

    elif "AI 硬體與車牌" in menu_choice:
        st.markdown(f"## 🤖 {current_tenant['name']}：AI 硬體與車牌/人臉辨識自助掛接")
        st.info("💡 管理公司內部的 AI 鏡頭與辨識設備。")
        if current_tenant["iot_devices"]:
            st.dataframe(pd.DataFrame(current_tenant["iot_devices"]), use_container_width=True)

    else:
        st.markdown(f"## 🇻🇳 {current_tenant['name']}：越南紅發票與應付帳款 (AP)")
        st.info("💡 在此處管理越南進項發票與應付帳款。")
        if current_tenant["ap_invoices"]:
            st.dataframe(pd.DataFrame(current_tenant["ap_invoices"]), use_container_width=True)
