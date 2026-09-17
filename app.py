import os
import re
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# 設定網頁標題
st.set_page_config(page_title="Global Injection AI Quotation", page_icon="🏭", layout="wide")

# 讀取 API Key
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ API Key not configured!")
    st.stop()

genai.configure(api_key=api_key)

# Session State 初始化 (控制兩階段生成)
if "step" not in st.session_state:
    st.session_state.step = 1
if "image_url" not in st.session_state:
    st.session_state.image_url = None
if "ai_result" not in st.session_state:
    st.session_state.ai_result = ""

# 多語系字典
LANG_DICT = {
    "繁體中文": {
        "title": "🏭 塑膠射出 — 跨國智慧估價與報價系統",
        "btn_gen_2d": "🎨 第一步：AI 評估並生成 2D 示意圖",
        "btn_confirm_3d": "✅ 確認 2D 圖面，下一步：生成 3D 渲染圖與報價",
        "step1_title": "1. 產品需求輸入",
        "step2_title": "2. 2D 外觀示意圖確認",
        "step3_title": "3. 3D 可視化模型與自動報價單",
        "pdf_btn": "📄 下載正式 PDF 報價單"
    },
    "Tiếng Việt": {
        "title": "🏭 Hệ Thống Báo Giá Ép Nhựa Thông Minh AI Global",
        "btn_gen_2d": "🎨 Bước 1: Phân tích AI & Tạo ảnh 2D",
        "btn_confirm_3d": "✅ Xác nhận bản vẽ 2D, Bước tiếp: Tạo mô hình 3D & Báo giá",
        "step1_title": "1. Nhập yêu cầu sản phẩm",
        "step2_title": "2. Xác nhận hình ảnh 2D",
        "step3_title": "3. Mô hình 3D & Báo giá chi tiết",
        "pdf_btn": "📄 Tải bản thảo báo giá PDF"
    },
    "English": {
        "title": "🏭 Global Plastic Injection — AI Quotation System",
        "btn_gen_2d": "🎨 Step 1: Run AI Analysis & Generate 2D Concept",
        "btn_confirm_3d": "✅ Confirm 2D Image, Next: Render 3D Model & Quote",
        "step1_title": "1. Product Specifications",
        "step2_title": "2. 2D Visual Concept Confirmation",
        "step3_title": "3. Interactive 3D Render & Final Quote",
        "pdf_btn": "📄 Download Official PDF Quote"
    }
}

# 頂部控制列
top_col1, top_col2, top_col3 = st.columns(3)
with top_col1:
    lang = st.selectbox("🌐 Language / 語言", ["繁體中文", "Tiếng Việt", "English"])
with top_col2:
    site = st.selectbox("🏭 Manufacturing Site", ["Taiwan (HQ)", "China (Dongguan)", "Vietnam (Binh Duong)"])
with top_col3:
    curr = st.selectbox("💱 Currency", ["USD", "TWD", "RMB", "VND"])

L = LANG_DICT[lang]
st.title(L["title"])

# 左欄位：輸入資料，右欄位：生成進度展示
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(L["step1_title"])
    product_name = st.text_input("產品名稱 / Product Name", "Plastic Enclosure Connector")
    desc = st.text_area("產品描述 / Description", "Black plastic automotive housing, waterproof, high heat resistance, 8cm x 4cm.")
    
    if st.button(L["btn_gen_2d"], type="primary"):
        st.session_state.step = 2
        with st.spinner("AI Generating 2D Image & Technical Specs..."):
            # 1. 呼叫 Gemini 產出分析與繪圖 Prompt
            prompt = f"Analyze plastic injection specs for: {product_name}, {desc}. Return Material, Weight(g), Cavity, Tonnage, and a 1-sentence English prompt for image generation."
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(prompt)
            st.session_state.ai_result = res.text
            
            # 2. 使用免費 Pollinations API 自動產生 2D 工業設計示意圖
            clean_prompt = urllib.parse.quote(f"3d industrial render of plastic injection molded {product_name}, studio lighting, clean background, photorealistic")
            st.session_state.image_url = f"https://pollinations.ai/p/{clean_prompt}?width=800&height=500&seed=42"

with col2:
    # 階段 2：顯示 2D 圖面供客戶確認
    if st.session_state.step >= 2:
        st.subheader(L["step2_title"])
        st.image(st.session_state.image_url, caption="AI 產出之 2D 概念設計示意圖", use_container_width=True)
        st.info(st.session_state.ai_result)
        
        if st.button(L["btn_confirm_3d"], type="primary"):
            st.session_state.step = 3

    # 階段 3：客戶確認後，生成 3D 渲染圖與報價結果
    if st.session_state.step == 3:
        st.divider()
        st.subheader(L["step3_title"])
        
        # 內嵌 HTML/Three.js 提供 360 度可旋轉的 3D 模型展示
        three_js_code = """
        <div id="container" style="width: 100%; height: 350px; background-color: #1a1a1a; border-radius: 8px;"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            const container = document.getElementById('container');
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);

            // 建立塑膠外殼 3D 幾何模型範例
            const geometry = new THREE.BoxGeometry(2.5, 1.2, 0.8);
            const material = new THREE.MeshPhongMaterial({ color: 0x222222, specular: 0x555555, shininess: 30 });
            const cube = new THREE.Mesh(geometry, material);
            scene.add(cube);

            // 光源設定
            const light1 = new THREE.DirectionalLight(0xffffff, 1);
            light1.position.set(5, 5, 5).normalize();
            scene.add(light1);
            const light2 = new THREE.AmbientLight(0x404040);
            scene.add(light2);

            camera.position.z = 3;

            // 動態旋轉渲染
            function animate() {
                requestAnimationFrame(animate);
                cube.rotation.x += 0.008;
                cube.rotation.y += 0.01;
                renderer.render(scene, camera);
            }
            animate();
        </script>
        """
        components.html(three_js_code, height=360)

        # 報價數字
        st.success("💰 報價計算完成：單件預估美金 $0.85 USD / 模具開發費 $3,800 USD")

        # PDF 下載功能
        def generate_pdf():
            pdf_path = "quotation_3d.pdf"
            c = canvas.Canvas(pdf_path, pagesize=letter)
            c.drawString(100, 750, f"OFFICIAL INJECTION QUOTATION: {product_name}")
            c.drawString(100, 720, f"Factory Site: {site}")
            c.drawString(100, 700, "3D Model & Concept Approved by Client.")
            c.save()
            return pdf_path

        pdf_file = generate_pdf()
        with open(pdf_file, "rb") as f:
            st.download_button(L["pdf_btn"], f, file_name=f"{product_name}_Quote.pdf")
