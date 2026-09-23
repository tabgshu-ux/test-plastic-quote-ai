import streamlit as st
import pandas as pd

def render_invoice_management_page():
    st.title("🧾 通用信箱電子發票讀取與解析系統")
    st.caption("自動連線 IMAP 信箱，讀取並解析近 30 天越南 XML 電子發票 (Hóa đơn điện tử)")

    with st.expander("⚙️ IMAP 信箱伺服器設定", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("IMAP Host", value="imap.gmail.com")
            st.text_input("帳號 (Email)", value="finance@company.com")
        with col2:
            st.number_input("Port", value=993)
            st.text_input("應用程式密碼", type="password", value="••••••••••••")

    st.subheader("📥 待解析/已匯入電子發票清單")
    
    invoices_data = pd.DataFrame({
        "發票號碼": ["INV-VN-2026-0891", "INV-VN-2026-0892", "INV-VN-2026-0893"],
        "賣方公司名稱": ["CÔNG TY TNHH HÓA CHẤT VIỆT NAM", "CÔNG TY ĐIỆN LỰC BÌNH DƯƠNG", "CÔNG TY NHỰA ĐÔNG OANH"],
        "稅號 (MST)": ["3701234567", "3709876543", "0101122334"],
        "未稅金額 (VND)": ["₫ 150,000,000", "₫ 45,200,000", "₫ 320,000,000"],
        "狀態": ["🟢 解析成功 (已過賬)", "🟢 解析成功 (待審核)", "🟡 XML 附件讀取中"]
    })
    
    st.dataframe(invoices_data, use_container_width=True)

def show():
    render_invoice_management_page()

def main():
    render_invoice_management_page()
