import streamlit as st
import pandas as pd
import uuid

def render_app_store(current_tenant, all_departments=None):
    """
    樂高積木式模組市集與版本定價中心 (App Store)
    嚴格遵循您的要求：部門完全展開顯示（使用 radio），讓客人一目了然看到所有選項，並完美支援記憶與下方即時總覽。
    """
    st.markdown("## 🧩 企業部門樂高拼圖市集與版本定價中心 (App Store)")
    st.info("💡 *說明：左側完整展開所有部門與管理層供客戶一目了然地選擇；勾選功能後點擊儲存，下方即時總覽將完整顯示已開通的部門與模組明細。*")
    
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

    col_left, col_right = st.columns([1.1, 2.2])
    
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
        # 嚴格使用 st.radio 讓所有選項全部展開顯示，不使用下拉選單
        selected_dept = st.radio(
            "部門選擇",
            company_hierarchy_departments,
            index=0,
            label_visibility="collapsed"
        )
        
    with col_right:
        clean_dept_name = selected_dept.split('(')[0].strip()
        st.markdown(f"### 🛒 【{clean_dept_name}】樂高拼圖模組配置")
        
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
        
        # 取得目前該部門已儲存的模組清單
        saved_mods = tenant_data["dept_modules_db"].get(selected_dept, [])
        
        with st.form(f"form_store_{selected_dept}"):
            st.markdown(f"#### 📌 勾選【{clean_dept_name}】需要的 ERP 功能拼圖：")
            
            temp_selected = []
            for mod in available_mods_for_dept:
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
