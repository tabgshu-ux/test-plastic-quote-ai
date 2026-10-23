import streamlit as st
import pandas as pd
import uuid

def render_app_store(current_tenant=None, all_departments=None):
    """
    樂高積木式模組市集與版本定價中心 (App Store)
    完美內建 12 大產業與所有實體部門，保證無路徑匯入錯誤、絕不白屏。
    """
    st.markdown("## 🧩 全球多產業 1~4 級組織架構與樂高拼圖市集 (App Store)")
    st.info("💡 *說明：請先在下方選擇企業所屬的全球產業別；接著在左側完整展開所有部門，右側勾選專屬 ERP 功能拼圖，儲存後下方將即時總覽已開通的部門、功能與版本金額。*")
    
    # 1. 確保 session_state 穩定
    if "safe_tenant_db" not in st.session_state:
        st.session_state.safe_tenant_db = {
            "edition_name": "🚀 旗艦企業版 (Enterprise)",
            "price_usd": 2500.0,
            "dept_modules_db": {}
        }
    
    tenant_data = st.session_state.safe_tenant_db
    if not isinstance(tenant_data.get("dept_modules_db"), dict):
        tenant_data["dept_modules_db"] = {}

    # 2. 完整 12 大產業矩陣（內建，絕對不會發生找不到檔案的 KeyError）
    industries_matrix = {
        "一、 製造與代工業（Manufacturing & OEM）": [
            "👑 董事會 / CEO Office",
            "💰 資產財務處 / 財務部",
            "📦 供應鏈管理處 / 採購與物流倉儲部",
            "🏭 生產製造處 / 廠務製造部",
            "🛡️ 品質保證部 (QA/QC)",
            "🔬 研發部 (R&D Department)",
            "🛠️ 工程部 (Engineering Department)",
            "📢 業務營運處 / 國內外銷售部",
            "👥 人力資源與行政管理處"
        ],
        "二、 科技與軟體業（Tech & Software / SaaS）": [
            "👑 董事會 / CEO Office",
            "🔬 產品研發處 / 技術研發部",
            "💻 資料與運維處 / 雲端運維部",
            "🤝 商務推廣處 / 全球業務部",
            "🌟 客戶成功部 (Customer Success)",
            "👥 行政管理處 / 人力資源部"
        ],
        "三、 零售與電商業（Retail & E-Commerce）": [
            "👑 董事會 / CEO Office",
            "🌐 通路營運處 / 線上電商部與實體門市部",
            "📦 商品供應處 / 倉儲物流部",
            "📢 行銷增長處 / 數位行銷部"
        ],
        "四、 傳統服務業（Traditional Service Industry）": [
            "👑 董事會 / CEO Office",
            "🏬 連鎖營運處 / 區域店務部",
            "🏗️ 開店工程部 / 設備維護組",
            "🍲 供應鏈管理處 / 中央廚房與物流配送部",
            "🎫 會員與行銷處 / 會員經營部"
        ],
        "五、 投資顧問業（Investment Advisory / SITCA）": [
            "👑 董事會 / 總經理室",
            "📊 投資研究處 / 產業研究部",
            "🌐 全球策略部 / 總體經濟課",
            "🤝 業務發展處 / 會員經營部與法人業務部",
            "🛡️ 營運合規處 / 法務合規部",
            "💻 資訊技術部"
        ],
        "六、 保險業（Insurance Industry - 產險/壽險）": [
            "👑 董事會 / 總經理室",
            "📈 商品精算處 / 商品研發部",
            "🛡️ 核保理賠處 / 契約核保部與理賠服務部",
            "🤝 業務通路處 / 經代通路部與直轄營業部",
            "💰 財務資產處 / 保費會計部與投資運用部"
        ],
        "七、 銀行業（Banking Industry）": [
            "👑 董事會 / 總經理室",
            "💳 個人金融處 / 分行營運部與財富管理部",
            "🏢 企業金融處 / 放款審查部",
            "⚠️ 風險管理處 / 風險規劃部",
            "📦 營運支援處 / 集中作業部與總務採購部"
        ],
        "八、 生技醫藥開發業（Biotech & Pharmaceutical R&D）": [
            "👑 董事會 / 總經理室",
            "🔬 臨床前研發處 / 實驗室研發部",
            "📜 專利與智慧財產部",
            "🏥 臨床試驗處 (Clinical) / 臨床營運部",
            "🛡️ 法規事務部 (RA)",
            "📊 專案與財務處 (PMO)"
        ],
        "九、 營造與營建工程業（Construction & Engineering）": [
            "👑 董事會 / 總經理室",
            "🏗️ 工務營造處 / 工事專案部",
            "📦 發包採購部 / 下包商合約組",
            "🗺️ 開發規劃處 / 土地開發部",
            "💰 財務與成控處 / 成本控制部"
        ],
        "十、 物流與倉儲運輸業（Logistics & Transportation）": [
            "👑 董事會 / 總經理室",
            "🚚 運輸運務處 / 車隊管理部",
            "✈️ 海空運轉運部 / 報關組",
            "📦 倉儲物流處 / 轉運倉儲部",
            "💳 客戶與帳務處 / 營業帳務部"
        ],
        "十一、 觀光飯店與旅宿業（Hospitality & Hotel Industry）": [
            "👑 董事會 / 總經理室",
            "🏨 酒店營運處 / 客房部與餐飲部",
            "📢 行銷業務處 / 企業簽約與通路組"
        ],
        "十二、 遊戲與數位內容產業（Gaming & Digital Content）": [
            "👑 董事會 / 總經理室",
            "🎮 遊戲營運處 / 產品營運部",
            "🌐 通路與商務處 / 數位通路部",
            "💰 財務行政處 / 版權與財務部"
        ]
    }

    # 3. 產業與部門選單
    industry_keys = list(industries_matrix.keys())
    selected_industry = st.selectbox("📂 請選擇企業所屬的全球產業別母體", industry_keys)
    current_dept_list = industries_matrix[selected_industry]
    st.markdown("---")

    col_left, col_right = st.columns([1.1, 2.2])
    
    with col_left:
        st.markdown("### 🏢 選擇目標部門 / 管理層")
        selected_dept = st.radio(
            "部門選擇",
            current_dept_list,
            index=0,
            label_visibility="collapsed"
        )
        
    with col_right:
        clean_dept_name = selected_dept.split('(')[0].strip()
        st.markdown(f"### 🛒 【{clean_dept_name}】樂高拼圖模組配置")
        
        available_mods = [
            "老闆專屬現金流與 AR/AP 逾期預警看板",
            "即時綜合損益與動態成本分攤 (P&L)",
            "階層式物料清單 (BOM) 與版本控管",
            "專案 WBS 預算超支防呆與成本追蹤",
            "多據點條碼掃描入庫/出庫/調撥 (WMS)",
            "生產工單派發、製程報工與稼動率 (MES)",
            "ISO 標準文件版本管制與 CAPA 矯正預防措施",
            "溫室氣體盤查 (ESG 範疇一二三) 與碳排當量計算",
            "全方位數位簽核中心與多級呈核路由 (BPM)",
            "多階層動態佣金與通路分潤計算引擎"
        ]
        
        saved_mods = tenant_data["dept_modules_db"].get(selected_dept, [])
        
        # 4. 單一穩定表單
        with st.form(f"simple_form_{selected_dept}"):
            st.markdown(f"#### 📌 勾選【{clean_dept_name}】需要的 ERP 功能拼圖：")
            
            temp_selected = []
            for mod in available_mods:
                is_checked = mod in saved_mods
                if st.checkbox(mod, value=is_checked, key=f"cb_{selected_dept}_{mod}"):
                    temp_selected.append(mod)
            
            st.markdown("---")
            submitted = st.form_submit_button(f"💾 立即加入：儲存【{clean_dept_name}】的功能拼圖", type="primary", use_container_width=True)
            if submitted:
                tenant_data["dept_modules_db"][selected_dept] = temp_selected
                st.session_state.safe_tenant_db = tenant_data
                st.success(f"🎉 成功！【{clean_dept_name}】的功能拼圖已儲存！")
                st.rerun()

    # ========================================================
    # 📋 下方區塊：總覽與版本金額設定中心
    # ========================================================
    st.markdown("---")
    st.markdown("### 📋 【全公司租戶】已開通部門、功能總覽與版本金額設定")
    st.info("💡 *在此檢視目前已加入的部門與功能明細，並直接在下方設定該租戶的自訂銷售版本名稱與每月總訂閱金額 (USD)。*")

    active_db = tenant_data.get("dept_modules_db", {})
    summary_data = []
    for d_name, m_list in active_db.items():
        if m_list and len(m_list) > 0:
            summary_data.append({
                "已開通部門/管理層": d_name,
                "已勾選模組數量": f"{len(m_list)} 項",
                "詳細功能明細": ", ".join(m_list)
            })
            
    if summary_data:
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
    else:
        st.warning("⚠️ 目前尚未加入任何部門的模組勾選，請在上方勾選並點擊儲存按鈕。")
    
    # 5. 版本設定表單
    with st.form("version_price_form"):
        st.markdown("#### 🏷️ 租戶版本名稱與訂閱金額結算設定")
        v1, v2 = st.columns(2)
        with v1:
            custom_name = st.text_input("自訂銷售版本名稱", value=tenant_data.get("edition_name", "🚀 旗艦企業版 (Enterprise)"))
        with v2:
            custom_price = st.number_input("設定每月總訂閱金額 (USD)", value=float(tenant_data.get("price_usd", 2500.0)), step=100.0)
            
        if st.form_submit_button("💾 儲存下方版本名稱與總訂閱金額設定", type="primary", use_container_width=True):
            tenant_data["edition_name"] = custom_name
            tenant_data["price_usd"] = custom_price
            st.session_state.safe_tenant_db = tenant_data
            st.success(f"🎉 成功更新！版本名稱已設為 [{custom_name}]，總訂閱金額 `$ {custom_price} USD` 已同步！")
            st.rerun()
