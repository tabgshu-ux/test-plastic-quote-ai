# modules/app_store.py - 租戶專屬組織圖拼圖板（安全無迴圈版）
import streamlit as st
import pandas as pd

def render_app_store(current_tenant=None, all_departments=None):
    st.info("💡 說明：在此自由新增公司部門（不限階級），並點選部門在下方勾選專屬 ERP 功能拼圖。")
    
    if "global_tenants_db" not in st.session_state:
        st.session_state.global_tenants_db = {}
    
    if not current_tenant:
        current_tenant = "裕豐電機工業 (Reetech Industrial)"
        
    if current_tenant not in st.session_state.global_tenants_db:
        st.session_state.global_tenants_db[current_tenant] = {
            "edition_name": "🚀 旗艦企業版 (Enterprise)",
            "price_usd": 2500.0,
            "custom_org_chart": ["👑 董事會 / CEO Office", "🛠️ 工程部", "🏭 生產部"],
            "dept_modules_db": {}
        }
        
    tenant_data = st.session_state.global_tenants_db[current_tenant]
    
    if "custom_org_chart" not in tenant_data:
        tenant_data["custom_org_chart"] = ["👑 董事會 / CEO Office", "🛠️ 工程部", "🏭 生產部"]
        
    if "dept_modules_db" not in tenant_data:
        tenant_data["dept_modules_db"] = {}

    st.markdown("---")
    st.markdown("### 🏢 第一步：自由建構與拼裝您的企業組織架構")
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown("📌 **已建立的組織部門清單**：")
        current_org_list = tenant_data["custom_org_chart"]
        for idx, dept in enumerate(current_org_list):
            c_d1, c_d2 = st.columns([4, 1])
            with c_d1:
                st.markdown(f"🔹 {dept}")
            with c_d2:
                if st.button("🗑️", key=f"del_{current_tenant}_{idx}"):
                    current_org_list.pop(idx)
                    st.rerun()
                    
    with col2:
        st.markdown("➕ **新增自訂部門**")
        new_dept = st.text_input("輸入部門名稱", key=f"new_dept_input_{current_tenant}")
        if st.button("➕ 加入組織圖", type="primary"):
            if new_dept and new_dept not in current_org_list:
                current_org_list.append(new_dept)
                st.success(f"已新增 [{new_dept}]")
                st.rerun()

    st.markdown("---")
    st.markdown("### 🛒 第二步：點選部門，為其配置專屬 ERP 功能拼圖")
    
    if current_org_list:
        selected_dept = st.selectbox("🎯 選擇目標部門", current_org_list, key=f"sel_dept_{current_tenant}")
        
        available_mods = [
            "老闆專屬現金流與 AR/AP 逾期預警看板",
            "即時綜合損益與動態成本分攤 (P&L)",
            "階層式物料清單 (BOM) 與版本控管",
            "多據點條碼掃描入庫/出庫/調撥 (WMS)",
            "生產工單派發、製程報工與稼動率 (MES)",
            "全方位數位簽核中心與多級呈核路由 (BPM)"
        ]
        
        saved_mods = tenant_data["dept_modules_db"].get(selected_dept, [])
        
        st.markdown(f"#### 📌 勾選【{selected_dept}】的功能模組：")
        temp_selected = []
        for mod in available_mods:
            if st.checkbox(mod, value=(mod in saved_mods), key=f"chk_{current_tenant}_{selected_dept}_{mod}"):
                temp_selected.append(mod)
        
        if st.button(f"💾 儲存【{selected_dept}】的功能配置", type="primary"):
            tenant_data["dept_modules_db"][selected_dept] = temp_selected
            st.success("🎉 儲存成功！")
    else:
        st.warning("⚠️ 請先在上方新增部門。")

    # 版本與金額結算
    st.markdown("---")
    st.markdown("### 🏷️ 租戶版本與訂閱金額結算")
    custom_name = st.text_input("自訂銷售版本名稱", value=tenant_data.get("edition_name", "🚀 旗艦企業版"))
    custom_price = st.number_input("每月總訂閱金額 (USD)", value=float(tenant_data.get("price_usd", 2500.0)))
    if st.button("💾 儲存版本與金額"):
        tenant_data["edition_name"] = custom_name
        tenant_data["price_usd"] = custom_price
        st.success("🎉 版本與金額已更新！")
