import streamlit as st
import pandas as pd

def render_asset_management_page(sub_option=None):
    st.title("📦 裕豐電機工業 - 生產設備與資產管理")
    st.caption("管理西寧廠 CNC 銅排加工機、數控折床、自動烤漆塗裝線與檢測設備。")

    if "asset_db" not in st.session_state:
        st.session_state.asset_db = [
            {"id": "EQ-TN-001", "name": "CNC 數控母線銅排彎折加工機", "category": "銅排加工設備", "site": "🇻🇳 西寧廠 - 板金組", "status": "在用", "cost": "$45,000"},
            {"id": "EQ-TN-002", "name": "AMADA 數控液壓折床 150T", "category": "板金加工設備", "site": "🇻🇳 西寧廠 - 板金組", "status": "在用", "cost": "$78,000"},
            {"id": "EQ-TN-003", "name": "懸掛式半自動粉體塗裝烤漆線", "category": "塗裝設備", "site": "🇻🇳 西寧廠 - 烤漆組", "status": "在用", "cost": "$120,000"},
            {"id": "EQ-TN-004", "name": "高壓耐壓與絕緣測試儀 (5kV)", "category": "品管與檢測儀器", "site": "🇻🇳 西寧廠 - 組裝組", "status": "在用", "cost": "$12,000"}
        ]

    tab_overview, tab_add = st.tabs(["📑 設備與資產總覽", "➕ 新建設備登記"])

    with tab_overview:
        df_assets = pd.DataFrame(st.session_state.asset_db)
        st.dataframe(df_assets, use_container_width=True)

    with tab_add:
        with st.form("form_add_asset"):
            a_name = st.text_input("設備/資產名稱 *")
            a_cat = st.selectbox("資產分類", ["銅排加工設備", "板金加工設備", "塗裝設備", "品管與檢測儀器", "廠務公務車輛"])
            a_site = st.selectbox("存放地點", ["🇻🇳 西寧廠 - 板金組", "🇻🇳 西寧廠 - 烤漆組", "🇻🇳 西寧廠 - 組裝組", "🇻🇳 西寧廠 - 倉庫"])
            a_cost = st.number_input("採購金額 (USD)", min_value=0.0, value=10000.0)

            if st.form_submit_button("💾 儲存資產資料"):
                new_id = f"EQ-TN-{len(st.session_state.asset_db)+1:03d}"
                st.session_state.asset_db.append({
                    "id": new_id, "name": a_name, "category": a_cat, "site": a_site, "status": "在用", "cost": f"${a_cost:,.0f}"
                })
                st.success("設備登錄成功！")
                st.rerun()

def show(sub_option=None):
    render_asset_management_page(sub_option)

def main(sub_option=None):
    render_asset_management_page(sub_option)
