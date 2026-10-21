import streamlit as st
import pandas as pd
import uuid

def render_departments_manager(current_tenant):
    st.markdown("## 🏢 裕豐電機：多級組織架構管理（部 ➔ 科 ➔ 組）與模組動態對應")
    st.info("💡 *支援製造業標準的多級階層組織（事業群 ➔ 部 ➔ 科 ➔ 組/班），並可將相同的作業功能彈性指派到任何層級。*")
    
    # 初始化多級組織樹狀結構資料庫
    if "hierarchical_org_tree" not in current_tenant:
        current_tenant["hierarchical_org_tree"] = [
            {
                "id": "div_01",
                "level": "1級-事業群/處",
                "name": "生產製造事業群",
                "parent": "董事長室",
                "sub_departments": [
                    {
                        "dept_name": "配電盤製造部 (2級-部)",
                        "sections": [
                            {
                                "sec_name": "高壓盤組裝科 (3級-科)",
                                "groups": ["第一作業班 (4級-組)", "第二測試班 (4級-組)"]
                            },
                            {
                                "sec_name": "低壓盤配線科 (3級-科)",
                                "groups": ["焊接組", "佈線組"]
                            }
                        ]
                    }
                ],
                "assigned_modules": ["MES 電機製造執行與車間排程", "工地師傅手機快速回報"]
            }
        ]

    master_available_modules = [
        "👑 老闆級即時經營戰情室 (Executive BI)",
        "💼 商務接單與多幣別報價管理",
        "🏭 MES 電機製造執行與車間排程",
        "📱 工地師傅手機快速回報 (Mobile Field Worker)",
        "🖱️ 組織架構圖與節點管理",
        "👥 員工帳號與權限管理 (RBAC)",
        "🎨 企業品牌識別與 Logo 自訂",
        "📦 智慧倉儲與物料叫料管理",
        "💰 財務應收應付與電子發票系統"
    ]

    tab_tree, tab_assign = st.tabs(["🌳 1. 多級組織架構維護（部、科、組）", "🧩 2. 各部門/科組功能模組複用市集"])

    # ==================== 1. 多級組織架構維護 ====================
    with tab_tree:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🌳 建立與管理多級組織（部 ➔ 科 ➔ 組）")
        
        with st.form("multi_level_org_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                t1_div = st.text_input("1 級：事業群 / 處名稱", placeholder="例: 工程技術事業群")
            with c2:
                t2_dept = st.text_input("2 級：部名稱 (Department)", placeholder="例: 變壓器設計部")
            with c3:
                t3_sec = st.text_input("3 級：科名稱 (Section)", placeholder="例: 繞線技術科")
                
            t4_groups = st.text_input("4 級：組 / 班名稱 (可用逗號分隔)", placeholder="例: A班, B班, 特殊繞線組")
            
            if st.form_submit_button("💾 新增至多級組織樹", type="primary", use_container_width=True):
                if t1_div.strip() and t2_dept.strip():
                    groups_list = [g.strip() for g in t4_groups.split(",") if g.strip()]
                    
                    # 尋找是否已有此 1 級事業群
                    existing_div = next((d for d in current_tenant["hierarchical_org_tree"] if d["name"] == t1_div.strip()), None)
                    
                    if existing_div:
                        # 檢查 2 級部是否存在
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
                        
                    st.success(f"🎉 成功建立多級組織：【{t1_div}】➔ 【{t2_dept}】➔ 【{t3_sec}】！")
                    st.rerun()
                else:
                    st.error("❌ 請至少填寫 1 級事業群與 2 級部門名稱！")
        
        st.markdown("---")
        st.markdown("### 📋 現有企業多級組織樹檢視")
        for div in current_tenant["hierarchical_org_tree"]:
            st.markdown(f"**🏢 1級: {div['name']}**")
            for dept in div.get("sub_departments", []):
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;┗ 📂 *2級-部*: `{dept['dept_name']}`")
                for sec in dept.get("sections", []):
                    g_str = ", ".join(sec['groups']) if sec['groups'] else "無下屬組別"
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;┗ 📑 *3級-科*: `{sec['sec_name']}` ➔ 👥 *4級-組*: [{g_str}]")
            mods_assigned = ", ".join(div.get("assigned_modules", [])) or "尚未指派模組"
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;🧩 *已指派功能模組*: `{mods_assigned}`")
            st.markdown("---")
        st.markdown('</div>', unsafe_allow_html=True)

    # ==================== 2. 功能模組跨部門/科組複用市集 ====================
    with tab_assign:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🛒 跨部門功能模組彈性指派（同一個功能可在多個部門共用）")
        
        div_names = [d["name"] for d in current_tenant["hierarchical_org_tree"]]
        target_div = st.selectbox("選擇要指派功能的 1級/2級 事業群與部門", div_names)
        
        selected_obj = next(d for d in current_tenant["hierarchical_org_tree"] if d["name"] == target_div)
        
        with st.form(f"form_multi_mod_{target_div}"):
            current_mods = selected_obj.get("assigned_modules", [])
            selected_new_mods = []
            
            st.markdown(f"##### 📌 勾選【{target_div}】及其底下所有科、組可使用的 ERP 功能")
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
