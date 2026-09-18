import os
import datetime
import pandas as pd
import streamlit as st
import google.generativeai as genai

# ==============================
# 🌐 網頁設定
# ==============================
st.set_page_config(page_title="Global Injection AI ERP System", page_icon="🏭", layout="wide")

# ==============================
# 🔑 API Key 設定
# ==============================
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ API Key not configured!")
    st.stop()

genai.configure(api_key=api_key)

# ==============================
# 💾 Session State 初始化
# ==============================
if "quotation_db" not in st.session_state:
    st.session_state.quotation_db = [
        {"quote_id": "QT-20260918-001", "sales_rep": "Alex Chen (S-001)", "client_product": "喬丹11代風格水晶橡膠大底", "site": "Vietnam (Binh Duong)", "amount": 216500, "curr": "USD", "date": "2026-09-18"},
        {"quote_id": "QT-20260918-002", "sales_rep": "Nguyen Van A (S-005)", "client_product": "車用電子耐熱外殼", "site": "China (Dongguan)", "amount": 85000, "curr": "USD", "date": "2026-09-18"}
    ]

if "step" not in st.session_state:
    st.session_state.step = 1
if "ai_result" not in st.session_state:
    st.session_state.ai_result = ""

# ==============================
# 🎯 圖片資料庫
# ==============================
ACCURATE_GALLERY = {
    "sole": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&auto=format&fit=crop",
    "housing": "https://images.unsplash.com/photo-1527443195645-1133f7f28990?w=800&auto=format&fit=crop",
    "gear": "https://images.unsplash.com/photo-1530982011887-3cc11cc85693?w=800&auto=format&fit=crop",
    "default": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800&auto=format&fit=crop"
}

# ==============================
# 🌐 多語系字典（移到全域）
# ==============================
LANG_DICT = {
    "繁體中文": {
        "title": "🏭 塑膠射出 — 業務智慧估價系統",
        "btn_gen_2d": "🔍 第一步：AI 分析與歷史模具庫比對",
        "btn_confirm_3d": "✅ 確認產品樣式，下一步：生成 3D 渲染圖與報價",
        "step1_title": "1. 業務資訊與需求輸入",
        "step2_title": "2. 歷史大底打樣圖比對",
        "step3_title": "3. 3D 可視化模型與自動報價單",
    },
    "Tiếng Việt": {
        "title": "🏭 Hệ Thống Báo Giá Ép Nhựa Dành Cho NVKD",
        "btn_gen_2d": "🔍 Bước 1: Phân tích AI & Tìm kiếm hình ảnh",
        "btn_confirm_3d": "✅ Xác nhận hình ảnh, Bước tiếp: Tạo mô hình 3D & Báo giá",
        "step1_title": "1. Nhập thông tin NVKD & Yêu cầu",
        "step2_title": "2. Kết quả tìm kiếm từ thư viện AI",
        "step3_title": "3. Mô hình 3D & Báo giá chi tiết",
    },
    "English": {
        "title": "🏭 Global Plastic Injection — Sales Quotation System",
        "btn_gen_2d": "🔍 Step 1: AI Analysis & Database Match",
        "btn_confirm_3d": "✅ Confirm Reference, Next: Render 3D Model & Quote",
        "step1_title": "1. Sales Info & Specifications",
        "step2_title": "2. AI Database Match Result",
        "step3_title": "3. Interactive 3D Render & Final Quote",
    }
}

# ==============================
# 🧭 側邊欄：身份切換
# ==============================
st.sidebar.title("🏢 企業權限與系統切換")
user_role = st.sidebar.radio("請選擇操作模式 / Mode", ["👤 業務員前台報價 (Sales)", "🔑 後台管理員中心 (Admin Portal)"])
SALES_TEAM = ["Alex Chen (S-001)", "David Wang (S-002)", "Nguyen Van A (S-005)", "Jessica Lee (S-008)"]

# ==============================
# 情況 A：後台管理員中心
# ==============================
if user_role == "🔑 後台管理員中心 (Admin Portal)":
    st.header("📊 塑膠射出 — 後台管理與業務訂單總覽")
    df = pd.DataFrame(st.session_state.quotation_db)
    total_sales = df["amount"].sum()
    total_orders = len(df)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("總歷史報價單數", f"{total_orders} 筆")
    col_b.metric("總報價累積金額", f"${total_sales:,.2f} USD")
    col_c.metric("活躍業務員人數", f"{len(df['sales_rep'].unique())} 位")

    st.divider()
    st.subheader("📋 所有業務員報價歷史紀錄")

    selected_sales = st.selectbox("🔍 按業務員篩選紀錄", ["全部業務員 (All)"] + SALES_TEAM)
    filtered_df = df if selected_sales == "全部業務員 (All)" else df[df["sales_rep"] == selected_sales]
    st.dataframe(filtered_df, use_container_width=True)

    csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 匯出業務報價歷史報表 (CSV)", csv_data, file_name=f"Sales_Report_{datetime.date.today()}.csv")

# ==============================
# 情況 B：業務員前台報價系統
# ==============================
else:
    top_col1, top_col2, top_col3 = st.columns(3)
    with top_col1:
        lang = st.selectbox("🌐 Language / 語言", ["繁體中文", "Tiếng Việt", "English"])
    with top_col2:
        site = st.selectbox("🏭 Manufacturing Site", ["Taiwan (HQ)", "China (Dongguan)", "Vietnam (Binh Duong)"])
    with top_col3:
        curr = st.selectbox("💱 Currency", ["USD", "TWD", "RMB", "VND"])

    L = LANG_DICT[lang]
    st.title(L["title"])

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader(L["step1_title"])
        current_sales = st.selectbox("👤 經辦業務員 / Sales Representative", SALES_TEAM)
        product_name = st.text_input("產品名稱 / Product Name", "喬丹11代風格水晶橡膠大底 (AJ11 Translucent Outsole)")
        desc = st.text_area("產品描述 / Description", "需求數量 50,000 雙，採用耐磨透明橡膠與中底碳纖維板複合射出成型。要求高度透光性、防黃變，尺寸 32cm x 12cm。")

        if st.button(L["btn_gen_2d"], type="primary"):
            st.session_state.step = 2
            with st.spinner("AI 正在解析業務需求並比對廠內模具資料庫..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                try:
                    prompt_analysis = f"Analyze plastic/rubber injection specs for: {product_name}, {desc}. Return Material, Weight(g), Cavity, Tonnage in {lang}."
                    res_analysis = model.generate_content(prompt_analysis, request_options={"timeout": 10})
                    st.session_state.ai_result = res_analysis.text
                except:
                    st.session_state.ai_result = "💡 **預估材料建議**：建議採用高耐磨透明 TPU / 橡膠複合材質。\n- **預估單個重量**：180g\n- **建議模具穴數**：1
                    st.session_state.ai_result = """💡 **預估材料建議**：
                     建議採用高耐磨透明 TPU / 橡膠複合材質。
                     - **預估單個重量**：180g
                     - **建議模具穴數**：1 開 2
                     - **建議機台噸數**：250 噸"""

