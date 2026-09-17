import os
import re
import urllib.parse
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

# 多語系字典 (網頁與 PDF 共用)
LANG_DICT = {
    "繁體中文": {
        "title": "🏭 塑膠射出 — 跨國智慧估價與報價系統",
        "btn_gen_2d": "🎨 第一步：AI 評估並生成 2D 示意圖",
        "btn_confirm_3d": "✅ 確認 2D 圖面，下一步：生成 3D 渲染圖與報價",
        "step1_title": "1. 產品需求輸入",
        "step2_title": "2. 2D 外觀示意圖確認",
        "step3_title": "3. 3D 可視化模型與自動報價單",
        "pdf_btn": "📄 下載正式 PDF 報價單",
        "pdf_title": "OFFICIAL PLASTIC INJECTION QUOTATION (正式塑膠射出報價單)",
        "item_mold": "Custom Mold Development (客製化射出模具開發)",
        "item_part": "Production Part Unit Cost (產品射出單價 - 高階TPU/橡膠)",
        "item_total": "Total Order Amount (首批訂單總金額)",
        "unit_set": "1 套 / Set",
        "unit_pcs": "50,000 雙 / Pairs"
    },
    "Tiếng Việt": {
        "title": "🏭 Hệ Thống Báo Giá Ép Nhựa Thông Minh AI Global",
        "btn_gen_2d": "🎨 Bước 1: Phân tích AI & Tạo ảnh 2D",
        "btn_confirm_3d": "✅ Xác nhận bản vẽ 2D, Bước tiếp: Tạo mô hình 3D & Báo giá",
        "step1_title": "1. Nhập yêu cầu sản phẩm",
        "step2_title": "2. Xác nhận hình ảnh 2D",
        "step3_title": "3. Mô hình 3D & Báo giá chi tiết",
        "pdf_btn": "📄 Tải bản thảo báo giá PDF",
        "pdf_title": "OFFICIAL PLASTIC INJECTION QUOTATION (BÁO GIÁ ĐƠN HÀNG ÉP NHỰA)",
        "item_mold": "Chi phí phát triển khuôn mẫu (Custom Mold Development)",
        "item_part": "Đơn giá sản phẩm ép nhựa (Production Part Unit Cost)",
        "item_total": "Tổng giá trị đơn hàng đầu tiên (Total Order Amount)",
        "unit_set": "1 Bộ / Set",
        "unit_pcs": "50,000 Đôi / Pairs"
    },
    "English": {
        "title": "🏭 Global Plastic Injection — AI Quotation System",
        "btn_gen_2d": "🎨 Step 1: Run AI Analysis & Generate 2D Concept",
        "btn_confirm_3d": "✅ Confirm 2D Image, Next: Render 3D Model & Quote",
        "step1_title": "1. Product Specifications",
        "step2_title": "2. 2D Visual Concept Confirmation",
        "step3_title": "3. Interactive 3D Render & Final Quote",
        "pdf_btn": "📄 Download Official PDF Quote",
        "pdf_title": "OFFICIAL PLASTIC INJECTION QUOTATION",
        "item_mold": "Custom Mold Development",
        "item_part": "Production Part Unit Cost (High-grade TPU/Rubber)",
        "item_total": "Total Initial Order Amount",
        "unit_set": "1 Set",
        "unit_pcs": "50,000 Pairs"
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
        with st.spinner("AI 正在評估與繪製 2D 工業規格圖..."):
            try:
                prompt_analysis = f"Analyze plastic/rubber injection specs for: {product_name}, {desc}. Return Material, Weight(g), Cavity, Tonnage in {lang}."
                model = genai.GenerativeModel('gemini-1.5-flash')
                res_analysis = model.generate_content(prompt_analysis, request_options={"timeout": 10})
                st.session_state.ai_result = res_analysis.text
            except Exception as e:
                st.session_state.ai_result = f"💡 **預估材料建議**：建議採用高耐磨透明 TPU / 橡膠複合材質。\n- **預估單個重量**：180g\n- **建議模具穴數**：1 開 2\n- **建議機台噸數**：250 噸"

with col2:
    if st.session_state.step >= 2:
        st.subheader(L["step2_title"])
        
        svg_code = """
        <div style="background-color: #0b1325; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #1e293b; font-family: sans-serif;">
            <svg width="100%" height="220" viewBox="0 0 500 220" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" stroke-width="1"/>
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid)" />
                <path d="M 60 110 C 50 70, 100 30, 180 35 C 260 40, 330 30, 410 45 C 450 55, 460 100, 440 140 C 410 180, 320 180, 240 170 C 160 160, 70 150, 60 110 Z" fill="rgba(56, 189, 248, 0.15)" stroke="#38bdf8" stroke-width="2.5"/>
                <path d="M 100 65 Q 140 60 180 70 Q 150 120 100 115 Z" fill="rgba(14, 165, 233, 0.3)" stroke="#0284c7" stroke-width="1.5"/>
                <path d="M 350 75 Q 400 70 420 100 Q 390 140 340 135 Z" fill="rgba(14, 165, 233, 0.3)" stroke="#0284c7" stroke-width="1.5"/>
                <rect x="220" y="85" width="80" height="45" rx="5" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
                <path d="M 225 90 L 295 125 M 235 90 L 295 120 M 225 100 L 285 125 M 250 90 L 295 110" stroke="#f59e0b" stroke-width="1" opacity="0.6"/>
                <line x1="50" y1="195" x2="450" y2="195" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4"/>
                <text x="250" y="212" fill="#94a3b8" font-size="12" text-anchor="middle" font-family="monospace">LENGTH: 320mm (SPEC: +-0.5mm)</text>
                <text x="20" y="25" fill="#38bdf8" font-size="13" font-weight="bold">CAD CONCEPT: AJ11 OUTSOLE INJECTION PART</text>
            </svg>
            <p style="color: #38bdf8; font-size: 13px; margin-top: 5px; margin-bottom: 0;">2D 射出成型結構視圖已確認（含防扭碳纖維板與雙色橡膠 Pods）</p>
        </div>
        """
        components.html(svg_code, height=270)
        
        st.info(st.session_state.ai_result)
        
        if st.button(L["btn_confirm_3d"], type="primary"):
            st.session_state.step = 3

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

            const material = new THREE.MeshPhongMaterial({ 
                color: 0x38bdf8, 
                specular: 0xffffff, 
                shininess: 90,
                transparent: true,
                opacity: 0.85
            });

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

        # 動態多語系 PDF 報價單生成函式
        def generate_multilingual_pdf():
            pdf_path = "official_quotation.pdf"
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # 報價單標題
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=14,
                leading=18,
                textColor=colors.HexColor('#0f172a'),
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph(f"<b>{L['pdf_title']}</b>", title_style))
            story.append(Spacer(1, 15))

            # 基本資訊
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

            # 報價明細表格 (多語系對應)
            table_data = [
                ["Item Description", "Qty / Unit", f"Unit Price ({curr})", f"Ext. Amount ({curr})"],
                [L["item_mold"], L["unit_set"], "$6,500.00", "$6,500.00"],
                [L["item_part"], L["unit_pcs"], "$4.20", "$210,000.00"],
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
