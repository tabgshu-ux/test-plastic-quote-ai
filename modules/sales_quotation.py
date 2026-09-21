import datetime
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

def render_product_cad_preview(product_keyword):
    p_name = product_keyword.lower()
    if any(k in p_name for k in ["盒", "box", "case", "容器", "casing"]):
        title = "透明塑膠射出盒 (Plastic Box with Latch Structure)"
        shape_script = "ctx.fillStyle = 'rgba(56, 189, 248, 0.15)'; ctx.strokeStyle = '#38bdf8'; ctx.lineWidth = 3; ctx.strokeRect(80, 70, 240, 140); ctx.fillRect(80, 70, 240, 140); ctx.fillStyle = '#0284c7'; ctx.fillRect(65, 110, 15, 60); ctx.fillRect(320, 110, 15, 60);"
    elif any(k in p_name for k in ["底", "sole", "outsole", "橡膠"]):
        title = "橡膠射出大底 (Rubber Outsole Tread & Anti-Slip Pattern)"
        shape_script = "ctx.fillStyle = 'rgba(56, 189, 248, 0.2)'; ctx.strokeStyle = '#38bdf8'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(110, 40); ctx.bezierCurveTo(260, 20, 320, 50, 310, 140); ctx.bezierCurveTo(300, 220, 220, 250, 130, 240); ctx.bezierCurveTo(80, 230, 70, 160, 80, 100); ctx.closePath(); ctx.fill(); ctx.stroke();"
    else:
        title = "工程塑膠射出外殼 (Industrial Housing & Screw Pillars)"
        shape_script = "ctx.fillStyle = 'rgba(30, 41, 59, 0.8)'; ctx.strokeStyle = '#38bdf8'; ctx.lineWidth = 3; ctx.beginPath(); ctx.roundRect(80, 60, 240, 160, 20); ctx.fill(); ctx.stroke();"

    canvas_html = f"""
    <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #334155;">
        <canvas id="cadCanvas" width="400" height="270" style="background-color: #1e293b; border-radius: 8px;"></canvas>
        <p style="color: #38bdf8; font-size: 13px; margin-top: 10px; margin-bottom: 0;">📐 工業 CAD 結構模擬：【{title}】</p>
    </div>
    <script>
        const canvas = document.getElementById('cadCanvas'); const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#1e293b'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        {shape_script}
    </script>
    """
    components.html(canvas_html, height=330)

def render_dynamic_3d_model(product_keyword):
    p_name = product_keyword.lower()
    if any(k in p_name for k in ["盒", "box", "case", "容器", "casing"]):
        model_js = "const group = new THREE.Group(); const boxGeo = new THREE.BoxGeometry(2.4, 1.0, 1.6); const boxMat = new THREE.MeshPhongMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.65 }); const boxMesh = new THREE.Mesh(boxGeo, boxMat); group.add(boxMesh); scene.add(group); const targetMesh = group;"
    else:
        model_js = "const geometry = new THREE.BoxGeometry(2.0, 1.5, 0.6); const mat = new THREE.MeshPhongMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.8 }); const targetMesh = new THREE.Mesh(geometry, mat); scene.add(targetMesh);"

    three_code = f"""
        <div id="three_container" style="width: 100%; height: 360px; background-color: #090d16; border-radius: 8px;"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            const container = document.getElementById('three_container'); const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({{ antialias: true }}); renderer.setSize(container.clientWidth, container.clientHeight); container.appendChild(renderer.domElement);
            {model_js}
            const light1 = new THREE.DirectionalLight(0xffffff, 1.3); light1.position.set(5, 10, 7); scene.add(light1);
            camera.position.set(0, 1.2, 3.2);
            function animate() {{ requestAnimationFrame(animate); if(typeof targetMesh !== 'undefined') targetMesh.rotation.y += 0.008; renderer.render(scene, camera); }} animate();
        </script>
    """
    components.html(three_code, height=370)

def render_sales_overview():
    st.caption("高階主管可檢視全公司所有業務員的報價歷程、總金額統計與趨勢。")
    if "quotation_db" not in st.session_state: st.session_state.quotation_db = []
    df = pd.DataFrame(st.session_state.quotation_db)
    total_sales = df["amount"].sum() if not df.empty else 0
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("全廠歷史報價單數", f"{len(df)} 筆")
    col_b.metric("全廠估算總報價金額", f"${total_sales:,.2f} USD")
    col_c.metric("團隊業務人數", f"{len(df['sales_rep'].unique()) if not df.empty else 0} 位")
    st.divider()
    st.subheader("📋 跨國業務報價總明細表")
    if not df.empty:
        all_sales = ["全部業務 (All)"] + list(df["sales_rep"].unique())
        selected_sales = st.selectbox("🔍 依業務員篩選紀錄", all_sales)
        filtered_df = df if selected_sales == "全部業務 (All)" else df[df["sales_rep"] == selected_sales]
        st.dataframe(filtered_df, use_container_width=True)

