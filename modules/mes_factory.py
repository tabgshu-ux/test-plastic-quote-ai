import streamlit as st
import pandas as pd

def render_mes_factory(current_tenant):
    st.markdown("## 🏭 MES 製造執行系統：鞋款顏色與車間動態排程")
    st.info("💡 *前端門市客戶選定之鞋款顏色與尺寸，即時連動至橡膠射出機台與車間排程。*")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🎨 客製化鞋款顏色與車間派工單")
        
        col1, col2 = st.columns(2)
        with col1:
            shoe_color = st.selectbox("選定鞋款顏色 (Color)", ["拿鐵棕 (Latte Brown)", "抹茶綠 (Matcha Green)", "經典黑 (Classic Black)", "燕麥白 (Oatmeal White)"])
            shoe_size = st.selectbox("尺寸規格 (Size)", ["US 8", "US 9", "US 10", "US 11"])
            qty = st.number_input("排產數量 (雙)", value=50)
        with col2:
            machine_target = st.selectbox("指定橡膠射出機台", ["A1 號射出成型機", "A2 號自動化機台", "B1 號環保鞋大底機"])
            priority = st.selectbox("生產優先級", ["🔥 加急單 (Urgent)", "⚡ 標準排程 (Normal)"])
            
        if st.button("🚀 立即拋轉至車間 MES 排程", type="primary"):
            st.success(f"🎉 成功建立派工單！已將 [{shoe_color}] 尺寸 [{shoe_size}] 數量 [{qty} 雙] 指派至 [{machine_target}]進行生產。")
        st.markdown('</div>', unsafe_allow_html=True)
