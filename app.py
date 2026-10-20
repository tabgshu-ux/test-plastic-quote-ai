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
    lang = st.selectbox("選擇語系 / Select Language", ["繁體中文", "English", "Tiếng Việt (越南語)", "简体中文"])
    
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
            "實體據點與倉庫綁定管理 (Locations)",
            "跨國在地化與越南財稅模組 (VN Localization)",
            "系統運行與跨庫數據監控"
        ]
    )
    
    st.markdown("---")
    if st.button("🚪 登出系統", use_container_width=True):
        st.info("已安全登出系統。")

# 4. 主畫面邏輯路由
if "外部資料庫與異質資料來源" in menu_choice:
    st.markdown("## 🔌 外部資料庫與異質資料來源串聯設定 (Database Bridge)")
    st.markdown("💡 *在此處您可以設定與擴充對外連結的其他客戶資料庫或即時 API 來源（例如：台股/美股/越股行情 API、越南電子發票系統 API、總公司 SQL Server），無須修改程式碼。*")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        with st.form("db_bridge_form"):
            st.markdown("### ➕ 新增或設定外部資料庫 / API 來源")
            col1, col2 = st.columns(2)
            
            with col1:
                db_key = st.text_input("來源代碼 (Key)*", placeholder="例：vn_e_invoice_api 或 client_mysql")
                db_display_name = st.text_input("顯示名稱*", placeholder="例：越南總局電子發票 (Hóa đơn điện tử) API")
                db_type = st.selectbox("連線類型", ["RESTful API / JSON Bridge", "PostgreSQL / Supabase", "MySQL / MariaDB", "Microsoft SQL Server", "Oracle DB"])
                db_host = st.text_input("主機位址 / API Endpoint*", placeholder="例：https://api.einvoice.vn/v1 或 192.168.1.100")

            with col2:
                db_port = st.text_input("通訊埠 (Port) [若適用]", placeholder="例：3306 或 5432")
                db_name = st.text_input("資料庫名稱 / 路由路徑*", placeholder="例：v1/invoice/query")
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
        {"代碼 Key": "vn_einvoice_api", "名稱": "越南電子發票系統 (Minvoice/Viettel)", "類型": "RESTful API", "目標": "api.einvoice.vn", "狀態": "🟢 連線正常"},
        {"代碼 Key": "global_market_api", "名稱": "國際股市與匯率即時 API", "類型": "RESTful API", "目標": "api.marketdata.com", "狀態": "🟢 連線正常"}
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

        elif "會計與稅務管理部" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 📒 總帳與傳票管理")
                st.checkbox("會計科目表與會計期間設定", value=True)
                st.checkbox("一般傳票、轉帳傳票編製與審核", value=True)
                st.checkbox("自動過帳、試算表與總分類帳", value=True)
            with sub_col2:
                st.markdown("#### 🇻🇳 越南在地化財稅與發票 (VN Localization)")
                st.checkbox("越南電子發票 (Hóa đơn điện tử) 自動讀取與解析 (XML/PDF)", value=True)
                st.checkbox("越南紅發票進銷項 VAT 稅額自動勾稽", value=True)
                st.checkbox("發票明細自動對應會計科目並產生傳票", value=True)
                st.checkbox("越南稅務局 (GDT) 申報格式匯出與報稅輔助", value=True)
            with sub_col3:
                st.markdown("#### 🏛️ 一般稅務與資產")
                st.checkbox("固定資產卡片、折舊提列與盤點", value=True)
                st.checkbox("營業稅申報、進銷項憑證勾稽", value=True)
                st.checkbox("會計師專用查帳報表與財報產出", value=True)

        elif "生產製造與廠務管理部" in selected_department:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 🏭 生產製造執行 (MES)")
                st.checkbox("現場報工、條碼刷卡開工與完工回報", value=True)
                st.checkbox("製程站點流向管制與 WIP 在製品查詢", value=True)
                st.checkbox("模具管理、設備保養與維修履歷", value=True)
            with sub_col2:
                st.markdown("#### 📦 實體倉庫與據點管理 (Locations)")
                st.checkbox("生產部附屬實體倉庫/料區管轄權設定", value=True)
                st.checkbox("廠內各工段暫存倉與領退料管理", value=True)
                st.checkbox("倉庫實體位置與條碼對應關聯", value=True)
            with sub_col3:
                st.markdown("#### 📊 生產數據看板")
                st.checkbox("OEE 設備綜合效率即時監控", value=True)
                st.checkbox("產線瓶頸分析與產能產值報表", value=True)
                st.checkbox("製造成本分攤與實際工時結算", value=True)

        else:
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.markdown("#### 📋 組織日常作業模組 (A)")
                st.checkbox("基本資料維護與日常單據輸入", value=True)
                st.checkbox("審核流程與狀態追蹤", value=True)
            with sub_col2:
                st.markdown("#### 📊 組織日常作業模組 (B)")
                st.checkbox("報表統計與資料匯出", value=True)
                st.checkbox("權限控管與資料列級隔離 (RLS)", value=True)
            with sub_col3:
                st.markdown("#### 🤖 智慧與協作模組")
                st.checkbox("AI 語音助理與多語系即時翻譯", value=True)
                st.checkbox("行動端 (Mobile-First) 快速操作", value=True)

        st.markdown("---")
        if st.button(f"💾 儲存【{dept_name_only}】的專屬專業功能設定", type="primary", use_container_width=True):
            st.success(f"✅ 已成功將該部門專屬的細分功能設定儲存至資料庫！")

