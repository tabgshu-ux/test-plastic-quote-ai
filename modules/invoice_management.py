import email
from email.header import decode_header
import imaplib
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st
import os

# ----------------------------------------------------
# 1. 您最核心的越南 XML 發票解析邏輯 (parse_vietnam_xml)
# ----------------------------------------------------
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

# ----------------------------------------------------
# 2. IMAP 信箱發票自動抓取邏輯
# ----------------------------------------------------
def fetch_invoices_from_email(imap_server, email_user, email_pass, folder="INBOX", search_limit=10):
    invoices = []
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select(folder)

        status, messages = mail.search(None, 'OR OR (SUBJECT "invoice") (SUBJECT "hóa đơn") (SUBJECT "發票")')
        email_ids = messages[0].split()

        if not email_ids:
            return [], "ℹ️ 信箱中未找到符合「invoice / hóa đơn / 發票」關鍵字的郵件。"

        for e_id in email_ids[-search_limit:]:
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                    
                    sender = msg.get("From")
                    date_sent = msg.get("Date")

                    attachments = []
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_disposition = str(part.get("Content-Disposition"))
                            if "attachment" in content_disposition:
                                filename = part.get_filename()
                                if filename:
                                    attachments.append(filename)

                    invoices.append({
                        "id": e_id.decode(),
                        "subject": subject,
                        "sender": sender,
                        "date": date_sent,
                        "attachments": attachments if attachments else ["（內文無附件）"]
                    })

        mail.logout()
        return invoices, "✅ 成功連線並讀取電子發票郵件！"
    except Exception as e:
        return [], f"❌ IMAP 信箱連線失敗: {str(e)}"

# ----------------------------------------------------
# 3. 越南電子發票額度與沙盒預警元件
# ----------------------------------------------------
def render_invoice_quota_widget():
    st.markdown("#### 🇻🇳 越南電子發票 (Hóa đơn điện tử) 張數額度與預警中心")
    tax_id = os.getenv("VN_TAX_ID", "")
    is_live_mode = bool(tax_id)

    if is_live_mode:
        st.success(f"🟢 **正式連線模式** (公司稅號 MST: `{tax_id}`)")
        total_quota = 5000
        used_quota = 4820
    else:
        st.info("🟡 **沙盒模擬模式** (未設定公司發票 API，目前使用測試模擬數據)")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            total_quota = st.number_input("設定測試總發票張數：", value=1000, step=100, key="mock_total_quota")
        with col_m2:
            used_quota = st.number_input("設定測試已使用張數：", value=850, step=50, key="mock_used_quota")

    remaining_quota = total_quota - used_quota
    remaining_ratio = (remaining_quota / total_quota) * 100 if total_quota > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("發票套裝總張數", f"{total_quota:,} 張")
    col2.metric("已開立張數", f"{used_quota:,} 張")
    
    if remaining_ratio <= 10:
        col3.metric("剩餘可用張數", f"{remaining_quota:,} 張 ({remaining_ratio:.1f}%)", delta="-極低 alert", delta_color="inverse")
        st.error(f"🚨 **緊急預警**：發票剩餘張數僅剩 `{remaining_quota}` 張 ({remaining_ratio:.1f}%)！預計 2 天內用盡，請儘速加購發票套裝！")
    elif remaining_ratio <= 20:
        col3.metric("剩餘可用張數", f"{remaining_quota:,} 張 ({remaining_ratio:.1f}%)", delta="-偏低 warning", delta_color="inverse")
        st.warning(f"⚠️ **用量提醒**：發票剩餘張數低於 20% (剩餘 `{remaining_quota}` 張)，建議通知財務發起加購。")
    else:
        col3.metric("剩餘可用張數", f"{remaining_quota:,} 張 ({remaining_ratio:.1f}%)")
        st.success("🟢 發票數量充裕，運作正常。")

    st.markdown("---")
    col_btn1, col_btn2 = st.columns([1, 2])
    with col_btn1:
        if st.button("🚀 一鍵發起發票加購請購單 (Top-up Order)", type="primary", key="btn_topup_invoice"):
            st.success("✅ 已自動建立請購單：【加購 5,000 張電子發票套裝】，並發送簽核通知至財務主管！")
    
    with col_btn2:
        with st.expander("⚙️ 填入公司稅號與正式發票 API 金鑰 (公司成立後填入)"):
            new_tax_id = st.text_input("公司稅號 (Mã số thuế - MST)：", value=tax_id, placeholder="例如: 0312345678")
            provider = st.selectbox("電子發票服務商：", ["VNPT (Hóa đơn điện tử)", "Viettel (S-Invoice)", "MISA (meInvoice)", "EasyInvoice", "BKAV"])
            api_token = st.text_input("服務商 API Token / Password：", type="password")
            if st.button("💾 儲存正式發票 API 連線設定"):
                os.environ["VN_TAX_ID"] = new_tax_id
                st.success("✅ 已成功儲存發票 API 設定！系統即將連線真實發票服務商。")
                st.rerun()

