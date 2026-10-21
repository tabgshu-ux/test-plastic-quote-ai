import streamlit as st
import pandas as pd

def render_rbac(current_tenant):
    st.markdown("## 👥 裕豐電機工業：組織角色與部門權限設定 (RBAC)")
    st.info("💡 *精細化權限控制中心：設定各部門員工與高管的系統操作權限、角色分派與多語系偏好。*")
    
    # 確保資料結構存在
    if "staff" not in current_tenant:
        current_tenant["staff"] = [
            {"name": "許福村", "account": "boss", "password": "123", "role": "Tenant Admin (租戶管理員/老闆)", "dept": "董事長室", "lang": "繁體中文"},
            {"name": "財務副理", "account": "finance", "password": "123", "role": "財務副理", "dept": "財務與資本運作部", "lang": "Tiếng Việt (越南語)"}
        ]

    # ==================== 1. 新增員工與權限帳號表單 ====================
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### ➕ 新增內部員工與指派權限角色")
        
        with st.form("add_staff_form"):
            c1, c2 = st.columns(2)
            with c1:
                emp_name = st.text_input("員工姓名 (Full Name)", placeholder="例: Pham Van Nam")
                emp_account = st.text_input("電子郵件 / 登入帳號 (Email/Account)", placeholder="例: nam.pv@vina.com")
            with c2:
                emp_role = st.selectbox(
                    "指派系統權限角色 (Role)",
                    [
                        "Tenant Admin (租戶管理員/老闆)",
                        "General Manager (總經理)",
                        "Plant Manager (廠長)",
                        "Finance Manager (財務副理)",
                        "Engineering Lead (工程主管)",
                        "Field Technician (現場技術員/師傅)"
                    ]
                )
                emp_lang = st.selectbox("偏好語系 (Language)", ["繁體中文 (Traditional Chinese)", "Tiếng Việt (越南語)", "English (英文)"])
            
            if st.form_submit_button("💾 建立並寫入公司權限資料庫", type="primary", use_container_width=True):
                if emp_name.strip() and emp_account.strip():
                    current_tenant["staff"].append({
                        "name": emp_name.strip(),
                        "account": emp_account.strip(),
                        "password": "123", # 預設密碼
                        "role": emp_role,
                        "dept": "工程技術部",
                        "lang": emp_lang
                    })
                    st.success(f"🎉 成功建立員工【{emp_name.strip()}】帳號，並賦予【{emp_role}】權限！")
                    st.rerun()
                else:
                    st.error("❌ 請完整填寫員工姓名與登入帳號！")
        st.markdown('</div>', unsafe_allow_html=True)

    # ==================== 2. 內部員工與權限清單 (CRUD 表格) ====================
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("### 📋 內部員工與權限清單 (Access Control List)")
    
    df_staff = pd.DataFrame(current_tenant["staff"])
    
    # 互動式編輯表格
    edited_staff_df = st.data_editor(
        df_staff,
        num_rows="dynamic",
        use_container_width=True,
        key="rbac_staff_editor"
    )
    
    if st.button("💾 儲存員工權限修改", type="primary"):
        current_tenant["staff"] = edited_staff_df.to_dict(orient="records")
        st.success("✅ 員工權限資料已成功更新！")
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

    # ==================== 3. 組織角色與部門權限矩陣對照表 ====================
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("### 🛡️ 各部門角色可操作功能矩陣 (Permission Matrix)")
    st.info("💡 *對照您在舊版系統中規劃的部門權限範圍：*")
    
    matrix_data = {
        "部門名稱": ["董事長室 (Executive)", "管理部 (Management)", "全方位電子審批", "工程技術與設計中心", "生產製造部 (Production)", "資訊管理部 (IT System)"],
        "核心職責": ["全集團戰情與最高決策", "人事、行政與跨部門協調", "各類採購與合約電子簽核", "配電盤與變壓器圖紙/工藝", "車間產線排程與 OEE 監控", "資料庫、帳號與稽核軌跡"],
        "最高權限角色": ["Tenant Admin / 董仔", "Manager / 財務副理", "Approval Center Lead", "Engineering Director", "Plant Manager", "System Admin (IT)"],
        "狀態": ["🟢 啟動", "🟢 啟動", "🟢 啟動", "🟢 啟動", "🟢 啟動", "🟢 啟動"]
    }
    st.dataframe(pd.DataFrame(matrix_data), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
