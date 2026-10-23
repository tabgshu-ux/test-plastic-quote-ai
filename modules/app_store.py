import streamlit as st
import uuid

def render_app_store(current_tenant, all_departments=None):
    """
    企業部門與樂高積木模組市集 (App Store)
    專注於：部門與 ERP 功能拼圖的勾選、串連與權限開通（定價與方案統一由總控端管理）。
    """
    st.markdown("## 🧩 企業部門與樂高積木模組市集 (App Store)")
    st.info("💡 *說明：在此點選管理層或實際部門，勾選並串連該部門專屬的 ERP 功能拼圖。租戶開通與總訂閱金額統一由總控端方案進行管理。*")
    
    col_left, col_right = st.columns([1, 2.2])
    
    company_hierarchy_departments = [
        "👑 董事長室 / 總經理室 (Executive & CEO Office)",
        "🔬 研發部 (R&D Department)",
        "💰 財務部 (Finance & Accounting Dept)",
        "📢 行銷部 (Marketing Department)",
        "🤝 業務部 (Sales Department)",
        "🏭 生產部 (Production & Manufacturing Dept)",
        "📦 供應鏈與倉儲部 (Supply Chain & WMS)",
        "🛡️ 品保/品管部 (QA / QC Department)",
        "👥 人力資源與總務部 (HR & Admin Dept)"
    ]
    
    with col_left:
        st.markdown("### 🏢 選擇目標管理層 / 部門")
        selected_dept = st.radio(
            "部門選擇",
            company_hierarchy_departments,
            index=0,
            label_visibility="collapsed"
        )
        
    with col_right:
        clean_dept_name = selected_dept.split('(')[0].strip()
        st.markdown(f"### 🛒 【{clean_dept_name}】專屬的 ERP 樂高拼圖模組串連")
        
        department_modules_mapping = {
            "董事長室 / 總經理室": [
                "老闆專屬現金流與 AR/AP 逾期預警看板",
                "即時綜合損益與動態成本分攤 (P&L)",
                "全球股市、匯率與原料期貨行情 API 串聯",
                "溫室氣體盤查 (ESG 範疇一二三) 與碳排總體指標",
                "全方位數位簽核中心與多級呈核路由 (BPM)"
            ],
            "研發部": [
                "階層式物料清單 (BOM) 與版本控管",
                "專案 WBS 研發預算超支防呆與成本追蹤",
                "產品版本生命週期管理 (Release Note)"
            ],
            "財務部": [
                "總帳 (GL) 與應收/應付帳款 (AR/AP) 管理",
                "即時綜合損益與動態成本分攤 (P&L)",
                "固定資產折舊提列與資產負債表管理",
                "多國動態稅制引擎與會計總帳對接"
            ],
            "行銷部": [
                "數位行銷活動投資報酬率 (ROI) 分析",
                "會員點數錢包、儲值金管理與優惠券",
                "市場競品分析與品牌公關進度追蹤"
            ],
            "業務部": [
                "客戶關係管理 (CRM) 與客戶生命週期 (LTV)",
                "雙層式銷售報價與多幣別換算引擎",
                "訂閱制合約管理與業務業績獎金計算"
            ],
            "生產部": [
                "生產工單派發、製程報工與排程 (PMC)",
                "設備稼動率 (OEE) 與 MES 現場 IoT 監控",
                "廠區作業班別與產能負荷分析"
            ],
            "供應鏈與倉儲部": [
                "採購申請 (PR)、採購單 (PO) 與供應商評鑑",
                "多據點條碼掃描入庫/出庫/調撥 (WMS)",
                "動態安全庫存與自動補貨水位預警"
            ],
            "品保/品管部": [
                "進料品管 (IQC) 與製程品管 (IPQC) 追蹤",
                "ISO 標準文件版本管制與 CAPA 矯正預防措施",
                "量測儀器校驗履歷與供應商 QCD 評鑑"
            ],
            "人力資源與總務部": [
                "全球人事組織生命週期與數位履歷",
                "動態加班與在地化法規薪資引擎",
                "廠區門禁保全、公務車派車與總務資產管理"
            ]
        }
        
        matched_key = next((k for k in department_modules_mapping if k in selected_dept), "董事長室 / 總經理室")
        available_mods_for_dept = department_modules_mapping[matched_key]
        
        saved_dept_mods = current_tenant.get("dept_modules_db", {}).get(selected_dept, []) if current_tenant else []
        
        with st.form(f"form_store_{selected_dept}"):
            curr_selected = []
            st.markdown(f"#### 📌 勾選並串連【{clean_dept_name}】的 ERP 功能拼圖：")
            
            for mod in available_mods_for_dept:
                if st.checkbox(mod, value=mod in saved_dept_mods, key=f"store_{selected_dept}_{mod}"):
                    curr_selected.append(mod)
            
            st.markdown("---")
            st.info("💡 *提示：此處勾選將直接連動並解鎖該部門在系統中的實際操作權限。租戶方案版本與訂閱金額請至總控台進行設定。*")
            
            if st.form_submit_button(f"🚀 立即串連與儲存【{clean_dept_name}】的模組權限", type="primary", use_container_width=True):
                if current_tenant and isinstance(current_tenant, dict):
                    if "dept_modules_db" not in current_tenant:
                        current_tenant["dept_modules_db"] = {}
                    current_tenant["dept_modules_db"][selected_dept] = curr_selected
                st.success(f"🎉 成功！【{clean_dept_name}】的樂高拼圖模組權限已即時串連開通！")
