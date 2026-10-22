import streamlit as st
import pandas as pd
import uuid

def render_departments_manager(current_tenant):
    st.markdown("## 🏢 全球多租戶 SaaS 組織圖自由拼裝與模組動態對應")
    st.info("💡 *支援全球各行各業（大至跨國集團、小至微型企業）自由架設 1~4 級組織樹（事業群/處 ➔ 部 ➔ 科 ➔ 組/班），並可將標準功能模組彈性指派到任何組織節點。*")
    
    # 初始化多級組織樹狀結構資料庫
    if "hierarchical_org_tree" not in current_tenant:
        current_tenant["hierarchical_org_tree"] = [
            {
                "id": "div_01",
                "level": "1級-事業群/處/最高決策",
                "name": "總經理室 / 營運總部",
                "parent": "董事長",
                "sub_departments": [
                    {
                        "dept_name": "資訊與系統處 (2級-部)",
                        "sections": [
                            {
                                "sec_name": "系統開發科 (3級-科)",
                                "groups": ["前端工程組 (4級-組)", "後端維運組 (4級-組)"]
                            }
                        ]
                    }
                ],
                "assigned_modules": ["👑 老闆級即時經營戰情室 (Executive BI)", "👥 員工帳號與權限管理 (RBAC)"]
            }
        ]

    # 全球通用標準功能模組市集（白話易懂，供各部門自由勾選複用）
    master_available_modules = [
        "👑 老闆級即時經營戰情室 (Executive BI)",
        "💼 商務接單與多幣別報價管理",
        "🏭 生產製造執行與車間排程 (MES)",
        "📱 現場基層手機快速回報 (Mobile Field Worker)",
        "🖱️ 組織架構圖與節點管理 (Org Chart)",
        "👥 員工帳號與權限管理 (RBAC)",
        "🎨 企業品牌識別與 Logo 自訂",
        "📦 智慧倉儲與進銷存叫料管理",
        "💰 財務應收應付與電子發票系統",
        "🛡️ ISO 品質合規與異常改善 (CAPA)",
        "🌱 ESG 碳排與永續發展數據追蹤"
    ]

    tab_tree, tab_assign, tab_search = st.tabs([
        "🌳 1. 組織圖架構維護 (CRUD)", 
        "🧩 2. 部門功能模組複用市集",
        "🔍 3. 全組織節點與功能搜尋"
    ])

    # ==================== 1. 多級組織架構維護 (CRUD) ====================
    with tab_tree:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🌳 自由架設與管理 1~4 級組織樹（部 ➔ 科 ➔ 組）")
        
        # 新增組織表單
        with st.form("multi_level_org_form"):
            st.markdown("#### ➕ 新增 1~4 級組織節點")
            c1, c2, c3 = st.columns(3)
            with c1:
                t1_div = st.text_input("1 級：事業群 / 處 / 總經理室名稱", placeholder="例: 營運事業群")
            with c2:
                t2_dept = st.text_input("2 級：部名稱 (Department)", placeholder="例: 財務會計部")
            with c3:
                t3_sec = st.text_input("3 級：科 / 營運中心名稱 (Section)", placeholder="例: 總帳會計科")
                
            t4_groups = st.text_input("4 級：組 / 班名稱 (可用逗號分隔)", placeholder="例: 傳票登錄班, 稅務申報組")
            
            if st.form_submit_button("💾 新增至組織樹", type="primary", use_container_width=True):
                if t1_div.strip() and t2_dept.strip():
                    groups_list = [g.strip() for g in t4_groups.split(",") if g.strip()]
                    
                    existing_div = next((d for d in current_tenant["hierarchical_org_tree"] if d["name"] == t1_div.strip()), None)
                    
                    if existing_div:
                        existing_dept = next((dp for dp in existing_div["sub_departments"] if dp["dept_name"] == t2_dept.strip()), None)
                        if existing_dept:
                            if t3_sec.strip():
                                existing_dept["sections"].append({"sec_name": t3_sec.strip(), "groups": groups_list})
                        else:
                            existing_div["sub_departments"].append({
                                "dept_name": t2_dept.strip(),
                                "sections": [{"sec_name": t3_sec.strip(), "groups": groups_list}] if t3_sec.strip() else []
                            })
                    else:
                        current_tenant["hierarchical_org_tree"].append({
                            "id": f"div_{uuid.uuid4().hex[:6]}",
                            "level": "1級-事業群/處",
                            "name": t1_div.strip(),
                            "parent": "董事長室",
                            "sub_departments": [{
                                "dept_name": t2_dept.strip(),
                                "sections": [{"sec_name": t3_sec.strip(), "groups": groups_list}] if t3_sec.strip() else []
                            }],
                            "assigned_modules": []
                        })
                        
                    st.success(f"🎉 成功建立組織節點：【{t1_div}】➔ 【{t2_dept}】➔ 【{t3_sec}】！")
                    st.rerun()
                else:
                    st.error("❌ 請至少填寫 1 級事業群與 2 級部門名稱！")
        
        st.markdown("---")
        st.markdown("### 📋 現有企業組織樹與管理 (支援修改與刪除)")
        
        if not current_tenant["hierarchical_org_tree"]:
            st.warning("目前尚無組織節點，請透過上方表單新增。")
        else:
            for idx, div in enumerate(current_tenant["hierarchical_org_tree"]):
                with st.expander(f"🏢 1級組織：{div['name']} (已掛載 {len(div.get('assigned_modules', []))} 項功能)", expanded=True):
                    # 刪除與修改 1 級組織按鈕
                    col_info, col_del = st.columns([4, 1])
                    with col_del:
                        if st.button("🗑️ 刪除此1級組織", key=f"del_div_{idx}", use_container_width=True):
                            current_tenant["hierarchical_org_tree"].pop(idx)
                            st.success(f"已刪除 1 級組織：{div['name']}")
                            st.rerun()
                    
                    for dept in div.get("sub_departments", []):
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;┗ 📂 *2級-部*: `{dept['dept_name']}`")
                        for sec in dept.get("sections", []):
                            g_str = ", ".join(sec['groups']) if sec['groups'] else "無下屬組別"
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;┗ 📑 *3級-科*: `{sec['sec_name']}` ➔ 👥 *4級-組*: [{g_str}]")
                    
                    mods_assigned = ", ".join(div.get("assigned_modules", [])) or "尚未指派模組"
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;🧩 *已指派功能模組*: `{mods_assigned}`")
        st.markdown('</div>', unsafe_allow_html=True)

    # ==================== 2. 功能模組跨部門複用市集 ====================
    with tab_assign:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🛒 跨部門功能模組彈性指派（同一個功能可在多個部門共用）")
        
        if not current_tenant["hierarchical_org_tree"]:
            st.warning("請先至第一頁建立組織節點，才能在此指派功能模組。")
        else:
            div_names = [d["name"] for d in current_tenant["hierarchical_org_tree"]]
            target_div = st.selectbox("選擇要指派功能的 1級/2級 事業群與部門節點", div_names, key="assign_target_div")
            
            selected_obj = next(d for d in current_tenant["hierarchical_org_tree"] if d["name"] == target_div)
            
            with st.form(f"form_multi_mod_{target_div}"):
                current_mods = selected_obj.get("assigned_modules", [])
                selected_new_mods = []
                
                st.markdown(f"##### 📌 勾選【{target_div}】及其底下所有科、組可使用的 ERP 功能市集")
                cols = st.columns(2)
                for idx, mod in enumerate(master_available_modules):
                    with cols[idx % 2]:
                        if st.checkbox(mod, value=mod in current_mods, key=f"multi_chk_{target_div}_{idx}"):
                            selected_new_mods.append(mod)
                            
                if st.form_submit_button(f"💾 儲存【{target_div}】的功能模組對應", type="primary", use_container_width=True):
                    selected_obj["assigned_modules"] = list(set(selected_new_mods))
                    st.success(f"🎉 儲存成功！【{target_div}】已成功掛載 `{len(selected_new_mods)}` 項功能模組。")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ==================== 3. 全組織節點與功能搜尋 ====================
    with tab_search:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🔍 全組織與功能模組快速檢索")
        search_query = st.text_input("輸入關鍵字搜尋組織名稱、部門或功能（例：財務、生產、戰情室）：", placeholder="請輸入關鍵字...")
        
        if search_query:
            st.markdown(f"#### 🔎 搜尋結果：「{search_query}」")
            found_match = False
            for div in current_tenant["hierarchical_org_tree"]:
                matched_div = search_query.lower() in div["name"].lower()
                matched_mods = any(search_query.lower() in m.lower() for m in div.get("assigned_modules", []))
                
                if matched_div or matched_mods:
                    found_match = True
                    st.success(f"找到符合節點：【事業群/處：{div['name']}】")
                    st.write(f"• 已配置功能：{', '.join(div.get('assigned_modules', []))}")
                    st.markdown("---")
            if not found_match:
                st.warning("查無符合該關鍵字的組織或模組。")
        else:
            st.info("💡 請在上方輸入框輸入關鍵字以執行全組織快速檢索。")
        st.markdown('</div>', unsafe_allow_html=True)
