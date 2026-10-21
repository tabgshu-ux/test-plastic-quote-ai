import streamlit as st
import pandas as pd

def render_executive_bi(current_tenant):
    st.markdown(f"## 👑 {current_tenant['name']}：水電工程專案經營戰情室")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 本月已估驗工程總值", "$ 482,600 USD", "+ 15.4%")
    with col2:
        st.metric("⚡ 進行中水電案場", "12 場", "施工中")
    with col3:
        st.metric("👷 現場總點工數", "145 人/天", "今日出勤")
    with col4:
        st.metric("🛡️ 工安零事故天數", "360 天", "標準達標")
        
    st.markdown("---")
    
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 📈 各大水電案場工程營收與估驗佔比")
        chart_data = pd.DataFrame({
            "案場名稱": ["越南平陽科技廠機電案", "河內高爾夫會館水電工程", "胡志明市商辦大樓配電", "廠房消防與管線工程"],
            "估驗金額 (USD)": [180000, 150000, 95000, 57600]
        })
        st.bar_chart(chart_data.set_index("案場名稱"))
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_right:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🚨 工地叫料與預算超支預警")
        st.warning("⚠️ **【預算警報】** 越南平陽廠水電案場之 PVC 管材叫料金額已達預算 85%，請工地主任留意。")
        st.info("ℹ️ **【估驗審核】** 辦公大樓水電工程第 3 期估驗款 $35,000 USD 待總經理簽核。")
        st.success("✅ **【進度正常】** 各案場今日點工與材料進場回報無異常。")
        st.markdown('</div>', unsafe_allow_html=True)
