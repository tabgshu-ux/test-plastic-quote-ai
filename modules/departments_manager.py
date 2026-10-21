import streamlit as st
import pandas as pd
import uuid

def render_departments_manager(current_tenant):
    st.markdown("## 🏢 企業部門、海外廠區與組織架構動態管理")
    st.info("💡 *各家企業的組織與部門皆不相同。您可以在此自由新增、修改或刪除公司部門與廠區據點，系統將即時連動至拼圖模組市集與權限設定。*")
    
    # 確保資料結構存在
    if "org_nodes" not in current_tenant:
        current_tenant["org_nodes"] = [
            {"id": "node_root", "name": "董事長室", "type": "👑 頂層 (Board)", "parent": "無 (頂層)"},
            {"id": "node_eng", "name": "工程技術部", "type": "⚙️ 工程製造", "parent": "董事長室"},
            {"id": "node_vn", "name": "越南平陽廠區", "type": "🏭 製造廠區", "parent": "董事長室"}
        ]

    tab_add, tab_manage = st.tabs(["➕ 1. 新增部門或廠區", "📋 2. 現有部門列表與維護 (CRUD)"])
    
    # ==================== 1. 新增功能 (Create) ====================
    with tab_add:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### ➕ 新增組織節點（部門 / 廠區 / 辦事處）")
        
        with st.form("add_dept_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("部門或廠區名稱 (Name)", placeholder="例: 品管部、越南河內倉庫...")
                node_type = st.selectbox(
                    "節點屬性類型",
                    [
                        "👑 核心管理層 (Management)",
                        "⚙️ 工程與製造 (Engineering & Plant)",
                        "💼 業務與商務部 (Sales & Commerce)",
                        "💰 財務與會計部 (Finance)",
                        "📦 倉儲與物流部 (Warehouse & Logistics)",
                        "🛡️ 工安與品管部 (QA & Safety)",
                        "🌍 海外廠區 / 辦事處 (Overseas Plant/Branch)"
                    ]
                )
            with col2:
                # 取得現有節點作為父層選項
                parent_options = [n["name"] for n in current_tenant["org_nodes"]]
                parent_node = st.selectbox("上級歸屬部門 (Parent Node)", ["無 (頂層集團)"] + parent_options)
                currency_scope = st.selectbox("預設記帳幣別", ["USD (美元)", "VND (越南盾)", "RMB (人民幣)", "TWD (新台幣)"])
                
            if st.form_submit_button("💾 確認新增部門至資料庫", type="primary", use_container_width=True):
                if new_name.strip():
                    new_id = f"node_{uuid.uuid4().hex[:8]}"
                    current_tenant["org_nodes"].append({
                        "id": new_id,
                        "name": new_name.strip(),
                        "type": node_type,
                        "parent": parent_node
                    })
                    st.success(f"🎉 成功新增部門/廠區【{new_name.strip()}】！已同步至全系統組織架構。")
                    st.rerun()
                else:
                    st.error("❌ 請輸入有效的部門或廠區名稱！")
        st.markdown('</div>', unsafe_allow_html=True)
        
    # ==================== 2. 查看、修改與刪除 (Read, Update, Delete) ====================
    with tab_manage:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 📋 現有部門與廠區組織清單")
        
        df_nodes = pd.DataFrame(current_tenant["org_nodes"])
        
        # 互動式表格編輯與查看
        edited_df = st.data_editor(
            df_nodes,
            num_rows="dynamic",
            use_container_width=True,
            key="dept_data_editor"
        )
        
        # 同步更新編輯結果
        if st.buttun_update_saved := st.button("💾 儲存表格修改變更", type="primary"):
            current_tenant["org_nodes"] = edited_df.to_dict(orient="records")
            st.success("✅ 組織架構資料已成功更新並寫入資料庫！")
            st.rerun()
            
        st.markdown("---")
        st.markdown("### 🗑️ 指定刪除部門或廠區")
        col_d1, col_d2 = st.columns([2, 1])
        with col_d1:
            del_target = st.selectbox("選擇要移除的部門/廠區", [n["name"] for n in current_tenant["org_nodes"] if n["name"] != "董事長室"])
        with col_d2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ 確認刪除此部門", type="secondary"):
                current_tenant["org_nodes"] = [n for n in current_tenant["org_nodes"] if n["name"] != del_target]
                st.success(f"🗑️ 已成功移除部門【{del_target}】。")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
