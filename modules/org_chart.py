import streamlit as st
import uuid

def render_org_chart(current_tenant):
    """
    租戶後台：ProcessOn 標準組織架構圖與節點管理 (CRUD)
    """
    st.markdown(f"## 🖱️ {current_tenant['name']}：ProcessOn 標準組織架構圖與節點管理")
    st.info("💡 *在此處自由新增、修改或刪除公司內部組織節點，並即時檢視各部門在資料庫中對應啟用的功能！*")
    
    col_set, col_edit = st.columns([1, 1])
    existing_parents = [n["name"] for n in current_tenant["org_nodes"]]
    
    with col_set:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### ➕ 新增組織節點或據點 (寫入資料庫)")
        with st.form("org_add_form"):
            n_name = st.text_input("部門/據點名稱*", placeholder="例：財務部 / 台北旗艦總店")
            n_type = st.selectbox("部門層級屬性", ["👑 頂層 (Board / 董事會)", "👑 一級部門 (Headquarters)", "⚙️ 二級部門 (Functional Dept)", "🏢 三級據點/倉庫 (Branch / Warehouse)"])
            n_parent = st.selectbox("指定上級掛載點", existing_parents)
            
            if st.form_submit_button("🧱 寫入資料庫並新增節點", type="primary", use_container_width=True):
                if n_name:
                    current_tenant["org_nodes"].append({
                        "id": f"node_{uuid.uuid4().hex[:8]}",
                        "name": n_name,
                        "type": n_type,
                        "parent": n_parent
                    })
                    st.success(f"🎉 成功寫入資料庫：新增 [{n_name}]！")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_edit:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### ✏️ 修改或刪除現有節點 (資料庫同步更新)")
        if current_tenant["org_nodes"]:
            node_options = {f"{n['name']} ({n['type']}) [ID: {n['id']}]": n for n in current_tenant["org_nodes"]}
            selected_label = st.selectbox("選擇要管理的節點", list(node_options.keys()))
            target_node = node_options[selected_label]
            
            if target_node:
                with st.form("org_edit_form"):
                    up_name = st.text_input("修改名稱", value=target_node["name"])
                    up_parent = st.selectbox("修改上級掛載點", existing_parents, index=existing_parents.index(target_node["parent"]) if target_node["parent"] in existing_parents else 0)
                    
                    cb1, cb2 = st.columns(2)
                    with cb1:
                        sub_u = st.form_submit_button("💾 儲存修改", type="primary", use_container_width=True)
                    with cb2:
                        sub_d = st.form_submit_button("🗑️ 從資料庫刪除", type="primary", use_container_width=True)
                        
                    if sub_u:
                        target_node["name"] = up_name
                        target_node["parent"] = up_parent
                        st.success("🎉 資料庫更新成功！")
                        st.rerun()
                    if sub_d:
                        if target_node["parent"] == "無 (頂層)":
                            st.error("❌ 無法刪除頂層最高決策層！")
                        else:
                            current_tenant["org_nodes"] = [n for n in current_tenant["org_nodes"] if n["id"] != target_node["id"]]
                            st.success("🗑️ 節點已從資料庫刪除！")
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 資料庫即時組織架構與部門專屬功能總覽")
    st.info("💡 *下方即時呈現資料庫中的組織階層方塊圖，並自動帶出各部門在市集裡勾選啟用的功能模組！*")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        roots = [n for n in current_tenant["org_nodes"] if n["parent"] == "無 (頂層)"]
        others = [n for n in current_tenant["org_nodes"] if n["parent"] != "無 (頂層)"]
        dept_db = current_tenant.get("dept_modules_db", {})
        
        for r in roots:
            r_mods = []
            for k, v in dept_db.items():
                if r['name'] in k:
                    r_mods = v
            r_mods_str = ", ".join(r_mods) if r_mods else "尚未勾選模組"
            
            st.markdown(f"""
                <div style="text-align: center;">
                    <div class="org-root-card" style="background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; padding: 12px 20px; border-radius: 8px; display: inline-block; font-weight: bold; margin-bottom: 10px;">
                        👑 {r['name']} <span style="font-size: 12px; font-weight: normal;">({r['type']})</span><br>
                        <span style="font-size: 11px; opacity: 0.9;">📦 啟用功能：{r_mods_str}</span>
                    </div>
                </div>
                <div class="tree-connector" style="width: 2px; height: 20px; background-color: #94a3b8; margin: 0 auto;"></div>
            """, unsafe_allow_html=True)
            
            level1 = [n for n in others if n["parent"] == r["name"]]
            if level1:
                cols1 = st.columns(len(level1))
                for idx1, l1 in enumerate(level1):
                    with cols1[idx1]:
                        l1_mods = []
                        for k, v in dept_db.items():
                            if l1['name'] in k:
                                l1_mods = v
                        l1_mods_str = ", ".join(l1_mods) if l1_mods else "尚未勾選模組"
                        
                        st.markdown(f"""
                            <div style="text-align: center;">
                                <div class="org-level1-card" style="background: #ffffff; border: 2px solid #2563eb; color: #1e293b; padding: 10px 15px; border-radius: 8px; margin: 4px;">
                                    <b>{l1['name']}</b><br>
                                    <span style="font-size: 11px; color: gray;">{l1['type']}</span><br>
                                    <span style="font-size: 10px; color: #2563eb;">📌 功能：{l1_mods_str}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
