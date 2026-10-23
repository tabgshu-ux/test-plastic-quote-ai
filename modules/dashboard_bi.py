import streamlit as st
import pandas as pd

def render_dashboard_bi(tenant_info, user_perms):
    st.markdown("### 📈 全球企業戰情室與跨國 BI 分析中心")
    st.info("💡 *高階管理駕駛艙：即時掌握全球廠區營收總額、出勤率、MES 機台稼動率及各項異常警報。*")
    st.markdown("---")

    # 頂部關鍵指標卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="🌐 全球總營收 (USD)", value="$ 1,485,200", delta="+12.4%")
    with col2:
        st.metric(label="🏭 廠區機台稼動率", value="92.8%", delta="+1.5%")
    with col3:
        st.metric(label="⏱️ 今日出勤率", value="98.2%", delta="-0.3%")
    with col4:
        st.metric(label="🔴 待處理異常警報", value="2 筆", delta="-4 筆", delta_color="inverse")

    st.markdown("---")
    st.markdown("#### 📊 各廠區月度產能與營收分佈對比")
    chart_data = pd.DataFrame({
        "廠區": ["越南平陽廠 A 區", "越南平陽廠 B 區", "台北總公司"],
        "產能產值 (USD)": [650000, 480000, 355200]
    })
    st.bar_chart(chart_data.set_index("廠區"))
