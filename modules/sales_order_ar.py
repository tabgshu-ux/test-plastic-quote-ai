import streamlit as st
import pandas as pd
import datetime

def render_sales_order_ar_page(sub_option=None, lang="繁體中文"):
    st.title("📦 配電盤工程訂單與應收帳款管理 (Sales Order & AR)")
    st.caption("西寧廠配電盤新建工程、訂單追蹤與客戶分期應收帳款核銷。")

    if "ar_orders" not in st.session_state:
        st.session_state.ar_orders = pd.DataFrame([
            {
                "工程合約號": "HD-2026-TN01", 
                "客戶名稱": "CÔNG TY TNHH A-Z TÂY NINH", 
                "專案名稱": "西寧紡織廠 2000A 高壓主配電櫃新建工程", 
                "總金額 (VND)": 6350000000.0, 
                "付款條件": "30% 訂金 / 60% 進場 / 10% 驗收", 
                "當期應收 (VND)": 3810000000.0,
                "收款狀態": "⏳ 第二期未收款"
            }
        ])

    st.subheader("📋 配電盤工程項目與應付款期別")
    st.dataframe(st.session_state.ar_orders, use_container_width=True)

def show(sub_option=None, lang="繁體中文"):
    render_sales_order_ar_page(sub_option, lang)

def main(sub_option=None, lang="繁體中文"):
    render_sales_order_ar_page(sub_option, lang)
