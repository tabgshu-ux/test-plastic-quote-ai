import streamlit as st
import uuid

def render_app_store(current_tenant, all_departments=None):
    """
    總控中心 / 租戶後台：樂高積木式模組市集與功能開關 (App Store)
    支援：依產業別動態切換 1~4 級組織架構、勾選白話拼圖模組（含 ISO、ESG 與特殊行業核心引擎）、即時計費與串連。
    """
    st.markdown(f"## 🧩 樂高積木式模組市集與產業組織配置 (App Store)")
    st.info("💡 *說明：請先選擇【企業產業別】載入對應的 1~4 級組織樹，並在右側勾選專屬的 ERP 白話拼圖模組（含 ISO 與 ESG 合規模組），即時完成模組串連與定價計費！*")
    
    col_left, col_right = st.columns([1, 2.2])
    
    with col_left:
        st.markdown("### 🏭 1. 選擇企業產業別")
        industry_choice = st.selectbox(
            "產業別選擇",
            [
                "⚡ 製造與代工業 (Manufacturing & OEM)",
                "💻 科技與軟體業 (Tech & Software / SaaS)",
                "🛒 零售與電商業 (Retail & E-Commerce)",
                "🧬 生技醫藥與營建工程業 (Biotech & Construction)",
                "💰 金融、保險與投顧業 (Finance & Insurance)"
            ]
        )
        
        st.markdown("### 🏢 2. 1~4 級組織架構預覽")
        if "製造與代工業" in industry_choice:
            st.markdown("- 👑 **1級**: 董事會 / CEO Office\n  - 处級 (2級): 財務處 / 供應鏈處 / 生產製造處\n    - 部級 (3級): 財務部 / 供應鏈管理部 / 品保部\n      - 組級 (4級): 會計課 / 倉儲課 / PQC組")
        elif "科技與軟體業" in industry_choice:
            st.markdown("- 👑 **1級**: 董事會 / CEO Office\n  - 处級 (2級): 研發處 / 運維處 / 商務處\n    - 部級 (3級): 技術研發部 / 雲端運維部 / 客戶成功部\n      - 組級 (4級): 前端課 / 資安組 / LTV分析組")
        elif "零售與電商業" in industry_choice:
            st.markdown("- 👑 **1級**: 董事會 / CEO Office\n  - 处級 (2級): 通路處 / 商品處 / 行銷處\n    - 部級 (3級): 電商部 / 門市部 / 倉儲物流部\n      - 組級 (4級): 平台課 / POS對帳組 / 退貨組")
        elif "生技醫藥與營建工程業" in industry_choice:
            st.markdown("- 👑 **1級**: 董事會 / CEO Office\n  - 处級 (2級): 研發處 / 工務處 / 財務成控處\n    - 部級 (3級): 實驗室部 / 工事部 / 成本控制部\n      - 組級 (4級): 合成組 / 下包商合約組 / WBS成控")
        else:
            st.markdown("- 👑 **1級**: 董事會 / CEO Office\n  - 处級 (2級): 精算處 / 核保處 / 業務處\n    - 部級 (3級): 商品研發部 / 核保部 / 分潤部\n      - 組級 (4級): 準備金組 / 保經代組 / 組織樹組")

    with col_right:
        st.markdown("### 🛒 3. 白話樂高拼圖模組市集（含 ISO、ESG 與特殊引擎）")
        
        with st.form("form_lego_app_store"):
            curr_selected = []
            
            st.markdown("#### 📈 第一類：營運戰情與高階管理模組")
            c1, c2 = st.columns(2)
            with c1:
                if st.checkbox("老闆專屬現金流與 AR/AP 逾期預警看板", value=True): curr_selected.append("現金流看板")
                if st.checkbox("即時綜合損益與動態成本分攤 (P&L)", value=True): curr_selected.append("P&L 損益分攤")
            with c2:
                if st.checkbox("全球股市、匯率與原料期貨行情 API 串聯", value=False): curr_selected.append("全球原料匯率API")
                
            st.markdown("#### ⚡ 第二類：專案研發、WBS 預算與工程引擎")
            c3, c4 = st.columns(2)
            with c3:
                if st.checkbox("雙層式報價與多幣別換算引擎", value=True): curr_selected.append("多幣別報價引擎")
                if st.checkbox("專案 WBS 預算超支防呆與 CapEx/OpEx 轉列引擎 *(特殊行業)*", value=True): curr_selected.append("WBS專案預算引擎")
            with c4:
                if st.checkbox("階層式物料清單 (BOM) 與版本控管", value=True): curr_selected.append("BOM版本控管")
                
            st.markdown("#### 👤 第三類：人資、薪資與行政總務模組")
            c5, c6 = st.columns(2)
            with c5:
                if st.checkbox("動態加班與在地化法規薪資引擎", value=True): curr_selected.append("在地化薪資引擎")
                if st.checkbox("固定資產條碼化、折舊與廠區門禁派車", value=False): curr_selected.append("固定資產與門禁")
            with c6:
                if st.checkbox("全方位數位簽核中心與多級呈核路由 (BPM)", value=True): curr_selected.append("電子簽核中心")
                
            st.markdown("#### 📦 第四類：供應鏈、WMS 倉儲與 MES 製造模組")
            c7, c8 = st.columns(2)
            with c7:
                if st.checkbox("多據點條碼掃描入庫/出庫/調撥 (WMS)", value=True): curr_selected.append("WMS 倉儲條碼")
                if st.checkbox("製程工單派發、報工與設備稼動率監控 (MES)", value=True): curr_selected.append("MES 生產製造")
            with c8:
                if st.checkbox("多階層動態佣金與通路分潤計算引擎 *(特殊行業)*", value=False): curr_selected.append("多階層分潤引擎")
                
            st.markdown("#### 🛡️ 第五類：ISO 品質與 ESG 永續合規模組")
            c9, c10 = st.columns(2)
            with c9:
                if st.checkbox("ISO 標準文件版本管制與 CAPA 矯正預防措施", value=True): curr_selected.append("ISO合規與CAPA")
                if st.checkbox("量測儀器校驗履歷與供應商 QCD 評鑑", value=False): curr_selected.append("儀器校驗與供應商評鑑")
            with c10:
                if st.checkbox("溫室氣體盤查 (範疇一、二、三) 與碳排當量計算 (ESG)", value=True): curr_selected.append("ESG碳排盤查")
                if st.checkbox("水資源、廢棄物監控與永續報告書數據導出", value=False): curr_selected.append("水電廢棄物與永續報告")

            st.markdown("---")
            calculated_price = 800 + (len(curr_selected) * 100)
            if current_tenant and isinstance(current_tenant, dict):
                current_tenant["price_usd"] = calculated_price

            st.markdown(f"### 💳 系統計費試算：當前選定 `{len(curr_selected)}` 項樂高拼圖模組 ➔ 每月總訂閱費用：**`$ {calculated_price} USD`**")
            
            if st.form_submit_button(f"💾 立即寫入資料庫：儲存【{industry_choice.split('(')[0].strip()}】模組配置", type="primary", use_container_width=True):
                if current_tenant and isinstance(current_tenant, dict):
                    current_tenant["active_modules"] = curr_selected
                st.success(f"🎉 成功寫入資料庫！所選的產業組織與 {len(curr_selected)} 項樂高拼圖模組已即時串連生效。")
