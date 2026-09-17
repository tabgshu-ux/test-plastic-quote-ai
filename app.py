import os
import re
import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# 設定網頁標題與圖示
st.set_page_config(page_title="Global Injection Molding AI Quotation", page_icon="🌍", layout="wide")

# 讀取 API Key
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ API Key not configured!")
    st.stop()

genai.configure(api_key=api_key)

# 🌐 多語系字典設定
LANG_DICT = {
    "繁體中文": {
        "title": "🏭 塑膠射出 — 跨國智慧估價與報價系統",
        "subtitle": "支援多國語言、多廠區計價與多幣別自動換算",
        "site_label": "選擇生產廠區",
        "curr_label": "報價幣別",
        "input_sec": "1. 輸入產品需求資訊",
        "p_name": "產品名稱",
        "p_desc": "產品描述與特殊需求",
        "p_color": "外觀顏色",
        "cost_sec": "2. 廠內成本參數（可修正）",
        "btn_calc": "🚀 開始 AI 跨國估價與生成報價",
        "ai_sec": "🧠 AI 工程評估與材料建議",
        "quote_sec": "💰 跨國報價結果",
        "unit_price": "預估產品單價",
        "mold_price": "預估模具開發費",
        "total_price": "首批總金額 (5萬個)",
        "pdf_btn": "📄 下載正式 PDF 報價單草稿"
    },
    "簡體中文": {
        "title": "🏭 塑胶射出 — 跨国智慧估价与报价系统",
        "subtitle": "支持多国语言、多厂区计价与多币别自动换算",
        "site_label": "选择生产厂区",
        "curr_label": "报价币种",
        "input_sec": "1. 输入产品需求信息",
        "p_name": "产品名称",
        "p_desc": "产品描述与特殊需求",
        "p_color": "外观颜色",
        "cost_sec": "2. 厂内成本参数（可修正）",
        "btn_calc": "🚀 开始 AI 跨国估价与生成报价",
        "ai_sec": "🧠 AI 工程评估与材料建议",
        "quote_sec": "💰 跨国报价结果",
        "unit_price": "预估产品单价",
        "mold_price": "预估模具开发费",
        "total_price": "首批总金额 (5万个)",
        "pdf_btn": "📄 下载正式 PDF 报价单草稿"
    },
    "English": {
        "title": "🏭 Global Plastic Injection — AI Quotation System",
        "subtitle": "Multi-language, Multi-site Costing, Multi-currency Auto Conversion",
        "site_label": "Manufacturing Site",
        "curr_label": "Quotation Currency",
        "input_sec": "1. Product Requirements",
        "p_name": "Product Name",
        "p_desc": "Description & Specifications",
        "p_color": "Color Requirements",
        "cost_sec": "2. Cost Parameters",
        "btn_calc": "🚀 Run AI Evaluation & Quotation",
        "ai_sec": "🧠 AI Technical Analysis & Material Suggestion",
        "quote_sec": "💰 Quotation Summary",
        "unit_price": "Est. Unit Price",
        "mold_price": "Est. Mold Cost",
        "total_price": "Total Initial Order (50k pcs)",
        "pdf_btn": "📄 Download Draft PDF Quote"
    },
    "Tiếng Việt": {
        "title": "🏭 Hệ Thống Báo Giá Ép Nhựa Thông Minh AI Global",
        "subtitle": "Hỗ trợ đa ngôn ngữ, tính chi phí đa nhà máy & tự động quy đổi tiền tệ",
        "site_label": "Chọn nhà máy sản xuất",
        "curr_label": "Loại tiền tệ báo giá",
        "input_sec": "1. Nhập yêu cầu sản phẩm",
        "p_name": "Tên sản phẩm",
        "p_desc": "Mô tả sản phẩm & Yêu cầu đặc biệt",
        "p_color": "Yêu cầu màu sắc",
        "cost_sec": "2. Thông số chi phí nhà máy",
        "btn_calc": "🚀 Chạy phân tích AI & Báo giá",
        "ai_sec": "🧠 AI Phân tích kỹ thuật & Đề xuất vật liệu",
        "quote_sec": "💰 Tóm tắt báo giá",
        "unit_price": "Đơn giá dự kiến",
        "mold_price": "Chi phí khuôn dự kiến",
        "total_price": "Tổng đơn hàng đầu (50k cái)",
        "pdf_btn": "📄 Tải bản thảo báo giá PDF"
    }
}

