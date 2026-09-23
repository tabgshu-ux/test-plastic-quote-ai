import streamlit as st
import pandas as pd

def render_erp_dashboard_page():
    st.title("🏭 廠區營運 KPI 戰情室 (ERP Dashboard)")
    st.caption("追蹤各廠區射出機稼動率、模具開發進度與良率統計")

    tab1, tab2 = st.tabs(["⚡ 設備稼動率與 OEE", "🛠️ 模具開發與試模進度"])

    with tab1:
        st.subheader("機台即時狀態")
        m1, m2, m3 = st.columns(3)
        m1.metric("平陽廠 (BH) 射出機稼动率", "88.5%", "+2.1%")
        m2.metric("東莞廠 (DG) 射出機稼动率", "76.2%", "-4.0%")
        m3.metric("平均成品不良率 (PPM)", "1,200 PPM", "-150 PPM")

        status_df = pd.DataFrame({
            "機台編號": ["INJ-BH-01", "INJ-BH-02", "INJ-DG-01", "INJ-DG-02", "INJ-TW-01"],
            "鎖模噸數": ["250T", "350T", "180T", "500T", "120T"],
            "目前生產產品": ["喬丹10代橡膠大底", "EVA中底熱壓", "精密塑膠齒輪", "汽配外殼", "研發打樣"],
            "狀態": ["🟢 正常生產", "🟢 正常生產", "🟡 換模準備中", "🔴 停機維修", "🟢 正常生產"]
        })
        st.table(status_df)

    with tab2:
        st.subheader("開發中模具履歷")
        mold_df = pd.DataFrame({
            "模具編號": ["MOLD-2026-001", "MOLD-2026-002", "MOLD-2026-003"],
            "客戶": ["Nike", "Adidas", "Foxconn"],
            "模穴數": ["1模2穴", "1模4穴", "1模1穴"],
            "目前階段": ["T1 試模完成", "CNC 精雕溝槽中", "檢討 DFM 圖面"],
            "預計量產日": ["2026-04-10", "2026-04-25", "2026-05-01"]
        })
        st.dataframe(mold_df, use_container_width=True)

def show():
    render_erp_dashboard_page()

def main():
    render_erp_dashboard_page()
