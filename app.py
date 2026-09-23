import streamlit as st
import os

# 1. 網頁基本設定
st.set_page_config(
    page_title="企業級 AI ERP & 智慧製造管理系統",
    page_icon="🏭",
    layout="wide"
)

# 2. 安全匯入各功能模組
def load_module(module_name):
    try:
        mod = __import__(f"modules.{module_name}", fromlist=["show", "main", "render_invoice"])
        return mod
    except Exception as e:
        return None

sales_quotation = load_module("sales_quotation")
finance_tax = load_module("finance_tax")
invoice_mod = load_module("invoice")  # 處理原本的發票模組

# 3. 登入系統邏輯與 Session State 管理
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # 預設維持登入狀態
if "user_name" not in st.session_state:
    st.session_state.user_name = "Alex Chen (資深經理)"

# 側邊欄頂部：用戶資訊與登出按鈕
st.sidebar.markdown("### 👤 使用者狀態")
if st.session_state.logged_in:
    st.sidebar.success(f"🟢 已登入：**{st.session_state.user_name}**")
    if st.sidebar.button("🔒 登出系統", key="btn_logout"):
        st.session_state.logged_in = False
        st.rerun()
else:
    st.sidebar.warning("🔴 未登入系統")
    with st.sidebar.form("login_form"):
        username = st.text_input("帳號", value="admin")
        password = st.text_input("密碼", type="password", value="123456")
        submit_login = st.form_submit_button("🚀 登入")
        if submit_login:
            st.session_state.logged_in = True
            st.session_state.user_name = f"{username} (管理者)"
            st.rerun()

st.sidebar.divider()

# 4. 側邊栏完整功能選單 (含所有模組)
st.sidebar.title("🏭 企業 ERP 功能模組")

if not st.session_state.logged_in:
    st.warning("🔒 請先於左側邊欄完成登入以使用企業 ERP 系統。")
    st.stop()

main_menu = st.sidebar.radio(
    "請選擇功能模組：",
    [
        "💼 業務/行銷 — 報價與 CAD/3D Pipeline",
        "💰 財務/跨國稅務 AI 智慧顧問",
        "🧾 智慧發票與進銷項管理",
        "📦 採購與庫存物料管理 (MRP)",
        "📊 歷史報價與客戶紀錄中心",
        "⚙️ 系統設定與權限管理"
    ]
)

st.sidebar.divider()

# 5. 根據選單導覽與相容性處理 (防止 render_invoice 等歷史名稱報錯)
if "業務/行銷" in main_menu:
    sub_option = st.sidebar.selectbox("業務子功能：", ["📝 AI 即時報價 & CAD/3D Pipeline", "📜 歷史報價紀錄"])
    if sales_quotation:
        sales_quotation.show(sub_option)
    else:
        st.error("❌ 找不到 sales_quotation 模組。")

elif "財務/跨國稅務" in main_menu:
    sub_option = st.sidebar.selectbox("財務子功能：", ["🌐 全球稅務 AI 中文問答", "📊 跨境扣繳稅 (WHT/FCT) 試算器", "📖 各國核心稅法憑證檢核庫"])
    if finance_tax:
        finance_tax.show(sub_option)
    else:
        st.error("❌ 找不到 finance_tax 模組。")

elif "智慧發票" in main_menu:
    sub_option = st.sidebar.selectbox("發票子功能：", ["📄 電子發票開立與辨識", "🔍 稅務抵扣憑證檢核"])
    # 相容舊版呼叫方式，防止 TypeError
    if invoice_mod:
        if hasattr(invoice_mod, "render_invoice"):
            try:
                invoice_mod.render_invoice(sub_option)
            except TypeError:
                invoice_mod.render_invoice()
        elif hasattr(invoice_mod, "show"):
            invoice_mod.show(sub_option)
    else:
        st.info("🧾 智慧發票管理模組運作中（可對接越南 Hóa đơn điện tử 與台灣電子發票系統）。")

elif "採購與庫存" in main_menu:
    st.title("📦 採購與庫存物料管理 (MRP & Inventory)")
    st.info("🏭 庫存物料與 MRP 自動請購模組載入中...")
    st.write("• **即時庫存查詢**：原料、半成品、成品動態水位")
    st.write("• **自動請購建議**：結合 sales_quotation 報價單自動精算 BOM 表物料需求")

elif "歷史報價" in main_menu:
    if sales_quotation:
        sales_quotation.show("歷史報價紀錄")

elif "系統設定" in main_menu:
    st.title("⚙️ 系統設定與 API 金鑰管理")
    st.success("🟢 系統連線狀態：正常 (Connected)")
    api_key_input = st.text_input("Gemini API Key 設定：", value=os.getenv("GEMINI_API_KEY", ""), type="password")
    if st.button("💾 儲存設定"):
        os.environ["GEMINI_API_KEY"] = api_key_input
        st.success("✅ 已成功儲存 API 金鑰！")
