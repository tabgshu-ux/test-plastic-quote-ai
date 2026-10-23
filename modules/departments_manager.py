import streamlit as st
import pandas as pd
import uuid

def render_departments_manager(current_tenant):
    # 🌐 讀取目前全域語系（對應 app.py 中的 current_lang 設定）
    current_lang = st.session_state.get("current_lang", "繁體中文")
    
    # 🌐 多語系字典檔支援 (Localization)
    i18n = {
        "繁體中文": {
            "title": "🏢 全球多租戶 SaaS 組織圖智慧市集（多語系與手機優先）",
            "info": "💡 *系統已自動對應您的瀏覽語系，並針對手機與行動裝置優化。您只需用滑鼠切換產業與勾選，即可一秒組裝公司組織圖！*",
            "tab1": "⚡ 1. 全產業標準庫（滑鼠一鍵點選）",
            "tab2": "➕ 2. 特殊部門自訂（備用輸入）",
            "tab3": "🌳 3. 現有組織樹總覽與模組管理",
            "select_ind": "選擇企業所屬產業領域：",
            "apply_btn": "🚀 一鍵套用所選產業組織與拼圖配置",
            "success_apply": "🎉 成功為租戶套用標準 1~4 級組織樹與功能模組！"
        },
        "English": {
            "title": "🏢 Global Multi-Tenant SaaS Org Chart Marketplace (I18n & Mobile-First)",
            "info": "💡 *Optimized for mobile-first experience and multi-lingual translation. Simply select an industry and click to build your organizational chart!*",
            "tab1": "⚡ 1. Industry Standards (Click to Select)",
            "tab2": "➕ 2. Custom Departments (Manual Fallback)",
            "tab3": "🌳 3. Org Tree & Module Management",
            "select_ind": "Select Industry Sector:",
            "apply_btn": "🚀 Apply Selected Industry Org & Modules",
            "success_apply": "🎉 Successfully applied industry standards and module mapping!"
        },
        "Tiếng Việt": {
            "title": "🏢 Trung tâm Sơ đồ Tổ chức SaaS (Đa ngôn ngữ & Ưu tiên di động)",
            "info": "💡 *Tối ưu hóa cho thiết bị di động và hỗ trợ đa ngôn ngữ. Chỉ cần chọn ngành nghề và nhấp để xây dựng sơ đồ tổ chức!*",
            "tab1": "⚡ 1. Tiêu chuẩn ngành (Nhấp để chọn)",
            "tab2": "➕ 2. Tùy chỉnh bộ phận (Thủ công)",
            "tab3": "🌳 3. Quản lý cây tổ chức & Mô-đun",
            "select_ind": "Chọn lĩnh vực ngành nghề:",
            "apply_btn": "🚀 Áp dụng cấu hình tổ chức đã chọn",
            "success_apply": "🎉 Đã áp dụng thành công tiêu chuẩn ngành và mô-đun!"
        }
    }
    
    t = i18n.get(current_lang, i18n["繁體中文"])
    
    st.markdown(f"## {t['title']}")
    st.info(t['info'])
    
    # 初始化組織樹
    if "hierarchical_org_tree" not in current_tenant:
        current_tenant["hierarchical_org_tree"] = []

    # 全產業標準預設庫 (支援手機優先排版與多語系對應)
    industry_presets = {
        "科技資訊業 (Tech & IT)": {
            "desc": "適合軟體研發、系統整合與高科技企業 / Suitable for software & tech",
            "levels": [
                {
                    "level": "1級-最高決策層", 
                    "name": "總經理室 / 營運總部 (HQ & Management)", 
                    "sections": [
                        {"dept": "資訊處 (2級-部)", "sec": "軟體開發科 (3級-科)", "groups": ["前端工程組 (4級-組)", "後端維運組 (4級-組)"]}
                    ], 
                    "modules": ["👑 老闆級即時經營戰情室 (Executive BI)", "👥 員工帳號與權限管理 (RBAC)"]
                }
            ]
        },
        "傳統製造與勞動業 (Traditional Mfg & Labor)": {
            "desc": "適合機械加工、電機製造與工廠現場 / Suitable for manufacturing & plant",
            "levels": [
                {
                    "level": "1級-最高決策層", 
                    "name": "生產製造事業群 (Manufacturing Group)", 
                    "sections": [
                        {"dept": "配電盤製造部 (2級-部)", "sec": "高壓盤組裝科 (3級-科)", "groups": ["第一作業班", "第二測試班"]}
                    ], 
                    "modules": ["🏭 生產製造執行與車間排程 (MES)", "📱 現場基層手機快速回報 (Mobile Field Worker)"]
                }
            ]
        }
    }

    tab_preset, tab_custom, tab_view = st.tabs([t['tab1'], t['tab2'], t['tab3']])

    # Tab 1: 全產業標準庫點選生成 (手機優先響應式排版)
    with tab_preset:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        selected_industry = st.selectbox(t['select_ind'], list(industry_presets.keys()), key="preset_ind_select")
        preset_data = industry_presets[selected_industry]
        st.caption(f"💡 {preset_data['desc']}")

        selected_preset_items = []
        for idx, lvl_info in enumerate(preset_data["levels"]):
            # 手機版優先展開卡片，確保觸控友善
            with st.expander(f"📱 節點：【{lvl_info['name']}】", expanded=True):
                use_node = st.checkbox(f"啟用此組織節點 / Enable Node", value=True, key=f"use_node_{selected_industry}_{idx}")
                if use_node:
                    for sec in lvl_info["sections"]:
                        g_str = ", ".join(sec["groups"])
                        st.markdown(f"• 📂 `{sec['dept']}` ➔ 📑 `{sec['sec']}` ➔ 👥 班組: [{g_str}]")
                    
                    st.markdown("---")
                    st.markdown("**📌 配置功能模組 (Features):**")
                    node_mods = []
                    # 手機端使用直式或兩欄緊湊勾選框，避免跑版
                    for m_idx, mod in enumerate(lvl_info["modules"]):
                        if st.checkbox(mod, value=True, key=f"mod_chk_{selected_industry}_{idx}_{m_idx}"):
                            node_mods.append(mod)
                    
                    selected_preset_items.append({
                        "id": f"preset_{uuid.uuid4().hex[:6]}",
                        "name": lvl_info["name"],
                        "sub_departments": [{"dept_name": s["dept"], "sections": [{"sec_name": s["sec"], "groups": s["groups"]}]} for s in lvl_info["sections"]],
                        "assigned_modules": node_mods
                    })

        if st.button(t['apply_btn'], type="primary", use_container_width=True):
            current_tenant["hierarchical_org_tree"] = selected_preset_items
            st.success(t['success_apply'])
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 2: 手動自訂備用輸入
    with tab_custom:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### ➕ 自訂特殊部門節點 (Custom Department)")
        with st.form("custom_org_form"):
            t1 = st.text_input("1 級：事業群 / 處", placeholder="例: 特殊事業處")
            t2 = st.text_input("2 級：部", placeholder="例: 特殊專案部")
            t3 = st.text_input("3 級：科", placeholder="例: 創新研發科")
            t4 = st.text_input("4 級：組 (逗號分隔)", placeholder="例: A組, B組")
            
            if st.form_submit_button("💾 新增自訂組織節點", type="primary", use_container_width=True):
                if t1.strip() and t2.strip():
                    current_tenant["hierarchical_org_tree"].append({
                        "id": f"custom_{uuid.uuid4().hex[:6]}",
                        "name": t1.strip(),
                        "sub_departments": [{
                            "dept_name": t2.strip(),
                            "sections": [{"sec_name": t3.strip(), "groups": [g.strip() for g in t4.split(",") if g.strip()]}] if t3.strip() else []
                        }],
                        "assigned_modules": ["👑 老闆級即時經營戰情室 (Executive BI)"]
                    })
                    st.success("🎉 成功新增自訂組織節點！")
                    st.rerun()
                else:
                    st.error("請至少填寫 1 級與 2 級名稱！")
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 3: 現有組織樹總覽 (手機排版優先)
    with tab_view:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🌳 目前生效中的組織樹與功能配置 (Active Org Tree)")
        if not current_tenant["hierarchical_org_tree"]:
            st.warning("目前尚無組織節點，請至第一頁使用滑鼠點選套用產業標準庫。")
        else:
            for idx, item in enumerate(current_tenant["hierarchical_org_tree"]):
                with st.expander(f"🏢 組織節點：{item['name']}", expanded=True):
                    if st.button("🗑️ 移除此節點 / Remove", key=f"remove_node_{idx}", use_container_width=True):
                        current_tenant["hierarchical_org_tree"].pop(idx)
                        st.rerun()
                    for dept in item.get("sub_departments", []):
                        st.markdown(f"• 📂 `{dept['dept_name']}`")
                        for sec in dept.get("sections", []):
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;┗ 📑 `{sec['sec_name']}` ➔ 班組: {sec['groups']}")
                    st.markdown(f"• 🧩 **功能模組**：{', '.join(item.get('assigned_modules', []))}")
        st.markdown('</div>', unsafe_allow_html=True)