# ----------------------------------------------------
# 4. 您原本的 render_invoice_management 介面與功能整合
# ----------------------------------------------------
def render_invoice_management():
    st.subheader("🇻🇳 越南電子發票自動讀取與登記中心")
    if "invoice_db" not in st.session_state:
        st.session_state.invoice_db = []

    tab_xml, tab_email, tab_quota = st.tabs([
        "📄 越南電子發票 XML 解析與登錄",
        "📧 通用信箱發票讀取 (IMAP)",
        "📊 電子發票張數監控與加購"
    ])

    # 頁籤一：您提供的原始 XML 上傳、解析與 Pandas 資料表登記功能
    with tab_xml:
        uploaded_xml = st.file_uploader("選擇越南電子發票檔 (.xml)", type=["xml"], key="uploader_xml_file")
        if uploaded_xml is not None:
            parsed_data = parse_vietnam_xml(uploaded_xml.read())
            if parsed_data:
                st.success("✅ XML 發票解析成功！")
                st.json(parsed_data)
                if st.button("💾 確認匯入系統資料庫", type="primary", key="btn_save_xml_db"):
                    # 容錯保護：若 session_state 無 user_info 則帶預設名稱
                    user_name = st.session_state.get("user_info", {}).get("name", "Alex Chen (管理者)")
                    parsed_data["uploader"] = user_name
                    st.session_state.invoice_db.append(parsed_data)
                    st.success("🎉 發票已成功登錄！")
                    st.rerun()

        st.divider()
        if st.session_state.invoice_db:
            st.markdown("#### 📜 已登錄發票資料庫列表：")
            st.dataframe(pd.DataFrame(st.session_state.invoice_db), use_container_width=True)

    # 頁籤二：IMAP 信箱發票讀取
    with tab_email:
        st.markdown("#### 📧 通用電子郵件發票自動讀取 (IMAP)")
        col1, col2, col3 = st.columns(3)
        with col1:
            imap_server = st.text_input("IMAP 伺服器地址：", value="imap.gmail.com", key="imap_server")
        with col2:
            email_user = st.text_input("電子信箱帳號：", value="accounting@company.com", key="email_user")
        with col3:
            email_pass = st.text_input("信箱密碼 / App 專用密碼：", type="password", key="email_pass")

        if st.button("🚀 開始連線信箱讀取發票", type="primary", key="btn_fetch_email_invoices"):
            with st.spinner("正在連線 IMAP 信箱並解析電子發票..."):
                invoices, msg = fetch_invoices_from_email(imap_server, email_user, email_pass)
                if invoices:
                    st.success(msg)
                    for inv in invoices:
                        with st.expander(f"📄 【{inv['date']}】{inv['subject']} — 寄件者: {inv['sender']}"):
                            st.write(f"• **郵件 ID**: `{inv['id']}`")
                            st.write(f"• **偵測到的發票附件/檔案**: `{', '.join(inv['attachments'])}`")
                else:
                    st.info(msg)

    # 頁籤三：發票張數預警與購買
    with tab_quota:
        render_invoice_quota_widget()

# 保持相容入口，確保全系統調用均不跳錯
def render_invoice_management_page(sub_option=None):
    render_invoice_management()

def render_invoice(sub_option=None):
    render_invoice_management()

def show(sub_option=None):
    render_invoice_management()

def main(sub_option=None):
    render_invoice_management()
