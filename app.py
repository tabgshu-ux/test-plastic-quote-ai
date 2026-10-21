import streamlit as st

st.set_page_config(
    page_title="SaaS Platform & Enterprise ERP Gateway",
    page_icon="🚪",
    layout="wide"
)

if "active_portal" not in st.session_state:
    st.session_state.active_portal = None

if st.session_state.active_portal is None:
    st.markdown("""
        <style>
        .main { background-color: #f8f9fa; }
        .card-container { background-color: #ffffff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); margin-bottom: 20px; text-align: center; }
        h1 { color: #1e293b; }
        .stButton>button { border-radius: 8px; font-weight: 600; padding: 10px 24px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>🌐 SaaS 企業級多租戶 AI-ERP 平台</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>多租戶獨立雲端架構</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 👑 平台總控台 (Master)")
        st.markdown("管理全球租戶、訂閱與伺服器路由", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 進入總控台", type="primary", use_container_width=True):
            st.session_state.active_portal = "master"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🏭 企業租戶 ERP (Tenant)")
        st.markdown("各企業租戶專屬登入與多維度作業系統", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 進入租戶系統", type="primary", use_container_width=True):
            st.session_state.active_portal = "tenant"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

else:
    if st.session_state.active_portal == "master":
        import master_portal
        master_portal.render_master_portal()
    elif st.session_state.active_portal == "tenant":
        import tenant_app
        tenant_app.render_tenant_app()
