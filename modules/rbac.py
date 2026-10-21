import streamlit as st
import pandas as pd
import uuid

def render_rbac(current_tenant):
    """
    租戶後台：企業級權限與角色控制 (RBAC & Sandbox Security)
    精準劃分跨國組織中不同角色的操作權限與資料列級隔離 (Row-Level Security)。
    """
    st.markdown(f"## 👥 {current_tenant['name']}：企業級權限與角色控制 (RBAC)")
    st.info("💡 *在此處精準劃分跨國組織中不同角色的操作權限：從台灣高階主管、跨國 IT 到越南現場施工人員的存取隔離與語系偏好設定。*")

    # 初始化員工與權限資料庫
    if "staff" not in current_tenant:
        current_tenant["staff"] = [
            {"name": "許福村", "email": "fuchun@vina.com", "role": "Tenant Admin (租戶管理員)", "dept": "董事長室", "lang": "繁體中文"},
            {"name": "陳大為", "email": "david.tw@vina.com", "role": "Cross-border Manager (台灣跨國主管)", "dept": "財務部", "lang": "繁體中文"},
            {"name": "Nguyen Van An", "email": "an.vn@vina.com", "role": "Field Worker (越南現場工程人員)", "dept": "工程技術部", "lang": "Tiếng Việt"}
        ]

    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### ➕ 新增跨國員工帳號與角色指派")
        
        with st.form("add_staff_form"):
            col1, col2 = st.columns(2)
            with col1:
                s_name = st.text_input("員工姓名 (Full Name)", placeholder="例：Le Van Hung")
                s_email = st.text_input("電子郵件 / 登入帳號 (Email)", placeholder="例：hung@vina.com")
            with col2:
                s_role = st.selectbox(
                    "指派系統權限角色 (RBAC Role)",
                    [
                        "Tenant Admin (租戶管理員/老闆)",
                        "Cross-border Manager (台灣跨國主管/決策者)",
                        "IT Implementer (客戶端 IT / 元數據配置師)",
                        "Field Worker (越南現場工程人員/抖音化介面)"
                    ]
                )
                s_lang = st.selectbox("預設語系偏好 (Default Language)", ["Tiếng Việt (越南語)", "繁體中文 (Traditional Chinese)", "English (英文)"])

            if st.form_submit_button("👤 建立並寫入安全權限資料庫", type="primary", use_container_width=True):
                if s_name and s_email:
                    current_tenant["staff"].append({
                        "name": s_name,
                        "email": s_email,
                        "role": s_role,
                        "dept": "工程技術部",
                        "lang": s_lang
                    })
                    st.success(f"🎉 成功為 [{s_name}] 建立帳號並套用 [{s_role}] 權限隔離！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫完整員工姓名與電子郵件。")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 現有員工與跨國權限清單 (Access Control List)")
    st.info("💡 *系統將依據以下角色自動判定該使用者登入後的介面呈現方式（例如：越南現場工人的手機版語音介面 vs 台灣主管的跨國多維度 BI 決策報表）。*")
    
    if current_tenant["staff"]:
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            df_staff = pd.DataFrame(current_tenant["staff"])
            st.dataframe(df_staff, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
