import streamlit as st
import pandas as pd

def render_pos_retail(current_tenant):
    st.markdown("## ☕ 智慧零售、POS 收銀與會員行銷管理系統")
    st.info("💡 *標準 POS 收銀與多幣別結算模組，支援實體門市銷售、電子發票、會員管理，並完整整合越南在地主流 QR Code 掃碼支付與多種零售行銷模式。*")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 💳 POS 收銀與多元支付 (含越南在地掃碼)")
        st.write("支援 USD、TWD、VND、RMB 多幣別即時換算，並針對越南市場深度整合主流行動支付。")
        
        pay_method = st.selectbox(
            "選擇付款方式", 
            [
                "📱 QR Code 動態掃碼支付 (MoMo / ZaloPay / VNPay)", 
                "💵 現金結算 (Cash)", 
                "💳 實體信用卡 / 金融卡 (Card)", 
                "🌐 跨境數位錢包 / 銀行轉帳 (Bank Transfer)"
            ]
        )
        
        # 針對 QR Code 支付顯示額外提示
        if "QR Code" in pay_method:
            st.info("📲 *系統將自動連動支付閘道生成 QR Code，供顧客使用手機快速掃碼扣款。*")
            
        amount = st.number_input("結算金額 (VND / USD)", value=350000.0)
        
        if st.button("🖨️ 確認結算並開立電子發票", type="primary"):
            st.success(f"🎉 結算成功！已透過 [{pay_method}] 完成交易金額，並同步寫入財會總帳與庫存扣減。")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 👥 會員與行銷活動管理")
        st.write("記錄消費者歷程、積分回饋、會員專屬額度與推廣激勵機制。")
        member_id = st.text_input("輸入會員編號或刷卡辨識 ID", value="M-2026-8888")
        st.metric("目前會員可用回饋/額度", "12 點 / 專屬優惠中")
        if st.button("🎁 套用會員行銷折扣"):
            st.success("✅ 折扣套用成功！已自動計算促銷方案。")
        st.markdown('</div>', unsafe_allow_html=True)
