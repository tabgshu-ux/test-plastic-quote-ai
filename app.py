import streamlit as st
import os

# 1. 網頁基本設定
st.set_page_config(
    page_title="企業級 AI ERP & 智慧製造管理系統",
    page_icon="🏭",
    layout="wide"
)

# 2. 安全動態載入各模組
def load_module(module_name):
    try:
        mod = __import__(f"modules.{module_name}", fromlist=["show", "main", "render_invoice"])
        return mod
    except Exception as e:
        return None

sales_quotation = load_module("sales_quotation")
finance_tax = load_module("finance_tax")
invoice_mod = load_module("invoice")

# 3. Session State 使用者狀態初始化
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True
if "user_name" not in st.session_state:
    st.session_state.user_name = "Alex Chen (資深經理)"

# 4. 側邊欄頂部：使用者狀態與登出按鈕
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

if not st.session_state.logged_in:
    st.warning("🔒 請先於左側邊欄完成登入以使用企業 ERP 系統。")
    st.stop()

# 5. 完整公司部門組織選單 (Full ERP Departments)
st.sidebar.title("🏢 企業部門與功能模組")

dept_menu = st.sidebar.radio(
    "請選擇部門 / 功能分頁：",
    [
        "💼 業務/行銷部 (Sales & Marketing)",
        "💰 財務/會計部 — 跨國稅務 AI (Finance & Tax)",
        "🏢 董事長 / 總經理室 (Executive Management)",
        "🔬 研發與工程部 (R&D / Engineering)",
        "📦 採購與資材部 (Procurement & Logistics)",
        "🏭 生產與製造部 (Manufacturing & MES)",
        "🔍 品質保證部 (Quality Assurance - QA)",
        "📄 智慧發票與進銷項管理 (Invoice)",
        "⚙️ 系統設定與權限管理 (System Settings)"
    ]
)

st.sidebar.divider()

# 6. 導覽邏輯與模組分發
if "業務/行銷部" in dept_menu:
    sub_option = st.sidebar.selectbox("業務子功能：", ["📝 AI 即時報價 & CAD/3D Pipeline", "📜 歷史報價紀錄"])
    if sales_quotation:
        sales_quotation.show(sub_option)
    else:
        st.error("❌ 找不到 sales_quotation 模組。")

elif "財務/會計部" in dept_menu:
    sub_option = st.sidebar.selectbox("財務子功能：", ["🌐 全球稅務 AI 中文問答", "📊 跨境扣繳稅 (WHT/FCT) 試算器", "📖 各國核心稅法憑證檢核庫"])
    if finance_tax:
        finance_tax.show(sub_option)
    else:
        st.error("❌ 找不到 finance_tax 模組。")

elif "董事長" in dept_menu:
    st.title("🏢 董事長 / 總經理室 (Executive Management)")
    st.subheader("📊 企業經營 KPIs 與營運決策看板")
    st.info("💡 即時串接各部門數據：總接單金額、生產稼動率、跨國稅務合規風險與預估毛利。")
    col1, col2, col3 = st.columns(3)
    col1.metric("本月營收目標", "$1,250,000 USD", "+12.5%")
    col2.metric("工廠整體稼動率", "88.5%", "+3.2%")
    col3.metric("待處理報價單", "14 件", "-2")

elif "研發與工程部" in dept_menu:
    st.title("🔬 研發與工程部 (R&D & Engineering)")
    st.subheader("📐 3D 模具開發與產品 DFM 分析")
    st.write("• **CAD/CAM 圖資管理**：DWG, STEP, STL 檔案版本控管")
    st.write("• **模流分析 (Moldflow)**：射出壓力、保壓與冷卻時間預測")

elif "採購與資材部" in dept_menu:
    st.title("📦 採購與資材部 (Procurement & Materials)")
    st.subheader("🛒 物料需求規劃 (MRP) 與庫存控管")
    st.write("• **塑膠粒/橡膠原物料庫存**：PP, ABS, PC, SBR 庫存水位警示")
    st.write("• **供應商評鑑**：交期達成率與不良退貨率追蹤")

elif "生產與製造部" in dept_menu:
    st.title("🏭 生產與製造部 (Manufacturing & MES)")
    st.subheader("⚙️ 廠區機台排程與製造執行系統")
    st.write("• **射出機/熱壓機連線**：鎖模力噸數、模溫與週期時間監控")
    st.write("• **派工單管理**：現場工單進度即時回報")

elif "品質保證部" in dept_menu:
    st.title("🔍 品質保證部 (Quality Assurance)")
    st.subheader("🛡️ IPQC 巡檢與全檢品質報告")
    st.write("• **尺寸量測報告**：2D/3D 投影儀與三次元量測數據登錄")
    st.write("• **客訴與 CAPA 改善**：8D 改善報告流程管制")

elif "智慧發票" in dept_menu:
    sub_option = st.sidebar.selectbox("發票子功能：", ["📄 電子發票開立與辨識", "🔍 稅務抵扣憑證檢核"])
    if invoice_mod:
        if hasattr(invoice_mod, "render_invoice"):
            try:
                invoice_mod.render_invoice(sub_option)
            except TypeError:
                invoice_mod.render_invoice()
        elif hasattr(invoice_mod, "show"):
            invoice_mod.show(sub_option)
    else:
        st.info("🧾 智慧發票管理模组運作中（支援越南 Hóa đơn điện tử 與台灣電子發票）。")

elif "系統設定" in dept_menu:
    st.title("⚙️ 系統設定與權限管理")
    st.success("🟢 系統連線狀態：正常 (Connected)")
    api_key_input = st.text_input("Gemini API Key 設定：", value=os.getenv("GEMINI_API_KEY", ""), type="password")
    if st.button("💾 儲存設定"):
        os.environ["GEMINI_API_KEY"] = api_key_input
        st.success("✅ 已成功儲存 API 金鑰！")
