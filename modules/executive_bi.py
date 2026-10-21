import streamlit as st
import pandas as pd

def render_executive_bi(current_tenant):
    """
    專屬模組：老闆級即時經營戰情室 (Executive BI)
    程式碼短小精幹，專注於決策戰情與視覺化圖表。
    """
    st.markdown(f"## 👑 {current_tenant['name']}：老闆級即時經營戰情室 (Executive BI)")
    st.info("💡 *此為最高決策者專屬戰情看板，整合跨部門營收、庫存預警與智慧鞋業/咖啡廳跨界行銷關鍵指標。*")
    
    # 四大核心指標卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 本月即時總營收", "$ 128,450 USD", "+ 12.5%")
    with col2:
        st.metric("☕ 咖啡廳今日免費杯數", "342 / 500 杯", "消耗率 68%")
    with col3:
        st.metric("👟 咖啡絲環保鞋產量", "1,250 雙", "稼動率 92%")
    with col4:
        st.metric("⚡ 電動車激勵競賽積分第一", "Le Van Hung", "推薦 28 人")
        
    st.markdown("---")
    
    # 雙欄分析與異常預警
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 📈 各鞋款顏色喜好與銷售佔比")
        chart_data = pd.DataFrame({
            "鞋款顏色": ["拿鐵棕 (Latte Brown)", "抹茶綠 (Matcha Green)", "經典黑 (Classic Black)", "燕麥白 (Oatmeal White)"],
            "銷售數量 (雙)": [450, 320, 280, 200]
        })
        st.bar_chart(chart_data.set_index("鞋款顏色"))
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_right:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 🚨 跨部門重大異常與庫存預警通知")
        st.warning("⚠️ **【庫存警報】** 「咖啡絲環保原料」安全水位偏低（剩餘 15%），建議立即發起自動補貨採購單。")
        st.info("ℹ️ **【審核通知】** 有 3 筆超過 $5,000 USD 的設備採購單正等待董事長室進行最終電子簽核。")
        st.success("✅ **【系統狀態】** POS 收銀機與人臉辨識門市連線正常，今日無異常中斷記錄。")
        st.markdown('</div>', unsafe_allow_html=True)
