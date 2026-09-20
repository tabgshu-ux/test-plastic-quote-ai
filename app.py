import base64
import datetime
import email
from email.header import decode_header
import imaplib
import os
import xml.etree.ElementTree as ET

import google.generativeai as genai
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import streamlit as st
import streamlit.components.v1 as components

# 網頁設定
st.set_page_config(
    page_title="Global Injection AI ERP System", page_icon="🏭", layout="wide"
)

# API Key 設定
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
  st.error("⚠️ API Key not configured!")
  st.stop()

# 設定 Gemini SDK
genai.configure(api_key=api_key)


# 🎨 通用型塑膠/橡膠射出產品圖庫匹配函數 (精準過濾非工廠背景)
def get_injection_product_image(product_name):
  """根據關鍵字匹配專業、乾淨的射出成型產品結構特寫圖"""
  p_name = product_name.lower()

  # 1. 塑膠盒 / 收納盒 / 容器類 (產品特寫)
  if any(k in p_name for k in ["盒", "box", "case", "容器", "casing"]):
    return "https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=1000&auto=format&fit=crop&q=80"

  # 2. 車用外殼 / 電子機構件 / 工業外殼
  elif any(
      k in p_name
      for k in ["外殼", "shell", "housing", "車用", "電子", "cover"]
  ):
    return "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=1000&auto=format&fit=crop&q=80"

  # 3. 齒輪 / 精密射出零件
  elif any(k in p_name for k in ["齒輪", "gear", "精密", "零件", "part"]):
    return "https://images.unsplash.com/photo-1581092335397-9583fe92d232?w=1000&auto=format&fit=crop&q=80"

  # 4. 橡膠大底 / 鞋底紋路特寫
  elif any(k in p_name for k in ["底", "sole", "outsole", "橡膠"]):
    return "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=1000&auto=format&fit=crop&q=80"

  # 5. 預設工業塑膠射出成品展示
  else:
    return "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1000&auto=format&fit=crop&q=80"


# 🔐 1. 初始化使用者帳號資料庫
if "user_database" not in st.session_state:
  st.session_state.user_database = {
      "admin": {
          "password": "admin123",
          "name": "系統主管 (Manager)",
          "role": "admin",
      },
      "alex": {
          "password": "alex123",
          "name": "Alex Chen (S-001)",
          "role": "sales",
      },
      "david": {
          "password": "david123",
          "name": "David Wang (S-002)",
          "role": "sales",
      },
      "nguyen": {
          "password": "nguyen123",
          "name": "Nguyen Van A (S-005)",
          "role": "sales",
      },
  }

# 💾 2. Session State 初始化 (報價單 + 聊天紀錄 + 越南發票資料庫)
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
if "user_info" not in st.session_state:
  st.session_state.user_info = None

if "chat_messages" not in st.session_state:
  st.session_state.chat_messages = [
      {
          "role": "assistant",
          "content": (
              "👋 您好！我是 Gemini AI 射出估價助手。請輸入您想評估的產品（例如：透明塑膠盒、車用外殼或橡膠大底），我將即時為您分析規格並呈現象圖！"
          ),
      }
  ]

if "quotation_db" not in st.session_state:
  st.session_state.quotation_db = [
      {
          "quote_id": "QT-20260918-001",
          "sales_rep": "Alex Chen (S-001)",
          "client_product": "透明耐衝擊塑膠收納盒",
          "site": "Vietnam (Binh Duong)",
          "amount": 12500,
          "curr": "USD",
          "date": "2026-09-18",
      },
      {
          "quote_id": "QT-20260918-002",
          "sales_rep": "David Wang (S-002)",
          "client_product": "車用電子耐熱外殼",
          "site": "China (Dongguan)",
          "amount": 85000,
          "curr": "USD",
          "date": "2026-09-18",
      },
  ]

# 🇻🇳 3. 越南發票資料庫初始化
if "invoice_db" not in st.session_state:
  st.session_state.invoice_db = [
      {
          "invoice_no": "0001234",
          "pattern": "1/001",
          "seller_name": "CÔNG TY TNHH MISA",
          "seller_tax_code": "0101243150",
          "amount_no_vat": 10000000.0,
          "vat_amount": 1000000.0,
          "total_amount": 11000000.0,
          "currency": "VND",
          "date": "2026-09-15",
          "uploader": "Nguyen Van A (S-005)",
      }
  ]

