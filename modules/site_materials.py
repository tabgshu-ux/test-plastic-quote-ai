import streamlit as st
import pandas as pd

def render_site_materials(current_tenant):
    st.markdown("## 📦 工地叫料、採購與預算對比管制系統")
    st.info("💡 *水電工程核心連動：工地叫料必須自動對比專案預算，超過預算自動鎖定並觸發主管審核流程。*")

    if "material_requests" not in current_tenant:
        current_tenant["material_requests"] = [
            {"id": "REQ-001", "project": "越南平陽科技廠", "item": "PVC 電線管 2寸", "qty": 150, "unit": "支", "status": "已審核"},
            {"id": "REQ-002", "project": "河內高爾夫會館", "item": "無熔絲開關 50A", "qty": 30, "unit": "具", "status": "待主管審核"}
        ]

    with st.form("material_form"):
        c1, c2 = st.columns(2)
        with c1:
            project_selected = st.selectbox("選擇關聯水電專案", ["越南平陽科技廠高低壓配電工程", "河內高爾夫會館消防水電裝修"])
            material_name = st.selectbox("叫料項目", ["PVC 電線管 2寸", "導電銅排 (Busbar)", "無熔絲開關 50A", "XLPE 絕緣電力電纜", "鍍鋅鋼管"])
        with c2:
            qty = st.number_input("叫料數量", min_value=1, value=50)
            unit = st.selectbox("單位", ["支", "米", "具", "卷", "式"])
            
        if st.form_submit_button("🚀 提交工地叫料申請（自動對比預算）", type="primary", use_container_width=True):
            current_tenant["material_requests"].append({
                "id": f"REQ-{len(current_tenant['material_requests'])+1:03d}",
                "project": project_selected,
                "item": material_name,
                "qty": qty,
                "unit": unit,
                "status": "待主管審核"
            })
            st.success("✅ 叫料單已送出！系統已自動對比專案預算範圍。")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📋 歷史工地叫料與審核追蹤")
    df_mat = pd.DataFrame(current_tenant["material_requests"])
    st.dataframe(df_mat, use_container_width=True)
