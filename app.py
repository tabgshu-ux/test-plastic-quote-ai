import base64
import datetime
import email
from email.header import decode_header
import imaplib
import os
import re
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


# 🏢 0. 初始化公司與多廠區基本資訊
if "company_profile" not in st.session_state:
  st.session_state.company_profile = {
      "name": "環球塑膠射出工業股份有限公司 (Global Injection Molding Corp.)",
      "tax_id": "88889999",
      "website": "www.global-injection-demo.com",
      "sites": {
          "Taiwan (HQ)": {
              "site_name": "台灣總部與研發中心",
              "phone": "+886-2-2999-8888",
              "fax": "+886-2-2999-7777",
              "email": "hq@global-injection.com",
              "address": "新北市三重區光復路二段 88 號 10 樓",
          },
          "China (Dongguan)": {
              "site_name": "中國東莞華南製造基地",
              "phone": "+86-769-8123-4567",
              "fax": "+86-769-8123-4568",
              "email": "cn_sales@global-injection.com",
              "address": "廣東省東莞市長安鎮樟樹浦工業區 16 號",
          },
          "Vietnam (Binh Duong)": {
              "site_name": "越南平陽東安製造廠",
              "phone": "+84-274-3789-999",
              "fax": "+84-274-3789-888",
              "email": "vn_sales@global-injection.com",
              "address": "KCN Đồng An, Phường Bình Hòa, TP. Thuận An, Tỉnh Bình Dương, Việt Nam",
          },
      },
  }

# 👥 0.1 初始化越南員工人事資料庫 (靜態 HR 資料 + 額定本薪與保險)
if "employee_db" not in st.session_state:
  st.session_state.employee_db = [
      {
          "emp_id": "VN-001",
          "name": "Nguyễn Văn A",
          "cccd": "038095001234",
          "phone": "0912345678",
          "temp_address": "Số 12, Đường số 5, KDC Dĩ An, Bình Dương",
          "perm_address": "Xã Mỹ Xuyên, Huyện Mỹ Xuyên, Tỉnh Sóc Trăng",
          "hospital_name": "Bệnh viện Đa khoa Tỉnh Bình Dương",
          "hospital_address": "59 Phạm Ngọc Thạch, Hiệp Thành, TP. Thủ Dầu Một, Bình Dương",
          "join_date": "2024-03-01",
          "contract_date": "2024-03-05",
          "leave_date": "-",
          "base_salary": 9000000.0,
          "meal_allowance": 730000.0,
          "fuel_allowance": 500000.0,
          "phone_allowance": 300000.0,
      }
  ]

# 💵 0.2 每月發薪變動扣款資料庫 (Monthly Payroll Records)
if "monthly_payroll_db" not in st.session_state:
  st.session_state.monthly_payroll_db = [
      {
          "pay_month": "2026-09",
          "emp_id": "VN-001",
          "emp_name": "Nguyễn Văn A",
          "base_salary": 9000000.0,
          "allowance_total": 1530000.0,
          "insurance_deduct": 945000.0, # 10.5%
          "tardy_deduct": 150000.0,
          "leave_deduct": 300000.0,
          "advance_deduct": 1000000.0,
          "net_salary": 8135000.0,
      }
  ]