elif "企業組織與部門樹狀管理" in menu_choice:
    st.markdown("## 🏢 企業組織與部門樹狀管理 (Dynamic Org Chart)")
    st.info("💡 說明：動態建構企業組織架構，支援無限層級巢狀樹狀圖，確保不同部門與員工享有對應的資料列級隔離（Row-Level Security）。")

elif "實體據點與倉庫綁定管理" in menu_choice:
    st.markdown("## 🏭 實體據點與倉庫綁定管理 (Sites & Warehouses)")
    st.info("💡 說明：解決『倉庫不是獨立部門、而是附屬於生產部或其他部門底下的實體據點』之架構需求。您可以在此自由建立多個實體倉庫/廠房，並動態指定其歸屬的上級部門與負責人。")
    
    with st.form("warehouse_form"):
        st.markdown("### ➕ 新增實體據點 / 倉庫")
        wh_col1, wh_col2 = st.columns(2)
        with wh_col1:
            wh_code = st.text_input("據點/倉庫代碼*", placeholder="例：VN_BINH_DUONG_WH01")
            wh_name = st.text_input("據點/倉庫名稱*", placeholder="例：平陽廠一樓原物料主倉庫")
            wh_type = st.selectbox("據點類型", ["實體原料倉", "半成品暫存倉", "成品倉", "工地臨時料棧", "辦公室行政庫"])
        with wh_col2:
            parent_dept = st.selectbox("歸屬上級部門 (Parent Department)", [
                "🏭 生產製造與廠務管理部 (Manufacturing & Plant)",
                "📦 供應鏈與全球採購部 (Supply Chain & Procurement)",
                "🚚 倉儲物流與庫存管理部 (Warehouse & Logistics)",
                "⚙️ 工程與技術服務部 (Engineering & Technical)"
            ])
            wh_address = st.text_input("實體地址 / 廠區位置", placeholder="例：越南平陽省美福工業區二路 12 號")
            wh_manager = st.text_input("倉庫負責人", placeholder="例：Nguyễn Văn A / 林經理")
            
        if st.form_submit_button("💾 儲存並掛載實體據點", type="primary"):
            st.success(f"✅ 實體據點 [{wh_name}] 已成功掛載至部門：`{parent_dept}`！")
            
    st.markdown("---")
    st.markdown("### 📋 目前企業實體據點與倉庫清單")
    mock_wh_df = pd.DataFrame([
        {"據點代碼": "VN_BD_WH1", "名稱": "平陽廠原物料倉庫", "類型": "實體原料倉", "歸屬部門": "生產製造與廠務管理部", "負責人": "林經理"},
        {"据點代碼": "TW_HQ_WH", "名稱": "台灣總部備品倉", "類型": "成品倉", "歸屬部門": "倉儲物流與庫存管理部", "負責人": "張主任"}
    ])
    st.dataframe(mock_wh_df, use_container_width=True)

