import streamlit as st
import pandas as pd

def render_pos_retail(current_tenant):
    st.markdown("## ☕ 智慧零售、POS 收銀與全球跨境支付管理系統")
    st.info("💡 *全球化 POS 收銀與多幣別結算模組，支援多國實體門市、電子發票與全球各地主流支付方式（如東南亞掃碼、歐美信用卡、台灣行動支付、中國行動支付等）。*")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 💳 全球多元支付與跨境金流閘道")
        st.write("系統自動對應當地主流支付工具，支援多幣別即時換算與清算。")
        
        # 依據全球區域分類的支付方式
        global_pay_category = st.selectbox(
            "選擇支付區域與類型",
            [
                "🇻🇳 越南在地支付 (MoMo, ZaloPay, VNPay, VietQR)",
                "🇹🇼 台灣主流支付 (Line Pay, 街口支付, Apple Pay, 悠遊卡)",
                "🇨🇳 大中華區支付 (微信支付 WeChat Pay, 阿里支付 Alipay)",
                "🌍 歐美與全球通用 (Visa, Mastercard, American Express, PayPal)",
                "💵 傳統現金與實體銀行轉帳 (Cash / Bank Wire)"
            ]
        )
        
        # 動態細分選項
        if "越南" in global_pay_category:
            pay_method = st.selectbox("越南支付渠道", ["VietQR 動態掃碼", "MoMo 錢包掃碼", "ZaloPay 掃碼", "VNPay-QR", "COD 現金貨到付款"])
        elif "台灣" in global_pay_category:
            pay_method = st.selectbox("台灣支付渠道", ["Line Pay 條碼支付", "街口支付", "Apple Pay / Google Pay", "台灣 Pay / 信用卡刷卡"])
        elif "大中華區" in global_pay_category:
            pay_method = st.selectbox("大中華支付渠道", ["微信支付 (WeChat Pay QR)", "支付寶 (Alipay QR)", "銀聯卡 (UnionPay)"])
        elif "歐美" in global_pay_category:
            pay_method = st.selectbox("國際信用卡與錢包", ["Visa / Master 刷卡 (感應/晶片)", "PayPal 跨境支付", "Apple Pay 國際版", "Google Pay"])
        else:
            pay_method = st.selectbox("傳統支付渠道", ["實體現金 (Cash)", "企業間電匯 (Bank Wire Transfer)"])
            
        st.info(f"🌐 *當前選擇結算通道：【{pay_method}】，系統將自動透過對應的跨境金流 API 進行授權與扣款。*")
            
        amount = st.number_input("結算金額", value=150.0)
        currency = st.selectbox("交易幣別", ["USD (美元)", "TWD (新台幣)", "VND (越南盾)", "RMB (人民幣)", "EUR (歐元)"])
        
        if st.button("🖨️ 確認結算並開立電子發票", type="primary"):
            st.success(f"🎉 跨國結算成功！已透過 [{pay_method}] 完成交易 [{amount} {currency}]，並同步寫入財會總帳與庫存扣減。")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("### 👥 全球會員與跨國行銷活動管理")
        st.write("統一管理多國消費者的會員歷程、跨國積分回饋與行銷促銷方案。")
        member_id = st.text_input("輸入會員編號或跨國會員 ID", value="GLOBAL-M-2026-88")
        st.metric("會員跨國可用點數/回饋", "120 點 (可跨分店折抵)")
        if st.button("🎁 套用全球通用促銷折扣"):
            st.success("✅ 跨國折扣套用成功！")
        st.markdown('</div>', unsafe_allow_html=True)