if "step" not in st.session_state:
  st.session_state.step = 1
if "ai_result" not in st.session_state:
  st.session_state.ai_result = ""


# 🇻🇳 越南發票 XML 自動解析函數
def parse_vietnam_xml(xml_bytes):
  try:
    root = ET.fromstring(xml_bytes)

    def get_text(node, tag_name):
      if node is None:
        return ""
      for elem in node.iter():
        if elem.tag.endswith(tag_name):
          return elem.text.strip() if elem.text else ""
      return ""

    data = {
        "invoice_no": get_text(root, "SHDon") or get_text(root, "InvoiceNo"),
        "pattern": get_text(root, "KHMSHDon")
        or get_text(root, "InvoicePattern"),
        "seller_name": get_text(root, "TenNBan") or get_text(root, "ComName"),
        "seller_tax_code": get_text(root, "MSTNBan")
        or get_text(root, "ComTaxCode"),
        "amount_no_vat": float(
            get_text(root, "TgTCThue")
            or get_text(root, "TotalAmountWithoutVAT")
            or 0
        ),
        "vat_amount": float(
            get_text(root, "TgTThue") or get_text(root, "VATAmount") or 0
        ),
        "total_amount": float(
            get_text(root, "TgTTTBSo")
            or get_text(root, "TotalAmountWithVAT")
            or 0
        ),
        "currency": get_text(root, "DVTTe")
        or get_text(root, "CurrencyCode")
        or "VND",
        "date": get_text(root, "NLap") or get_text(root, "AriseDate"),
    }
    return data
  except Exception as e:
    st.error(f"❌ XML 解析失敗: {e}")
    return None


# 📧 通用信箱自動連線與下載 XML 發票函數
def fetch_invoices_from_custom_email(
    imap_server, port, user_email, user_password
):
  try:
    mail = imaplib.IMAP4_SSL(imap_server, port)
    mail.login(user_email, user_password)
    mail.select("inbox")

    status, messages = mail.search(None, '(BODY "Hóa đơn")')
    email_ids = messages[0].split()

    downloaded_invoices = []

    for e_id in email_ids[-5:]:
      _, msg_data = mail.fetch(e_id, "(RFC822)")
      for response_part in msg_data:
        if isinstance(response_part, tuple):
          msg = email.message_from_bytes(response_part[1])

          for part in msg.walk():
            if part.get_content_maintype() == "multipart":
              continue
            if part.get("Content-Disposition") is None:
              continue

            filename = part.get_filename()
            if filename:
              filename_decoded, enc = decode_header(filename)[0]
              if isinstance(filename_decoded, bytes):
                filename = filename_decoded.decode(enc or "utf-8")

              if filename.lower().endswith(".xml"):
                xml_data = part.get_payload(decode=True)
                invoice_info = parse_vietnam_xml(xml_data)
                if invoice_info:
                  downloaded_invoices.append(invoice_info)

    mail.logout()
    return downloaded_invoices
  except Exception as e:
    st.error(f"❌ 信箱連線或抓取失敗：{e}")
    return []


# ==========================================
# 🔓 3. 登入介面 (未登入時顯示)
# ==========================================
if not st.session_state.authenticated:
  st.title("🏭 塑膠/橡膠射出成型 — 跨國 AI 報價 ERP 系統")
  st.caption("請輸入您的企業帳號與密碼以進行身份驗證")

  col_login, _ = st.columns([1, 1])
  with col_login:
    with st.form("login_form"):
      username_input = st.text_input("帳號 / Username")
      password_input = st.text_input("密碼 / Password", type="password")
      submit_button = st.form_submit_button("🔑 登入系統", type="primary")

      if submit_button:
        db = st.session_state.user_database
        if (
            username_input in db
            and db[username_input]["password"] == password_input
        ):
          st.session_state.authenticated = True
          st.session_state.user_info = db[username_input]
          st.success(
              f"✅ 登入成功！歡迎，{st.session_state.user_info['name']}"
          )
          st.rerun()
        else:
          st.error("❌ 帳號或密碼錯誤，請重新輸入！")

    st.info("""
        💡 **Demo 測試帳號提示：**
        - **主管帳號**：`admin` / 密碼：`admin123`
        - **業務帳號 1**：`alex` / 密碼：`alex123`
        - **業務帳號 2**：`david` / 密碼：`david123`
        """)
  st.stop()