# 🎨 2D CAD 高清動態渲染
def render_product_cad_preview(product_keyword):
  p_name = product_keyword.lower()

  if any(k in p_name for k in ["盒", "box", "case", "容器", "casing"]):
    title = "透明塑膠射出盒 (Plastic Box with Latch Structure)"
    shape_script = """
            ctx.fillStyle = 'rgba(56, 189, 248, 0.15)';
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 3;
            ctx.strokeRect(80, 70, 240, 140);
            ctx.fillRect(80, 70, 240, 140);
            ctx.fillStyle = '#0284c7';
            ctx.fillRect(65, 110, 15, 60);
            ctx.fillRect(320, 110, 15, 60);
            ctx.strokeStyle = 'rgba(255,255,255,0.4)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(80, 70); ctx.lineTo(320, 210);
            ctx.moveTo(320, 70); ctx.lineTo(80, 210);
            ctx.stroke();
        """
  elif any(k in p_name for k in ["底", "sole", "outsole", "橡膠"]):
    title = "橡膠射出大底 (Rubber Outsole Tread & Anti-Slip Pattern)"
    shape_script = """
            ctx.fillStyle = 'rgba(56, 189, 248, 0.2)';
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(110, 40); ctx.bezierCurveTo(260, 20, 320, 50, 310, 140);
            ctx.bezierCurveTo(300, 220, 220, 250, 130, 240);
            ctx.bezierCurveTo(80, 230, 70, 160, 80, 100); ctx.closePath();
            ctx.fill(); ctx.stroke();
            ctx.strokeStyle = '#0284c7'; ctx.lineWidth = 2;
            for (let y = 60; y < 220; y += 18) {
                ctx.beginPath();
                for (let x = 110; x < 280; x += 30) {
                    ctx.moveTo(x, y); ctx.lineTo(x + 15, y - 8); ctx.lineTo(x + 30, y);
                }
                ctx.stroke();
            }
        """
  else:
    title = "工程塑膠射出外殼 (Industrial Housing & Screw Pillars)"
    shape_script = """
            ctx.fillStyle = 'rgba(30, 41, 59, 0.8)';
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 3;
            ctx.beginPath(); ctx.roundRect(80, 60, 240, 160, 20); ctx.fill(); ctx.stroke();
            ctx.fillStyle = '#38bdf8';
            ctx.beginPath();
            ctx.arc(110, 90, 10, 0, Math.PI*2); ctx.arc(290, 90, 10, 0, Math.PI*2);
            ctx.arc(110, 190, 10, 0, Math.PI*2); ctx.arc(290, 190, 10, 0, Math.PI*2);
            ctx.fill();
        """

  canvas_html = f"""
    <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #334155;">
        <canvas id="cadCanvas" width="400" height="270" style="background-color: #1e293b; border-radius: 8px; box-shadow: inset 0 0 10px #000;"></canvas>
        <p style="color: #38bdf8; font-size: 13px; margin-top: 10px; margin-bottom: 0;">
            📐 工業 CAD 結構模擬：【{title}】
        </p>
    </div>
    <script>
        const canvas = document.getElementById('cadCanvas');
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = '#334155'; ctx.lineWidth = 0.5;
        for(let i=0; i<canvas.width; i+=20) {{ ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,canvas.height); ctx.stroke(); }}
        for(let j=0; j<canvas.height; j+=20) {{ ctx.beginPath(); ctx.moveTo(0,j); ctx.lineTo(canvas.width,j); ctx.stroke(); }}
        
        {shape_script}
    </script>
    """
  components.html(canvas_html, height=330)


# 🧊 3D 中空盒體渲染
def render_dynamic_3d_model(product_keyword):
  p_name = product_keyword.lower()

  if any(k in p_name for k in ["盒", "box", "case", "容器", "casing"]):
    model_js = """
            const group = new THREE.Group();
            const boxGeo = new THREE.BoxGeometry(2.4, 1.0, 1.6);
            const boxMat = new THREE.MeshPhongMaterial({ color: 0x38bdf8, specular: 0xffffff, shininess: 90, transparent: true, opacity: 0.65, side: THREE.DoubleSide });
            const boxMesh = new THREE.Mesh(boxGeo, boxMat);
            group.add(boxMesh);

            const edgeGeo = new THREE.EdgesGeometry(boxGeo);
            const edgeMat = new THREE.LineBasicMaterial({ color: 0x7dd3fc, linewidth: 2 });
            const wireframe = new THREE.LineSegments(edgeGeo, edgeMat);
            group.add(wireframe);

            const lidGeo = new THREE.BoxGeometry(2.44, 0.1, 1.64);
            const lidMat = new THREE.MeshPhongMaterial({ color: 0x0284c7, transparent: true, opacity: 0.85 });
            const lidMesh = new THREE.Mesh(lidGeo, lidMat);
            lidMesh.position.set(0, 0.75, -0.6);
            lidMesh.rotation.x = -Math.PI / 4;
            group.add(lidMesh);

            scene.add(group);
            const targetMesh = group;
        """
  elif any(k in p_name for k in ["底", "sole", "outsole", "橡膠"]):
    model_js = """
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
            const mat = new THREE.MeshPhongMaterial({ color: 0x38bdf8, specular: 0xffffff, shininess: 90, transparent: true, opacity: 0.85 });
            const targetMesh = new THREE.Mesh(geometry, mat);
            targetMesh.rotation.x = -Math.PI / 3;
            scene.add(targetMesh);
        """
  else:
    model_js = """
            const geometry = new THREE.BoxGeometry(2.0, 1.5, 0.6);
            const mat = new THREE.MeshPhongMaterial({ color: 0x38bdf8, specular: 0xffffff, shininess: 80, transparent: true, opacity: 0.8 });
            const targetMesh = new THREE.Mesh(geometry, mat);
            scene.add(targetMesh);
        """

  three_code = f"""
        <div id="three_container" style="width: 100%; height: 360px; background-color: #090d16; border-radius: 8px;"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            const container = document.getElementById('three_container');
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);

            {model_js}

            const light1 = new THREE.DirectionalLight(0xffffff, 1.3);
            light1.position.set(5, 10, 7);
            scene.add(light1);
            const light2 = new THREE.AmbientLight(0x555555);
            scene.add(light2);

            camera.position.set(0, 1.2, 3.2);

            function animate() {{
                requestAnimationFrame(animate);
                if(typeof targetMesh !== 'undefined') {{
                    targetMesh.rotation.y += 0.008;
                }}
                renderer.render(scene, camera);
            }}
            animate();
        </script>
    """
  components.html(three_code, height=370)


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

