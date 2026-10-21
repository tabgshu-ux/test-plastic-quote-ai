import streamlit as st
import pandas as pd
import uuid

def render_rbac(current_tenant):
    """
    租戶後台：企業級權限與角色控制 (RBAC)
    精準劃分企業內部不同角色的操作權限與資料列級隔離。
    """
    st.markdown(f"## 👥 {current_tenant['name']}：企業級員工與權限管理 (RBAC)")
    st.info("💡 *在此處管理企業內部的員工帳號與存取角色，系統將依據角色自動對應其最適切的操作介面與語系。*")

    # 初始化員工與權限資料庫
    if "staff" not in current_tenant:
        current_tenant["staff"] = [
            {"name": "許福村", "email": "fuchun@vina.com", "role": "Tenant Admin (租戶管理員)", "dept": "董事長室", "lang": "繁體中文"},
            {"name": "陳大為", "email": "david.tw@vina.com", "role": "Department Manager (部門主管)", "dept": "財務部", "lang": "繁體中文"},
            {"name": "Nguyen Van An", "email": "an.vn@vina.com", "role": "Field Worker (現場作業人員)", "dept": "工程技術部", "lang": "Tiếng Việt"}
        ]

    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### ➕ 新增員工帳號與角色指派")
        
        with st.form("add_staff_form"):
            col1, col2 = st.columns(2)
            with col1:
                s_name = st.text_input("員工姓名 (Full Name)", placeholder="例：Le Van Hung")
                s_email = st.text_input("電子郵件 / 登入帳號 (Email)", placeholder="例：hung@vina.com")
            with col2:
                s_role = st.selectbox(
                    "指派系統權限角色 (Role)",
                    [
                        "Tenant Admin (租戶管理員/老闆)",
                        "Department Manager (部門主管/決策者)",
                        "IT Administrator (企業 IT / 系統管理師)",
                        "Field Worker (現場作業人員/直覺化介面)"
                    ]
                )
                s_lang = st.selectbox("偏好語系 (Language)", ["Tiếng Việt (越南語)", "繁體中文 (Traditional Chinese)", "English (英文)"])

            if st.form_submit_button("👤 建立並寫入權限資料庫", type="primary", use_container_width=True):
                if s_name and s_email:
                    current_tenant["staff"].append({
                        "name": s_name,
                        "email": s_email,
                        "role": s_role,
                        "dept": "工程技術部",
                        "lang": s_lang
                    })
                    st.success(f"🎉 成功為 [{s_name}] 建立帳號並指派權限！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫完整員工姓名與電子郵件。")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 現有員工與權限清單 (Access Control List)")
    
    if current_tenant["staff"]:
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            df_staff = pd.DataFrame(current_tenant["staff"])
            st.dataframe(df_staff, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
