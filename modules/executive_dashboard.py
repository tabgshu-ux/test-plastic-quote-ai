import streamlit as st
import pandas as pd
import numpy as np

def render_executive_dashboard_page():
    st.title("📈 跨國營運戰情室 (Executive Dashboard)")
    st.caption("即時監控台灣總部、東莞廠與平陽廠之營運數據、匯率趨勢與應收帳款預警")

    # 關鍵指標卡片
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("本月集團總營收 (USD)", "$1,280,000", "+8.5%")
    col2.metric("台灣總部 (TWD)", "NT$ 12,500,000", "+3.2%")
    col3.metric("東莞廠 (RMB)", "¥ 3,400,000", "-1.5%")
    col4.metric("越南平陽廠 (VND)", "₫ 12.8 Billion", "+12.4%")

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📊 近半季三廠營收成長趨勢 (USD)")
        chart_data = pd.DataFrame(
            np.random.randn(20, 3) * 10000 + [50000, 40000, 35000],
            columns=['台灣總部 (TW)', '東莞廠 (DG)', '平陽廠 (BH)']
        )
        st.line_chart(chart_data)

    with col_right:
        st.subheader("🚨 AR / DSO 應收帳款預警")
        st.warning("⚠️ **Nike Vietnam**: 帳款逾期 15 天 ($45,000 USD)")
        st.info("ℹ️ **Adidas Taiwan**: 預計 3 天內入帳 (NT$ 1,200,000)")
        st.success("✅ **Shopee Seller A**: 帳款已全數結清")

# 相容舊版進入點名稱
def show():
    render_executive_dashboard_page()

def main():
    render_executive_dashboard_page()
