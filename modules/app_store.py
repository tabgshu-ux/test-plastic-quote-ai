# modules/app_store.py - 企業實務功能模組包市集與動態費用試算引擎
import streamlit as st
import pandas as pd

def render_app_store(current_tenant=None, all_departments=None):
    st.info("💡 *說明：請在此先設定該租戶的所屬產業別，並在上方自由建構組織部門。接著在下方點選目標部門，勾選對應的企業實務功能模組包，系統將自動進行動態費用結算！*")
    
    if "global_tenants_db" not in st.session_state:
        st.session_state.global_tenants_db = {}
    
    if not current_tenant:
        current_tenant = "裕豐電機工業 (Reetech Industrial)"
        
    if current_tenant not in st.session_state.global_tenants_db:
        st.session_state.global_tenants_db[current_tenant] = {
            "edition_name": "🚀 旗艦企業版 (Enterprise)",
            "base_price_usd": 1500.0,
            "industry_type": "🏭 製造與工程重工業 (Manufacturing & Engineering)",
            "custom_org_chart": ["👑 董事會 / CEO Office", "👥 管理部 (Management)", "📋 電子簽核中心", "📐 工程與設計管理中心", "🏭 生產部 (Production)"],
            "dept_modules_db": {}
        }
        
    tenant_data = st.session_state.global_tenants_db[current_tenant]
    
    # 確保基本欄位存在
    if "industry_type" not in tenant_data:
        tenant_data["industry_type"] = "🏭 製造與工程重工業 (Manufacturing & Engineering)"
    if "custom_org_chart" not in tenant_data:
        tenant_data["custom_org_chart"] = ["👑 董事會 / CEO Office", "👥 管理部 (Management)", "📐 工程與設計管理中心", "🏭 生產部 (Production)"]
    if "dept_modules_db" not in tenant_data:
        tenant_data["dept_modules_db"] = {}
    if "base_price_usd" not in tenant_data:
        tenant_data["base_price_usd"] = 1500.0

    st.markdown("---")
    
    # ==========================================================
    # 🌐 第零步：選擇企業所屬產業別
    # ==========================================================
    st.markdown("### 🌐 第零步：設定企業所屬產業別")
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
        st.success("🎉 產業別已更新！")
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
            new_dept_name = st.text_input("輸入部門或組別名稱", placeholder="例如：資訊管理部 / 塗裝組")
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
    # 🛒 第二步：配置四大核心模組包與實務功能
    # ==========================================================
    st.markdown("### 🛒 第二步：點選目標部門，為其配置企業實務 ERP 功能拼圖包")
    
    if current_org_list:
        selected_target_dept = st.selectbox("🎯 請選擇要配置功能的目標部門/單位", current_org_list, key=f"target_dept_sel_{current_tenant}")
        
        # 對應您實際開發的四大核心模組包與豐富細項
        comprehensive_modules_suites = {
            "👑 總經理室 / 董事會戰情室模組包": [
                "原料價格與 Gemini 智慧採購顧問 (LME銅價與匯率避險)",
                "財務類顯示資料 (AR/AP 應收應付總額與毛利稅後淨利)",
                "工程專案進度與現場異常監控看板"
            ],
            "👥 管理部與跨國人事薪資模組包 (含越南法規)": [
                "公司重要公告與佈告欄管理",
                "員工個人檔案與人事管理 (含越南勞動法稅號與登記醫院)",
                "廠內員工固定打卡與出勤紀錄",
                "外勤出勤統計與工地人數監控 (含GPS拍照防呆)",
                "幹部宿舍伙食與採購控管",
                "廠區與工作廠區管理 / 廠區車輛進出口門禁與派車審核",
                "車輛維修保養紀錄 / 固定資產與設備管理",
                "採購與應付帳款 (AP) / 應收帳款與對帳管理中心",
                "越南稅務標準財務報表 (Thông tư 200) / 電子發票綜合管理",
                "員工薪資計算與保險扣除 (支援外派雙薪與第二幣別)"
            ],
            "📋 全公司電子簽核中心模組包": [
                "提交請假、採購請 PR、公務派車與專案報撥",
                "待審核案件審查 (主管專用區)",
                "簽核進度即時追蹤 / 保全門禁車輛放行查驗"
            ],
            "📐 工程與設計管理中心模組包": [
                "工程主管戰情室與案場管理 (合約總額與案場一覽)",
                "工程專案報價系統 (支援多幣別 VND/USD/RMB/TWD)",
                "現場外勤打卡與作業登記 (GPS定位與強制拍照)",
                "施工日報表與點工點料登記",
                "AI 施工照片辨識與安衛稽核",
                "工程師證照與施工機具檢驗到期預警",
                "配電盤電氣與機構設計圖庫 Storage 與生產下發",
                "配電盤 BOM 零件自動展開與採購連動",
                "外包商計價與工進估驗管理 (勞動法計薪)",
                "FAT / SAT 出廠與現場驗收管理 (QR Code 驗收)"
            ],
            "🏭 生產製造與廠區品管模組包": [
                "倉庫庫存與資材條碼管理 (WMS)",
                "板金加工組工單與條碼管理 (進度燈號與圖面附檔)",
                "粉體塗裝烤漆組品管與製程追蹤 (水池管制與烤箱固化)",
                "配電盤組裝配線組與拍照入庫 (完工拍照自動入庫)"
            ],
            "⚙️ IT 系統管理與動態設定模組包": [
                "系統角色權限與模組開關設定 (RBAC)",
                "客戶 ERP 模組授權與功能開關",
                "系統雲端 Storage 儲存庫路徑與 API 串聯動態設定"
            ]
        }
        
        saved_mods = tenant_data["dept_modules_db"].get(selected_target_dept, [])
        
        with st.form(f"form_modules_{current_tenant}_{selected_target_dept}"):
            st.markdown(f"#### 📌 為【{selected_target_dept}】勾選實務 ERP 功能模組包：")
            
            temp_selected = []
            for suite_name, mod_list in comprehensive_modules_suites.items():
                st.markdown(f"##### **{suite_name}**")
                for mod in mod_list:
                    is_checked = mod in saved_mods
                    if st.checkbox(mod, value=is_checked, key=f"mod_chk_{current_tenant}_{selected_target_dept}_{mod}"):
                        temp_selected.append(mod)
                st.markdown("")
            
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
    base_fee = float(tenant_data.get("base_price_usd", 1500.0))
    addon_fee_per_module = 50.0  # 每個細項實務模組單價
    calculated_total_price = base_fee + (total_selected_modules_count * addon_fee_per_module)
    
    st.info(f"💰 **系統即時訂閱費用試算**：基礎平台費 ($ {base_fee} USD) + 已選配實務功能 ({total_selected_modules_count} 項 × $ {addon_fee_per_module} USD) = **總計每月 $ {calculated_total_price} USD**")
