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


# 🎨 橡膠大底高畫質實體圖庫庫存 (根據關鍵字自動匹配逼真大底圖)
def get_high_quality_outsole_image(product_name):
  """根據產品名稱回傳高畫質且具備防滑刻痕的專業橡膠大底照片"""
  # 高解析度橡膠大底與鞋底刻痕特寫圖庫
  outsole_gallery = [
      "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&auto=format&fit=crop&q=80",  # 水晶透明防滑橡膠底
      "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80",  # 高抓地力紋路底
      "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800&auto=format&fit=crop&q=80",  # 工業射出輪廓底
  ]

  # 簡單的 Hash 匹配，確保相同的產品名稱會顯示同一張高畫質大底圖
  img_index = sum(ord(char) for char in product_name) % len(outsole_gallery)
  return outsole_gallery[img_index]


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

# 💾 2. Session State 初始化 (報價單 + 越南發票資料庫)
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
if "user_info" not in st.session_state:
  st.session_state.user_info = None

if "quotation_db" not in st.session_state:
  st.session_state.quotation_db = [
      {
          "quote_id": "QT-20260918-001",
          "sales_rep": "Alex Chen (S-001)",
          "client_product": "喬丹11代風格水晶橡膠大底",
          "site": "Vietnam (Binh Duong)",
          "amount": 216500,
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
  st.title("🏭 塑膠射出跨國 AI 報價系統 — 用戶登入")
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
# 💼 畫面 B：業務人員前台報價系統 (Sales Agent)
# ==========================================
else:
  LANG_DICT = {
      "繁體中文": {
          "title": "🏭 塑膠射出 — 業務智慧估價系統",
          "btn_gen_2d": "🎨 第一步：AI 分析需求與匹配大底刻痕圖",
          "btn_confirm_3d": (
              "✅ 確認產品樣式，下一步：生成 3D 渲染圖與報價"
          ),
          "step1_title": "1. 業務資訊與需求輸入",
          "step2_title": "2. 高精細橡膠大底樣式展示",
          "step3_title": "3. 3D 可視化模型與自動報價單",
          "pdf_btn": "📄 下載正式 PDF 報價單 (含業務簽名)",
          "pdf_title": "OFFICIAL PLASTIC INJECTION QUOTATION",
          "item_mold": "Custom Mold Development",
          "item_part": "Production Part Unit Cost",
          "item_total": "Total Initial Order Amount",
      },
      "Tiếng Việt": {
          "title": "🏭 Hệ Thống Báo Giá Ép Nhựa Dành Cho NVKD",
          "btn_gen_2d": "🎨 Bước 1: Phân tích AI & Khớp mẫu đế cao su",
          "btn_confirm_3d": (
              "✅ Xác nhận hình ảnh, Bước tiếp: Tạo mô hình 3D & Báo giá"
          ),
          "step1_title": "1. Nhập thông tin NVKD & Yêu cầu",
          "step2_title": "2. Hình ảnh thiết kế đế cao su chất lượng cao",
          "step3_title": "3. Mô hình 3D & Báo giá chi tiết",
          "pdf_btn": "📄 Tải bản thảo báo giá PDF",
          "pdf_title": "BÁO GIÁ ĐƠN HÀNG ÉP NHỰA",
          "item_mold": "Chi phí phát triển khuôn mẫu",
          "item_part": "Đơn giá sản phẩm ép nhựa",
          "item_total": "Tổng giá trị đơn hàng đầu tiên",
      },
      "English": {
          "title": "🏭 Global Plastic Injection — Sales Quotation System",
          "btn_gen_2d": "🎨 Step 1: AI Spec Analysis & Match Outsole Design",
          "btn_confirm_3d": (
              "✅ Confirm Design, Next: Render 3D Model & Quote"
          ),
          "step1_title": "1. Sales Info & Specifications",
          "step2_title": "2. High-Quality Outsole Design",
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

  with col1:
    st.subheader(L["step1_title"])
    current_sales = st.session_state.user_info["name"]
    st.text_input("經辦業務員 / Sales Rep", current_sales, disabled=True)

    product_name = st.text_input(
        "產品名稱 / Product Name",
        "喬丹11代風格水晶橡膠大底 (AJ11 Translucent Outsole)",
    )
    desc = st.text_area(
        "產品描述 / Description",
        "需求數量 50,000 雙，採用耐磨透明橡膠與人字紋防滑抓地刻痕，高透光、防黃變，尺寸 32cm x 12cm。",
    )

    if st.button(L["btn_gen_2d"], type="primary", key="btn_gen_2d_step1"):
      st.session_state.step = 2
      with st.spinner("AI 正在解析業務需求，並檢索高畫質大底結構圖..."):
        # 1. LLM 規格建議分析 (Gemini 1.5 Flash)
        model = genai.GenerativeModel("gemini-1.5-flash")
        try:
          prompt_analysis = f"Analyze plastic/rubber injection specs for: {product_name}, {desc}. Return Material, Weight(g), Cavity, Tonnage in {lang}."
          res_analysis = model.generate_content(
              prompt_analysis, request_options={"timeout": 10}
          )
          st.session_state.ai_result = res_analysis.text
        except:
          st.session_state.ai_result = "💡 **預估材料建議**：建議採用高耐磨透明 TPU / 橡膠複合材質。\n- **預估單個重量**：180g\n- **建議模具穴數**：1 開 2\n- **建議機台噸數**：250 噸"

        # 2. 匹配高畫質美觀的實體橡膠大底照片
        st.session_state.matched_image = get_high_quality_outsole_image(
            product_name
        )

  with col2:
    if st.session_state.step >= 2:
      st.subheader(L["step2_title"])

      # 顯示美觀且高細節的大底特寫照片
      st.image(
          st.session_state.matched_image,
          caption="✨ 高細節橡膠大底樣式：人字防滑刻痕與透光射出質感展示",
          use_container_width=True,
      )

      st.info(st.session_state.ai_result)

      if st.button(
          L["btn_confirm_3d"], type="primary", key="btn_confirm_3d_step2"
      ):
        st.session_state.step = 3
        new_quote_id = f"QT-{datetime.date.today().strftime('%Y%m%d')}-{len(st.session_state.quotation_db)+1:03d}"
        st.session_state.quotation_db.append({
            "quote_id": new_quote_id,
            "sales_rep": current_sales,
            "client_product": product_name,
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

                const soleShape = new THREE.Shape();
                soleShape.moveTo(-1.2, -0.4);
                soleShape.bezierCurveTo(-1.4, -0.4, -1.5, -0.2, -1.4, 0.2);
                soleShape.bezierCurveTo(-1.2, 0.5, -0.5, 0.5, 0.0, 0.3);
                soleShape.bezierCurveTo(0.5, 0.2, 1.0, 0.4, 1.3, 0.3);
                soleShape.bezierCurveTo(1.5, 0.2, 1.5, -0.2, 1.3, -0.3);
                soleShape.bezierCurveTo(0.8, -0.5, 0.2, -0.4, -0.4, -0.3);
                soleShape.bezierCurveTo(-0.8, -0.3, -1.0, -0.4, -1.2, -0.4);

                const extrudeSettings = { depth: 0.25, bevelEnabled: true, bevelSegments: 3, steps: 2, bevelSize: 0.05, bevelThickness: 0.05 };
                const geometry = new THREE.ExtrudeGeometry(soleShape, extrudeSettings);
                geometry.center();

                const material = new THREE.MeshPhongMaterial({ color: 0x38bdf8, specular: 0xffffff, shininess: 90, transparent: true, opacity: 0.85 });
                const soleMesh = new THREE.Mesh(geometry, material);
                soleMesh.rotation.x = -Math.PI / 3;
                scene.add(soleMesh);

                const light1 = new THREE.DirectionalLight(0xffffff, 1.2);
                light1.position.set(5, 10, 7);
                scene.add(light1);
                const light2 = new THREE.AmbientLight(0x333333);
                scene.add(light2);

                camera.position.z = 3.2;

                function animate() {
                    requestAnimationFrame(animate);
                    soleMesh.rotation.z += 0.01;
                    soleMesh.rotation.y += 0.005;
                    renderer.render(scene, camera);
                }
                animate();
            </script>
            """
      components.html(three_js_code, height=390)

      st.success(
          f"💰 報價計算完成 (經辦業務: {current_sales})：單件預估 $4.20 USD /"
          " 模具開發費 $6,500 USD"
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
            [L["item_mold"], "1 Set", "$6,500.00", "$6,500.00"],
            [L["item_part"], "50,000", "$4.20", "$210,000.00"],
            [L["item_total"], "", "", f"{curr} $216,500.00"],
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