# 💾 2. Session State 初始化
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
if "current_keyword" not in st.session_state:
  st.session_state.current_keyword = "塑膠盒"


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


# 📧 信箱連線與下載 XML 發票函數
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
# 🔓 3. 登入介面
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

  tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
      "📊 業務報價總覽與資料庫",
      "🏢 跨國多廠區/公司資訊設定 (Multi-Site Profile)",
      "📋 人事檔案 (Employee Profiles)",
      "💵 每月薪資發放與變動扣款 (Monthly Payroll)",
      "👥 系統使用者管理 (User Management)",
      "🧾 越南電子發票登記 (Hóa đơn điện tử)",
  ])

  # 分頁 1：業務報價總覽
  with tab1:
    st.caption("您可以檢視全公司所有業務員的報價歷程、總金額統計，並匯出報表。")
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

  # 分頁 2：多廠區/公司資訊設定
  with tab2:
    st.subheader("🏢 跨國企業多廠區與公司抬頭設定")
    st.caption("在此設定的各地廠區資訊將會自動連線套用至 PDF 報價單。")

    cp = st.session_state.company_profile

    with st.form("company_general_form"):
      st.markdown("#### 1. 公司集團基本資料")
      col_g1, col_g2 = st.columns(2)
      with col_g1:
        cp_name = st.text_input("公司總稱 (Company Name)", cp["name"])
        cp_tax_id = st.text_input("統一編號 / 稅號 (Tax ID)", cp["tax_id"])
      with col_g2:
        cp_website = st.text_input("官方網站 (Website)", cp["website"])

      if st.form_submit_button("💾 儲存集團基本資料"):
        st.session_state.company_profile["name"] = cp_name
        st.session_state.company_profile["tax_id"] = cp_tax_id
        st.session_state.company_profile["website"] = cp_website
        st.toast("✅ 公司集團基本資料已更新！", icon="💾")

    st.divider()

    st.markdown("#### 2. 個別廠區/分公司聯絡資訊")
    sites_dict = cp["sites"]
    selected_site_key = st.selectbox(
        "選擇要編輯的廠區 (Select Site)", list(sites_dict.keys())
    )
    current_sdata = sites_dict[selected_site_key]

    with st.form("edit_site_form"):
      st.caption(f"正在編輯：`{selected_site_key}` 的聯絡資訊")
      s_name = st.text_input("廠區中文名稱", current_sdata["site_name"])
      s_phone = st.text_input("電話 (Tel)", current_sdata["phone"])
      s_fax = st.text_input("傳真 (Fax)", current_sdata["fax"])
      s_email = st.text_input("公用 Email", current_sdata["email"])
      s_address = st.text_input("廠區完整地址 (Address)", current_sdata["address"])

      if st.form_submit_button("💾 更新此廠區資訊", type="primary"):
        st.session_state.company_profile["sites"][selected_site_key] = {
            "site_name": s_name,
            "phone": s_phone,
            "fax": s_fax,
            "email": s_email,
            "address": s_address,
        }
        st.success(f"✅ `{selected_site_key}` 資訊已更新！")
        st.rerun()

    with st.expander("➕ 新增其他廠區 / 分公司"):
      with st.form("add_new_site_form"):
        new_s_key = st.text_input("新廠區代號")
        new_s_name = st.text_input("廠區中文全稱")
        new_s_phone = st.text_input("電話 (Tel)")
        new_s_fax = st.text_input("傳真 (Fax)")
        new_s_email = st.text_input("Email")
        new_s_address = st.text_input("廠區完整地址")

        if st.form_submit_button("➕ 確認建立新廠區"):
          if new_s_key and new_s_address:
            st.session_state.company_profile["sites"][new_s_key] = {
                "site_name": new_s_name,
                "phone": new_s_phone,
                "fax": new_s_fax,
                "email": new_s_email,
                "address": new_s_address,
            }
            st.success(f"🎉 新廠區 `{new_s_key}` 建立成功！")
            st.rerun()
          else:
            st.error("請至少填寫廠區代號與地址！")

  # 分頁 3：靜態人事檔案 (Employee Profiles - 包含合規日期與固定薪資/保險)
  with tab3:
    st.subheader("📋 靜態人事檔案與保險底薪管理")
    st.caption("維護員工個人資料、合規日期（入職/簽約/離職）、醫療保險與每月固定保險額 (10.5%)。")

    # 新增員工表單
    with st.expander("➕ 新增員工個人檔案 (Add New Employee)", expanded=True):
      with st.form("add_static_emp_form"):
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
          emp_id = st.text_input("員工編號 (Mã NV)", f"VN-{len(st.session_state.employee_db)+1:03d}")
          emp_name = st.text_input("員工全名 (Họ và Tên)", "Trần Thị B")
          emp_cccd = st.text_input("身份證字號 (Số CCCD)", "038095009999")
          emp_phone = st.text_input("聯絡電話", "0987654321")
        with col_e2:
          emp_join_date = st.date_input("入職日期 (Ngày vào làm)", datetime.date(2024, 3, 1))
          emp_contract_date = st.date_input("合約簽署日期 (Ngày ký HĐLĐ)", datetime.date(2024, 3, 5))
          emp_leave_date_str = st.text_input("離職日期 (若仍在庫請填 -)", "-")
        with col_e3:
          emp_temp_addr = st.text_input("暫住地址 (Địa chỉ tạm trú)", "Khu phố 3, P. An Phú, Thuận An, Bình Dương")
          emp_perm_addr = st.text_input("戶籍地址 (Địa chỉ thường trú)", "Xã Tam Bình, Cai Lậy, Tiền Giang")
          emp_hosp_name = st.text_input("保險就醫醫院 (Nơi KCB)", "Bệnh viện Quốc tế Hạnh Phúc")
          emp_hosp_addr = st.text_input("醫院地址", "Đại lộ Bình Dương, Thuận An, Bình Dương")

        st.markdown("##### 💵 每月固定薪資與津貼 (Fixed Salary Structure)")
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
          base_sal = st.number_input("本薪 / 保險底薪 (VND)", min_value=0.0, value=8500000.0, step=100000.0)
        with col_s2:
          meal_allow = st.number_input("餐費補助 (Phụ cấp ăn)", min_value=0.0, value=730000.0, step=10000.0)
        with col_s3:
          fuel_allow = st.number_input("油費補助 (Phụ cấp xăng)", min_value=0.0, value=500000.0, step=50000.0)
        with col_s4:
          phone_allow = st.number_input("電話補助 (Phụ cấp ĐT)", min_value=0.0, value=300000.0, step=50000.0)

        submit_emp = st.form_submit_button("✅ 儲存員工靜態檔案", type="primary")

        if submit_emp:
          st.session_state.employee_db.append({
              "emp_id": emp_id,
              "name": emp_name,
              "cccd": emp_cccd,
              "phone": emp_phone,
              "temp_address": emp_temp_addr,
              "perm_address": emp_perm_addr,
              "hospital_name": emp_hosp_name,
              "hospital_address": emp_hosp_addr,
              "join_date": str(emp_join_date),
              "contract_date": str(emp_contract_date),
              "leave_date": emp_leave_date_str,
              "base_salary": base_sal,
              "meal_allowance": meal_allow,
              "fuel_allowance": fuel_allow,
              "phone_allowance": phone_allow,
          })
          st.success(f"🎉 員工 `{emp_name}` 檔案已成功建立！")
          st.rerun()

    st.divider()

    # 刪除員工功能
    col_del, _ = st.columns([1, 1])
    with col_del:
      if st.session_state.employee_db:
        emp_options = [f"{e['emp_id']} - {e['name']}" for e in st.session_state.employee_db]
        selected_del_emp = st.selectbox("❌ 選擇要刪除的員工", emp_options, key="select_del_static_emp")
        if st.button("🗑️ 刪除此員工檔案", type="primary", key="btn_del_static_emp"):
          target_id = selected_del_emp.split(" - ")[0]
          st.session_state.employee_db = [e for e in st.session_state.employee_db if e["emp_id"] != target_id]
          st.success(f"🗑️ 員工 `{selected_del_emp}` 已成功刪除！")
          st.rerun()

    st.divider()

    # 人事總表顯示 (含 10.5% 強制保險固定扣算)
    st.subheader("📋 越南員工靜態檔案與基本保險總表")
    if st.session_state.employee_db:
      static_list = []
      for emp in st.session_state.employee_db:
        ins_deduct = emp["base_salary"] * 0.105
        static_list.append({
            "工號": emp["emp_id"],
            "姓名": emp["name"],
            "CCCD": emp["cccd"],
            "電話": emp["phone"],
            "入職日期": emp.get("join_date", "-"),
            "合約簽署日": emp.get("contract_date", "-"),
            "離職日期": emp.get("leave_date", "-"),
            "就醫醫院": emp["hospital_name"],
            "本薪 (VND)": f"{emp['base_salary']:,.0f}",
            "津貼小計": f"{(emp['meal_allowance']+emp['fuel_allowance']+emp['phone_allowance']):,.0f}",
            "每月固定保險自付 (10.5%)": f"-{ins_deduct:,.0f}",
        })
      st.dataframe(pd.DataFrame(static_list), use_container_width=True)

  # 分頁 4：全新功能 — 💵 每月薪資發放與變動扣款 (Monthly Payroll Processing)
  with tab4:
    st.subheader("💵 每月動態薪資發放與變動扣款結算中心")
    st.caption("在此輸入**當月份實際發生**的「遲到早退罰款、請假扣款與借款/預支扣除」，系統將產出正式薪資單 PDF。")

    # 1. 登記當月變動扣款
    with st.expander("📝 輸入員工【當月變動考勤與借款扣款】", expanded=True):
      if st.session_state.employee_db:
        with st.form("monthly_payroll_form"):
          col_p1, col_p2, col_p3 = st.columns(3)
          with col_p1:
            pay_month = st.text_input("發薪月份 (Tháng lương)", datetime.date.today().strftime("%Y-%m"))
            emp_sel_payroll = st.selectbox("選擇結算員工", [f"{e['emp_id']} - {e['name']}" for e in st.session_state.employee_db])
          
          # 找出選定員工
          target_emp_id = emp_sel_payroll.split(" - ")[0]
          emp_info = next((e for e in st.session_state.employee_db if e["emp_id"] == target_emp_id), None)

          with col_p2:
            st.info(f"📌 **{emp_info['name']}** 約定本薪：`{emp_info['base_salary']:,.0f} VND`")
            ins_105 = emp_info['base_salary'] * 0.105
            st.caption(f"🛡️ 每月固定保險扣除 (10.5%): `{ins_105:,.0f} VND`")

          with col_p3:
            tardy_m = st.number_input("當月遲到/早退扣款 (Trừ đi trễ)", min_value=0.0, value=100000.0, step=10000.0)
            leave_m = st.number_input("當月請假/無薪假扣款 (Trừ nghỉ phép)", min_value=0.0, value=300000.0, step=50000.0)
            advance_m = st.number_input("當月預支借款扣除 (Trừ tạm ứng)", min_value=0.0, value=1000000.0, step=100000.0)

          submit_pay = st.form_submit_button("✅ 算算並發放此月薪資 (Calculate Payroll)", type="primary")

          if submit_pay:
            allow_tot = emp_info['meal_allowance'] + emp_info['fuel_allowance'] + emp_info['phone_allowance']
            gross_m = emp_info['base_salary'] + allow_tot
            net_m = gross_m - ins_105 - tardy_m - leave_m - advance_m

            st.session_state.monthly_payroll_db.append({
                "pay_month": pay_month,
                "emp_id": emp_info['emp_id'],
                "emp_name": emp_info['name'],
                "base_salary": emp_info['base_salary'],
                "allowance_total": allow_tot,
                "insurance_deduct": ins_105,
                "tardy_deduct": tardy_m,
                "leave_deduct": leave_m,
                "advance_deduct": advance_m,
                "net_salary": net_m,
            })
            st.success(f"🎉 `{pay_month}` 月份 `{emp_info['name']}` 薪資已成功計算！實領薪資: `{net_m:,.0f} VND`")
            st.rerun()

    st.divider()

    # 2. 顯示當月薪資結算表與生成單人 PDF 薪資單
    st.subheader("📊 每月薪資結算總明細表")
    if st.session_state.monthly_payroll_db:
      pay_df = pd.DataFrame(st.session_state.monthly_payroll_db)
      st.dataframe(pay_df, use_container_width=True)

      col_dl1, col_dl2 = st.columns([1, 1])
      with col_dl1:
        pay_csv = pay_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 匯出每月薪資發放明細總表 (CSV)",
            pay_csv,
            file_name=f"Monthly_Payroll_Summary_{datetime.date.today()}.csv",
        )

      # 生成中/越雙語電子薪資單 PDF 供員工簽名
      with col_dl2:
        with st.expander("📄 下載個人雙語正式薪資單 PDF (Payslip)", expanded=True):
          pay_records = [f"{p['pay_month']} - {p['emp_id']} {p['emp_name']}" for p in st.session_state.monthly_payroll_db]
          sel_payslip = st.selectbox("選擇薪資單紀錄", pay_records)

          def generate_payslip_pdf(pay_record):
            pdf_path = "official_payslip.pdf"
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            cp = st.session_state.company_profile
            vn_site = cp['sites'].get("Vietnam (Binh Duong)", list(cp['sites'].values())[0])

            title_style = ParagraphStyle("PTitle", parent=styles["Heading1"], fontSize=13, textColor=colors.HexColor("#0f172a"))
            story.append(Paragraph(f"<b>{cp['name']} - {vn_site['site_name']}</b>", title_style))
            story.append(Paragraph(f"<b>PHIẾU LƯƠNG HÀNG THÁNG / 每月正式薪資單 ({pay_record['pay_month']})</b>", ParagraphStyle("SubP", fontSize=11, textColor=colors.HexColor("#0284c7"))))
            story.append(Spacer(1, 10))

            info_p = [
                ["Mã NV / 工號:", pay_record['emp_id'], "Tên NV / 姓名:", pay_record['emp_name']],
                ["Tháng lương / 月份:", pay_record['pay_month'], "Ngày chi trả / 發薪日:", str(datetime.date.today())]
            ]
            t_pinfo = Table(info_p, colWidths=[120, 150, 120, 150])
            t_pinfo.setStyle(TableStyle([('FONTSIZE', (0,0), (-1,-1), 9), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
            story.append(t_pinfo)
            story.append(Spacer(1, 10))

            pay_table_data = [
                ["Hạng mục / 薪資與扣款項目", "Số tiền / 金額 (VND)"],
                ["Lương cơ bản / 本薪", f"{pay_record['base_salary']:,.0f}"],
                ["Tổng phụ cấp / 津貼總額 (餐費/油費/電話)", f"{pay_record['allowance_total']:,.0f}"],
                ["Trừ BHXH (10.5%) / 每月保險自付 (10.5%)", f"-{pay_record['insurance_deduct']:,.0f}"],
                ["Trừ đi trễ / 當月遲到早退扣款", f"-{pay_record['tardy_deduct']:,.0f}"],
                ["Trừ nghỉ phép / 當月請假扣款", f"-{pay_record['leave_deduct']:,.0f}"],
                ["Trừ tạm ứng / 當月預支借款扣除", f"-{pay_record['advance_deduct']:,.0f}"],
                ["LƯƠNG THỰC NHẬN / 當月實領薪資 (NET)", f"{pay_record['net_salary']:,.0f}"]
            ]
            t_ptable = Table(pay_table_data, colWidths=[340, 180])
            t_ptable.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor("#cbd5e1")),
                ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#f1f5f9")),
                ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor("#0284c7")),
                ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6)
            ]))
            story.append(t_ptable)
            story.append(Spacer(1, 25))

            sig_data = [["Chữ ký người lập biểu / 製表人簽名", "Chữ ký nhân viên / 員工簽名確認"]]
            t_sig = Table(sig_data, colWidths=[260, 260])
            t_sig.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTSIZE', (0,0), (-1,-1), 9)]))
            story.append(t_sig)

            doc.build(story)
            return pdf_path

          target_p_index = pay_records.index(sel_payslip)
          target_p_record = st.session_state.monthly_payroll_db[target_p_index]
          ps_pdf = generate_payslip_pdf(target_p_record)

          with open(ps_pdf, "rb") as pf:
            st.download_button(
                "📥 下載此員工雙語薪資單 PDF (Print Payslip)",
                pf,
                file_name=f"Payslip_{target_p_record['pay_month']}_{target_p_record['emp_id']}.pdf",
                key="btn_dl_payslip_pdf"
            )

  # 分頁 5：使用者管理
  with tab5:
    st.caption("管理者可以在此新增新員工帳號、重設業務員密碼或調整帳號權限。")
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

  # 分頁 6：越南發票登記
  with tab6:
    st.subheader("🇻🇳 越南電子發票自動讀取與登記中心")
    st.caption("您可以透過手動連線公司信箱、上傳 XML 檔案 或 手動輸入 進行發票登記。")

    with st.expander("📧 模式 A：設定公司專屬信箱，自動連線抓取發票", expanded=True):
      col_m1, col_m2 = st.columns(2)
      with col_m1:
        mail_server = st.text_input("IMAP 伺服器地址 (Server)", "mail.yourcompany.com")
        mail_port = st.number_input("IMAP Port (預設 SSL: 993)", value=993)
      with col_m2:
        mail_user = st.text_input("信箱帳號 (Email)", "invoice@yourcompany.com")
        mail_pwd = st.text_input("信箱密碼 (Password)", type="password")

      if st.button("🚀 開始連線信箱並讀取最新發票", type="primary", key="btn_fetch_email"):
        with st.spinner("正在安全連線至公司信箱並搜尋 XML 發票..."):
          fetched_invs = fetch_invoices_from_custom_email(mail_server, mail_port, mail_user, mail_pwd)
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
      uploaded_xml = st.file_uploader("選擇越南電子發票檔 (.xml)", type=["xml"])

      if uploaded_xml is not None:
        xml_bytes = uploaded_xml.read()
        parsed_data = parse_vietnam_xml(xml_bytes)

        if parsed_data:
          st.success("✅ XML 發票解析成功！")
          st.json(parsed_data)

          if st.button("💾 確認匯入系統資料庫", type="primary", key="btn_import_xml"):
            parsed_data["uploader"] = st.session_state.user_info["name"]
            st.session_state.invoice_db.append(parsed_data)
            st.toast("🎉 發票已成功登錄至發票總表！", icon="🧾")
            st.rerun()

    with col_preview:
      st.markdown("### 📝 模式 C：手動輸入發票")
      with st.form("manual_invoice_form"):
        inv_no = st.text_input("發票號碼 (Số hóa đơn)", "0005678")
        inv_pattern = st.text_input("發票代碼 (Mẫu số)", "1/001")
        seller_name = st.text_input("賣方公司 (Bên bán)", "CÔNG TY TNHH PLASTIC VN")
        seller_tax = st.text_input("賣方稅號 (MST)", "3701234567")
        total_amt = st.number_input("總金額 (含稅 VND)", min_value=0.0, value=2500000.0, step=1000.0)
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
# 💼 畫面 B：業務人員前台報價系統
# ==========================================
else:
  LANG_DICT = {
      "繁體中文": {
          "title": "🏭 塑膠/橡膠射出成型 — 業務智慧估價系統",
          "step1_title": "1. 🤖 Gemini AI 需求對話與規格輸入",
          "step2_title": "2. 📐 工業 2D CAD 產品結構模擬",
          "step3_title": "3. 🧊 客製化 3D 中空模型與容量/噸數計算",
          "pdf_btn": "📄 下載正式 PDF 報價單 (帶選定廠區抬頭與簽名)",
          "pdf_title": "OFFICIAL PLASTIC INJECTION QUOTATION",
          "item_mold": "Custom Mold Development",
          "item_part": "Production Part Unit Cost",
          "item_total": "Total Initial Order Amount",
      },
      "Tiếng Việt": {
          "title": "🏭 Hệ Thống Báo Giá Ép Nhựa Dành Cho NVKD",
          "step1_title": "1. 🤖 Gemini AI Phân Tích & Nhập Yêu Cầu",
          "step2_title": "2. 📐 Mô Phỏng Cấu Trúc 2D CAD Sản Phẩm",
          "step3_title": "3. Mô hình 3D Chi Tiết & Tính Dung Tích",
          "pdf_btn": "📄 Tải bản thảo báo giá PDF",
          "pdf_title": "BÁO GIÁ ĐƠN HÀNG ÉP NHỰA",
          "item_mold": "Chi phí phát triển khuôn mẫu",
          "item_part": "Đơn giá sản phẩm ép nhựa",
          "item_total": "Tổng giá trị đơn hàng đầu tiên",
      },
      "English": {
          "title": "🏭 Global Plastic Injection — Sales Quotation System",
          "step1_title": "1. 🤖 Gemini AI Copilot & Specs Input",
          "step2_title": "2. 📐 2D CAD Product Structure Preview",
          "step3_title": "3. Customized 3D Hollow Render & Volume Calc",
          "pdf_btn": "📄 Download Official PDF Quote",
          "pdf_title": "OFFICIAL PLASTIC INJECTION QUOTATION",
          "item_mold": "Custom Mold Development",
          "item_part": "Production Part Unit Cost",
          "item_total": "Total Initial Order Amount",
      },
  }

  top_col1, top_col2, top_col3 = st.columns(3)
  with top_col1:
    lang = st.selectbox("🌐 Language / 語言", ["繁體中文", "Tiếng Việt", "English"])

  available_sites = list(st.session_state.company_profile["sites"].keys())
  with top_col2:
    site = st.selectbox("🏭 Manufacturing Site / 出貨廠區", available_sites)
  with top_col3:
    curr = st.selectbox("💱 Currency", ["USD", "TWD", "RMB", "VND"])

  L = LANG_DICT[lang]
  st.title(L["title"])

  col1, col2 = st.columns([1, 1])

  with col1:
    st.subheader(L["step1_title"])
    current_sales = st.session_state.user_info["name"]
    st.text_input("經辦業務員 / Sales Rep", current_sales, disabled=True)

    uploaded_design = st.file_uploader(
        "📤 上傳客戶原廠 2D / CAD 圖面 (.jpg, .png)",
        type=["jpg", "jpeg", "png"],
    )

    st.caption("💬 與 Gemini AI 討論需求，系統將同步於右側生成圖面與估價：")
    chat_container = st.container(height=280)

    for msg in st.session_state.chat_messages:
      with chat_container.chat_message(msg["role"]):
        st.write(msg["content"])

    if user_prompt := st.chat_input("輸入產品需求（例如：長20寬15高8公分透明塑膠盒...）"):
      st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
      st.session_state.step = 2
      st.session_state.current_keyword = user_prompt

      with st.spinner("Gemini 正在分析產品規格與計算容量..."):
        model = genai.GenerativeModel("gemini-1.5-flash")
        try:
          sys_prompt = f"You are an expert plastic and rubber injection molding consultant. Analyze user request: '{user_prompt}'. Provide technical suggestions on Material, Dimensions(cm), Volume(ml), Part Weight(g), Mold Cavities, Machine Tonnage, and Estimated Unit Cost in {lang}."
          response = model.generate_content(sys_prompt, request_options={"timeout": 12})
          ai_reply = response.text
        except:
          ai_reply = "💡 **Gemini AI 建議**：根據射出需求，建議採用耐衝擊高透光 PP/ABS 材料。\n- **預估尺寸與容量**：20cm x 15cm x 8cm (1,200 ml)\n- **預估單個重量**：120g\n- **模具穴數**：1 開 2 (Cavity)\n- **建議機台噸數**：180 噸"

      st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply})

      if uploaded_design is not None:
        st.session_state.uploaded_file = uploaded_design
        st.session_state.is_uploaded = True
      else:
        st.session_state.is_uploaded = False

      st.rerun()

  with col2:
    if st.session_state.step >= 2:
      st.subheader(L["step2_title"])

      if st.session_state.get("is_uploaded", False):
        st.image(
            st.session_state.uploaded_file,
            caption="📄 業務上傳之客戶原廠 2D 圖面 / 設計圖",
            use_container_width=True,
        )
      else:
        render_product_cad_preview(st.session_state.current_keyword)

      if st.button("✅ 確認產品樣式，生成 3D 中空模型與容量分析", type="primary", key="btn_confirm_3d_step2"):
        st.session_state.step = 3
        new_quote_id = f"QT-{datetime.date.today().strftime('%Y%m%d')}-{len(st.session_state.quotation_db)+1:03d}"
        st.session_state.quotation_db.append({
            "quote_id": new_quote_id,
            "sales_rep": current_sales,
            "client_product": st.session_state.current_keyword,
            "site": site,
            "amount": 216500,
            "curr": curr,
            "date": str(datetime.date.today()),
        })
        st.toast(f"✅ 報價單 {new_quote_id} 已成功上傳後台主管系統！", icon="💾")

    if st.session_state.step == 3:
      st.divider()
      st.subheader(L["step3_title"])

      render_dynamic_3d_model(st.session_state.current_keyword)

      st.markdown("### 📐 產品尺寸與內容積 (Volume Calculator)")

      col_dim1, col_dim2, col_dim3 = st.columns(3)
      with col_dim1:
        length_cm = st.number_input("長度 (Length, cm)", min_value=1.0, value=20.0, step=1.0)
      with col_dim2:
        width_cm = st.number_input("寬度 (Width, cm)", min_value=1.0, value=15.0, step=1.0)
      with col_dim3:
        height_cm = st.number_input("高度 (Height, cm)", min_value=1.0, value=8.0, step=1.0)

      box_vol_cm3 = length_cm * width_cm * height_cm
      box_vol_ml = box_vol_cm3
      box_vol_liters = box_vol_ml / 1000.0

      proj_area = length_cm * width_cm
      est_tonnage = int(proj_area * 0.4)

      metric_col1, metric_col2, metric_col3 = st.columns(3)
      metric_col1.metric("📦 估算內容積 (毫升)", f"{box_vol_ml:,.0f} ml")
      metric_col2.metric("🥛 估算內容積 (公升)", f"{box_vol_liters:.2f} L")
      metric_col3.metric("⚙️ 建議射出機鎖模力", f"≈ {est_tonnage} 噸")

      st.success(
          f"💰 報價計算完成 (經辦業務: {current_sales})：單件估算 $0.85 USD / 射出模具開發費 $4,500 USD (出貨基地: {site})"
      )

      def generate_multilingual_pdf():
        pdf_path = "official_quotation.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        cp = st.session_state.company_profile
        selected_site_data = cp["sites"].get(site, list(cp["sites"].values())[0])

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=12,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
        )
        story.append(Paragraph(f"<b>{cp['name']} - {selected_site_data.get('site_name', site)}</b>", title_style))

        sub_style = ParagraphStyle(
            "SubStyle",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#475569"),
            fontName="Helvetica",
        )
        company_info_text = (
            f"Tax ID: {cp['tax_id']} | Tel: {selected_site_data['phone']} | Fax: {selected_site_data['fax']}<br/>"
            f"Email: {selected_site_data['email']} | Web: {cp['website']}<br/>"
            f"Address: {selected_site_data['address']}"
        )
        story.append(Paragraph(company_info_text, sub_style))
        story.append(Spacer(1, 10))

        q_title_style = ParagraphStyle(
            "QTitleStyle",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=colors.HexColor("#0284c7"),
            fontName="Helvetica-Bold",
        )
        story.append(Paragraph(f"<b>{L['pdf_title']}</b>", q_title_style))
        story.append(Spacer(1, 10))

        info_data = [
            ["Sales Agent:", current_sales, "Date:", str(datetime.date.today())],
            ["Manufacturing Site:", site, "Currency:", curr],
            ["Product Volume:", f"{box_vol_ml:,.0f} ml ({box_vol_liters:.2f}L)", "Est. Tonnage:", f"{est_tonnage} Tons"],
        ]
        t_info = Table(info_data, colWidths=[120, 160, 80, 140])
        t_info.setStyle(
            TableStyle([
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#334155")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(t_info)
        story.append(Spacer(1, 12))

        table_data = [
            ["Item Description", "Qty / Unit", f"Unit Price ({curr})", f"Ext. Amount ({curr})"],
            [L["item_mold"], "1 Set", "$4,500.00", "$4,500.00"],
            [L["item_part"], "20,000", "$0.85", "$17,000.00"],
            [L["item_total"], "", "", f"{curr} $21,500.00"],
        ]
        t_detail = Table(table_data, colWidths=[220, 80, 100, 100])
        t_detail.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -2), 0.5, colors.HexColor("#cbd5e1")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
                ("TEXTCOLOR", (0, -1), (-1, -1), colors.HexColor("#0f172a")),
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
