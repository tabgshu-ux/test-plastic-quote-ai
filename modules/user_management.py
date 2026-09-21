import pandas as pd
import streamlit as st

def render_company_profile_setting():
    st.subheader("🏢 跨國企業多廠區與公司抬頭設定")
    cp = st.session_state.company_profile
    with st.form("company_general_form"):
        cp_name = st.text_input("公司總稱 (Company Name)", cp["name"])
        cp_tax_id = st.text_input("統一編號 / 稅號 (Tax ID)", cp["tax_id"])
        if st.form_submit_button("💾 儲存集團基本資料"):
            st.session_state.company_profile["name"] = cp_name
            st.session_state.company_profile["tax_id"] = cp_tax_id
            st.toast("✅ 公司集團基本資料已更新！", icon="💾")

def render_user_management(role_name_map):
    st.subheader("📄 現有使用者權限名單")
    user_list = [{"帳號": uname, "姓名": udata["name"], "角色": role_name_map.get(udata["role"], udata["role"])} for uname, udata in st.session_state.user_database.items()]
    st.dataframe(pd.DataFrame(user_list), use_container_width=True)

    with st.form("add_user_form"):
        new_username = st.text_input("新帳號").strip().lower()
        new_password = st.text_input("預設密碼").strip()
        new_name = st.text_input("顯示姓名與職稱")
        new_role_key = st.selectbox("設定角色權限", ["executive", "hr", "finance", "sales"], format_func=lambda x: role_name_map[x])

        if st.form_submit_button("✅ 建立帳號", type="primary"):
            if new_username and new_password and new_name:
                st.session_state.user_database[new_username] = {"password": new_password, "name": new_name, "role": new_role_key}
                st.success(f"🎉 帳號 `{new_username}` 建立成功！")
                st.rerun()
