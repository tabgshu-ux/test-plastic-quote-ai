import streamlit as st
import pandas as pd
import uuid

# 因為 app_store.py 與 industries_matrix.py 同樣都在 modules/ 資料夾內，直接同級引用！
import industries_matrix as matrix

def render_app_store(current_tenant=None, all_departments=None):
    """
    樂高積木式模組市集與版本定價中心 (App Store)
    外掛模組化架構：從同級的 modules/industries_matrix.py 引入 12 大產業與部門矩陣。
    """
    st.markdown("## 🧩 全球多產業 1~4 級組織架構與樂高拼圖市集 (App Store)")
    st.info("💡 *說明：請先在下方下拉選單選擇企業所屬的 12 大產業別外掛母體；接著在左側完整展開所有部門供客戶點選，右側勾選專屬 ERP 功能拼圖，儲存後下方將即時總覽已開通的部門、功能與版本金額。*")
    
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

    # 1. 從同目錄的 industries_matrix 讀取 12 大產業別
    industry_keys = list(matrix.GLOBAL_INDUSTRIES_MATRIX.keys())
    selected_industry = st.selectbox("📂 請選擇企業所屬的全球產業別外掛母體", industry_keys)
    
    industry_info = matrix.GLOBAL_INDUSTRIES_MATRIX[selected_industry]
    current_dept_list = industry_info["departments"]
    
    st.markdown(f"📌 **產業說明**：*{industry_info['desc']}*")
    st.markdown("---")

    col_left, col_right = st.columns([1.1, 2.2])
    
    with col_left:
        st.markdown("### 🏢 選擇目標部門 / 管理層")
        # 嚴格使用 st.radio 讓該產業的所有部門完全展開顯示
        selected_dept = st.radio(
            "部門選擇",
            current_dept_list,
            index=0,
            label_visibility="collapsed"
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
            "ISO 標準文件版本管制與 CAPA 矯正預防措施",
            "溫室氣體盤查 (ESG 範疇一二三) 與碳排當量計算",
            "全方位數位簽核中心與多級呈核路由 (BPM)",
            "多階層動態佣金與通路分潤計算引擎"
        ]
        
        saved_mods = tenant_data["dept_modules_db"].get(selected_dept, [])
        
        with st.form(f"form_store_{selected_dept}"):
            st.markdown(f"#### 📌 勾選【{clean_dept_name}】需要的 ERP 功能拼圖：")
            
            temp_selected = []
            for mod in available_mods_for_dept:
                is_currently_checked = mod in saved_mods
                if st.checkbox(mod, value=is_currently_checked, key=f"chk_{selected_industry}_{selected_dept}_{mod}"):
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
    st.info("💡 *在此檢視目前已加入的部門與功能明細，並直接 en 下方設定該租戶的自訂銷售版本名稱與每月總訂閱金額 (USD)。*")

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
