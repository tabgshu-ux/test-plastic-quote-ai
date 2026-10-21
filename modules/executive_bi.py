import streamlit as st
import pandas as pd

def render_executive_bi(current_tenant):
    # 讀取該租戶的產業類型（預設為裕豐的電機製造業）
    industry_type = current_tenant.get("industry_type", "電機製造業")
    
    st.markdown(f"## 👑 {current_tenant['name']}：老闆級即時經營戰情室 (Executive BI)")
    st.info(f"💡 *系統自動識別當前租戶產業：【{industry_type}】，已為您動態加載專屬的營運指標與圖表引擎。*")
    
    # 根據不同產業動態渲染不同的戰情指標
    if industry_type == "電機製造業":
        # ⚡ 裕豐電機專屬指標
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 本月即時總營收", "$ 482,600 USD", "+ 15.4%")
        with col2:
            st.metric("⚡ 變壓器與配電盤產量", "340 台", "達成率 94%")
        with col3:
            st.metric("⚙️ 車間設備 OEE 稼動率", "88.5%", "+ 2.1%")
        with col4:
            st.metric("🛡️ 產品出廠檢驗良率", "99.2%", "高品質標準")
            
        st.markdown("---")
        
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 📈 主力電機產品線營收佔比")
            chart_data = pd.DataFrame({
                "產品系列": ["高低壓配電盤", "電力變壓器", "馬達控制中心", "工業自動化控制箱"],
                "銷售額 (USD)": [180000, 150000, 95000, 57600]
            })
            st.bar_chart(chart_data.set_index("產品系列"))
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c_right:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 🚨 廠務與關鍵原物料異常警報")
            st.warning("⚠️ **【庫存警報】** 銅線與導電銅排水位低於 18%，請採購部立即發起補貨。")
            st.info("ℹ️ **【審核通知】** 越南廠區有一筆 $35,000 USD 的數控折彎機採購案等待簽核。")
            st.success("✅ **【產線狀態】** 變壓器繞線機組運作正常。")
            st.markdown('</div>', unsafe_allow_html=True)
            
    elif industry_type == "鞋業與環保製造業":
        # 👟 鞋業製造專屬指標（如果未來有鞋業客戶）
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 本月即時總營收", "$ 210,000 USD", "+ 8.2%")
        with col2:
            st.metric("👟 環保鞋產量", "12,500 雙", "稼動率 91%")
        with col3:
            st.metric("咖啡絲原料存量", "3,200 公斤", "正常")
        with col4:
            st.metric("出貨準時率", "98.5%", "優良")
            
        st.markdown("---")
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 📈 各鞋款顏色銷售佔比")
            chart_data = pd.DataFrame({
                "鞋款顏色": ["拿鐵棕", "抹茶綠", "經典黑", "燕麥白"],
                "銷售數量 (雙)": [4500, 3200, 2800, 2000]
            })
            st.bar_chart(chart_data.set_index("鞋款顏色"))
            st.markdown('</div>', unsafe_allow_html=True)
        with c_right:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 🚨 生產與原料預警")
            st.warning("⚠️ 咖啡絲環保原料安全水位偏低。")
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        # 🌐 通用預設產業指標
        st.markdown("### 📈 通用企業營運戰情")
        st.metric("本月營收", "$ 100,000 USD")
