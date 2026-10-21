import streamlit as st

st.set_page_config(
    page_title="SaaS Platform & Enterprise ERP Gateway",
    page_icon="🚪",
    layout="centered"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card-container { background-color: #ffffff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); margin-bottom: 20px; text-align: center; }
    h1 { color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🌐 SaaS 企業級多租戶 AI-ERP 平台</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>請選擇您要進入的系統入口</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("### 👑 平台總控台 (Master)")
    st.markdown("專屬平台開發商與財務人員<br>管理全球租戶、定價與權限", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 進入總控台", type="primary", use_container_width=True):
        st.switch_page("master_portal.py")  # 需 Streamlit 1.31+ 支援，或改用說明導引
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("### 🏭 企業租戶 ERP (Tenant)")
    st.markdown("專屬企業內部員工與主管<br>執行進銷存、POS、戰情室與 MES", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 進入租戶系統", type="primary", use_container_width=True):
        st.switch_page("tenant_app.py")
    st.markdown('</div>', unsafe_allow_html=True)
