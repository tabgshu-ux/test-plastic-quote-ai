import streamlit as st
import pandas as pd

def render_api_gateway_config(tenant_info, user_perms):
    st.markdown("### 🔌 第三方 API 閘道器與動態網頁配置中心")
    st.info("💡 *供客戶 IT 自主配置：在網頁端對接當地物流、電子發票或銀行 API 的 JSON Schema，供 AI 系統進行動態 Function Calling 調用。*")
    st.markdown("---")

    tab1, tab2 = st.tabs(["📋 已綁定第三方 API 列表", "➕ 新增自訂 API 網頁配置"])

    with tab1:
        st.markdown("#### 🔗 現行租戶自訂 API 綁定主檔")
        api_df = pd.DataFrame([
            {"api_id": "API-VN-INV01", "api_name": "越南 Viettel 電子發票 API", "endpoint": "https://api.viettel.vn/invoice/v2", "method": "POST", "status": "🟢 啟用中"},
            {"api_id": "API-LOGISTICS", "api_name": "跨國物流即時追蹤 API", "endpoint": "https://api.logistics-global.com/track", "method": "GET", "status": "🟢 啟用中"}
        ])
        st.dataframe(api_df, use_container_width=True)

    with tab2:
        st.markdown("#### ➕ 註冊新第三方 API 服務")
        with st.form("api_config_form"):
            c1, c2 = st.columns(2)
            with c1:
                api_name = st.text_input("API 服務名稱", placeholder="例: 當地海關申報 API")
                endpoint_url = st.text_input("API Endpoint 網址", placeholder="https://api.example.com/v1/endpoint")
            with c2:
                http_method = st.selectbox("HTTP Method", ["POST", "GET", "PUT", "DELETE"])
                json_schema = st.text_area("JSON Schema 結構定義", placeholder='{"type": "object", "properties": {...}}')

            if st.form_submit_button("🚀 儲存並註冊 API 綁定", type="primary", use_container_width=True):
                st.success(f"🎉 第三方 API [{api_name}] 已成功掛載至系統閘道器，AI 隨時可透過 Function Calling 動態調用！")
