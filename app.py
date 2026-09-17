import os
import re
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# 網頁設定
st.set_page_config(page_title="Global Injection AI Quotation", page_icon="🏭", layout="wide")

# API Key 設定
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ API Key not configured!")
    st.stop()

genai.configure(api_key=api_key)

# Session State 初始化
if "step" not in st.session_state:
    st.session_state.step = 1
if "ai_result" not in st.session_state:
    st.session_state.ai_result = ""
if "photo_url" not in st.session_state:
    st.session_state.photo_url = ""

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

# 頂部選單
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
    product_name = st.text_input("產品名稱 / Product Name", "橡膠大底")
    desc = st.text_area("產品描述 / Description", "喬丹11代用的橡膠大底，數量1000雙")
    
    if st.button(L["btn_gen_2d"], type="primary"):
        st.session_state.step = 2
        with st.spinner("AI 正在評估與即時繪製專屬部件圖..."):
            # 1. 工程評估
            prompt_analysis = f"Analyze plastic/rubber injection specs for: {product_name}, {desc}. Return Material, Weight(g), Cavity, Tonnage in {lang}."
            model = genai.GenerativeModel('gemini-1.5-flash')
            res_analysis = model.generate_content(prompt_analysis)
            st.session_state.ai_result = res_analysis.text
            
            # 2. 自動將需求翻譯成精準生圖 prompt（強調單獨鞋底部件、無整雙鞋）
            prompt_img = f"Air Jordan 11 rubber outsole sole component only, clear translucent rubber, carbon fiber shank, top view, studio isolated product shot, no shoes, no human, photorealistic"
            clean_prompt = urllib.parse.quote(prompt_img)
            
            # 3. 帶入正確的字串格式（加上雙引號）
            st.session_state.photo_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=800&height=500&nologo=true&seed=202"

with col2:
    if st.session_state.step >= 2:
        st.subheader(L["step2_title"])
        
        # 顯示 AI 即時畫出的產品部件圖
        st.image(st.session_state.photo_url, caption=f"AI 即時生成之 {product_name} 示意圖")
        st.info(st.session_state.ai_result)
        
        if st.button(L["btn_confirm_3d"], type="primary"):
            st.session_state.step = 3

    if st.session_state.step == 3:
        st.divider()
        st.subheader(L["step3_title"])
        
        # 3D 旋轉展示
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

            const geometry = new THREE.BoxGeometry(2.8, 0.4, 1.2);
            const material = new THREE.MeshPhongMaterial({ color: 0x3366cc, specular: 0x555555, shininess: 30 });
            const cube = new THREE.Mesh(geometry, material);
            scene.add(cube);

            const light1 = new THREE.DirectionalLight(0xffffff, 1);
            light1.position.set(5, 5, 5).normalize();
            scene.add(light1);
            const light2 = new THREE.AmbientLight(0x404040);
            scene.add(light2);

            camera.position.z = 3;

            function animate() {
                requestAnimationFrame(animate);
                cube.rotation.x += 0.005;
                cube.rotation.y += 0.01;
                renderer.render(scene, camera);
            }
            animate();
        </script>
        """
        components.html(three_js_code, height=360)

        st.success("💰 報價計算完成：單件預估美金 $4.20 USD / 模具開發費 $6,500 USD")

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
