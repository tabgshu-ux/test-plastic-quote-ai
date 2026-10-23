# modules/app_store.py - 樂高模組拼圖市集與外掛調用程式
import streamlit as st
import pandas as pd

def render_app_store(current_tenant=None, all_departments=None):
    """
    樂高積木式模組市集與版本定價中心 (App Store)
    外掛模組化架構：從 industries/ 資料夾動態載入產業外掛。
    """
    st.info("💡 *說明：請在下方選擇產業別外掛，左側展開對應部門，右側勾選拼圖模組，下方即時總覽與版本金額設定。*")
    
    # 確保租戶資料庫安全連動
    if "global_tenants_db" not in st.session_state:
        st.session_state.global_tenants_db = {}
    
    # 若未傳入指定租戶，預設抓取第一個或建立暫存
    if not current_tenant:
        current_tenant = "裕豐電機工業 (Reetech Industrial)"
        
    if current_tenant not in st.session_state.global_tenants_db:
        st.session_state.global_tenants_db[current_tenant] = {
            "edition_name": "🚀 旗艦企業版 (Enterprise)",
            "price_usd": 2500.0,
            "dept_modules_db": {}
        }
        
    tenant_data = st.session_state.global_tenants_db[current_tenant]
    if "dept_modules_db" not in tenant_data:
        tenant_data["dept_modules_db"] = {}

    # 動態引入 industries/tech_it.py 外掛
    try:
        import industries.tech_it as tech_module
        tech_matrix = getattr(tech_module, "INDUSTRY_DATA", {
            "name": "二、 科技與軟體業（Tech & Software / SaaS）",
            "desc": "強調敏捷開發與訂閱制管理。",
            "departments": ["👑 董事會 / CEO Office", "🔬 產品研發處", "💻 資料與運維處", "🛠️ 工程部 (Engineering Department)"]
        })
    except Exception:
        tech_matrix = {
            "name": "二、 科技與軟體業（Tech & Software / SaaS）",
            "desc": "科技軟體業外掛載入中",
            "departments": ["👑 董事會 / CEO Office", "🔬 產品研發處", "🛠️ 工程部 (Engineering Department)"]
        }

    industries_options = {
        tech_matrix["name"]: tech_matrix,
        "一、 製造與代工業（Manufacturing & OEM）": {
            "desc": "ERP 系統最複雜、層級最嚴謹的傳統大宗。",
            "departments": ["👑 董事會 / CEO Office", "💰 資產財務處", "🏭 生產製造處", "🛠️ 工程部 (Engineering Department)"]
        }
    }

    selected_industry_name = st.selectbox("📂 請選擇企業所屬的全球產業別（來自 industries/ 外掛）", list(industries_options.keys()), key=f"ind_select_{current_tenant}")
    current_industry_info = industries_options[selected_industry_name]
    current_dept_list = current_industry_info["departments"]
    
    st.markdown(f"📌 **外掛產業說明**：*{current_industry_info['desc']}*")
    st.markdown("---")

    col_left, col_right = st.columns([1.1, 2.2])
    
    with col_left:
        st.markdown("### 🏢 選擇目標部門 / 管理層")
        selected_dept = st.radio(
            "部門選擇",
            current_dept_list,
            index=0,
            label_visibility="collapsed",
            key=f"dept_radio_{current_tenant}"
        )
        
    with col_right:
        clean_dept_name = selected_dept.split('(')[0].strip()
        st.markdown(f"### 🛒 【{clean_dept_name}】樂高拼圖模組配置")
        
        available_mods_for_dept = [
            "老闆專屬現金流與 AR/AP 逾期預警看板",
            "即時綜合損益與動態成本分攤 (P&L)",
            "階層式物料清單 (BOM) 與版本控管",
            "專案 WBS 預算超支防呆與成本追蹤",
            "多據點條碼掃描入庫/出庫/調撥 (WMS)",
            "生產工單派發、製程報工與稼動率 (MES)",
            "工程專案 WBS 合約與下包商點工計價",
            "全方位數位簽核中心與多級呈核路由 (BPM)"
        ]
        
        saved_mods = tenant_data["dept_modules_db"].get(selected_dept, [])
        
        with st.form(f"form_store_{current_tenant}_{selected_dept}"):
            st.markdown(f"#### 📌 勾選【{clean_dept_name}】需要的 ERP 功能拼圖：")
            
            temp_selected = []
            for mod in available_mods_for_dept:
                is_currently_checked = mod in saved_mods
                if st.checkbox(mod, value=is_currently_checked, key=f"chk_mod_{current_tenant}_{selected_dept}_{mod}"):
                    temp_selected.append(mod)
            
            st.markdown("---")
            if st.form_submit_button(f"💾 立即加入：儲存【{clean_dept_name}】的功能拼圖", type="primary", use_container_width=True):
                tenant_data["dept_modules_db"][selected_dept] = temp_selected
                st.session_state.global_tenants_db[current_tenant] = tenant_data
                st.success(f"🎉 成功！【{current_tenant} - {clean_dept_name}】的功能拼圖已儲存！")
                st.rerun()

    # ========================================================
    # 📋 下方區塊：總覽與版本金額設定中心
    # ========================================================
    st.markdown("---")
    st.markdown(f"### 📋 【{current_tenant}】已開通部門、功能總覽與版本金額設定")
    
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
        st.warning("⚠️ 目前該租戶尚未在上方勾選任何部門模組。")
    
    # 版本設定表單
    with st.form(f"version_price_form_{current_tenant}"):
        st.markdown("#### 🏷️ 租戶版本名稱與訂閱金額結算設定")
        v1, v2 = st.columns(2)
        with v1:
            custom_name = st.text_input("自訂銷售版本名稱", value=tenant_data.get("edition_name", "🚀 旗艦企業版 (Enterprise)"))
        with v2:
            custom_price = st.number_input("設定每月總訂閱金額 (USD)", value=float(tenant_data.get("price_usd", 2500.0)), step=100.0)
            
        if st.form_submit_button("💾 儲存該租戶版本名稱與總訂閱金額", type="primary", use_container_width=True):
            tenant_data["edition_name"] = custom_name
            tenant_data["price_usd"] = custom_price
            st.session_state.global_tenants_db[current_tenant] = tenant_data
            st.success(f"🎉 成功更新 [{current_tenant}]！版本已設為 [{custom_name}]，總訂閱金額 `$ {custom_price} USD` 已同步！")
            st.rerun()
