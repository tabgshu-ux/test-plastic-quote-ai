import streamlit as st
import pandas as pd
from datetime import datetime

# ==============================================================================
# 🧩 SaaS 企業級多租戶 AI-ERP 系統 (全功能部門與樂高模組市集 App Store)
# ==============================================================================

st.set_page_config(
    page_title="SaaS Enterprise Modular AI-ERP & Feature App Store",
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
    </style>
""", unsafe_allow_html=True)

# 3. 初始化全域資料
if "global_pricing" not in st.session_state:
    st.session_state.global_pricing = {"base_fee": 150, "module_fee": 15}

if "global_fx_rates" not in st.session_state:
    st.session_state.global_fx_rates = {"USD": 1.0, "TWD": 31.50, "VND": 25400.00, "RMB": 7.20}

# 市面上所有企業主流部門清單
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

# 各部門對應的模組市集大合集
DEPARTMENT_MODULE_CATALOG = {
    "👑 董事長室 / 總經理室 (Executive & Board Room)": {
        "col1": ["全球原物料即時行情看板", "國際匯率多幣別換算中心", "全球股市財經大盤監控", "綜合損益表與資產負債表", "企業 KPI 與多維度 BI 戰情室"],
        "col2": ["智能進銷存與批號效期管理", "全球供應鏈採購比價系統", "倉儲物流與條碼掃描(WMS)", "供應商交期與品質評鑑系統", "進出口報關與海運物流追蹤", "條碼/QR Code與資產標籤列印"],
        "col3": ["總帳會計、傳票與會計師報表", "生產排程、BOM表與製程智考", "CRM 客戶關係與外貿商機管理", "人事薪酬、勞健保與考勤排班", "電子簽核流程引擎 (BPM)", "AI 智慧語音助理與跨國翻譯"]
    },
    "👥 人力資源與行政管理部 (HR & Admin Dept)": {
        "col1": ["人事組織架構與編制管理", "員工考勤打卡與GPS定位管理", "多國薪資計算與勞健保投保", "教育訓練與考核績效追蹤", "辦公資產與福委會管理系統"],
        "col2": ["內部公告與員工公文簽核", "訪客預約與門禁人臉辨識對接", "會議室與公司車輛預約系統", "辦公用品請購與庫存申領", "勞安衛檢查與教育訓練紀錄"],
        "col3": ["AI 履歷篩選與面試排程助手", "員工滿意度調查與離職分析", "法規合規與勞資糾紛預防資料庫", "多語言員工自助服務 App 介面", "跨國簽證與外籍員工管理"]
    },
    "💰 財務與資本運作部 (Finance Dept)": {
        "col1": ["全球多幣別資金水位管理", "應收帳款(AR)與催收追蹤", "應付帳款(AP)與付款排程", "銀行融資與信用狀(LC)管理", "現金流量預測與財報分析模型"],
        "col2": ["各子公司損益合併報表", "稅務申報試算與發票勾稽", "預算編列與部門費用控管", "資本支出(CAPEX)審核追蹤", "企業投資與資產配置戰情室"],
        "col3": ["AI 異常財務交易自動預警", "電子發票與越南紅發票整合", "區塊鏈供應鏈金融融資對接", "自動化傳票生成與會計勾稽", "跨國利潤匯出與稅務合規分析"]
    },
    "⚙️ 工程與技術服務部 (Engineering & Technical)": {
        "col1": ["水電工程專案與工項預算編號", "工程估驗與計價請款追蹤", "工地現場點工點料管理", "施工日報表與工時扣減聯動", "工程合約與外包商管理"],
        "col2": ["設備維修履歷與保養排程", "CAD/BIM 圖檔雲端協同檢視", "工地現場安衛與檢驗查核", "工程材料進場驗收與檢驗", "外包商工班計價與應付帳款"],
        "col3": ["AI 工程預算超支自動預警", "行動裝置 PDA 現場叫料系統", "工程現場物聯網(IoT)設備監控", "多國工程技術文件資料庫", "智能施工進度甘特圖與排程"]
    },
    "🏭 生產製造與廠務管理部 (Manufacturing & Plant)": {
        "col1": ["MES 製造執行系統與動態報工", "BOM 表與多階用料清單管理", "產線排程與機台產能規劃", "製程工藝與標準作業程序(SOP)", "廠內在製品(WIP)即時追蹤"],
        "col2": ["設備 OEE 稼動率與故障預警", "模具壽命與保養維護管理", "產線人員績效與計件薪資計算", "車間能源消耗與碳排監控", "製程異常與不良品追蹤處理"],
        "col3": ["AI 產能瓶頸自動優化建議", "機器視覺(AI)瑕疵檢測對接", "AGV 無人搬運車派工整合", "智慧燈號與大螢幕產線看板", "多工廠產能平衡調度系統"]
    }
}

if "tenants_db" not in st.session_state:
    st.session_state.tenants_db = {
        "tenant_vina_水电": {
            "name": "🇻🇳 越南平陽水電工程有限公司",
            "region": "越南 (Binh Duong, VN)",
            "plan": "旗艦版 (Enterprise)",
            "price_usd": 170,
            "expiry_date": "2027-10-20",
            "active_department": "👑 董事長室 / 總經理室 (Executive & Board Room)",
            "enabled_modules": ["全球原物料即時行情看板", "國際匯率多幣別換算中心", "水電工程專案與工項預算編號", "工程估驗與計價請款追蹤"],
            "org_nodes": [{"id": "n_1", "name": "董事長室", "type": "👑 董事會", "parent": "無 (頂層)"}],
            "iot_devices": [{"dev_id": "DEV-01", "name": "平陽廠人臉辨識機", "type": "人臉辨識", "ip": "192.168.10.50", "status": "🟢 聯機中"}],
            "ap_invoices": [{"invoice_no": "000123", "supplier": "越南材料行", "items": "PVC管", "amount_vnd": "15,000,000", "status": "🔴 待付款"}],
            "staff": [{"name": "許福村", "email": "fuchun@vina.com", "role": "Tenant Admin"}],
            "audit_logs": [{"time": "2026-10-20 14:10:22", "user": "許福村", "action": "初始化系統", "ip": "192.168.10.2"}]
        },
        "tenant_taipei_wash": {
            "name": "🇹🇼 台北極速智慧洗車坊",
            "region": "台灣 (Taipei, TW)",
            "plan": "標準版 (Standard)",
            "price_usd": 80,
            "expiry_date": "2026-11-05",
            "active_department": "👥 人力資源與行政管理部 (HR & Admin Dept)",
            "enabled_modules": ["人事組織架構與編制管理", "員工考勤打卡與GPS定位管理"],
            "org_nodes": [{"id": "w_1", "name": "董事長室", "type": "👑 董事會", "parent": "無 (頂層)"}],
            "iot_devices": [{"dev_id": "W-01", "name": "車牌辨識 (ANPR)", "type": "車牌辨識", "ip": "10.0.0.15", "status": "🟢 運作中"}],
            "ap_invoices": [],
            "staff": [{"name": "張店長", "email": "manager@wash.com", "role": "Tenant Admin"}],
            "audit_logs": [{"time": "2026-10-19 10:00:00", "user": "張店長", "action": "初始化系統", "ip": "1.2.3.4"}]
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
    
    st.markdown("---
    st.markdown("### 📌 系統導覽選單")
    
    if st.session_state.current_portal == "Master":
        menu_choice = st.radio(
            "選擇總控台模組 (Master Hub)",
            [
                "🏢 全球企業租戶動態總覽與管理 (Tenants Hub)",
                "💱 全球多幣別與即時匯率中樞 (Global FX)",
                "⚙️ 全球定價策略與費率自訂 (Pricing)"
            ]
        )
    else:
        current_t_name = st.session_state.tenants_db[st.session_state.current_portal]["name"]
        menu_choice = st.radio(
            f"內部模組 ({current_t_name})",
            [
                "🧩 樂高積木式模組拼圖與功能開關 (App Store)",
                "🖱️ 企業組織與部門階層圖管理",
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
        st.info("💡 *在此處檢視所有企業客戶，並可直接點擊進入該公司後台協助核對與管理！*")
        
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
            tenant_list_data.append({
                "租戶代碼": t_key,
                "公司名稱": t_val["name"],
                "地區位置": t_val["region"],
                "訂閱方案": t_val["plan"],
                "每月價格 (USD)": t_val["price_usd"],
                "啟用部門數": 1,
                "啟用功能數": len(t_val.get("enabled_modules", [])),
                "狀態": "🟢 正常營運"
            })
        df_tenants = pd.DataFrame(tenant_list_data)

        if search_keyword:
            df_tenants = df_tenants[df_tenants.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False)).any(axis=1)]
        if region_filter != "全部地區":
            df_tenants = df_tenants[df_tenants["地區位置"] == region_filter]

        st.markdown("### 📋 企業租戶列表")
        st.dataframe(df_tenants, use_container_width=True)
        
        st.markdown("### 🚀 快速進入指定客戶租戶後台與模組市集")
        quick_cols = st.columns(len(st.session_state.tenants_db))
        for idx, (t_key, t_val) in enumerate(st.session_state.tenants_db.items()):
            with quick_cols[idx]:
                st.markdown(f"""
                    <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; margin-bottom: 10px;">
                        <b>{t_val['name']}</b><br>
                        <span style="font-size: 12px; color: gray;">{t_val['region']} | ${t_val['price_usd']}/月</span>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"📂 進入模組市集", key=f"btn_{t_key}", use_container_width=True):
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
        st.markdown("## ⚙️ SaaS 平台總控台：全球定價策略與費率自訂")
        st.info("設定全平台的方案月費與部門加購價。")

