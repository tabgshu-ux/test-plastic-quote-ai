import streamlit as st
import uuid

def render_app_store(current_tenant, all_departments=None):
    """
    樂高積木式模組市集 (App Store)
    精準對應：左側為製造業真實部門（研發部、財務部、行銷部、業務部、生產部等），右側顯示該部門專屬的 ERP 拼圖功能。
    """
    st.markdown("## 🧩 企業部門與樂高積木模組市集 (App Store)")
    st.info("💡 *說明：請從左側點選您企業的實際部門（如研發部、財務部、業務部、生產部等），右側就會精準顯示該部門專屬的 ERP 功能拼圖，供您勾選與即時計費！*")
    
    col_left, col_right = st.columns([1, 2.2])
    
    # 您指定製造業標準部門
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
        
        # 依據不同部門，精準對應其專屬的功能拼圖
        department_modules_mapping = {
            "研發部": [
                "階層式物料清單 (BOM) 與版本控管",
                "專案 WBS 預算超支防呆與 CapEx/OpEx 轉列引擎",
                "雙層式報價與多幣別換算引擎"
            ],
            "財務部": [
                "老闆專屬現金流與 AR/AP 逾期預警看板",
                "即時綜合損益與動態成本分攤 (P&L)",
                "動態加班與在地化法規薪資引擎",
                "全方位數位簽核中心與多級呈核路由 (BPM)"
            ],
            "行銷部": [
                "全球股市、匯率與原料期貨行情 API 串聯",
                "溫室氣體盤查與碳排當量計算 (ESG)",
                "水資源、廢棄物監控與永續報告書數據導出"
            ],
            "業務部": [
                "雙層式報價與多幣別換算引擎",
                "老闆專屬現金流與 AR/AP 逾期預警看板",
                "多階層動態佣金與通路分潤計算引擎"
            ],
            "生產部": [
                "製程工單派發、報工與設備稼動率監控 (MES)",
                "多據點條碼掃描入庫/出庫/調撥 (WMS)",
                "ISO 標準文件版本管制與 CAPA 矯正預防措施"
            ],
            "供應鏈與倉儲部": [
                "多據點條碼掃描入庫/出庫/調撥 (WMS)",
                "老闆專屬現金流與 AR/AP 逾期預警看板",
                "固定資產條碼化、折舊與廠區門禁派車"
            ],
            "品保/品管部": [
                "ISO 標準文件版本管制與 CAPA 矯正預防措施",
                "量測儀器校驗履歷與供應商 QCD 評鑑",
                "製程工單派發、報工與設備稼動率監控 (MES)"
            ],
            "人力資源與總務部": [
                "動態加班與在地化法規薪資引擎",
                "全方位數位簽核中心與多級呈核路由 (BPM)",
                "固定資產條碼化、折舊與廠區門禁派車"
            ]
        }
        
        # 找出當前選擇部門對應的功能清單
        matched_key = next((k for k in department_modules_mapping if k in selected_dept), "研發部")
        available_mods_for_dept = department_modules_mapping[matched_key]
        
        saved_dept_mods = current_tenant.get("dept_modules_db", {}).get(selected_dept, [])
        
        with st.form(f"form_store_{selected_dept}"):
            curr_selected = []
            st.markdown(f"#### 📌 勾選【{clean_dept_name}】需要開通的模組：")
            
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
                st.success(f"🎉 成功！【{clean_dept_name}】的專屬樂高拼圖模組已成功寫入並即時串連！")
