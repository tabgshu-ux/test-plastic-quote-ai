import email
from email.header import decode_header
import imaplib
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st

def parse_vietnam_xml(xml_bytes):
    try:
        root = ET.fromstring(xml_bytes)
        def get_text(node, tag_name):
            if node is None: return ""
            for elem in node.iter():
                if elem.tag.endswith(tag_name): return elem.text.strip() if elem.text else ""
            return ""

        return {
            "invoice_no": get_text(root, "SHDon") or get_text(root, "InvoiceNo"),
            "pattern": get_text(root, "KHMSHDon") or get_text(root, "InvoicePattern"),
            "seller_name": get_text(root, "TenNBan") or get_text(root, "ComName"),
            "seller_tax_code": get_text(root, "MSTNBan") or get_text(root, "ComTaxCode"),
            "total_amount": float(get_text(root, "TgTTTBSo") or get_text(root, "TotalAmountWithVAT") or 0),
            "currency": get_text(root, "DVTTe") or "VND",
            "date": get_text(root, "NLap") or get_text(root, "AriseDate"),
        }
    except Exception as e:
        st.error(f"❌ XML 解析失敗: {e}")
        return None

def render_invoice_management():
    st.subheader("🇻🇳 越南電子發票自動讀取與登記中心")
    if "invoice_db" not in st.session_state:
        st.session_state.invoice_db = []

    uploaded_xml = st.file_uploader("選擇越南電子發票檔 (.xml)", type=["xml"])
    if uploaded_xml is not None:
        parsed_data = parse_vietnam_xml(uploaded_xml.read())
        if parsed_data:
            st.success("✅ XML 發票解析成功！")
            st.json(parsed_data)
            if st.button("💾 確認匯入系統資料庫", type="primary"):
                parsed_data["uploader"] = st.session_state.user_info["name"]
                st.session_state.invoice_db.append(parsed_data)
                st.success("🎉 發票已成功登錄！")
                st.rerun()

    st.divider()
    if st.session_state.invoice_db:
        st.dataframe(pd.DataFrame(st.session_state.invoice_db), use_container_width=True)