# 💱 匯率與廠區預設數據 (基準點以 TWD 為主)
EXCHANGE_RATES = {"TWD": 1.0, "USD": 0.031, "RMB": 0.22, "VND": 780.0}
SITE_COST_MULTIPLIER = {"Taiwan (HQ)": 1.0, "China (Dongguan/Kunshan)": 0.85, "Vietnam (Binh Duong)": 0.75}

# 頂部選單：語言、廠區、幣別切換
top_col1, top_col2, top_col3 = st.columns(3)
with top_col1:
    lang = st.selectbox("🌐 Language / 語言", ["繁體中文", "簡體中文", "English", "Tiếng Việt"])
with top_col2:
    site = st.selectbox(LANG_DICT[lang]["site_label"], ["Taiwan (HQ)", "China (Dongguan/Kunshan)", "Vietnam (Binh Duong)"])
with top_col3:
    curr = st.selectbox(LANG_DICT[lang]["curr_label"], ["USD", "TWD", "RMB", "VND"])

L = LANG_DICT[lang]

st.title(L["title"])
st.caption(L["subtitle"])

# 畫面佈局
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(L["input_sec"])
    product_name = st.text_input(L["p_name"], "Auto Housing Connector")
    desc = st.text_area(L["p_desc"], "8cm x 4cm, High heat resistance, oil proof, for automotive engine room, 50,000 pcs/year.")
    color = st.selectbox(L["p_color"], ["Black", "White/Transparent", "Custom Color"])
    
    st.subheader(L["cost_sec"])
    with st.expander("Modify Base Costs"):
        pa66_price = st.number_input("PA66+GF Price (TWD/kg)", value=140.0)
        machine_rate = st.number_input("150T Machine Rate (TWD/hr)", value=600.0)

    btn_calc = st.button(L["btn_calc"], type="primary")

if btn_calc:
    with col2:
        st.subheader(L["ai_sec"])
        with st.spinner("AI processing for global factory specifications..."):
            
            prompt = f"""
            You are an expert plastic injection mold engineer.
            Please analyze the following product requirements and respond in {lang}:
            Product Name: {product_name}
            Description: {desc}

            Format your response clearly:
            - Recommended Material: [Material]
            - Estimated Weight: [Number] g
            - Recommended Cavity: [Number]
            - Machine Tonnage: [Number] Ton
            - Cycle Time: [Number] Seconds
            - Engineering Analysis: [Brief explanation]
            """

            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            result_text = response.text

            st.write(result_text)

            # 基礎報價計算 (台幣)
            weight_g = 30.0
            weight_match = re.search(r"(\d+)\s*g", result_text)
            if weight_match:
                weight_g = float(weight_match.group(1))

            # 套用廠區成本係數
            site_mult = SITE_COST_MULTIPLIER[site]
            mat_cost_twd = (weight_g / 1000) * pa66_price
            proc_cost_twd = (machine_rate / 3600) * 25 / 2 * site_mult
            unit_price_twd = (mat_cost_twd + proc_cost_twd) * 1.3
            mold_cost_twd = 120000 * site_mult

            # 轉化為目標幣別
            rate = EXCHANGE_RATES[curr]
            unit_price = round(unit_price_twd * rate, 3 if curr in ["USD", "RMB"] else 0)
            mold_cost = round(mold_cost_twd * rate, 0)
            total_first_order = round((unit_price * 50000) + mold_cost, 0)

            st.divider()
            st.markdown(f"### {L['quote_sec']} ({curr} - {site})")
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric(L["unit_price"], f"{curr} {unit_price:,}")
            res_col2.metric(L["mold_price"], f"{curr} {mold_cost:,}")
            res_col3.metric(L["total_price"], f"{curr} {total_first_order:,}")

            # 生成 PDF
            def generate_pdf():
                pdf_path = "quotation.pdf"
                c = canvas.Canvas(pdf_path, pagesize=letter)
                c.setFont("Helvetica-Bold", 16)
                c.drawString(100, 750, "GLOBAL INJECTION QUOTATION")
                c.setFont("Helvetica", 12)
                c.drawString(100, 720, f"Factory Site: {site}")
                c.drawString(100, 700, f"Product: {product_name}")
                c.drawString(100, 680, f"Unit Price: {curr} {unit_price:,}")
                c.drawString(100, 660, f"Mold Development: {curr} {mold_cost:,}")
                c.save()
                return pdf_path

            pdf_file = generate_pdf()
            with open(pdf_file, "rb") as f:
                st.download_button(L["pdf_btn"], f, file_name=f"{product_name}_Quote_{curr}.pdf")
