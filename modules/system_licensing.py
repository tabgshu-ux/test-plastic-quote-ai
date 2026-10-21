import streamlit as st
import pandas as pd
import datetime

def render_system_licensing_page(tenant_info=None, lang="繁體中文", **kwargs):
    st.markdown("### 🔑 資訊管理部 - 租戶模組權限與外部 API 串聯中心")
    st.caption("供本公司 IT 管理員自行勾選自家啟用的模組、設定外部股市與金屬原物料 API 及抓取頻率。")

    # 1. 初始化該租戶的模組開關設定 (存在 session_state 供全站動態讀取)
    if "tenant_active_modules" not in st.session_state:
        st.session_state.tenant_active_modules = [
            "總經理室 (Executive Office)",
            "管理部 (Management Dept)",
            "全方位電子簽核中心 (Approval Center)",
            "工程與設計管理中心 (Engineering & Design Center)",
            "生產部 (Production Dept)",
            "資訊管理部 (IT & System)"
        ]

    # 2. 初始化該租戶的外部 API 與頻率設定
    if "tenant_exec_config" not in st.session_state:
        st.session_state.tenant_exec_config = {
            "api_provider": "Alpha Vantage / LME Metal API",
            "api_key": "",
            "fetch_interval_min": 5, # 預設 5 分鐘
        }

    tab1, tab2 = st.tabs(["🧩 自主挑選與勾選自家開通模組", "🔌 外部股市與金屬原物料 API 參數設定"])

    # ----------------------------------------------------
    # Tab 1: 租戶自主勾選模組
    # ----------------------------------------------------
    with tab1:
        st.markdown("##### 📌 請勾選本公司需要開啟的系統模組（未勾選將不會顯示在側邊欄）：")
        
        all_possible_modules = [
            "總經理室 (Executive Office)",
            "管理部 (Management Dept)",
            "全方位電子簽核中心 (Approval Center)",
            "工程與設計管理中心 (Engineering & Design Center)",
            "生產部 (Production Dept)",
            "資訊管理部 (IT & System)"
        ]

        current_selected = st.session_state.tenant_active_modules

        with st.form("form_tenant_module_selector"):
            selected_mods = []
            for m in all_possible_modules:
                is_checked = st.checkbox(m, value=(m in current_selected))
                if is_checked:
                    selected_mods.append(m)

            if st.form_submit_button("💾 儲存本公司模組設定", type="primary", use_container_width=True):
                st.session_state.tenant_active_modules = selected_mods
                st.success("🎉 本公司的模組開關已成功更新！側邊欄將立即依此顯示。")
                st.rerun()

    # ----------------------------------------------------
    # Tab 2: 外部 API 與頻率設定
    # ----------------------------------------------------
    with tab2:
        st.markdown("##### 🔌 總經理室戰情室所需的外部 API 與更新頻率設定")
        with st.form("form_tenant_market_api"):
            cfg = st.session_state.tenant_exec_config
            api_key_input = st.text_input("輸入本公司專屬的股市/金屬 API Key", value=cfg.get("api_key", ""))
            fetch_freq = st.slider("資料自動擷取頻率 (分鐘 / Minutes)", min_value=1, max_value=60, value=cfg.get("fetch_interval_min", 5))
            st.info("💡 設定為 1 分鐘將提供接近即時的行情，但會增加伺服器網路請求負荷；建議設定為 5 ~ 15 分鐘。")
            
            if st.form_submit_button("💾 儲存 API 與頻率參數", type="primary", use_container_width=True):
                st.session_state.tenant_exec_config["api_key"] = api_key_input
                st.session_state.exec_config["fetch_interval_min"] = fetch_freq
                st.success("🎉 外部 API 參數與擷取頻率已成功生效！")

# 兼容包裝函式
def show(tenant_info=None, lang="繁體中文", **kwargs):
    render_system_licensing_page(tenant_info=tenant_info, lang=lang, **kwargs)

def main(tenant_info=None, lang="繁體中文", **kwargs):
    render_system_licensing_page(tenant_info=tenant_info, lang=lang, **kwargs)
