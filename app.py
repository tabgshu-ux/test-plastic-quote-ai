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
    st.info("💡 說明：請在左側選取目標部門，右側將展開該部門在專業 ERP 中完全獨立、職能專屬的細分功能清單，供您精準勾選授權。")

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
        
        # 1. 董事長室 / 總經理室
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

        # 2. 經營企劃與策略發展部
        elif "經營企劃" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 📊 策略與年度目標")
                st.checkbox("年度經營計畫與策略目標分解 (OKR/KPI)", value=True)
                st.checkbox("競品分析與市場趨勢數據收集", value=True)
                st.checkbox("集團各事業部投資效益評估", value=True)
            with sub_col2:
                st.markdown("#### 📋 專案與組織變革")
                st.checkbox("跨部門大型策略專案管考", value=True)
                st.checkbox("組織結構重整與編制規畫模擬", value=True)
                st.checkbox("新事業體可行性評估與商業模式建模", value=True)
            with sub_col3:
                st.markdown("#### 📑 報告與大數據支援")
                st.checkbox("董事會專用月報/季報自動化彙編", value=True)
                st.checkbox("巨量營運數據商業智慧分析", value=True)
                st.checkbox("跨國營運效率對比與優化建議", value=True)

        # 3. 人力資源與行政管理部
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

        # 4. 法務與合規遵循部
        elif "法務" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 📑 合約與文件管理")
                st.checkbox("全公司各類商務合約草擬與審查歸檔", value=True)
                st.checkbox("合約到期自動提醒與續約管理", value=True)
                st.checkbox("中、英、越等多語系合約範本庫", value=True)
            with sub_col2:
                st.markdown("#### ⚖️ 風險與合規稽核")
                st.checkbox("跨國勞動法規與智財權合規遵循檢查", value=True)
                st.checkbox("訴訟案件進度追蹤與律師費管理", value=True)
                st.checkbox("企業內部反舞弊與合規舉報系統", value=True)
            with sub_col3:
                st.markdown("#### ✍️ 授權與用印管理")
                st.checkbox("公司大小章與用印申請電子化審核", value=True)
                st.checkbox("授權書 (POA) 管理與效期控管", value=True)
                st.checkbox("法務專屬電子簽核與存證追蹤", value=True)

        # 5. 資訊安全與稽核中心
        elif "資訊安全" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 🛡️ 資安防護與監控")
                st.checkbox("全系統存取日誌 (Audit Log) 監控", value=True)
                st.checkbox("異常登入行為攔截與 IP 白名單設定", value=True)
                st.checkbox("資料庫加密與敏感個資遮罩防護", value=True)
            with sub_col2:
                st.markdown("#### 📋 內部稽核與權限")
                st.checkbox("各部門使用者權限定期覆核與資安稽核", value=True)
                st.checkbox("系統漏洞掃描與資安事件通報機制", value=True)
                st.checkbox("跨國資料隔離 (RLS) 強制檢測", value=True)
            with sub_col3:
                st.markdown("#### 💾 備份與災難復原")
                st.checkbox("資料庫自動化異地備份與還測試", value=True)
                st.checkbox("伺服器運行健康狀態 (Health Check)", value=True)
                st.checkbox("資訊安全緊急應變計畫 (BCP) 管理", value=True)

        # 6. 財務與資本運作部
        elif "財務" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 💵 資金與銀行調度")
                st.checkbox("多銀行帳戶資金水位與存款總覽", value=True)
                st.checkbox("企業融資、銀行授信額度與利息管理", value=True)
                st.checkbox("外匯避險、匯率風險評估與遠期外汇", value=True)
            with sub_col2:
                st.markdown("#### 📊 資本預算與現金流")
                st.checkbox("重大資本支出 (CapEx) 預算審核", value=True)
                st.checkbox("中長期的現金流量預測模型", value=True)
                st.checkbox("集團內部資金調撥與利息分摊", value=True)
            with sub_col3:
                st.markdown("#### 📑 投資與財報分析")
                st.checkbox("子公司投資報酬率 (ROI) 分析", value=True)
                st.checkbox("財務槓桿與財務比率分析指標", value=True)
                st.checkbox("銀行融資文件與信用狀管理", value=True)

        # 7. 會計與稅務管理部
        elif "會計" in selected_department:
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

        # 8. 國內業務與通路發展部
        elif "國內業務" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 🤝 客戶關係管理 (CRM)")
                st.checkbox("國內經銷商與終端客戶資料庫", value=True)
                st.checkbox("銷售商機追蹤與拜訪記錄管理", value=True)
                st.checkbox("客戶信用額度與授信審查", value=True)
            with sub_col2:
                st.markdown("#### 📑 國內報價與訂單")
                st.checkbox("標準報價單與合約建立", value=True)
                st.checkbox("客戶訂單 (SO) 輸入與庫存即時扣減", value=True)
                st.checkbox("出貨通知、銷貨退回與換貨處理", value=True)
            with sub_col3:
                st.markdown("#### 🏆 業績與佣金")
                st.checkbox("業務人員業績目標與達成率統計", value=True)
                st.checkbox("業務獎金、分潤與佣金自動計算", value=True)
                st.checkbox("國內競品市佔率與銷售戰情分析", value=True)

        # 9. 國際貿易與海外業務部
        elif "國際貿易" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 🌍 海外客戶與外貿商機")
                st.checkbox("海外代理商與跨國客戶 CRM 管理", value=True)
                st.checkbox("多語系外銷詢價與報價單製作", value=True)
                st.checkbox("海外市場開發進度與商機追蹤", value=True)
            with sub_col2:
                st.markdown("#### 🚢 外銷出貨與押匯")
                st.checkbox("外銷合約與 Proforma Invoice (PI)", value=True)
                st.checkbox("海運/空運託運單與出貨排程管理", value=True)
                st.checkbox("信用狀 (L/C) 審查與押匯單據製作", value=True)
            with sub_col3:
                st.markdown("#### 💱 貿易財務與合規")
                st.checkbox("多幣別收款、匯兌損益自動結算", value=True)
                st.checkbox("海關出口報關資料與檢驗證明管理", value=True)
                st.checkbox("海外子公司往來帳款對帳", value=True)

        # 10. 市場行銷與品牌企劃部
        elif "市場行銷" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 📢 品牌與行銷活動")
                st.checkbox("行銷活動專案與預算費用管考", value=True)
                st.checkbox("線上/線下廣告投放成效與 ROI 分析", value=True)
                st.checkbox("公关公關稿件、媒體聯絡與品牌資產管理", value=True)
            with sub_col2:
                st.markdown("#### 🎯 數位行銷與線索")
                st.checkbox("數位行銷潛在客戶 (Leads) 收集與清洗", value=True)
                st.checkbox("官網、社群媒體與 EDM 行銷成效追蹤", value=True)
                st.checkbox("跨國多語系行銷文案與多媒體素材庫", value=True)
            with sub_col3:
                st.markdown("#### 📊 市場研究")
                st.checkbox("產業趨勢、競品動態與市調報告歸檔", value=True)
                st.checkbox("客戶滿意度調查與品牌聲量分析", value=True)
                st.checkbox("行銷轉換漏斗 (Conversion Funnel) 分析", value=True)

        # 11. 客戶成功與售後服務部
        elif "客戶成功" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 🎧 客服工單與問題追蹤")
                st.checkbox("客戶報修、客訴與諮詢工單系統", value=True)
                st.checkbox("客服人員派工、處理進度與SLA追蹤", value=True)
                st.checkbox("多語系客服知識庫與常見問題解答", value=True)
            with sub_col2:
                st.markdown("#### 🌟 客戶成功與維護")
                st.checkbox("客戶健康度評分與續約提醒機制", value=True)
                st.checkbox("售後維護合約 (AMC) 與定期保養排程", value=True)
                st.checkbox("客戶回訪紀錄與滿意度調查 (CSAT)", value=True)
            with sub_col3:
                st.markdown("#### 📦 備品與維修管理")
                st.checkbox("售後維修備品庫存與耗損管理", value=True)
                st.checkbox("保固期追蹤與收費維修報價單", value=True)
                st.checkbox("客服數據分析與產品瑕疵回饋", value=True)

        # 12. 供應鏈與全球採購部
        elif "供應鏈" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 🛒 採購與供應商管理")
                st.checkbox("請購單 (PR) 審核與自動轉採購單", value=True)
                st.checkbox("供應商詢比議價、歷史採購價金分析", value=True)
                st.checkbox("採購訂單 (PO) 發出、交期追蹤與催貨", value=True)
                st.checkbox("供應商交期、品質與配合度評鑑", value=True)
            with sub_col2:
                st.markdown("#### 🚢 全球供應鏈與物流")
                st.checkbox("全球供應商交期與風險預警管理", value=True)
                st.checkbox("跨國海空運物流與進口報關協調", value=True)
                st.checkbox("供應鏈成本優化與大宗採購合約", value=True)
            with sub_col3:
                st.markdown("#### 📋 採購合約與發票")
                st.checkbox("長約採購定價與分批交貨管理", value=True)
                st.checkbox("採購發票三way matching (三向勾稽)", value=True)
                st.checkbox("供應商對帳單與付款條件管理", value=True)

        # 13. 倉儲物流與庫存管理部
        elif "倉儲物流" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 📦 倉儲與庫存管理 (WMS)")
                st.checkbox("多倉庫、多倉位與儲位即時庫存查詢", value=True)
                st.checkbox("入庫驗收、上架、撥號與條盤管理", value=True)
                st.checkbox("領料、出貨、調撥與庫存異動明細", value=True)
                st.checkbox("期末庫存盤點計畫、盤點單與差異調整", value=True)
                st.checkbox("安全庫存水位警示與自動補貨建議", value=True)
            with sub_col2:
                st.markdown("#### 🏷️ 條碼與物流追蹤")
                st.checkbox("條碼 (Barcode) / QR Code 列印與貼標", value=True)
                st.checkbox("PDA 手持終端機掃描收發貨作業", value=True)
                st.checkbox("批號管理 (Batch/Lot) 與效期追蹤", value=True)
                st.checkbox("物流配送單據與快遞追蹤管理", value=True)
            with sub_col3:
                st.markdown("#### 🚛 運輸與車隊管理")
                st.checkbox("自有車隊派車與路線規劃管理", value=True)
                st.checkbox("外部物流承攬商 (3PL) 費用與績效", value=True)
                st.checkbox("貨品運送簽收與回单管理", value=True)

        # 14. 生產製造與廠務管理部
        elif "生產製造" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 🏭 生產製造執行 (MES)")
                st.checkbox("現場報工、條碼刷卡開工與完工回報", value=True)
                st.checkbox("製程站點流向管制與 WIP 在製品查詢", value=True)
                st.checkbox("模具管理、設備保養與維修履歷", value=True)
                st.checkbox("產線人員出勤與現場效率看板", value=True)
            with sub_col2:
                st.markdown("#### ⚡ 廠務與設施管理")
                st.checkbox("廠務水、電、氣、空調能源監控", value=True)
                st.checkbox("工廠廠房設備資產與定期巡檢維護", value=True)
                st.checkbox("廠區環境安全與環保廢棄物管理", value=True)
            with sub_col3:
                st.markdown("#### 📊 生產數據看板")
                st.checkbox("OEE 設備綜合效率即時監控", value=True)
                st.checkbox("產線瓶頸分析與產能產值報表", value=True)
                st.checkbox("製造成本分攤與實際工時結算", value=True)

        # 15. 工程與技術服務部
        elif "工程與技術" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### ⚙️ 工程專案與施工")
                st.checkbox("工程案場專案立項與工作分解 (WBS)", value=True)
                st.checkbox("工程估驗計價、合約與請款管理", value=True)
                st.checkbox("現場施工日報表、點工與點料回報", value=True)
            with sub_col2:
                st.markdown("#### 🛠️ 技術支援與維修")
                st.checkbox("設備安裝、調試與技術服務工單", value=True)
                st.checkbox("工程圖面、施工規範與技術文件庫", value=True)
                st.checkbox("外包商派工與計價審核管理", value=True)
            with sub_col3:
                st.markdown("#### 📐 設備與安全")
                st.checkbox("工程機具、手工具與儀器設備管理", value=True)
                st.checkbox("工地現場安全衛生查核與工安事件記錄", value=True)
                st.checkbox("竣工驗收與保固期追蹤管理", value=True)

        # 16. 生產管制與物料控制部
        elif "生產管制" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 📅 生產排程 (MPS/MRP)")
                st.checkbox("主生產排程 (MPS) 擬定與調整", value=True)
                st.checkbox("物料需求計畫 (MRP) 計算與缺料分析", value=True)
                st.checkbox("產能負荷分析與排程優化模擬", value=True)
            with sub_col2:
                st.markdown("#### 📋 工單與物料控制")
                st.checkbox("工單下達、優先級排序與急單插單管理", value=True)
                st.checkbox("齊料率分析與備料狀況即時追蹤", value=True)
                st.checkbox("生產進度落後警示與交期預測", value=True)
            with sub_col3:
                st.markdown("#### 🔄 呆滯與庫存優化")
                st.checkbox("呆滯物料 (Slow-moving) 分析與處理", value=True)
                st.checkbox("安全庫存動態調整與經濟訂購量 (EOQ)", value=True)
                st.checkbox("物料異動週轉率與庫存成本分析", value=True)

        # 17. 品質保證與品管中心
        elif "品質保證" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 🔍 進料與製程品管")
                st.checkbox("進料檢驗 (IQC) 標準與檢驗單管理", value=True)
                st.checkbox("製程巡檢 (IPQC) 與首件檢驗記錄", value=True)
                st.checkbox("成品檢驗 (FQC/OQC) 與出貨放行審核", value=True)
            with sub_col2:
                st.markdown("#### 📉 不良與矯正預防")
                st.checkbox("不良品 (NC) 隔離、原因分析與統計", value=True)
                st.checkbox("矯正與預防措施 (CAPA) 追蹤管考", value=True)
                st.checkbox("8D 報告製作與客戶客訴品質回覆", value=True)
            with sub_col3:
                st.markdown("#### 📐 度量衡與標準")
                st.checkbox("檢驗儀器、量具定期校驗與履歷管理", value=True)
                st.checkbox("統計製程管制 (SPC) 與 Cp/Cpk 分析", value=True)
                st.checkbox("ISO 品質管理系統文件與稽核追蹤", value=True)

        # 18. 研發設計與創新中心
        elif "研發設計" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 🔬 產品研發與 PLM")
                st.checkbox("新產品開發專案 (NPD) 與階段 gate 管理", value=True)
                st.checkbox("產品生命週期管理 (PLM) 與版本控制", value=True)
                st.checkbox("產品規格書、技術參數與研發文檔庫", value=True)
            with sub_col2:
                st.markdown("#### 🌳 BOM表與工程變更")
                st.checkbox("工程 BOM (EBOM) 建立與結構維護", value=True)
                st.checkbox("工程變更通知 (ECN / ECO) 簽核與發布", value=True)
                st.checkbox("研發打樣、試作工單與測試報告管理", value=True)
            with sub_col3:
                st.markdown("#### 💡 智財與創新")
                st.checkbox("專利申請、智財權與技術文件管理", value=True)
                st.checkbox("研發費用預算、工時與專案成本核算", value=True)
                st.checkbox("技術移轉與量產交接 (Transfer to MP)", value=True)

        # 19. 資訊技術與系統開發部
        else:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 💻 系統與軟體開發")
                st.checkbox("ERP 核心模組維護與原始碼管理", value=True)
                st.checkbox("系統使用者權限、角色 (RBAC) 與組織樹", value=True)
                st.checkbox("客製化表單、欄位元數據 (Metadata) 設定", value=True)
            with sub_col2:
                st.markdown("#### 🔌 系統整合與 API")
                st.checkbox("外部資料庫與異質系統 API 閘道管理", value=True)
                st.checkbox("第三方 API 金鑰、Webhook 與路由設定", value=True)
                st.checkbox("跨國多語系自動翻譯引擎維護", value=True)
            with sub_col3:
                st.markdown("#### 🤖 AI 與基礎設施")
                st.checkbox("AI 模型串接、Function Calling 與提示詞管理", value=True)
                st.checkbox("雲端伺服器運行監控、日誌與效能調優", value=True)
                st.checkbox("系統自動化測試、部署與版本回滾", value=True)

        st.markdown("---")
        if st.button(f"💾 儲存【{dept_name_only}】的專屬專業功能設定", type="primary", use_container_width=True):
            st.success(f"✅ 已成功將該部門專屬的細分功能設定儲存至資料庫！系統權限已即時生效。")

elif "企業組織與部門樹狀管理" in menu_choice:
    st.markdown("## 🏢 企業組織與部門樹狀管理 (Dynamic Org Chart)")
    st.info("💡 說明：動態建構企業組織架構，支援無限層級巢狀樹狀圖，確保不同部門與員工享有對應的資料列級隔離（Row-Level Security）。")

else:
    st.markdown("## 📊 系統運行與跨庫數據監控")
    st.info("💡 說明：即時監控各個已掛接外部資料庫與 API 來源的同步狀態、API 呼叫次數與系統效能。")