elif "跨國在地化與越南財稅模組" in menu_choice:
    st.markdown("## 🇻🇳 跨國在地化與越南財稅模組 (Vietnam Localization & E-Invoice)")
    st.info("💡 說明：針對越南市場所需之在地化功能，支援越南電子發票（Hóa đơn điện tử / Red Invoice）自動讀取、XML 解析、VAT 稅額勾稽與傳票自動入帳。")
    
    vn_tab1, vn_tab2 = st.tabs(["📥 越南電子發票自動解析與入帳 (E-Invoice Reader)", "📊 越企進銷項 VAT 與稅務申報 (Mẫu 01/GTGT)"])
    
    with vn_tab1:
        st.markdown("### 📄 上傳或串接越南紅發票 (Red Invoice - XML / PDF)")
        uploaded_invoice = st.file_uploader("請上傳越南電子發票檔案 (支援 XML 或 PDF 格式)", type=["xml", "pdf"])
        if uploaded_invoice:
            st.success("🎉 發票解析成功！系統已自動識別以下稅務與金額資訊：")
            col_iv1, col_iv2 = st.columns(2)
            with col_iv1:
                st.markdown("- **發票代號 (Ký hiệu / Symbol)**: `1C24TTP`")
                st.markdown("- **發票號碼 (Số hóa đơn)**: `00012345`")
                st.markdown("- **開立日期 (Ngày lập)**: `2026-10-20`")
                st.markdown("- **賣方統編 (Mã số thuế NCC)**: `3700123456`")
            with col_iv2:
                st.markdown("- **未稅金額 (Tiền hàng chưa thuế)**: `15,000,000 VND`")
                st.markdown("- **VAT 稅率 (Thuế suất)**: `10%`")
                st.markdown("- **VAT 稅額 (Tiền thuế VAT)**: `1,500,000 VND`")
                st.markdown("- **總計金額 (Tổng tiền thanh toán)**: `16,500,000 VND`")
                
            if st.button("🚀 自動對應會計科目並寫入會計帳冊", type="primary"):
                st.success("✅ 發票已成功轉入財務模組，借：原物料/費用 15,000,000，借：進項稅額 1,500,000，貸：應付帳款 16,500,000！")
                
    with vn_tab2:
        st.markdown("### 📊 越南月度/季度增值稅申報表輔助 (Tờ khai thuế GTGT)")
        st.info("💡 自動彙整本期越南進銷項發票，產生符合越南稅務局 (GDT) 標準的申報數據。")
        mock_tax_data = pd.DataFrame([
            {"項目": "1. 銷售免稅貨品/勞務金額", "金額 (VND)": "0"},
            {"項目": "2. 應稅銷售額 (稅率 8%)", "金額 (VND)": "120,000,000"},
            {"項目": "3. 應稅銷售額 (稅率 10%)", "金額 (VND)": "450,000,000"},
            {"項目": "4. 進項稅額總計 (VAT ĐẦU VÀO)", "金額 (VND)": "42,000,000"},
            {"項目": "5. 本期應納/留抵稅額", "金額 (VND)": "-3,500,000 (留抵)"}
        ])
        st.dataframe(mock_tax_data, use_container_width=True)

else:
    st.markdown("## 📊 系統運行與跨庫數據監控")
    st.info("💡 說明：即時監控各個已掛接外部資料庫與 API 來源的同步狀態、API 呼叫次數與系統效能。")
