import streamlit as st
import uuid

def render_app_store(current_tenant, all_departments=None):
    """
    樂高積木式模組市集 (App Store)
    嚴格依照各部門真實職掌與商業邏輯精準對應功能拼圖。
    """
    st.markdown("## 🧩 企業部門與樂高積木模組市集 (App Store)")
    st.info("💡 *說明：請從左側點選企業的實際部門，右側就會精準顯示該部門專屬、符合真實業界邏輯的 ERP 功能拼圖！*")
    
    col_left, col_right = st.columns([1, 2.2])
    
    manufacturing_departments = [
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
        st.markdown("### 🏢 選擇目標部門")
        selected_dept = st.radio(
            "部門選擇",
            manufacturing_departments,
            index=0,
            label_visibility="collapsed"
        )
        
    with col_right:
        clean_dept_name = selected_dept.split('(')[0].strip()
        st.markdown(f"### 🛒 【{clean_dept_name}】專屬的 ERP 樂高拼圖模組")
        
        # 嚴格符合各部門真實職掌的對應字典
        department_modules_mapping = {
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
                "全球股市、匯率與原料期貨行情 API 串聯"
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
                "全方位數位簽核中心與多級呈核路由 (BPM)",
                "廠區門禁保全、公務車派車與總務資產管理",
                "溫室氣體盤查 (ESG 範疇一二三) 與碳排計算"
            ]
        }
        
        matched_key = next((k for k in department_modules_mapping if k in selected_dept), "研發部")
        available_mods_for_dept = department_modules_mapping[matched_key]
        
        saved_dept_mods = current_tenant.get("dept_modules_db", {}).get(selected_dept, [])
        
        with st.form(f"form_store_{selected_dept}"):
            curr_selected = []
            st.markdown(f"#### 📌 勾選【{clean_dept_name}】真實業務需要的模組：")
            
            for mod in available_mods_for_dept:
                if st.checkbox(mod, value=mod in saved_dept_mods, key=f"store_{selected_dept}_{mod}"):
                    curr_selected.append(mod)
            
            st.markdown("---")
            calculated_price = 500 + (len(curr_selected) * 150)
            if current_tenant and isinstance(current_tenant, dict):
                current_tenant["price_usd"] = calculated_price
            
            st.markdown(f"### 💳 試算：【{clean_dept_name}】選定 `{len(curr_selected)}` 項模組 ➔ 該部門每月費用：**`$ {calculated_price} USD`**")
            
            if st.form_submit_button(f"💾 立即儲存【{clean_dept_name}】的模組配置", type="primary", use_container_width=True):
                if "dept_modules_db" not in current_tenant:
                    current_tenant["dept_modules_db"] = {}
                current_tenant["dept_modules_db"][selected_dept] = curr_selected
                st.success(f"🎉 成功！【{clean_dept_name}】的專屬功能已完美對應並儲存！")
