import streamlit as st

def render_pricing_hub():
    """
    SaaS 平台總控台：全球定價策略與方案模組自訂 (Pricing App Store)
    負責統一管理全平台的訂閱方案、基本底價、預設包含的樂高模組，以及全平台大合集庫。
    """
    st.markdown("## ⚙️ SaaS 平台總控台：全球定價策略與方案模組自訂 (Pricing App Store)")
    st.info("💡 *在此處統一管理【全功能模組大合集庫】，並為【旗艦版】、【正式商業版】與【標準訂閱版】自訂預設解鎖的樂高模組與每月基本定價！*")
    
    # 建立分頁籤：各大方案 + 全平台模組庫管理
    plan_tabs = st.tabs(list(st.session_state.global_plans_db.keys()) + ["🌟 管理全平台大合集模組庫 (Master Library)"])
    master_lib = st.session_state.master_module_library
    
    # 1. 編輯各大訂閱方案 (旗艦版、正式商業版、標準訂閱版)
    for idx, (plan_name, plan_data) in enumerate(st.session_state.global_plans_db.items()):
        with plan_tabs[idx]:
            with st.form(f"form_plan_{plan_name}"):
                st.markdown(f"### 📦 編輯商業方案：{plan_name}")
                
                col_p1, col_p2 = st.columns([2, 1])
                with col_p1:
                    p_desc = st.text_input("方案商業描述說明", value=plan_data["description"], key=f"desc_{plan_name}")
                with col_p2:
                    p_price = st.number_input("每月基本定價 (USD $)", value=float(plan_data["base_price"]), step=10.0, key=f"price_{plan_name}")
                
                st.markdown("---")
                st.markdown("#### 🧱 從【全平台大合集模組庫】中勾選此方案預設解鎖的模組：")
                
                selected_plan_mods = []
                for cat_name, mod_list in master_lib.items():
                    st.markdown(f"**{cat_name}**")
                    cols_m = st.columns(3)
                    for m_idx, mod in enumerate(mod_list):
                        with cols_m[m_idx % 3]:
                            # 判斷是否在此方案的預設包含清單中
                            is_checked = mod in plan_data["included_modules"]
                            if st.checkbox(mod, value=is_checked, key=f"p_mod_{plan_name}_{mod}"):
                                selected_plan_mods.append(mod)
                    st.markdown("---")
                            
                # 商業計費說明與儲存按鈕
                st.markdown(f"💳 **當前方案試算**：基本底價 `$ {p_price} USD` 含 `{len(selected_plan_mods)}` 項核心模組。")
                
                if st.form_submit_button(f"💾 立即寫入資料庫：更新【{plan_name}】定價與模組規則", type="primary", use_container_width=True):
                    st.session_state.global_plans_db[plan_name]["description"] = p_desc
                    st.session_state.global_plans_db[plan_name]["base_price"] = p_price
                    st.session_state.global_plans_db[plan_name]["included_modules"] = selected_plan_mods
                    st.success(f"🎉 成功將 [{plan_name}] 的商業定價與模組規則寫入全域資料庫！")
                    st.rerun()
                    
    # 2. 管理全平台大合集模組庫 (Master Library)
    with plan_tabs[-1]:
        st.markdown("### 🌟 全平台獨立模組庫管理 (Master Module Library)")
        st.info("💡 *在此處新增或檢視市面上所有的 ERP 功能模組。新增後，所有方案定價與租戶部門市集將自動同步串聯！*")
        
        with st.form("add_master_mod_form"):
            col_m1, col_m2 = st.columns([1, 2])
            with col_m1:
                new_cat = st.selectbox("選擇模組所屬分類", list(master_lib.keys()))
            with col_m2:
                new_mod_name = st.text_input("新增 ERP 模組名稱", placeholder="例：AI 智慧工安影像辨識模組")
                
            if st.form_submit_button("➕ 增加至全平台大合集庫", type="primary", use_container_width=True):
                if new_mod_name and new_mod_name not in master_lib[new_cat]:
                    master_lib[new_cat].append(new_mod_name)
                    st.success(f"🎉 成功新增模組 [{new_mod_name}] 至全平台大合集庫！")
                    st.rerun()
                elif not new_mod_name:
                    st.warning("⚠️ 請輸入模組名稱。")
                else:
                    st.warning("⚠️ 該模組名稱已存在於分類中。")
                    
        st.markdown("---")
        st.markdown("#### 📋 目前全平台大合集庫中的所有模組總覽：")
        for cat_n, m_list in master_lib.items():
            st.markdown(f"**{cat_n}**（共 {len(m_list)} 項）：")
            st.markdown("`" + "`, `".join(m_list) + "`")
            st.markdown("")
