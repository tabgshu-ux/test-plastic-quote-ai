# modules/app_store.py - 產業動態過濾與多維度功能拼圖市集（升級版）
import streamlit as st
import pandas as pd

def render_app_store(current_tenant=None, all_departments=None):
    st.info("💡 *說明：請先設定該租戶的【所屬產業別】，接著在上方自由建構組織部門，並點選對應部門勾選該單位的專屬功能拼圖！*")
    
    if "global_tenants_db" not in st.session_state:
        st.session_state.global_tenants_db = {}
    
    if not current_tenant:
        current_tenant = "裕豐電機工業 (Reetech Industrial)"
        
    if current_tenant not in st.session_state.global_tenants_db:
        st.session_state.global_tenants_db[current_tenant] = {
            "edition_name": "🚀 旗艦企業版 (Enterprise)",
            "price_usd": 2500.0,
            "industry_type": "🏭 製造與工程重工業 (Manufacturing & Engineering)",
            "custom_org_chart": ["👑 董事會 / CEO Office", "🛠️ 工程部", "🏭 生產部", "📦 倉庫組"],
            "dept_modules_db": {}
        }
        
    tenant_data = st.session_state.global_tenants_db[current_tenant]
    
    if "industry_type" not in tenant_data:
        tenant_data["industry_type"] = "🏭 製造與工程重工業 (Manufacturing & Engineering)"
    if "custom_org_chart" not in tenant_data:
        tenant_data["custom_org_chart"] = ["👑 董事會 / CEO Office", "🛠️ 工程部", "🏭 生產部"]
    if "dept_modules_db" not in tenant_data:
        tenant_data["dept_modules_db"] = {}

    st.markdown("---")
    
    # ==========================================================
    # 🌟 第零步：選擇企業所屬產業別
    # ==========================================================
    st.markdown("### 🌐 第零步：設定企業所屬產業別（決定底層可用功能庫）")
    industries_list = [
        "🏭 製造與工程重工業 (Manufacturing & Engineering)",
        "💻 科技軟體與 SaaS 服務業 (Tech & Software)",
        "🏗️ 營造與大型工程專案業 (Construction & Projects)",
        "📦 批發零售與多據點物流業 (Retail & Distribution)"
    ]
    
    current_ind = tenant_data.get("industry_type", industries_list[0])
    selected_industry = st.selectbox("選擇公司核心產業別", industries_list, index=industries_list.index(current_ind) if current_ind in industries_list else 0, key=f"ind_sel_{current_tenant}")
    
    if selected_industry != current_ind:
        tenant_data["industry_type"] = selected_industry
        st.session_state.global_tenants_db[current_tenant] = tenant_data
        st.success("🎉 產業別已更新，功能拼圖庫已自動切換！")
        st.rerun()

    st.markdown("---")
    
    # ==========================================================
    # 🏢 第一步：自由建構與拼裝組織圖
    # ==========================================================
    st.markdown("### 🏢 第一步：自由建構與拼裝您的企業組織架構")
    
    col_b1, col_b2 = st.columns([1.5, 1])
    with col_b1:
        st.markdown("📌 **目前該租戶已建立的組織部門清單**：")
        current_org_list = tenant_data["custom_org_chart"]
        
        for idx, dept in enumerate(current_org_list):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"🔹 **{dept}**")
            with c2:
                if st.button("🗑️ 刪除", key=f"del_dept_{current_tenant}_{idx}"):
                    current_org_list.pop(idx)
                    tenant_data["custom_org_chart"] = current_org_list
                    st.session_state.global_tenants_db[current_tenant] = tenant_data
                    st.rerun()
                    
    with col_b2:
        st.markdown("➕ **新增自訂部門 / 單位**")
        with st.form(f"add_dept_form_{current_tenant}"):
            new_dept_name = st.text_input("輸入部門或組別名稱", placeholder="例如：塗裝組 / 外地施工隊")
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
    # 🛒 第二步：根據產業與部門，動態勾選功能拼圖
    # ==========================================================
    st.markdown("### 🛒 第二步：點選目標部門，為其配置專屬 ERP 功能拼圖")
    
    if current_org_list:
        selected_target_dept = st.selectbox("🎯 請選擇要配置功能的目標部門/單位", current_org_list, key=f"target_dept_sel_{current_tenant}")
        
        # 依據產業別提供精準的模組清單（包含您要求的各項新功能）
        industry_modules_mapping = {
            "🏭 製造與工程重工業 (Manufacturing & Engineering)": [
                "👑 老闆專屬現金流與 AR/AP 逾期預警看板",
                "📊 即時綜合損益與動態成本分攤 (P&L)",
                "📦 倉庫管理與多據點條碼掃描入庫/出庫 (WMS)",
                "🔬 階層式物料清單 (BOM) 與版本控管",
                "🏭 生產工單派發、製程報工與機台稼動率 (MES)",
                "📐 工程設計圖上傳與主管線上審閱中心",
                "📍 工程/外地人員 GPS 定位打卡與工時回報 (選配)",
                "👥 員工上班資料、出勤與人事薪資管理",
                "📝 全方位數位簽核中心與多級呈核路由 (BPM)"
            ],
            "💻 科技軟體與 SaaS 服務業 (Tech & Software)": [
                "👑 老闆專屬 ARR/MRR 訂閱營收與現金流看板",
                "💻 研發專案分工與 Jira/GitHub 整合看板",
                "📍 遠距/外地員工彈性 GPS 打卡與工時回報",
                "👥 員工上班資料、出勤與人事薪資管理",
                "🌟 客戶成功 (CS) 續約率追蹤與支援服務系統",
                "📝 全方位數位簽核中心 (BPM)"
            ],
            "🏗️ 營造與大型工程專案業 (Construction & Projects)": [
                "👑 老闆專屬工程專案總預算與現金流看板",
                "🏗️ 工程專案 WBS 合約、進度與下包商點工計價",
                "📐 施工設計圖上傳與主管線上批示審閱",
                "📍 工地現場人員 GPS 打卡與出勤回報 (選配)",
                "📦 工地材料倉儲與機具進出管理 (WMS)",
                "👥 員工上班資料、出勤與人事薪資管理"
            ]
        }
        
        available_modules = industry_modules_mapping.get(selected_industry, industry_modules_mapping["🏭 製造與工程重工業 (Manufacturing & Engineering)"])
        saved_mods = tenant_data["dept_modules_db"].get(selected_target_dept, [])
        
        with st.form(f"form_modules_{current_tenant}_{selected_target_dept}"):
            st.markdown(f"#### 📌 為【{selected_target_dept}】勾選專屬 ERP 功能拼圖：")
            
            temp_selected = []
            for mod in available_modules:
                is_checked = mod in saved_mods
                if st.checkbox(mod, value=is_checked, key=f"mod_chk_{current_tenant}_{selected_target_dept}_{mod}"):
                    temp_selected.append(mod)
            
            st.markdown("---")
            if st.form_submit_button(f"💾 儲存【{selected_target_dept}】的功能配置", type="primary", use_container_width=True):
                tenant_data["dept_modules_db"][selected_target_dept] = temp_selected
                st.session_state.global_tenants_db[current_tenant] = tenant_data
                st.success(f"🎉 成功！【{selected_target_dept}】的功能拼圖已儲存並即時生效！")
                st.rerun()
    else:
        st.warning("⚠️ 目前組織圖中尚未建立任何部門，請先在上方新增部門。")

    # ==========================================================
    # 📋 第三區塊：全公司總覽與即時費用試算
    # ==========================================================
    st.markdown("---")
    st.markdown(f"### 📋 【{current_tenant}】全公司組織架構與功能總覽")
    
    active_db = tenant_data.get("dept_modules_db", {})
    summary_data = []
    total_selected_modules_count = 0
    for d_name in current_org_list:
        m_list = active_db.get(d_name, [])
        total_selected_modules_count += len(m_list)
        summary_data.append({
            "自訂組織部門": d_name,
            "已開通模組數": f"{len(m_list)} 項",
            "功能明細": ", ".join(m_list) if m_list else "尚未選擇功能"
        })
        
    if summary_data:
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
        
    # 動態模組費用試算
    base_fee = 1500.0  # 基礎平台費
    addon_fee_per_module = 150.0  # 每個勾選的功能拼圖單價
    calculated_total_price = base_fee + (total_selected_modules_count * addon_fee_per_module)
    
    st.info(f"💰 **系統即時訂閱費用試算**：基礎平台費 ($ {base_fee} USD) + 已選配拼圖 ({total_selected_modules_count} 項 × $ {addon_fee_per_module} USD) = **總計每月 $ {calculated_total_price} USD**")