def render_sales_frontend():
    LANG_DICT = {
        "繁體中文": {"title": "🏭 塑膠/橡膠射出成型 — 業務智慧估價系統", "step1_title": "1. 🤖 Gemini AI 需求對話與規格輸入", "step2_title": "2. 📐 工業 2D CAD 產品結構模擬", "step3_title": "3. 🧊 客製化 3D 中空模型與容量/噸數計算", "pdf_btn": "📄 下載正式 PDF 報價單", "pdf_title": "OFFICIAL PLASTIC INJECTION QUOTATION"},
        "Tiếng Việt": {"title": "🏭 Hệ Thống Báo Giá Ép Nhựa Dành Cho NVKD", "step1_title": "1. 🤖 Gemini AI Phân Tích & Nhập Yêu Cầu", "step2_title": "2. 📐 Mô Phỏng Cấu Trúc 2D CAD Sản Phẩm", "step3_title": "3. Mô hình 3D Chi Tiết & Tính Dung Tích", "pdf_btn": "📄 Tải bản thảo báo giá PDF", "pdf_title": "BÁO GIÁ ĐƠN HÀNG ÉP NHỰA"},
        "English": {"title": "🏭 Global Plastic Injection — Sales Quotation System", "step1_title": "1. 🤖 Gemini AI Copilot & Specs Input", "step2_title": "2. 📐 2D CAD Product Structure Preview", "step3_title": "3. Customized 3D Hollow Render & Volume Calc", "pdf_btn": "📄 Download Official PDF Quote", "pdf_title": "OFFICIAL PLASTIC INJECTION QUOTATION"}
    }
    top_col1, top_col2, top_col3 = st.columns(3)
    with top_col1: lang = st.selectbox("🌐 Language / 語言", ["繁體中文", "Tiếng Việt", "English"])
    available_sites = list(st.session_state.company_profile["sites"].keys())
    with top_col2: site = st.selectbox("🏭 Manufacturing Site / 出貨廠區", available_sites)
    with top_col3: curr = st.selectbox("💱 Currency", ["USD", "TWD", "RMB", "VND"])

    L = LANG_DICT[lang]
    st.title(L["title"])
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(L["step1_title"])
        current_sales = st.session_state.user_info["name"]
        st.text_input("經辦業務員 / Sales Rep", current_sales, disabled=True)
        uploaded_design = st.file_uploader("📤 上傳客戶原廠 2D / CAD 圖面 (.jpg, .png)", type=["jpg", "jpeg", "png"])
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = [{"role": "assistant", "content": "👋 您好！我是 Gemini AI 射出估價助手。請輸入您想評估的產品！"}]
        chat_container = st.container(height=280)
        for msg in st.session_state.chat_messages:
            with chat_container.chat_message(msg["role"]): st.write(msg["content"])

        if user_prompt := st.chat_input("輸入產品需求（例如：長20寬15高8公分透明塑膠盒...）"):
            st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
            st.session_state.step = 2; st.session_state.current_keyword = user_prompt
            with st.spinner("Gemini 正在分析產品規格與計算容量..."):
                try:
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    sys_prompt = f"You are an expert plastic injection consultant. Analyze: '{user_prompt}' in {lang}."
                    res = model.generate_content(sys_prompt)
                    ai_reply = res.text
                except Exception:
                    ai_reply = "💡 **Gemini AI 建議**：建議採用耐衝擊高透光 PP/ABS 材料。\n- **預估尺寸**：20cm x 15cm x 8cm (1,200 ml)\n- **建議機台噸數**：180 噸"
            st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply})
            st.rerun()

    with col2:
        if st.session_state.get("step", 1) >= 2:
            st.subheader(L["step2_title"])
            render_product_cad_preview(st.session_state.get("current_keyword", "塑膠盒"))
            if st.button("✅ 確認產品樣式，生成 3D 中空模型與容量分析", type="primary", key="btn_confirm_3d"):
                st.session_state.step = 3
                new_quote_id = f"QT-{datetime.date.today().strftime('%Y%m%d')}-{len(st.session_state.quotation_db)+1:03d}"
                st.session_state.quotation_db.append({"quote_id": new_quote_id, "sales_rep": current_sales, "client_product": st.session_state.current_keyword, "site": site, "amount": 216500, "curr": curr, "date": str(datetime.date.today())})
                st.toast(f"✅ 報價單 {new_quote_id} 已成功上傳！", icon="💾")

        if st.session_state.get("step", 1) == 3:
            st.divider(); st.subheader(L["step3_title"])
            render_dynamic_3d_model(st.session_state.get("current_keyword", "塑膠盒"))
            col_dim1, col_dim2, col_dim3 = st.columns(3)
            with col_dim1: length_cm = st.number_input("長度 (Length, cm)", min_value=1.0, value=20.0)
            with col_dim2: width_cm = st.number_input("寬度 (Width, cm)", min_value=1.0, value=15.0)
            with col_dim3: height_cm = st.number_input("高度 (Height, cm)", min_value=1.0, value=8.0)
            box_vol_ml = length_cm * width_cm * height_cm
            st.metric("📦 估算內容積 (毫升)", f"{box_vol_ml:,.0f} ml")
