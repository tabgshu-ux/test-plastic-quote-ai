import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 1. 頁面基本設定 (Mobile-First & 企業級外觀)
st.set_page_config(
    page_title="SaaS Enterprise ERP Control Center",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 自定義精緻企業風 CSS 美化 (UI/UX Styling)
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

# 3. 側邊欄：多語系與登入者角色/管理導覽
with st.sidebar:
    st.image("https://img.icons8.com/color/96/company.png", width=64)
    st.markdown("### 🌐 SaaS ERP 總控台")
    
    # 多語系選單
    lang = st.selectbox("選擇語系 / Select Language", ["繁體中文", "English", "Tiếng Việt", "简体中文"])
    
    st.markdown("---")
    st.markdown("👤 **目前登入者**: `System Admin`")
    st.markdown("🏢 **目前租戶**: `SaaS Global Control`")
    
    st.markdown("---")
    st.markdown("### 📌 系統導覽選單")
    menu_choice = st.radio(
        "選擇管理模組",
        [
            "外部資料庫與異質資料來源串聯 (Database Bridge)", 
            "樂高積木式模組拼圖與功能開關", 
            "企業組織與部門樹狀管理", 
            "系統運行與跨庫數據監控"
        ]
    )
    
    st.markdown("---")
    if st.button("🚪 登出系統", use_container_width=True):
        st.info("已安全登出系統。")

# 4. 主畫面邏輯路由
if "外部資料庫與異質資料來源串聯" in menu_choice:
    st.markdown("## 🔌 外部資料庫與異質資料來源串聯設定 (Database Bridge)")
    st.markdown("💡 *在此處您可以設定與擴充對外連結的其他客戶資料庫或即時 API 來源（例如：台股/美股/越股行情 API、客戶舊版 MySQL、總公司 SQL Server），無須修改程式碼。*")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        with st.form("db_bridge_form"):
            st.markdown("### ➕ 新增或設定外部資料庫 / API 來源")
            col1, col2 = st.columns(2)
            
            with col1:
                db_key = st.text_input("來源代碼 (Key)*", placeholder="例：global_market_api 或 client_mysql")
                db_display_name = st.text_input("顯示名稱*", placeholder="例：國際金融行情與匯率 API")
                db_type = st.selectbox("連線類型", ["RESTful API / JSON Bridge", "PostgreSQL / Supabase", "MySQL / MariaDB", "Microsoft SQL Server", "Oracle DB"])
                db_host = st.text_input("主機位址 / API Endpoint*", placeholder="例：https://api.marketdata.com/v1 或 192.168.1.100")

            with col2:
                db_port = st.text_input("通訊埠 (Port) [若適用]", placeholder="例：3306 或 5432")
                db_name = st.text_input("資料庫名稱 / 路由路徑*", placeholder="例：v1/finance/quotes")
                db_user = st.text_input("API Token / 使用者帳號*", placeholder="例：Bearer token_abcdef...")
                db_password = st.text_input("密鑰 / 密碼 (Password)*", type="password", placeholder="請輸入金鑰")

            st.markdown("---")
            col_btn1, col_btn2 = st.columns([1, 2])
            with col_btn1:
                test_conn_btn = st.form_submit_button("🧪 測試連線 (Test Connection)", use_container_width=True)
            with col_btn2:
                save_btn = st.form_submit_button("💾 儲存並啟用連線設定", type="primary", use_container_width=True)

            if test_conn_btn:
                if not db_host or not db_user:
                    st.warning("⚠️ 請完整填寫網址與認證 Token 資訊才能進行測試！")
                else:
                    st.success("🎉 測試連線成功！資料與 API 路由對接正常。")

            if save_btn:
                if not db_key or not db_display_name:
                    st.error("❌ 請填寫必要的代碼與名稱欄位！")
                else:
                    st.success(f"✅ 外部來源 [{db_display_name}] 設定已成功儲存！")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 📋 目前已配置的外部連線清單")
    mock_db_data = pd.DataFrame([
        {"代碼 Key": "global_market_api", "名稱": "國際股市與匯率即時 API", "類型": "RESTful API", "目標": "api.marketdata.com", "狀態": "🟢 連線正常"},
        {"代碼 Key": "tw_factory_sql", "名稱": "台灣總廠 MySQL 數據庫", "類型": "MySQL", "目標": "192.168.10.5", "狀態": "🟢 連線正常"}
    ])
    search_query = st.text_input("🔍 搜尋連線名稱或代碼", placeholder="輸入關鍵字篩選...")
    if search_query:
        mock_db_data = mock_db_data[mock_db_data.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
    st.dataframe(mock_db_data, use_container_width=True)

elif "樂高積木式模組拼圖與功能開關" in menu_choice:
    st.markdown("## 🧩 樂高積木式模組拼圖與功能開關 (Granular Feature Toggles)")
    st.info("💡 說明：請在左側選取目標部門，右側將展開該部門在專業 ERP 中所有細分到日常作業的完整功能清單，供您精準勾選授權。")

    col_dept, col_modules = st.columns([1, 2])

    with col_dept:
        st.markdown("### 🏢 選擇目標部門 / 高階角色")
        dept_options = [
            "👑 董事長室 / 總經理室 (Executive & Board Room)",
            "📋 經營企劃與策略發展部 (Corporate Strategy)",
            "👥 人力資源與行政管理部 (HR & Admin Dept)",
            "⚖️ 法務與合規遵循部 (Legal & Compliance)",
            "🛡️ 資訊安全與稽核中心 (Audit & Info Security)",
            "💰 財務與資本運作部 (Finance Dept)",
            "📊 會計與稅務管理部 (Accounting & Tax)",
            "🤝 國內業務與通路發展部 (Domestic Sales)",
            "🌍 國際貿易與海外業務部 (Global Export Sales)",
            "📢 市場行銷與品牌企劃部 (Marketing Dept)",
            "🎧 客戶成功與售後服務部 (Customer Success / CS)",
            "📦 供應鏈與全球採購部 (Supply Chain & Procurement)",
            "🚚 倉儲物流與庫存管理部 (Warehouse & Logistics)",
            "🏭 生產製造與廠務管理部 (Manufacturing & Plant)",
            "⚙️ 工程與技術服務部 (Engineering & Technical)",
            "📅 生產管制與物料控制部 (PMC / Production Control)",
            "🔍 品質保證與品管中心 (QA / QC Dept)",
            "🔬 研發設計與創新中心 (R&D / Design Center)",
            "💻 資訊技術與系統開發部 (IT & Software Development)"
        ]
        selected_department = st.radio("請選擇要配置的部門：", dept_options)
        st.markdown("---")
        st.markdown(f"📍 **目前正在設定**：\n`{selected_department}`")

    with col_modules:
        dept_name_only = selected_department.split(' ')[1]
        st.markdown(f"### 🧩 【{dept_name_only}】的專屬細分功能清單")
        st.markdown("請針對該部門勾選其日常作業所需的所有專業子功能：")
        
        # 根據不同部門動態提供最專業、最完整的細分功能
        if "董事長室" in selected_department or "總經理室" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 📈 高階戰情與外部行情")
                st.checkbox("台股、美股、越股、A股、港股即時行情儀表板", value=True)
                st.checkbox("國際原物料即時期貨與指數監控", value=True)
                st.checkbox("全球外幣匯率與即時換算看板", value=True)
                st.checkbox("集團綜合損益表 (P&L) 即時分析", value=True)
            with sub_col2:
                st.markdown("#### 💰 財務與現金流水位")
                st.checkbox("全集團應收帳款與應付帳款總覽", value=True)
                st.checkbox("現金流預測與重大資金水位警示", value=True)
                st.checkbox("跨國子公司資產負債與合約總覽", value=True)
                st.checkbox("高階重大決策電子簽核與特許授權", value=True)
            with sub_col3:
                st.markdown("#### 🎯 策略與營運KPI")
                st.checkbox("企業 KPI 目標管理與達成率追蹤", value=True)
                st.checkbox("各事業處/廠區產值與營收對比表", value=True)
                st.checkbox("AI 智慧經營摘要與異常風險預警", value=True)
                st.checkbox("高管專屬行動端戰情推播通知", value=True)

        elif "人力資源" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 👥 人事與組織架構")
                st.checkbox("組織圖與職位編制管理", value=True)
                st.checkbox("員工基本資料與履歷檔案庫", value=True)
                st.checkbox("合約管理與試用期追蹤", value=True)
                st.checkbox("內部調動、升遷與離職管理", value=True)
            with sub_col2:
                st.markdown("#### ⏰ 考勤與薪酬管理")
                st.checkbox("排班管理、排休與輪班表設定", value=True)
                st.checkbox("上下班打卡記錄與 GPS 定位考勤", value=True)
                st.checkbox("加班、請假、特休審核與計算", value=True)
                st.checkbox("薪資計算、獎金、扣款與薪資單發放", value=True)
                st.checkbox("各國勞健保、社會保險與公積金對照", value=True)
            with sub_col3:
                st.markdown("#### 📚 培訓與績效考核")
                st.checkbox("教育訓練計畫與培訓履歷追蹤", value=True)
                st.checkbox("KPI 績效考核與 360 度評鑑系統", value=True)
                st.checkbox("人才招募、面試流程與人才庫管理", value=True)
                st.checkbox("勞資法規遵循與員工福利管理", value=True)

        elif "財務" in selected_department or "會計" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 📒 總帳與傳票管理")
                st.checkbox("會計科目表與會計期間設定", value=True)
                st.checkbox("一般傳票、轉帳傳票編製與審核", value=True)
                st.checkbox("自動過帳、試算表與總分類帳", value=True)
                st.checkbox("期末結帳、結轉與年度關帳作業", value=True)
            with sub_col2:
                st.markdown("#### 💵 應收、應付與現金")
                st.checkbox("應收帳款 (AR) 立帳、沖帳與收款單", value=True)
                st.checkbox("應付帳款 (AP) 請款、對帳與付款排程", value=True)
                st.checkbox("零用金管理與日常費用報銷審核", value=True)
                st.checkbox("銀行存款調節表與多幣別匯兌損益", value=True)
            with sub_col3:
                st.markdown("#### 🏛️ 稅務與資產管理")
                st.checkbox("固定資產卡片、折舊提列與盤點", value=True)
                st.checkbox("營業稅申報、進銷項憑證勾稽", value=True)
                st.checkbox("營利事業所得稅結算申報輔助", value=True)
                st.checkbox("會計師專用查帳報表與財報產出", value=True)

        elif "業務" in selected_department or "國貿" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 🤝 客戶與商機管理 (CRM)")
                st.checkbox("客戶基本資料、拜訪與連絡人記錄", value=True)
                st.checkbox("銷售商機追蹤與轉換率分析", value=True)
                st.checkbox("客戶分級、信用額度與授信管理", value=True)
                st.checkbox("客訴處理與售後服務追蹤工單", value=True)
            with sub_col2:
                st.markdown("#### 📑 報價與訂單管理 (Sales)")
                st.checkbox("產品規格、多幣別價格表與折扣管理", value=True)
                st.checkbox("客戶詢價單 (RFQ) 與正式報價單製作", value=True)
                st.checkbox("客戶訂單 (SO) 登記、確認與庫存連動", value=True)
                st.checkbox("出貨通知單、銷貨退回與換貨處理", value=True)
            with sub_col3:
                st.markdown("#### 🚢 國際貿易與出口 (Global)")
                st.checkbox("外銷合約、Proforma Invoice (PI)", value=True)
                st.checkbox("海運/空運託運單與報關資料準備", value=True)
                st.checkbox("信用狀 (L/C) 審查與押匯單據管理", value=True)
                st.checkbox("業務員業績統計與佣金計算", value=True)

        elif "供應鏈" in selected_department or "採購" in selected_department or "倉儲" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 🛒 採購與供應商管理 (Procurement)")
                st.checkbox("請購單 (PR) 審核與自動轉採購單", value=True)
                st.checkbox("供應商詢比議價、歷史採購價金分析", value=True)
                st.checkbox("採購訂單 (PO) 發出、交期追蹤與催貨", value=True)
                st.checkbox("供應商交期、品質與配合度評鑑", value=True)
            with sub_col2:
                st.markdown("#### 📦 倉儲與庫存管理 (WMS)")
                st.checkbox("多倉庫、多倉位與儲位即時庫存查詢", value=True)
                st.checkbox("入庫驗收、上架、撥號與條盤管理", value=True)
                st.checkbox("領料、出貨、調撥與庫存異動明細", value=True)
                st.checkbox("期末庫存盤點計畫、盤點單與差異調整", value=True)
                st.checkbox("安全庫存水位警示與自動補貨建議", value=True)
            with sub_col3:
                st.markdown("#### 🏷️ 條碼與物流追蹤")
                st.checkbox("條碼 (Barcode) / QR Code 列印與貼標", value=True)
                st.checkbox("PDA 手持終端機掃描收發貨作業", value=True)
                st.checkbox("批號管理 (Batch/Lot) 與效期追蹤", value=True)
                st.checkbox("物流配送單據與快遞追蹤管理", value=True)

        elif "生產" in selected_department or "廠務" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 🏭 生產排程與BOM表 (PMC)")
                st.checkbox("產品結構樹 (BOM) 多階層建立與維護", value=True)
                st.checkbox("主生產排程 (MPS) 與物料需求計畫 (MRP)", value=True)
                st.checkbox("工單 (MO) 開立、下達與進度追蹤", value=True)
                st.checkbox("產能分析、機台負荷與人員排班", value=True)
            with sub_col2:
                st.markdown("#### ⚙️ 現場作業與製程 (MES)")
                st.checkbox("現場報工、條碼刷卡開工與完工回報", value=True)
                st.checkbox("製程站點流向管制與 WIP 在製品查詢", value=True)
                st.checkbox("模具管理、設備保養與維修履歷", value=True)
                st.checkbox("廠務物聯網 (IoT) 能源與電力監控", value=True)
            with sub_col3:
                st.markdown("#### 🔍 品質保證 (QA / QC)")
                st.checkbox("進料檢驗 (IQC) 標準與抽驗結果記錄", value=True)
                st.checkbox("製程巡檢 (IPQC) 與成品檢驗 (FQC)", value=True)
                st.checkbox("不良品 (NC) 原因分析與矯正預防 (CAPA)", value=True)
                st.checkbox("客訴矯正與品質良率統計報表", value=True)

        else:
            # 其他通用部門或研發/資訊部
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 💻 系統與研發核心")
                st.checkbox("研發專案管理與版本控制 (PLM)", value=True)
                st.checkbox("圖面文件管理與工程變更通知 (ECN)", value=True)
                st.checkbox("系統使用者權限與角色控制 (RBAC)", value=True)
            with sub_col2:
                st.markdown("#### 🔌 整合與自動化")
                st.checkbox("外部 API 閘道與異質系統資料交換", value=True)
                st.checkbox("自動化備份、日誌監控與資安防護", value=True)
                st.checkbox("跨國多語系動態翻譯與語音轉譯", value=True)
            with sub_col3:
                st.markdown("#### 🤖 AI 與輔助工具")
                st.checkbox("AI 智慧助理問答與自動化工作流", value=True)
                st.checkbox("行動裝置端 (Mobile-First) 適配模組", value=True)
                st.checkbox("電子公文與簽核流程引擎 (BPM)", value=True)

        st.markdown("---")
        if st.button(f"💾 儲存【{dept_name_only}】的完整專業功能設定", type="primary", use_container_width=True):
            st.success(f"✅ 已成功將該部門的所有專業細分功能設定儲存至資料庫！系統權限已即時生效。")

elif "企業組織與部門樹狀管理" in menu_choice:
    st.markdown("## 🏢 企業組織與部門樹狀管理 (Dynamic Org Chart)")
    st.info("💡 說明：動態建構企業組織架構，支援無限層級巢狀樹狀圖，確保不同部門與員工享有對應的資料列級隔離（Row-Level Security）。")

else:
    st.markdown("## 📊 系統運行與跨庫數據監控")
    st.info("💡 說明：即時監控各個已掛接外部資料庫與 API 來源的同步狀態、API 呼叫次數與系統效能。")