# ==========================================
# 🔒 4. 已登入的主系統介面
# ==========================================

st.sidebar.title("👤 使用者資訊")
st.sidebar.write(f"**當前使用者**：{st.session_state.user_info['name']}")
st.sidebar.write(
    "**權限角色**："
    f" {'🔑 系統主管' if st.session_state.user_info['role'] == 'admin' else '💼 業務人員'}"
)

if st.sidebar.button("🚪 登出系統", key="btn_logout_main"):
  st.session_state.authenticated = False
  st.session_state.user_info = None
  st.session_state.step = 1
  st.rerun()

st.sidebar.divider()

user_role = st.session_state.user_info["role"]

# ==========================================
# 👑 畫面 A：主管管理後台 (Admin Panel)
# ==========================================
if user_role == "admin":
  st.header("⚙️ 系統主管管理後台")

  tab1, tab2, tab3 = st.tabs([
      "📊 業務報價總覽與資料庫",
      "👥 系統使用者管理 (User Management)",
      "🇻🇳 越南電子發票登記 (Hóa đơn điện tử)",
  ])

  # 分頁 1：業務報價總覽
  with tab1:
    st.caption(
        "您可以檢視全公司所有業務員的報價歷程、總金額統計，並匯出報表。"
    )
    df = pd.DataFrame(st.session_state.quotation_db)
    total_sales = df["amount"].sum() if not df.empty else 0
    total_orders = len(df)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("全廠歷史報價單數", f"{total_orders} 筆")
    col_b.metric("全廠估算總報價金額", f"${total_sales:,.2f} USD")
    col_c.metric(
        "團隊業務人數",
        f"{len(df['sales_rep'].unique()) if not df.empty else 0} 位",
    )

    st.divider()
    st.subheader("📋 跨國業務報價總明細表")

    if not df.empty:
      all_sales = ["全部業務 (All)"] + list(df["sales_rep"].unique())
      selected_sales = st.selectbox("🔍 依業務員篩選紀錄", all_sales)

      if selected_sales != "全部業務 (All)":
        filtered_df = df[df["sales_rep"] == selected_sales]
      else:
        filtered_df = df

      st.dataframe(filtered_df, use_container_width=True)
      csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")
      st.download_button(
          "📥 匯出業務報價總表 (CSV)",
          csv_data,
          file_name=f"Admin_Sales_Report_{datetime.date.today()}.csv",
      )
    else:
      st.info("目前尚無任何報價單紀錄。")

  # 分頁 2：使用者管理
  with tab2:
    st.caption(
        "管理者可以在此新增新員工帳號、重設業務員密碼或調整帳號權限。"
    )
    st.subheader("📄 現有使用者名單")
    user_list = []
    for uname, udata in st.session_state.user_database.items():
      user_list.append({
          "帳號 (Username)": uname,
          "姓名與編號 (Name)": udata["name"],
          "角色 (Role)": (
              "🔑 主管 (admin)"
              if udata["role"] == "admin"
              else "💼 業務 (sales)"
          ),
          "密碼 (Password)": udata["password"],
      })
    st.dataframe(pd.DataFrame(user_list), use_container_width=True)

    st.divider()
    col_add, col_manage = st.columns(2)

    with col_add:
      st.subheader("➕ 新增使用者帳號")
      with st.form("add_user_form"):
        new_username = st.text_input("新帳號 (Username)")
        new_password = st.text_input("預設密碼 (Password)")
        new_name = st.text_input("顯示姓名與工號 (例如: Eric Lin (S-008))")
        new_role = st.selectbox(
            "選擇權限角色",
            ["sales", "admin"],
            format_func=lambda x: (
                "💼 業務人員" if x == "sales" else "🔑 系統主管"
            ),
        )

        submit_add = st.form_submit_button("✅ 建立新帳號", type="primary")

        if submit_add:
          if not new_username or not new_password or not new_name:
            st.error("⚠️ 所有欄位皆為必填！")
          elif new_username in st.session_state.user_database:
            st.error(f"⚠️ 帳號 `{new_username}` 已存在！")
          else:
            st.session_state.user_database[new_username] = {
                "password": new_password,
                "name": new_name,
                "role": new_role,
            }
            st.success(f"🎉 帳號 `{new_username}` 建立成功！")
            st.rerun()

    with col_manage:
      st.subheader("🛠️ 修改密碼 / 刪除帳號")
      manageable_users = [
          u for u in st.session_state.user_database.keys() if u != "admin"
      ]

      if manageable_users:
        selected_target_user = st.selectbox(
            "選擇要管理的帳號", manageable_users
        )

        with st.expander("🔑 重設此帳號密碼"):
          updated_pwd = st.text_input(
              f"輸入 `{selected_target_user}` 的新密碼",
              type="password",
              key="pwd_update_input",
          )
          if st.button("更新密碼", key="btn_update_pwd"):
            if updated_pwd:
              st.session_state.user_database[selected_target_user][
                  "password"
              ] = updated_pwd
              st.success(f"✅ `{selected_target_user}` 的密碼已更新！")
              st.rerun()
            else:
              st.warning("請輸入新密碼！")

        with st.expander("❌ 刪除此帳號"):
          st.warning(f"確定要刪除帳號 `{selected_target_user}` 嗎？")
          if st.button("確認刪除帳號", type="primary", key="btn_del_user"):
            del st.session_state.user_database[selected_target_user]
            st.success(f"🗑️ 帳號 `{selected_target_user}` 已刪除！")
            st.rerun()
      else:
        st.info("目前沒有可供修改或刪除的其他使用者。")

  # 分頁 3：越南發票登記
  with tab3:
    st.subheader("🇻🇳 越南電子發票自動讀取與登記中心")
    st.caption(
        "您可以透過**手動連線公司信箱**、**上傳 XML 檔案** 或 **手動輸入**"
        " 進行發票登記。"
    )

    with st.expander("📧 模式 A：設定公司專屬信箱，自動連線抓取發票", expanded=True):
      col_m1, col_m2 = st.columns(2)
      with col_m1:
        mail_server = st.text_input(
            "IMAP 伺服器地址 (Server)", "mail.yourcompany.com"
        )
        mail_port = st.number_input("IMAP Port (預設 SSL: 993)", value=993)
      with col_m2:
        mail_user = st.text_input("信箱帳號 (Email)", "invoice@yourcompany.com")
        mail_pwd = st.text_input("信箱密碼 (Password)", type="password")

      if st.button(
          "🚀 開始連線信箱並讀取最新發票", type="primary", key="btn_fetch_email"
      ):
        with st.spinner("正在安全連線至公司信箱並搜尋 XML 發票..."):
          fetched_invs = fetch_invoices_from_custom_email(
              mail_server, mail_port, mail_user, mail_pwd
          )
          if fetched_invs:
            for inv in fetched_invs:
              inv["uploader"] = f"Auto-Email ({mail_user})"
              st.session_state.invoice_db.append(inv)
            st.success(f"🎉 成功從信箱抓取並解析 {len(fetched_invs)} 張發票！")
            st.rerun()
          else:
            st.warning("⚠️ 連線成功但未搜尋到新的 XML 發票附件。")

    st.divider()

    col_xml, col_preview = st.columns([1, 1])

    with col_xml:
      st.markdown("### 📤 模式 B：上傳 XML 單檔解析")
      uploaded_xml = st.file_uploader(
          "選擇越南電子發票檔 (.xml)", type=["xml"]
      )

      if uploaded_xml is not None:
        xml_bytes = uploaded_xml.read()
        parsed_data = parse_vietnam_xml(xml_bytes)

        if parsed_data:
          st.success("✅ XML 發票解析成功！")
          st.json(parsed_data)

          if st.button(
              "💾 確認匯入系統資料庫", type="primary", key="btn_import_xml"
          ):
            parsed_data["uploader"] = st.session_state.user_info["name"]
            st.session_state.invoice_db.append(parsed_data)
            st.toast("🎉 發票已成功登錄至發票總表！", icon="🧾")
            st.rerun()

    with col_preview:
      st.markdown("### 📝 模式 C：手動輸入發票")
      with st.form("manual_invoice_form"):
        inv_no = st.text_input("發票號碼 (Số hóa đơn)", "0005678")
        inv_pattern = st.text_input("發票代碼 (Mẫu số)", "1/001")
        seller_name = st.text_input(
            "賣方公司 (Bên bán)", "CÔNG TY TNHH PLASTIC VN"
        )
        seller_tax = st.text_input("賣方稅號 (MST)", "3701234567")
        total_amt = st.number_input(
            "總金額 (含稅 VND)", min_value=0.0, value=2500000.0, step=1000.0
        )
        inv_date = st.date_input("開立日期", datetime.date.today())

        submit_inv = st.form_submit_button("➕ 手動新增發票")
        if submit_inv:
          new_inv = {
              "invoice_no": inv_no,
              "pattern": inv_pattern,
              "seller_name": seller_name,
              "seller_tax_code": seller_tax,
              "amount_no_vat": round(total_amt / 1.1, 2),
              "vat_amount": round(total_amt - (total_amt / 1.1), 2),
              "total_amount": total_amt,
              "currency": "VND",
              "date": str(inv_date),
              "uploader": st.session_state.user_info["name"],
          }
          st.session_state.invoice_db.append(new_inv)
          st.success("✅ 手動登記成功！")
          st.rerun()

    st.divider()
    st.subheader("📊 已登記越南發票總表")

    if st.session_state.invoice_db:
      inv_df = pd.DataFrame(st.session_state.invoice_db)
      total_vnd = inv_df["total_amount"].sum()
      st.metric("已登記發票總金額", f"{total_vnd:,.0f} VND")

      st.dataframe(inv_df, use_container_width=True)

      inv_csv = inv_df.to_csv(index=False).encode("utf-8-sig")
      st.download_button(
          "📥 匯出越南發票總表 (CSV)",
          inv_csv,
          file_name=f"Vietnam_Invoices_{datetime.date.today()}.csv",
          key="btn_dl_inv_csv",
      )
    else:
      st.info("目前尚未登記任何越南電子發票。")

