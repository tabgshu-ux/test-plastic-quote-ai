import streamlit as st
import pandas as pd

def render_pos_retail(current_tenant):
    st.markdown("## ☕ 智慧零售、POS 收銀與會員咖啡廳管理系統")
    st.info("💡 *專為異業結盟設計：買咖啡絲環保鞋即贈免費咖啡額度、人臉辨識快速辨識、推薦分潤與電動車激勵競賽。*")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 💳 POS 收銀機與多幣別結算")
        st.write("支援 USD、TWD、VND、RMB 多幣別即時換算與電子發票開立。")
        pay_method = st.selectbox("選擇付款方式", ["現金 (Cash)", "信用卡/行動支付 (Card/Mobile Pay)", "跨境數位錢包"])
        amount = st.number_input("結算金額 (USD)", value=150.0)
        if st.button("🖨️ 確認結算並列印發票", type="primary"):
            st.success(f"🎉 結算成功！已透過 [{pay_method}] 完成 $ {amount} USD 交易，並同步扣減庫存。")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### ☕ VIP 咖啡廳免費額度與人臉辨識")
        st.write("AI 鏡頭偵測到 VIP 會員進場，自動帶出剩餘咖啡杯數與推薦積分。")
        member_phone = st.text_input("輸入會員手機或刷臉辨識 ID", value="0912-345-678")
        st.metric("會員剩餘免費咖啡額度", "12 / 30 杯")
        if st.button("☕ 兌換 1 杯拿鐵 (扣減額度)"):
            st.success("✅ 兌換成功！已扣除 1 杯，今日剩餘 11 杯。")
        st.markdown('</div>', unsafe_allow_html=True)
