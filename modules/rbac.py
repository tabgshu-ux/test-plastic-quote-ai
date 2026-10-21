import streamlit as st
import pandas as pd
import uuid

def render_rbac(current_tenant):
    """
    租戶後台：企業級員工與權限管理 (RBAC)
    由租戶自主管理的內部員工權限清單，落實嚴格的資料隔離與資安信賴。
    """
    st.markdown(f"## 👥 {current_tenant['name']}：企業內部員工與權限管理 (RBAC)")
    st.info("💡 *在此處管理貴公司內部的員工帳號與存取角色，所有資料僅限貴公司內部獨立使用與自主控管。*")

    # 初始化租戶自己的員工清單（完全不包含平台總管理員）
    if "staff" not in current_tenant:
        current_tenant["staff"] = [
            {"name": "Trần Văn Minh", "email": "minh.tv@vina.com", "role": "Tenant Admin (租戶管理員/老闆)", "dept": "董事長室", "lang": "Tiếng Việt"},
            {"name": "Nguyễn Thị Hạnh", "email": "hanh.nt@vina.com", "role": "Department Manager (部門主管)", "dept": "財務部", "lang": "Tiếng Việt"},
            {"name": "Le Van Hung", "email": "hung.lv@vina.com", "role": "Field Worker (現場作業人員)", "dept": "工程技術部", "lang": "Tiếng Việt"}
        ]

    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### ➕ 新增公司內部員工帳號")
        
        with st.form("add_staff_form"):
            col1, col2 = st.columns(2)
            with col1:
                s_name = st.text_input("員工姓名 (Full Name)", placeholder="例：Pham Van Nam")
                s_email = st.text_input("電子郵件 / 登入帳號 (Email)", placeholder="例：nam.pv@vina.com")
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

            if st.form_submit_button("👤 建立並寫入公司權限資料庫", type="primary", use_container_width=True):
                if s_name and s_email:
                    current_tenant["staff"].append({
                        "name": s_name,
                        "email": s_email,
                        "role": s_role,
                        "dept": "工程技術部",
                        "lang": s_lang
                    })
                    st.success(f"🎉 成功為 [{s_name}] 建立內部帳號！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫完整員工姓名與電子郵件。")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 內部員工與權限清單 (Access Control List)")
    
    if current_tenant["staff"]:
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            df_staff = pd.DataFrame(current_tenant["staff"])
            st.dataframe(df_staff, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
