# modules/app_store.py - 租戶專屬的自由組織圖拼圖板與模組市集
import streamlit as st
import pandas as pd

def render_app_store(current_tenant=None, all_departments=None):
    """
    租戶專屬介面：自由組織圖建構與 ERP 功能拼圖隨選 (Org-Chart Builder & App Store)
    """
    st.info("💡 *說明：這是該租戶專屬的【自由組織圖與功能拼圖配置台】。您可以先在上方自行新增與建構公司組織架構，接著在下方點選該部門，勾選專屬的 ERP 功能模組！*")
    
    if "global_tenants_db" not in st.session_state:
        st.session_state.global_tenants_db = {}
    
    if not current_tenant:
        current_tenant = "裕豐電機工業 (Reetech Industrial)"
        
    if current_tenant not in st.session_state.global_tenants_db:
        st.session_state.global_tenants_db[current_tenant] = {
            "edition_name": "🚀 旗艦企業版 (Enterprise)",
            "price_usd": 2500.0,
            "custom_org_chart": [
                "👑 董事會 / CEO Office",
                "🛠️ 工程部",
                "🔬 設計部",
                "🏭 生產部",
                "📦 倉庫組",
                "🔩 板金組"
            ],
            "dept_modules_db": {}
        }
        
    tenant_data = st.session_state.global_tenants_db[current_tenant]
    
    if "custom_org_chart" not in tenant_data:
        tenant_data["custom_org_chart"] = ["👑 董事會 / CEO Office", "🛠️ 工程部", "🏭 生產部"]
        
    if "dept_modules_db" not in tenant_data:
        tenant_data["dept_modules_db"] = {}

    st.markdown("---")
    
    # ==========================================================
    # 🏢 第一區塊：租戶自定義組織圖自由拼裝區
    # ==========================================================
    st.markdown("### 🏢 第一步：自由建構與拼裝您的企業組織架構")
    
    col_builder_1, col_builder_2 = st.columns([1.5, 1])
    
    with col_builder_1:
        st.markdown("📌 **目前該租戶已建立的組織部門清單**：")
        current_org_list = tenant_data["custom_org_chart"]
        
        for idx, dept in enumerate(current_org_list):
            c_d1, c_d2 = st.columns([4, 1])
            with c_d1:
                st.markdown(f"🔹 **{dept}**")
            with c_d2:
                if st.button("🗑️ 刪除", key=f"del_dept_{current_tenant}_{idx}"):
                    current_org_list.pop(idx)
                    st.session_state.global_tenants_db[current_tenant] = tenant_data
                    st.rerun()
                    
    with col_builder_2:
        st.markdown("➕ **新增自訂部門 / 單位**")
        with st.form(f"add_dept_form_{current_tenant}"):
            new_dept_name = st.text_input("輸入部門或組別名稱", placeholder="例如：海外事業處 / 塗裝組")
            if st.form_submit_button("➕ 加入組織圖拼圖板", type="primary", use_container_width=True):
                if new_dept_name and new_dept_name not in current_org_list:
                    current_org_list.append(new_dept_name)
                    tenant_data["custom_org_chart"] = current_org_list
                    st.session_state.global_tenants_db[current_tenant] = tenant_data
                    st.success(f"🎉 成功加入部門 [{new_dept_name}]！")
                    st.rerun()
                else:
                    st.error("❌ 名稱不可為空或已存在！")

    st.markdown("---")
    
    # ==========================================================
    # 🛒 第二區塊：點選部門並在下方勾選專屬功能拼圖
    # ==========================================================
    st.markdown("### 🛒 第二步：點選上方任一部門，為其配置專屬 ERP 功能拼圖")
    
    if current_org_list:
        selected_dept_target = st.selectbox("🎯 請選擇要配置功能的目標部門/單位", current_org_list, key=f"target_dept_sel_{current_tenant}")
        
        available_erp_modules = [
            "老闆專屬現金流與 AR/AP 逾期預警看板",
            "即時綜合損益與動態成本分攤 (P&L)",
            "階層式物料清單 (BOM) 與版本控管",
            "專案 WBS 預算超支防呆與成本追蹤",
            "多據點條碼掃描入庫/出庫/調撥 (WMS)",
            "生產工單派發、製程報工與稼動率 (MES)",
            "工程專案 WBS 合約與下包商點工計價",
            "全方位數位簽核中心與多級呈核路由 (BPM)",
            "溫室氣體盤查 (ESG 範疇一二三) 與碳排計算"
        ]
        
        saved_mods = tenant_data["dept_modules_db"].get(selected_dept_target, [])
        
        with st.form(f"form_modules_{current_tenant}_{selected_dept_target}"):
            st.markdown(f"#### 📌 勾選【{selected_dept_target}】需要的 ERP 功能模組：")
            
            temp_selected = []
            for mod in available_erp_modules:
                is_checked = mod in saved_mods
                if st.checkbox(mod, value=is_checked, key=f"mod_chk_{current_tenant}_{selected_dept_target}_{mod}"):
                    temp_selected.append(mod)
            
            st.markdown("---")
            if st.form_submit_button(f"💾 儲存【{selected_dept_target}】的功能配置", type="primary", use_container_width=True):
                tenant_data["dept_modules_db"][selected_dept_target] = temp_selected
                st.session_state.global_tenants_db[current_tenant] = tenant_data
                st.success(f"🎉 成功！【{selected_dept_target}】的功能拼圖已儲存並即時生效！")
                st.rerun()
    else:
        st.warning("⚠️ 目前組織圖中尚未建立任何部門，請先在上方新增部門。")

    # ==========================================================
    # 📋 第三區塊：全公司組織與拼圖總覽暨版本訂閱金額結算
    # ==========================================================
    st.markdown("---")
    st.markdown(f"### 📋 【{current_tenant}】全公司組織架構與功能總覽")
    
    active_db = tenant_data.get("dept_modules_db", {})
    summary_data = []
    for d_name in current_org_list:
        m_list = active_db.get(d_name, [])
        summary_data.append({
            "自訂組織部門": d_name,
            "已開通模組數": f"{len(m_list)} 項",
            "功能明細": ", ".join(m_list) if m_list else "尚未選擇功能"
        })
        
    if summary_data:
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
    
    # 版本與金額結算設定
    with st.form(f"version_price_form_{current_tenant}"):
        st.markdown("#### 🏷️ 租戶版本名稱與訂閱金額結算設定")
        v1, v2 = st.columns(2)
        with v1:
            custom_name = st.text_input("自訂銷售版本名稱", value=tenant_data.get("edition_name", "🚀 旗艦企業版 (Enterprise)"))
        with v2:
            custom_price = st.number_input("設定每月總訂閱金額 (USD)", value=float(tenant_data.get("price_usd", 2500.0)), step=100.0)
            
        if st.form_submit_button("💾 儲存版本名稱與總訂閱金額設定", type="primary", use_container_width=True):
            tenant_data["edition_name"] = custom_name
            tenant_data["price_usd"] = custom_price
            st.session_state.global_tenants_db[current_tenant] = tenant_data
            st.success(f"🎉 成功更新！版本已設為 [{custom_name}]，總訂閱金額 `$ {custom_price} USD` 已同步！")
            st.rerun()
