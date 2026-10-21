import streamlit as st
import uuid

def render_app_store(current_tenant, all_departments):
    """
    租戶後台：樂高積木式模組市集與功能開關 (App Store)
    動態讀取全平台大合集模組庫，供各部門勾選並即時計費。
    """
    st.markdown(f"## 🧩 {current_tenant['name']}：樂高積木式模組市集與功能開關 (App Store)")
    st.info("💡 *說明：點選左側任意部門，右側會自動動態載入【全平台獨立模組庫】，讓您自由勾選該部門專屬的 ERP 功能模組，並即時計費！*")
    
    col_left, col_right = st.columns([1, 2.5])
    
    with col_left:
        st.markdown("### 🏢 選擇目標部門 / 管理層")
        selected_dept = st.radio(
            "部門選擇",
            all_departments,
            index=0,
            label_visibility="collapsed"
        )
        
    with col_right:
        clean_dept_name = selected_dept.split('(')[0].strip()
        st.markdown(f"### 🛒 【{clean_dept_name}】的動態模組市集 (App Store)")
        
        # 直接讀取全平台獨立模組庫
        master_lib = st.session_state.master_module_library
        saved_dept_mods = current_tenant.get("dept_modules_db", {}).get(selected_dept, [])
        
        with st.form(f"form_store_{selected_dept}"):
            curr_selected = []
            
            for cat_name, mod_list in master_lib.items():
                st.markdown(f"#### {cat_name}")
                cols_m = st.columns(3)
                for m_idx, mod in enumerate(mod_list):
                    with cols_m[m_idx % 3]:
                        if st.checkbox(mod, value=mod in saved_dept_mods, key=f"store_{selected_dept}_{mod}"):
                            curr_selected.append(mod)
                st.markdown("---")
                        
            total_all_mods = sum(len(mods) for mods in current_tenant.get("dept_modules_db", {}).values())
            calculated_price = 80 + (total_all_mods * 5)
            current_tenant["price_usd"] = calculated_price
            
            st.markdown(f"### 💳 系統計費試算：當前部門選定 `{len(curr_selected)}` 項模組 ➔ 企業每月總訂閱費用：**`$ {current_tenant['price_usd']} USD`**")
            
            if st.form_submit_button(f"💾 立即寫入資料庫：儲存【{clean_dept_name}】模組配置", type="primary", use_container_width=True):
                if "dept_modules_db" not in current_tenant:
                    current_tenant["dept_modules_db"] = {}
                current_tenant["dept_modules_db"][selected_dept] = list(set(curr_selected))
                
                # 同步寫入組織節點
                node_names = [n["name"] for n in current_tenant["org_nodes"]]
                short_name = clean_dept_name
                for prefix in ["👑", "📈", "👥", "⚖️", "🔒", "💰", "📊", "🌍", "🌐", "📢", "🤝", "🛒", "📦", "🏭", "⚙️", "🛡️", "💡", "💻"]:
                    short_name = short_name.replace(prefix, "")
                short_name = short_name.strip()
                
                if short_name not in node_names:
                    current_tenant["org_nodes"].append({
                        "id": f"node_{uuid.uuid4().hex[:8]}",
                        "name": short_name,
                        "type": selected_dept,
                        "parent": "董事長室" if "董事長室" not in short_name else "無 (頂層)"
                    })
                    
                st.success(f"🎉 成功寫入資料庫！【{short_name}】部門及其專屬功能已永久紀錄並同步至組織架構圖。")
                st.rerun()
