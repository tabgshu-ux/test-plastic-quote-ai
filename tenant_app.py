import streamlit as st

def render_tenant_branding_settings(current_tenant):
    st.markdown("## 🎨 企業品牌識別與 Logo 自訂中心 (Tenant Branding)")
    st.info("💡 *在此您可以自由更改系統左上角顯示的公司標誌 (Logo URL 或圖案) 與顯示名稱。*")
    
    with st.form("branding_form"):
        # 如果是裕豐，預設帶入裕豐的專屬名稱與預設標誌
        default_name = current_tenant.get("name", "裕豐電機工業 (Reetech Industrial)")
        default_logo = current_tenant.get("logo_url", "https://img.icons8.com/color/96/factory.png")
        
        new_company_name = st.text_input("公司顯示名稱 (Company Display Name)", value=default_name)
        new_logo_url = st.text_input("左上角 Logo 圖片網址 (Logo Image URL)", value=default_logo)
        
        st.markdown("---")
        st.markdown("### 👁️ 即時預覽效果")
        col_prev1, col_prev2 = st.columns([1, 4])
        with col_prev1:
            st.image(new_logo_url, width=64)
        with col_prev2:
            st.markdown(f"### {new_company_name}")
            
        if st.form_submit_button("💾 儲存並更新品牌識別", type="primary", use_container_width=True):
            current_tenant["name"] = new_company_name
            current_tenant["logo_url"] = new_logo_url
            st.success(f"🎉 成功更新！左上角圖案與公司名稱已即時套用至 [{new_company_name}]。")
            st.rerun()
