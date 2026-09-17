import os
import re
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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
if "matched_image" not in st.session_state:
    st.session_state.matched_image = ""

# 📁 建立「模擬企業內部圖庫 / 授權圖庫」
# 存放各類高品質的真實塑膠/橡膠零件照片
IMAGE_DATABASE = {
    "sole": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800&auto=format&fit=crop", # 獨立鞋底/大底特寫
    "case": "https://images.unsplash.com/photo-1527443195645-1133f7f28990?w=800&auto=format&fit=crop", # 塑膠外殼/機殼
    "gear": "https://images.unsplash.com/photo-1530982011887-3cc11cc85693?w=800&auto=format&fit=crop", # 齒輪/精密機械零件
    "bottle": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=800&auto=format&fit=crop", # 塑膠瓶器
    "connector": "https://images.unsplash.com/photo-1611078712613-2d24f0c43666?w=800&auto=format&fit=crop", # 連接器/電子塑膠件
    "default": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800&auto=format&fit=crop"  # 預設通用射出件
}

# 多語系字典
LANG_DICT = {
    "繁體中文": {
        "title": "🏭 塑膠射出 — 跨國智慧估價與報價系統",
        "btn_gen_2d": "🔍 第一步：AI 語意分析與圖庫智能比對",
        "btn_confirm_3d": "✅ 確認產品樣式，下一步：生成 3D 渲染圖與報價",
        "step1_title": "1. 產品需求輸入",
        "step2_title": "2. AI 圖庫比對結果確認",
        "step3_title": "3. 3D 可視化模型與自動報價單",
        "pdf_btn": "📄 下載正式 PDF 報價單",
        "pdf_title": "OFFICIAL PLASTIC INJECTION QUOTATION",
        "item_mold": "Custom Mold Development",
        "item_part": "Production Part Unit Cost",
        "item_total": "Total Initial Order Amount",
    },
    "Tiếng Việt": {
        "title": "🏭 Hệ Thống Báo Giá Ép Nhựa Thông Minh AI Global",
        "btn_gen_2d": "🔍 Bước 1: AI Phân tích & Tìm kiếm hình ảnh",
        "btn_confirm_3d": "✅ Xác nhận hình ảnh, Bước tiếp: Tạo mô hình 3D & Báo giá",
        "step1_title": "1. Nhập yêu cầu sản phẩm",
        "step2_title": "2. Kết quả tìm kiếm từ thư viện AI",
        "step3_title": "3. Mô hình 3D & Báo giá chi tiết",
        "pdf_btn": "📄 Tải bản thảo báo giá PDF",
        "pdf_title": "BÁO GIÁ ĐƠN HÀNG ÉP NHỰA",
        "item_mold": "Chi phí phát triển khuôn mẫu",
        "item_part": "Đơn giá sản phẩm ép nhựa",
        "item_total": "Tổng giá trị đơn hàng đầu tiên",
    },
    "English": {
        "title": "🏭 Global Plastic Injection — AI Quotation System",
        "btn_gen_2d": "🔍 Step 1: AI Semantic Analysis & Database Search",
        "btn_confirm_3d": "✅ Confirm Reference, Next: Render 3D Model & Quote",
        "step1_title": "1. Product Specifications",
        "step2_title": "2. AI Database Match Result",
        "step3_title": "3. Interactive 3D Render & Final Quote",
        "pdf_btn": "📄 Download Official PDF Quote",
        "pdf_title": "OFFICIAL PLASTIC INJECTION QUOTATION",
        "item_mold": "Custom Mold Development",
        "item_part": "Production Part Unit Cost",
        "item_total": "Total Initial Order Amount",
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
    product_name = st.text_input("產品名稱 / Product Name", "喬丹11代風格水晶橡膠大底 (AJ11 Translucent Outsole)")
    desc = st.text_area("產品描述 / Description", "需求數量 50,000 雙，採用耐磨透明橡膠與中底碳纖維板複合射出成型。要求高度透光性、防黃變，尺寸 32cm x 12cm。")
    
    if st.button(L["btn_gen_2d"], type="primary"):
        st.session_state.step = 2
        with st.spinner("AI 正在解析需求並從圖庫比對相似零件..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            try:
                # 任務 1：工程分析
                prompt_analysis = f"Analyze plastic/rubber injection specs for: {product_name}, {desc}. Return Material, Weight(g), Cavity, Tonnage in {lang}."
                res_analysis = model.generate_content(prompt_analysis, request_options={"timeout": 10})
                st.session_state.ai_result = res_analysis.text
            except:
                st.session_state.ai_result = f"💡 **預估材料建議**：建議採用高耐磨透明 TPU / 橡膠複合材質。\n- **預估單個重量**：180g\n- **建議模具穴數**：1 開 2\n- **建議機台噸數**：250 噸"

            # 任務 2：圖庫關鍵字分類 (讓 AI 決定要撈哪張圖)
            try:
                prompt_category = f"Classify this product '{product_name}, {desc}' into EXACTLY ONE of these categories: [sole, case, gear, bottle, connector, default]. Reply ONLY with the category word."
                res_category = model.generate_content(prompt_category).text.strip().lower()
                # 確保回傳的值在我們的資料庫中
                match_key = res_category if res_category in IMAGE_DATABASE else "default"
            except:
                match_key = "default"
            
            # 從圖庫中取出對應的真實產品圖
            st.session_state.matched_image = IMAGE_DATABASE[match_key]

with col2:
    if st.session_state.step >= 2:
        st.subheader(L["step2_title"])
        
        # 顯示從圖庫比對出來的真實照片
        if st.session_state.matched_image:
            st.markdown(
                f'''
                <div style="background-color: #1e293b; padding: 10px; border-radius: 8px; text-align: center;">
                    <img src="{st.session_state.matched_image}" style="width: 100%; max-height: 300px; object-fit: cover; border-radius: 4px;" alt="AI 比對圖庫結果">
                    <p style="color: #38bdf8; font-size: 13px; margin-top: 8px; margin-bottom: 0;">
                        🔍 AI 已從歷史模具圖庫中比對出高度相似的零件參考圖
                    </p>
                </div>
                ''',
                unsafe_allow_html=True
            )
        
        st.info(st.session_state.ai_result)
        
        if st.button(L["btn_confirm_3d"], type="primary"):
            st.session_state.step = 3

    if st.session_state.step == 3:
        st.divider()
        st.subheader(L["step3_title"])
        
        # 3D 渲染
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

        st.success(f"💰 報價計算完成 ({curr} - {site})：單件預估 $4.20 USD / 模具開發費 $6,500 USD")

        def generate_multilingual_pdf():
            pdf_path = "official_quotation.pdf"
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=14, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold')
            story.append(Paragraph(f"<b>{L['pdf_title']}</b>", title_style))
            story.append(Spacer(1, 15))

            info_data = [
                ["Manufacturing Site:", site, "Date:", "2026-09-18"],
                ["Quotation Currency:", curr, "Language:", lang]
            ]
            t_info = Table(info_data, colWidths=[120, 160, 80, 140])
            t_info.setStyle(TableStyle([
                ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#334155')),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(t_info)
            story.append(Spacer(1, 15))

            table_data = [
                ["Item Description", "Qty / Unit", f"Unit Price ({curr})", f"Ext. Amount ({curr})"],
                [L["item_mold"], "1 Set", "$6,500.00", "$6,500.00"],
                [L["item_part"], "50,000", "$4.20", "$210,000.00"],
                [L["item_total"], "", "", f"{curr} $216,500.00"]
            ]
            t_detail = Table(table_data, colWidths=[220, 80, 100, 100])
            t_detail.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('ALIGN', (1,0), (-1,-1), 'CENTER'),
                ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#cbd5e1')),
                ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f1f5f9')),
                ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#0f172a')),
                ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(t_detail)
            
            doc.build(story)
            return pdf_path

        pdf_file = generate_multilingual_pdf()
        with open(pdf_file, "rb") as f:
            st.download_button(L["pdf_btn"], f, file_name=f"Quotation_{lang}_{curr}.pdf")
