import streamlit as st
import pandas as pd
import uuid

def render_app_store(current_tenant, all_departments=None):
    """
    樂高積木式模組市集與版本定價中心 (App Store)
    完美對齊：上方勾選部門功能與設定版本金額，下方即時總覽已開通的部門、功能與總訂閱狀況。
    """
    st.markdown("## 🧩 企業部門樂高拼圖市集與版本定價中心 (App Store)")
    st.info("💡 *說明：在上方勾選各部門的 ERP 拼圖功能並設定版本金額；儲存後，下方將即時列出全公司已開通的部門與功能總覽。*")
    
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
        st.markdown(f"### 🛒 【{clean_dept_name}】樂高拼圖模組與版本定價配置")
        
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
        
        if not current_tenant or not isinstance(current_tenant, dict):
            current_tenant = {"name": "預設租戶", "price_usd": 2500.0, "edition_name": "🚀 旗艦企業版 (Enterprise)", "dept_modules_db": {}}
            
        saved_dept_mods = current_tenant.get("dept_modules_db", {}).get(selected_dept, [])
        
        with st.form(f"form_store_{selected_dept}"):
            curr_selected = []
            st.markdown(f"#### 📌 勾選【{clean_dept_name}】需要的 ERP 功能拼圖：")
            
            for mod in available_mods_for_dept:
                is_checked = mod in saved_dept_mods
                if st.checkbox(mod, value=is_checked, key=f"store_{selected_dept}_{mod}"):
                    curr_selected.append(mod)
            
            st.markdown("---")
            st.markdown("#### 🏷️ 該租戶之版本名稱與訂閱金額設定")
            
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                custom_edition_name = st.text_input("自訂銷售版本名稱", value=current_tenant.get("edition_name", "🚀 旗艦企業版 (Enterprise)"))
            with col_v2:
                current_custom_price = st.number_input("設定每月總訂閱金額 (USD)", value=float(current_tenant.get("price_usd", 2500.0)), step=100.0)
            
            if st.form_submit_button(f"💾 立即寫入資料庫：儲存【{clean_dept_name}】模組與版本定價", type="primary", use_container_width=True):
                if "dept_modules_db" not in current_tenant:
                    current_tenant["dept_modules_db"] = {}
                current_tenant["dept_modules_db"][selected_dept] = curr_selected
                current_tenant["edition_name"] = custom_edition_name
                current_tenant["price_usd"] = current_custom_price
                
                st.success(f"🎉 成功寫入資料庫！【{clean_dept_name}】的樂高拼圖已儲存並同步更新版本定價！")
                st.rerun()

    # ========================================================
    # 📋 下方區塊：全公司已開通的部門與樂高模組即時總覽 (對應圖二)
    # ========================================================
    st.markdown("---")
    st.markdown("### 📋 【全公司租戶】目前已開通的部門與樂高模組即時總覽")
    st.info("💡 *此處即時列出目前所有已儲存的部門與勾選功能，讓您隨時核對版本內容、開通項目與訂閱金額。*")

    active_db = current_tenant.get("dept_modules_db", {})
    if active_db:
        summary_data = []
        for d_name, m_list in active_db.items():
            if m_list:
                summary_data.append({
                    "已開通部門/管理層": d_name,
                    "已勾選模組數量": f"{len(m_list)} 項",
                    "詳細功能明細": ", ".join(m_list)
                })
        if summary_data:
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
        else:
            st.warning("⚠️ 目前尚未儲存任何部門的模組勾選。")
    else:
        st.info("ℹ️ 尚無已儲存的模組資料，請在上方勾選並點擊儲存按鈕。")
    
    st.markdown(f"📌 **當前版本方案**：`{current_tenant.get('edition_name', '未設定')}` | 💰 **當前設定月費**：`$ {current_tenant.get('price_usd', 0)} USD/月`")
