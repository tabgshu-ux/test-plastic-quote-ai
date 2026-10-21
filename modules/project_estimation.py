import streamlit as st
import pandas as pd

def render_project_estimation(current_tenant):
    st.markdown("## 📋 水電工程專案估驗與多幣別報價系統")
    st.info("💡 *支援台幣 (TWD)、美元 (USD)、越南盾 (VND)、人民幣 (RMB) 等多幣別報價與專案工項預算編號轉換。*")

    if "projects_db" not in current_tenant:
        current_tenant["projects_db"] = [
            {"code": "PRJ-2026-01", "name": "越南平陽科技廠高低壓配電工程", "client": "Binh Duong Tech", "currency": "USD", "amount": 180000, "status": "施工中"},
            {"code": "PRJ-2026-02", "name": "河內高爾夫會館消防水電裝修", "client": "Hanoi Golf Club", "currency": "VND", "amount": 4500000000, "status": "規劃中"}
        ]

    tab_add, tab_list = st.tabs(["➕ 1. 新增專案估驗與報價", "📊 2. 專案合約與估驗進度清單"])

    with tab_add:
        with st.form("estimation_form"):
            c1, c2 = st.columns(2)
            with c1:
                proj_code = st.text_input("專案編號 (Project Code)", value="PRJ-2026-03")
                proj_name = st.text_input("專案與案場名稱", placeholder="例: 胡志明市商辦大樓配電工程")
                client_name = st.text_input("業主 / 客戶名稱", placeholder="例: Vina Real Estate")
            with c2:
                currency = st.selectbox("計價幣別 (Currency)", ["USD (美元)", "VND (越南盾)", "RMB (人民幣)", "TWD (新台幣)"])
                total_amount = st.number_input("專案總報價金額", min_value=0.0, value=50000.0, step=1000.0)
                status = st.selectbox("專案階段", ["規劃中 (Planning)", "施工中 (In Progress)", "已完工驗收 (Completed)"])

            if st.form_submit_button("💾 儲存並轉入專案預算編號", type="primary", use_container_width=True):
                if proj_code.strip() and proj_name.strip():
                    current_tenant["projects_db"].append({
                        "code": proj_code.strip(),
                        "name": proj_name.strip(),
                        "client": client_name.strip(),
                        "currency": currency.split()[0],
                        "amount": total_amount,
                        "status": status
                    })
                    st.success(f"🎉 成功建立專案【{proj_name}】！已自動轉為系統預算編號與應收帳款基準。")
                    st.rerun()
                else:
                    st.error("❌ 請填寫專案編號與名稱！")

    with tab_list:
        st.markdown("### 📋 現有水電專案合約與估驗清單")
        df_proj = pd.DataFrame(current_tenant["projects_db"])
        
        edited_proj = st.data_editor(
            df_proj,
            num_rows="dynamic",
            use_container_width=True,
            key="proj_editor"
        )
        
        if st.button("💾 儲存專案修改變更", type="primary"):
            current_tenant["projects_db"] = edited_proj.to_dict(orient="records")
            st.success("✅ 專案資料庫已更新！")
            st.rerun()