else:
    # ==================== 個別租戶後台：樂高積木式模組拼圖市集 (App Store) ====================
    current_tenant = st.session_state.tenants_db[st.session_state.current_portal]
    
    if "樂高積木式模組拼圖與功能開關" in menu_choice:
        st.markdown(f"## 🧩 {current_tenant['name']}：樂高積木式模組拼圖與功能開關 (App Store)")
        st.info("💡 *說明：此展示系統【全功能模組大合集】。您可以點選左側任意部門，並自由勾選或組合市面上所有企業管理、高階決策、財會與供應鏈所需的完整模組拼圖。*")
        
        col_left, col_right = st.columns([1, 2.5])
        
        with col_left:
            st.markdown("### 🏢 選擇目標部門 / 管理層")
            st.markdown("<span style='font-size: 13px; color: gray;'>請點選要配置的部門：</span>", unsafe_allow_html=True)
            
            # 使用 radio 讓租戶點選左側部門
            selected_dept = st.radio(
                "部門選擇",
                ALL_ENTERPRISE_DEPARTMENTS,
                index=ALL_ENTERPRISE_DEPARTMENTS.index(current_tenant.get("active_department", ALL_ENTERPRISE_DEPARTMENTS[0])) if current_tenant.get("active_department") in ALL_ENTERPRISE_DEPARTMENTS else 0,
                label_visibility="collapsed"
            )
            current_tenant["active_department"] = selected_dept
            
        with col_right:
            st.markdown(f"### 🛒 【{selected_dept.split('(')[0].strip()}】的企業全功能模組市集 (App Store)")
            st.markdown("<span style='font-size: 13px; color: gray;'>頻勾選此部門/高階角色可解鎖啟用的所有功能與價情儀表板：</span>", unsafe_allow_html=True)
            
            # 取得當前部門對應的模組清單，若不在預設字典則給予通用模組
            cat_data = DEPARTMENT_MODULE_CATALOG.get(selected_dept, {
                "col1": ["全局戰情室", "高階決策審核", "營運總控台", "跨部門協調", "督導管理"],
                "col2": ["進銷存與批號效期管理", "供應鏈採購比價系統", "倉儲物流與條碼掃描(WMS)", "供應商交期與品質評鑑", "進出口報關與海運追蹤"],
                "col3": ["總帳會計與報表", "生產排程與BOM管理", "CRM客戶關係與商機管理", "人事考勤與薪資計算", "電子簽核流程引擎(BPM)"]
            })
            
            if "enabled_modules" not in current_tenant:
                current_tenant["enabled_modules"] = []
                
            with st.form("module_appstore_form"):
                mc1, mc2, mc3 = st.columns(3)
                
                new_selected_mods = []
                
                with mc1:
                    st.markdown("#### 📈 高階決策與即時行情")
                    for mod in cat_data["col1"]:
                        is_checked = st.checkbox(mod, value=mod in current_tenant["enabled_modules"], key=f"mod_{mod}")
                        if is_checked:
                            new_selected_mods.append(mod)
                            
                with mc2:
                    st.markdown("#### 📦 供應鏈與進銷存 (SCM)")
                    for mod in cat_data["col2"]:
                        is_checked = st.checkbox(mod, value=mod in current_tenant["enabled_modules"], key=f"mod_{mod}")
                        if is_checked:
                            new_selected_mods.append(mod)
                            
                with mc3:
                    st.markdown("#### 💰 財會、生產與其他核心")
                    for mod in cat_data["col3"]:
                        is_checked = st.checkbox(mod, value=mod in current_tenant["enabled_modules"], key=f"mod_{mod}")
                        if is_checked:
                            new_selected_mods.append(mod)
                            
                st.markdown("---")
                
                # 計算動態價格
                total_mods_count = len(set(new_selected_mods))
                calculated_price = 80 + (total_mods_count * 5)
                current_tenant["price_usd"] = calculated_price
                
                st.markdown(f"### 💳 目前配置計費試算：已選定 `{total_mods_count}` 項模組 ➔ 預估每月總訂閱費用：**`$ {calculated_price} USD`**")
                
                if st.form_submit_button(f"💾 儲存【{selected_dept.split('(')[0].strip()}】的全功能拼圖圈定", type="primary", use_container_width=True):
                    current_tenant["enabled_modules"] = list(set(new_selected_mods))
                    st.success(f"🎉 成功儲存 [{selected_dept.split('(')[0].strip()}] 的模組拼圖設定！當前總月費更新為 ${calculated_price} USD。")
                    st.rerun()

    elif "企業組織與部門階層圖管理" in menu_choice:
        st.markdown(f"## 🖱️ {current_tenant['name']}：企業組織與部門階層圖管理")
        st.info("💡 在此處檢視與管理您公司的組織架構圖與節點掛載。")
        if current_tenant["org_nodes"]:
            st.dataframe(pd.DataFrame(current_tenant["org_nodes"]), use_container_width=True)

    elif "員工帳號與權限角色管理" in menu_choice:
        st.markdown(f"## 👥 {current_tenant['name']}：員工帳號與權限角色管理 (RBAC)")
        st.info("💡 建立公司內部員工帳號與職務。")
        if current_tenant["staff"]:
            st.dataframe(pd.DataFrame(current_tenant["staff"]), use_container_width=True)

    elif "系統資安稽核日誌" in menu_choice:
        st.markdown(f"## 🔒 {current_tenant['name']}：系統資安稽核日誌")
        st.info("💡 記錄公司內部員工操作軌跡。")
        if current_tenant["audit_logs"]:
            st.dataframe(pd.DataFrame(current_tenant["audit_logs"]), use_container_width=True)

    elif "AI 硬體與車牌" in menu_choice:
        st.markdown(f"## 🤖 {current_tenant['name']}：AI 硬體與車牌/人臉辨識自助掛接")
        if current_tenant["iot_devices"]:
            st.dataframe(pd.DataFrame(current_tenant["iot_devices"]), use_container_width=True)

    else:
        st.markdown(f"## 🇻🇳 {current_tenant['name']}：越南紅發票與應付帳款 (AP)")
        st.info("💡 在此處管理越南進項發票與應付帳款。")
        if current_tenant["ap_invoices"]:
            st.dataframe(pd.DataFrame(current_tenant["ap_invoices"]), use_container_width=True)
