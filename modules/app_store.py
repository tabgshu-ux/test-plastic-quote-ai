import streamlit as st
import pandas as pd
import uuid

def render_app_store(current_tenant, all_departments=None):
    """
    全球 SaaS 多產業 1~4 級組織架構與樂高拼圖模組市集 (App Store)
    完整內建白皮書中的 12 大產業母體庫與所有實體部門（含工程部等），採全部展開顯示。
    """
    st.markdown("## 🧩 全球多產業 1~4 級組織架構與樂高拼圖市集 (App Store)")
    st.info("💡 *說明：請先選擇企業所屬的【12大產業別】之一；接著在左側完整展開所有部門與管理層（含工程部），右側勾選專屬 ERP 功能拼圖，儲存後下方將即時總覽已開通的部門、功能與版本金額。*")
    
    # 確保全域 session_state 中有穩固的租戶與模組儲存結構
    if "current_tenant_mock" not in st.session_state:
        st.session_state.current_tenant_mock = {
            "name": "裕豐電機工業 (Reetech)",
            "edition_name": "🚀 旗艦企業版 (Enterprise)",
            "price_usd": 2500.0,
            "dept_modules_db": {}
        }
    
    tenant_data = st.session_state.current_tenant_mock
    if "dept_modules_db" not in tenant_data:
        tenant_data["dept_modules_db"] = {}

    # 1. 完整收錄您白皮書中的 12 大產業別
    industry_options = [
        "一、 製造與代工業（Manufacturing & OEM）",
        "二、 科技與軟體業（Tech & Software / SaaS）",
        "三、 零售與電商業（Retail & E-Commerce）",
        "四、 傳統服務業（Traditional Service Industry）",
        "五、 投資顧問業（Investment Advisory / SITCA）",
        "六、 保險業（Insurance Industry - 產險/壽險）",
        "七、 銀行業（Banking Industry）",
        "八、 生技醫藥開發業（Biotech & Pharmaceutical R&D）",
        "九、 營造與營建工程業（Construction & Engineering）",
        "十、 物流與倉儲運輸業（Logistics & Transportation）",
        "十一、 觀光飯店與旅宿業（Hospitality & Hotel Industry）",
        "十二、 遊戲與數位內容產業（Gaming & Digital Content）"
    ]
    
    selected_industry = st.selectbox("📂 請選擇企業所屬的全球產業別母體", industry_options)
    st.markdown("---")

    col_left, col_right = st.columns([1.1, 2.2])
    
    # 2. 完整涵蓋所有實體部門（包含您特別點名的工程部、研發部、財務部、行銷部、業務部、生產部、工程部等）
    full_departments_list = [
        "👑 董事會 / CEO Office (1級總裁層)",
        "💰 資產財務處 / 財務部",
        "📦 供應鏈管理處 / 採購與物流倉儲部",
        "🏭 生產製造處 / 廠務製造部",
        "🛡️ 品質保證部 (QA/QC)",
        "🔬 研發部 (R&D Department)",
        "🛠️ 工程部 (Engineering Department)",
        "📢 行銷部 / 行銷增長處",
        "🤝 業務營運處 / 國內外銷售部",
        "💻 資訊與雲端運維部 (IT & DevOps)",
        "👥 人力資源與行政管理處 (HR & Admin)"
    ]
    
    with col_left:
        st.markdown("### 🏢 選擇目標部門 / 管理層")
        # 嚴格使用 st.radio 讓所有部門完全展開顯示，供客戶一目了然
        selected_dept = st.radio(
            "部門選擇",
            full_departments_list,
            index=0,
            label_visibility="collapsed"
        )
        
    with col_right:
        clean_dept_name = selected_dept.split('(')[0].strip()
        st.markdown(f"### 🛒 【{clean_dept_name}】樂高拼圖模組配置")
        
        # 各部門專屬功能對應字典
        department_modules_mapping = {
            "董事會": [
                "老闆專屬現金流與 AR/AP 逾期預警看板",
                "即時綜合損益與動態成本分攤 (P&L)",
                "全球股市、匯率與原料期貨行情 API 串聯",
                "溫室氣體盤查 (ESG 範疇一二三) 與碳排總體指標",
                "全方位數位簽核中心與多級呈核路由 (BPM)"
            ],
            "資產財務處": [
                "總帳 (GL) 與應收/應付帳款 (AR/AP) 管理",
                "固定資產折舊提列與資產負債表管理",
                "多國動態稅制引擎與會計總帳對接"
            ],
            "供應鏈管理處": [
                "採購申請 (PR)、採購單 (PO) 與供應商評鑑",
                "多據點條碼掃描入庫/出庫/調撥 (WMS)",
                "動態安全庫存與自動補貨水位預警"
            ],
            "生產製造處": [
                "生產工單派發、製程報工與排程 (PMC)",
                "設備稼動率 (OEE) 與 MES 現場 IoT 監控",
                "廠區作業班別與產能負荷分析"
            ],
            "品質保證部": [
                "進料品管 (IQC) 與製程品管 (IPQC) 追蹤",
                "ISO 標準文件版本管制與 CAPA 矯正預防措施",
                "量測儀器校驗履歷與供應商 QCD 評鑑"
            ],
            "研發部": [
                "階層式物料清單 (BOM) 與版本控管",
                "專案 WBS 研發預算超支防呆與成本追蹤",
                "產品版本生命週期管理 (Release Note)"
            ],
            "工程部": [
                "工程專案 WBS 合約與下包商點工計價",
                "工程預算編列與超支預警（變更設計）",
                "工地進度報工、工程日誌與發票核銷"
            ],
            "行銷部": [
                "數位行銷活動投資報酬率 (ROI) 分析",
                "會員點數錢包、儲值金管理與優惠券",
                "市場競品分析與品牌公關進度追蹤"
            ],
            "業務營運處": [
                "客戶關係管理 (CRM) 與客戶生命週期 (LTV)",
                "雙層式銷售報價與多幣別換算引擎",
                "訂閱制合約管理與業務業績獎金計算"
            ],
            "資訊與雲端運維部": [
                "雲端伺服器成本分攤與 API 流量計費統計",
                "IT 資產配置、網頁動態模組權限與資安稽核",
                "組織權限矩陣與 RBAC 細粒度隔離"
            ],
            "人力資源": [
                "全球人事組織生命週期與數位履歷",
                "動態加班與在地化法規薪資引擎",
                "廠區門禁保全、公務車派車與總務資產管理"
            ]
        }
        
        # 尋找對應功能的匹配項
        matched_mods = []
        for key, mods in department_modules_mapping.items():
            if key in selected_dept:
                matched_mods = mods
                break
        if not matched_mods:
            matched_mods = [
                "階層式物料清單 (BOM) 與版本控管",
                "全方位數位簽核中心與多級呈核路由 (BPM)",
                "專案專屬 WBS 預算控管與追蹤"
            ]
        
        saved_mods = tenant_data["dept_modules_db"].get(selected_dept, [])
        
        with st.form(f"form_store_{selected_dept}"):
            st.markdown(f"#### 📌 勾選【{clean_dept_name}】需要的 ERP 功能拼圖：")
            
            temp_selected = []
            for mod in matched_mods:
                is_currently_checked = mod in saved_mods
                if st.checkbox(mod, value=is_currently_checked, key=f"chk_{selected_dept}_{mod}"):
                    temp_selected.append(mod)
            
            st.markdown("---")
            if st.form_submit_button(f"💾 立即加入：儲存【{clean_dept_name}】的功能拼圖", type="primary", use_container_width=True):
                tenant_data["dept_modules_db"][selected_dept] = temp_selected
                st.session_state.current_tenant_mock = tenant_data
                st.success(f"🎉 成功！【{clean_dept_name}】的功能拼圖已加入並即時生效！")
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
    
    # 版本名稱與金額設定表單
    with st.form("bottom_version_pricing_form"):
        st.markdown("#### 🏷️ 租戶版本名稱與訂閱金額結算設定")
        bv1, bv2 = st.columns(2)
        with bv1:
            custom_edition_name = st.text_input("自訂銷售版本名稱", value=tenant_data.get("edition_name", "🚀 旗艦企業版 (Enterprise)"))
        with bv2:
            current_custom_price = st.number_input("設定每月總訂閱金額 (USD)", value=float(tenant_data.get("price_usd", 2500.0)), step=100.0)
            
        if st.form_submit_button("💾 儲存下方版本名稱與總訂閱金額設定", type="primary", use_container_width=True):
            tenant_data["edition_name"] = custom_edition_name
            tenant_data["price_usd"] = current_custom_price
            st.session_state.current_tenant_mock = tenant_data
            st.success(f"🎉 成功更新！版本名稱已設為 [{custom_edition_name}]，總訂閱金額 `$ {current_custom_price} USD` 已同步！")
            st.rerun()