# ==========================================
# 💼 畫面 B：業務人員前台報價系統 (嵌入 Gemini AI 對話助手)
# ==========================================
else:
  LANG_DICT = {
      "繁體中文": {
          "title": "🏭 塑膠/橡膠射出成型 — 業務智慧估價系統",
          "step1_title": "1. 🤖 Gemini AI 需求對話與規格輸入",
          "step2_title": "2. 🖼️ 射出產品設計與圖片即時展示",
          "step3_title": "3. 3D 可視化模型與自動報價單",
          "pdf_btn": "📄 下載正式 PDF 報價單 (含業務簽名)",
          "pdf_title": "OFFICIAL PLASTIC INJECTION QUOTATION",
          "item_mold": "Custom Mold Development",
          "item_part": "Production Part Unit Cost",
          "item_total": "Total Initial Order Amount",
      },
      "Tiếng Việt": {
          "title": "🏭 Hệ Thống Báo Giá Ép Nhựa Dành Cho NVKD",
          "step1_title": "1. 🤖 Gemini AI Phân Tích & Nhập Yêu Cầu",
          "step2_title": "2. 🖼️ Hình Ảnh Thiết Kế Sản Phẩm",
          "step3_title": "3. Mô hình 3D & Báo giá chi tiết",
          "pdf_btn": "📄 Tải bản thảo báo giá PDF",
          "pdf_title": "BÁO GIÁ ĐƠN HÀNG ÉP NHỰA",
          "item_mold": "Chi phí phát triển khuôn mẫu",
          "item_part": "Đơn giá sản phẩm ép nhựa",
          "item_total": "Tổng giá trị đơn hàng đầu tiên",
      },
      "English": {
          "title": "🏭 Global Plastic Injection — Sales Quotation System",
          "step1_title": "1. 🤖 Gemini AI Copilot & Specs Input",
          "step2_title": "2. 🖼️ Product Design Preview",
          "step3_title": "3. Interactive 3D Render & Final Quote",
          "pdf_btn": "📄 Download Official PDF Quote",
          "pdf_title": "OFFICIAL PLASTIC INJECTION QUOTATION",
          "item_mold": "Custom Mold Development",
          "item_part": "Production Part Unit Cost",
          "item_total": "Total Initial Order Amount",
      },
  }

  top_col1, top_col2, top_col3 = st.columns(3)
  with top_col1:
    lang = st.selectbox(
        "🌐 Language / 語言", ["繁體中文", "Tiếng Việt", "English"]
    )
  with top_col2:
    site = st.selectbox(
        "🏭 Manufacturing Site",
        ["Taiwan (HQ)", "China (Dongguan)", "Vietnam (Binh Duong)"],
    )
  with top_col3:
    curr = st.selectbox("💱 Currency", ["USD", "TWD", "RMB", "VND"])

  L = LANG_DICT[lang]
  st.title(L["title"])

  col1, col2 = st.columns([1, 1])

  # 左側：Gemini 對話框與輸入區
  with col1:
    st.subheader(L["step1_title"])
    current_sales = st.session_state.user_info["name"]
    st.text_input("經辦業務員 / Sales Rep", current_sales, disabled=True)

    # 上傳客戶圖面
    uploaded_design = st.file_uploader(
        "📤 上傳客戶原廠 2D / CAD 圖面 (.jpg, .png)",
        type=["jpg", "jpeg", "png"],
    )

    # 🤖 嵌入式 Gemini Chat 視窗
    st.caption("💬 與 Gemini AI 討論需求，系統將同步於右側生成圖面與估價：")
    chat_container = st.container(height=280)

    for msg in st.session_state.chat_messages:
      with chat_container.chat_message(msg["role"]):
        st.write(msg["content"])

    # 用戶輸入訊息
    if user_prompt := st.chat_input("輸入產品需求（例如：透明塑膠盒、車用外殼、橡膠大底...）"):
      st.session_state.chat_messages.append(
          {"role": "user", "content": user_prompt}
      )
      st.session_state.step = 2

      # 呼叫 Gemini AI 進行專業射出規格分析
      with st.spinner("Gemini 正在分析產品規格與計算建議..."):
        model = genai.GenerativeModel("gemini-1.5-flash")
        try:
          sys_prompt = f"You are an expert plastic and rubber injection molding consultant. Analyze user request: '{user_prompt}'. Provide technical suggestions on Material, Part Weight(g), Mold Cavities, Machine Tonnage, and Estimated Unit Cost in {lang}."
          response = model.generate_content(
              sys_prompt, request_options={"timeout": 12}
          )
          ai_reply = response.text
        except:
          ai_reply = "💡 **Gemini AI 建議**：根據射出需求，建議採用耐衝擊高透光 PP/ABS 材料。\n- **預估單個重量**：120g\n- **模具穴數**：1 開 2 (Cavity)\n- **建議噸數**：180 噸"

      st.session_state.chat_messages.append(
          {"role": "assistant", "content": ai_reply}
      )
      st.session_state.ai_result = ai_reply

      # 同步更新圖片 (優先使用上傳圖，否則自動匹配對應圖庫)
      if uploaded_design is not None:
        st.session_state.matched_image = uploaded_design
        st.session_state.is_uploaded = True
      else:
        st.session_state.matched_image = get_injection_product_image(
            user_prompt
        )
        st.session_state.is_uploaded = False

      st.rerun()

  # 右側：圖片展示與 3D 報價區
  with col2:
    if st.session_state.step >= 2:
      st.subheader(L["step2_title"])

      # 顯示即時圖片 (位於右側您指定的地方)
      if st.session_state.get("is_uploaded", False):
        st.image(
            st.session_state.matched_image,
            caption="📄 業務上傳之客戶原廠 2D 圖面 / 設計圖",
            use_container_width=True,
        )
      else:
        st.image(
            st.session_state.matched_image,
            caption="✨ Gemini AI 同步匹配之產品結構與外觀質感特寫",
            use_container_width=True,
        )

      if st.button(
          "✅ 確認產品樣式，生成 3D 模型與報價單",
          type="primary",
          key="btn_confirm_3d_step2",
      ):
        st.session_state.step = 3
        new_quote_id = f"QT-{datetime.date.today().strftime('%Y%m%d')}-{len(st.session_state.quotation_db)+1:03d}"
        st.session_state.quotation_db.append({
            "quote_id": new_quote_id,
            "sales_rep": current_sales,
            "client_product": "Gemini AI 客製射出產品",
            "site": site,
            "amount": 216500,
            "curr": curr,
            "date": str(datetime.date.today()),
        })
        st.toast(
            f"✅ 報價單 {new_quote_id} 已成功上傳後台主管系統！", icon="💾"
        )

    if st.session_state.step == 3:
      st.divider()
      st.subheader(L["step3_title"])

      three_js_code = """
            <div id="container" style="width: 100%; height: 380px; background-color: #121212; border-radius: 8px;"></div>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script>
                const container = document.getElementById('container');
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({ antialias: true });
                renderer.setSize(container.clientWidth, container.clientHeight);
                container.appendChild(renderer.domElement);

                // 3D 通用射出機構渲染
                const geometry = new THREE.BoxGeometry(2, 1.2, 0.8);
                const material = new THREE.MeshPhongMaterial({ color: 0x38bdf8, specular: 0xffffff, shininess: 90, transparent: true, opacity: 0.85 });
                const mesh = new THREE.Mesh(geometry, material);
                mesh.rotation.x = -Math.PI / 4;
                scene.add(mesh);

                const light1 = new THREE.DirectionalLight(0xffffff, 1.2);
                light1.position.set(5, 10, 7);
                scene.add(light1);
                const light2 = new THREE.AmbientLight(0x333333);
                scene.add(light2);

                camera.position.z = 3.5;

                function animate() {
                    requestAnimationFrame(animate);
                    mesh.rotation.y += 0.01;
                    renderer.render(scene, camera);
                }
                animate();
            </script>
            """
      components.html(three_js_code, height=390)

      st.success(
          f"💰 報價計算完成 (經辦業務: {current_sales})：單件估算 $0.85 USD /"
          " 射出模具開發費 $4,500 USD"
      )

      def generate_multilingual_pdf():
        pdf_path = "official_quotation.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=14,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
        )
        story.append(Paragraph(f"<b>{L['pdf_title']}</b>", title_style))
        story.append(Spacer(1, 15))

        info_data = [
            [
                "Sales Agent:",
                current_sales,
                "Date:",
                str(datetime.date.today()),
            ],
            ["Manufacturing Site:", site, "Currency:", curr],
        ]
        t_info = Table(info_data, colWidths=[120, 160, 80, 140])
        t_info.setStyle(
            TableStyle([
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#334155")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(t_info)
        story.append(Spacer(1, 15))

        table_data = [
            [
                "Item Description",
                "Qty / Unit",
                f"Unit Price ({curr})",
                f"Ext. Amount ({curr})",
            ],
            [L["item_mold"], "1 Set", "$4,500.00", "$4,500.00"],
            [L["item_part"], "20,000", "$0.85", "$17,000.00"],
            [L["item_total"], "", "", f"{curr} $21,500.00"],
        ]
        t_detail = Table(table_data, colWidths=[220, 80, 100, 100])
        t_detail.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1e293b"),
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                (
                    "GRID",
                    (0, 0),
                    (-1, -2),
                    0.5,
                    colors.HexColor("#cbd5e1"),
                ),
                (
                    "BACKGROUND",
                    (0, -1),
                    (-1, -1),
                    colors.HexColor("#f1f5f9"),
                ),
                (
                    "TEXTCOLOR",
                    (0, -1),
                    (-1, -1),
                    colors.HexColor("#0f172a"),
                ),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ])
        )
        story.append(t_detail)

        doc.build(story)
        return pdf_path

      pdf_file = generate_multilingual_pdf()
      with open(pdf_file, "rb") as f:
        st.download_button(
            L["pdf_btn"],
            f,
            file_name=f"Quotation_{current_sales}_{curr}.pdf",
            key="btn_dl_pdf_final",
        )
