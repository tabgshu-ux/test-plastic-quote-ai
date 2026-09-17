import os
import re
import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# 設定網頁標題與圖示
st.set_page_config(page_title="塑膠射出 AI 自動報價系統", page_icon="🏭", layout="wide")

# 讀取 API Key
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ 未設定 GEMINI_API_KEY，請在 Streamlit Secrets 中設定！")
    st.stop()

genai.configure(api_key=api_key)

st.title("🏭 塑膠射出成型 — AI 智慧評估與報價系統 (POC Demo)")
st.caption("輸入產品需求，AI 自動評估塑料材質、模具穴數、機台噸數並即時計算報價！")

# 畫面佈局：左邊輸入需求，右邊顯示結果
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 輸入產品需求資訊")
    product_name = st.text_input("產品名稱", "汽車防水連接器外殼")
    desc = st.text_area("產品描述與特殊需求", "長 8cm, 寬 4cm，需要耐高溫、防油，用於車載引擎室，預計每年產量 5 萬個。")
    color = st.selectbox("外觀顏色需求", ["黑色 (Black)", "白色/透明", "客製化顏色"])
    
    st.subheader("2. 廠內成本參數設定（可自訂）")
    with st.expander("點擊修改基礎成本參數"):
        abs_price = st.number_input("ABS 塑料單價 (元/kg)", value=75.0)
        pa66_price = st.number_input("PA66+GF 塑料單價 (元/kg)", value=140.0)
        machine_rate = st.number_input("150噸 射出機台每小時工費 (元)", value=600.0)

    btn_calc = st.button("🚀 開始 AI 評估與生成報價", type="primary")

if btn_calc:
    with col2:
        st.subheader("3. AI 工程分析與自動報價結果")
        with st.spinner("AI 正在分析模具結構與材料特性..."):
            
            # 建立 Prompt 讓 Gemini 做出結構化判斷
            prompt = f"""
            你是一位專業的塑膠射出成型工程師與估價專家。
            請根據以下產品需求進行評估，並嚴格按照指定的格式回答：
            產品名稱：{product_name}
            產品描述：{desc}

            請評估：
            1. 建議塑料材質（例如：ABS, PC, PA66+30%GF 等）
            2. 預估單個產品重量 (公克, g)
            3. 建議模具穴數 (Cavity, 例如：1開2 或 1開4)
            4. 建議射出機噸數 (噸, Ton)
            5. 預估成型週期 (秒)

            回答格式請務必包含：
            - 建議材質：[材質名稱]
            - 單個重量：[數字] g
            - 模具穴數：[數字]
            - 建議噸數：[數字] 噸
            - 成型週期：[數字] 秒
            - 工程分析說明：[簡短理由]
            """

            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            result_text = response.text

            st.markdown("### 🧠 AI 工程評估建議")
            st.write(result_text)

            # 報價演算法 (簡化邏輯供 Demo)
            weight_g = 30  # 預設估計值
            qty = 50000
            
            # 從 AI 文字中提取重量數字（若有）
            weight_match = re.search(r"單個重量：.*?(\d+)\s*g", result_text)
            if weight_match:
                weight_g = float(weight_match.group(1))

            material_cost_per_unit = (weight_g / 1000) * (pa66_price if "PA" in result_text else abs_price)
            processing_cost_per_unit = (machine_rate / 3600) * 25 / 2 # 假設25秒週期，1開2
            profit_margin = 1.3 # 30% 利潤
            
            unit_price = round((material_cost_per_unit + processing_cost_per_unit) * profit_margin, 2)
            mold_cost = 120000 # 假設基礎模具費

            st.divider()
            st.markdown("### 💰 自動報價試算")
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("預估產品單價", f"NT$ {unit_price} / 個")
            res_col2.metric("預估開發模具費", f"NT$ {mold_cost:,} 元")
            res_col3.metric("首批總金額 (5萬個)", f"NT$ {int(unit_price * qty + mold_cost):,} 元")

            st.divider()
            st.markdown("### 🎨 外觀示意與 3D 視覺模型")
            
            # 示意圖片 (使用免費開放繪圖網址範例)
            st.image("https://placehold.co/600x300/222/FFF?text=Plastic+Injection+3D+Render", caption="AI 產出之視覺渲染示意圖")

            # 生成 PDF 下載按鈕功能
            def generate_pdf():
                pdf_path = "quotation.pdf"
                c = canvas.Canvas(pdf_path, pagesize=letter)
                c.setFont("Helvetica-Bold", 16)
                c.drawString(100, 750, "PLASTIC INJECTION QUOTATION")
                c.setFont("Helvetica", 12)
                c.drawString(100, 720, f"Product: {product_name}")
                c.drawString(100, 700, f"Estimated Unit Price: NTD {unit_price}")
                c.drawString(100, 680, f"Mold Development Fee: NTD {mold_cost:,}")
                c.drawString(100, 650, "Generated automatically by AI System.")
                c.save()
                return pdf_path

            pdf_file = generate_pdf()
            with open(pdf_file, "rb") as f:
                st.download_button("📄 下載正式 PDF 報價單草稿", f, file_name=f"{product_name}_報價單.pdf")
