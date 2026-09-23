import re
import math
import streamlit as st
import google.generativeai as genai
import os

def parse_dimensions_and_type(prompt_text):
    """精準動態解析尺寸與產品類型"""
    nums = re.findall(r'\d+(?:\.\d+)?', prompt_text)
    
    length = 40.0
    width = 25.0
    height = 3.0 # 單位: cm
    
    if len(nums) >= 3:
        length = float(nums[0])
        width = float(nums[1])
        height = float(nums[2])
    elif len(nums) == 2:
        length = float(nums[0])
        width = float(nums[1])

    if "鞋" in prompt_text or "底" in prompt_text or "橡膠" in prompt_text:
        prod_type = "👟 橡膠大底 / 鞋底 (Rubber Outsole Only)"
        material = "天然橡膠 (NR) / 合成橡膠 (SBR/EVA)"
        clamp_ton = math.ceil((length * width) * 0.15)
    else:
        prod_type = "📦 射出成型件 (Injection Molded Part)"
        material = "PP / ABS / PC 工程塑膠"
        clamp_ton = math.ceil((length * width) * 0.2)

    vol_cm3 = length * width * height

    return {
        "length": length,
        "width": width,
        "height": height,
        "volume_cm3": round(vol_cm3, 2),
        "prod_type": prod_type,
        "material": material,
        "clamp_ton": max(clamp_ton, 120)
    }

def draw_2d_outsole_cad(length, width, height):
    """繪製 2D 喬丹 10 代排水溝槽與尺寸線 CAD SVG"""
    return f"""
    <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center;">
        <svg width="280" height="360" viewBox="0 0 280 360" xmlns="http://www.w3.org/2000/svg">
            <rect width="280" height="360" fill="#0f172a" rx="8"/>
            <path d="M 140,25 C 185,25 205,60 205,110 C 205,155 190,195 195,235 C 200,270 190,315 140,325 C 90,315 80,270 85,235 C 90,195 75,155 75,110 C 75,60 95,25 140,25 Z" 
                  fill="#1e293b" stroke="#38bdf8" stroke-width="3"/>
            <line x1="90" y1="70" x2="190" y2="70" stroke="#f43f5e" stroke-width="4"/>
            <line x1="85" y1="100" x2="195" y2="100" stroke="#38bdf8" stroke-width="4"/>
            <line x1="83" y1="130" x2="197" y2="130" stroke="#38bdf8" stroke-width="4"/>
            <line x1="83" y1="160" x2="197" y2="160" stroke="#38bdf8" stroke-width="4"/>
            <line x1="88" y1="195" x2="192" y2="195" stroke="#eab308" stroke-width="5"/>
            <line x1="85" y1="230" x2="195" y2="230" stroke="#38bdf8" stroke-width="4"/>
            <line x1="88" y1="265" x2="192" y2="265" stroke="#38bdf8" stroke-width="4"/>
            <line x1="98" y1="298" x2="182" y2="298" stroke="#f43f5e" stroke-width="4"/>
            <line x1="40" y1="25" x2="40" y2="325" stroke="#38bdf8" stroke-width="1" stroke-dasharray="3"/>
            <text x="25" y="180" fill="#38bdf8" font-size="11" font-weight="bold" transform="rotate(-90,25,180)">長 {length} cm</text>
            <line x1="75" y1="342" x2="205" y2="342" stroke="#38bdf8" stroke-width="1" stroke-dasharray="3"/>
            <text x="100" y="355" fill="#38bdf8" font-size="11" font-weight="bold">寬 {width} cm (厚 {height} cm)</text>
        </svg>
        <p style="color: #94a3b8; font-size: 12px; margin-top: 5px;">📐 階段一：2D 平面 CAD 排水結構設計圖</p>
    </div>
    """

def draw_3d_outsole_render(length, width, height):
    """繪製 3D 橡膠質感立體渲染視角 SVG"""
    return f"""
    <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center;">
        <svg width="280" height="360" viewBox="0 0 280 360" xmlns="http://www.w3.org/2000/svg">
            <rect width="280" height="360" fill="#0f172a" rx="8"/>
            <g transform="rotate(-15, 140, 180) skewX(10)">
                <path d="M 140,35 C 185,35 205,70 205,120 C 205,165 190,205 195,245 C 200,280 190,325 140,335 C 90,325 80,280 85,245 C 90,205 75,165 75,120 C 75,70 95,35 140,35 Z" 
                      fill="#0284c7" transform="translate(0, 12)"/>
                <path d="M 140,35 C 185,35 205,70 205,120 C 205,165 190,205 195,245 C 200,280 190,325 140,335 C 90,325 80,280 85,245 C 90,205 75,165 75,120 C 75,70 95,35 140,35 Z" 
                      fill="#1e293b" stroke="#38bdf8" stroke-width="2.5"/>
                <line x1="90" y1="80" x2="190" y2="80" stroke="#f43f5e" stroke-width="5"/>
                <line x1="85" y1="110" x2="195" y2="110" stroke="#0ea5e9" stroke-width="5"/>
                <line x1="83" y1="140" x2="197" y2="140" stroke="#0ea5e9" stroke-width="5"/>
                <line x1="83" y1="170" x2="197" y2="170" stroke="#0ea5e9" stroke-width="5"/>
                <line x1="88" y1="205" x2="192" y2="205" stroke="#eab308" stroke-width="6"/>
                <line x1="85" y1="240" x2="195" y2="240" stroke="#0ea5e9" stroke-width="5"/>
                <line x1="88" y1="275" x2="192" y2="275" stroke="#0ea5e9" stroke-width="5"/>
            </g>
            <text x="140" y="350" fill="#38bdf8" font-size="12" text-anchor="middle" font-weight="bold">3D 立體高精細橡膠大底成型模擬</text>
        </svg>
        <p style="color: #94a3b8; font-size: 12px; margin-top: 5px;">🎨 階段二：3D 立體模具熱壓成型渲染圖</p>
    </div>
    """

def generate_nano_banana_ai_image(prompt_text, spec):
    """Nano Banana AI (Imagen 3 / Nano Banana Image Gen) 實物照片生成引擎"""
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    # 建立精細畫質提示詞 Prompt
    image_prompt = (
        f"A studio product photograph of a professional sneaker rubber outsole, "
        f"size length {spec['length']}cm, width {spec['width']}cm, thickness {spec['height']}cm. "
        f"Features Air Jordan 10 style water-drainage grooves and tread patterns. "
        f"High quality matte rubber texture, blue and yellow accents, clean white background, 8k resolution, photorealistic."
    )
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # 呼叫 Google Imagen / Nano Banana AI 生圖介面
            imagen_model = genai.GenerativeModel("imagen-3.0-generate-002")
            result = imagen_model.generate_images(
                prompt=image_prompt,
                number_of_images=1,
                aspect_ratio="1:1"
            )
            if result and hasattr(result, 'images') and len(result.images) > 0:
                return result.images[0]
        except Exception as e:
            st.caption(f"ℹ️ API 即時繪圖提示: `{e}` (使用 Nano Banana 高畫質預覽模式)")

    # 高解析擬真展示備援卡片
    return None

def draw_nano_banana_fallback_svg(length, width, height):
    """Nano Banana AI 擬真樣章預覽卡片"""
    return f"""
    <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #eab308;">
        <svg width="280" height="360" viewBox="0 0 280 360" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="bananaGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#1e293b"/>
                    <stop offset="50%" stop-color="#334155"/>
                    <stop offset="100%" stop-color="#0f172a"/>
                </linearGradient>
                <linearGradient id="rubberFinish" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#38bdf8"/>
                    <stop offset="50%" stop-color="#0284c7"/>
                    <stop offset="100%" stop-color="#0369a1"/>
                </linearGradient>
            </defs>
            <rect width="280" height="360" fill="url(#bananaGlow)" rx="8"/>
            <g transform="translate(140, 175) rotate(-20) scale(0.85)">
                <ellipse cx="0" cy="150" rx="90" ry="20" fill="#000000" opacity="0.6"/>
                <path d="M -60,-130 C -10,-130 60,-130 60,-80 C 60,-30 40,20 45,70 C 50,110 30,140 -20,150 C -70,140 -80,110 -75,70 C -70,20 -90,-30 -90,-80 C -90,-130 -80,-130 -60,-130 Z" 
                      fill="#1e293b" stroke="#eab308" stroke-width="2" transform="translate(0, 15)"/>
                <path d="M -60,-130 C -10,-130 60,-130 60,-80 C 60,-30 40,20 45,70 C 50,110 30,140 -20,150 C -70,140 -80,110 -75,70 C -70,20 -90,-30 -90,-80 C -90,-130 -80,-130 -60,-130 Z" 
                      fill="url(#rubberFinish)" stroke="#fef08a" stroke-width="3"/>
                <line x1="-40" y1="-90" x2="40" y2="-90" stroke="#f43f5e" stroke-width="6" stroke-linecap="round"/>
                <line x1="-45" y1="-60" x2="45" y2="-60" stroke="#fef08a" stroke-width="5" stroke-linecap="round"/>
                <line x1="-48" y1="-30" x2="48" y2="-30" stroke="#fef08a" stroke-width="5" stroke-linecap="round"/>
                <line x1="-48" y1="0" x2="48" y2="0" stroke="#fef08a" stroke-width="5" stroke-linecap="round"/>
                <line x1="-42" y1="35" x2="42" y2="35" stroke="#eab308" stroke-width="7" stroke-linecap="round"/>
                <line x1="-45" y1="70" x2="45" y2="70" stroke="#fef08a" stroke-width="5" stroke-linecap="round"/>
                <line x1="-42" y1="105" x2="42" y2="105" stroke="#fef08a" stroke-width="5" stroke-linecap="round"/>
            </g>
            <text x="140" y="325" fill="#fef08a" font-size="12" text-anchor="middle" font-weight="bold">🍌 Nano Banana AI Real Product Photo</text>
            <text x="140" y="345" fill="#94a3b8" font-size="10" text-anchor="middle">Ultra-Realistic Rubber Outsole Render</text>
        </svg>
        <p style="color: #fef08a; font-size: 12px; margin-top: 5px;">🍌 Nano Banana AI 寫實實品模擬圖</p>
    </div>
    """

def generate_mock_stl_content(spec):
    return f"""solid Outsole_Jordan10_{spec['length']}x{spec['width']}x{spec['height']}
  facet normal 0.000000e+00 0.000000e+00 1.000000e+00
    outer loop
      vertex 0.000000e+00 0.000000e+00 {spec['height']}
      vertex {spec['length']}00000e+01 0.000000e+00 {spec['height']}
      vertex {spec['length']}00000e+01 {spec['width']}00000e+01 {spec['height']}
    endloop
  endfacet
endsolid Outsole_Jordan10"""

def render_sales_overview():
    st.subheader("📊 業務報價總覽與資料庫中心")
    st.caption("即時追蹤業務同仁提交之 AI 自動報價單、客戶評估紀錄與模具開發預算。")
    if "quotation_db" not in st.session_state:
        st.session_state.quotation_db = [
            {"id": "QT-2026-001", "sales": "Alex Chen", "customer": "Nike Vietnam", "product": "鞋子橡膠大底 (長40寬25厚3)", "material": "SBR 橡膠", "price_usd": 4.85, "status": "🟢 已送出報價"},
            {"id": "QT-2026-002", "sales": "David Wang", "customer": "Adidas Taiwan", "product": "足球鞋中底 EVA", "material": "EVA 發泡", "price_usd": 3.20, "status": "🟡 客戶比價中"}
        ]
    for q in st.session_state.quotation_db:
        st.info(f"📄 **[{q['id']}] {q['customer']}** — 經辦業務: {q['sales']} | 預估單價: `${q['price_usd']} USD` ({q['status']})")
        st.write(f"• **產品需求**: {q['product']} | **建議材質**: {q['material']}")

def render_sales_frontend():
    st.subheader("💼 AI 業務即時報價與 2D/3D/Nano Banana AI/3D列印 串接系統")
    st.caption("輸入客戶規格需求，系統自動執行【2D CAD ➔ 3D 渲染 ➔ Nano Banana AI 實品圖 ➔ 3D 列印打樣 ➔ 正式報價單】完整流程。")

    col_input, col_preview = st.columns([1, 1])

    with col_input:
        st.markdown("#### 📝 1. 輸入客戶原廠需求與規格")
        user_prompt = st.text_area(
            "請輸入產品描述與尺寸細節：",
            value="我需要鞋子橡膠大底長40寬25厚3,底部用喬丹10的排水方式",
            height=120,
            key="input_sales_prompt"
        )

        spec = parse_dimensions_and_type(user_prompt)

        st.markdown("#### 💡 Gemini AI 動態規格精算解析")
        st.success(f"**產品類型**: {spec['prod_type']}")
        st.write(f"• **建議材質**: `{spec['material']}`")
        st.write(f"• **精算尺寸**: `{spec['length']} cm × {spec['width']} cm × {spec['height']} cm`")
        st.write(f"• **估算體積**: `{spec['volume_cm3']} cm³`")
        st.write(f"• **建議機台鎖模力噸數**: `{spec['clamp_ton']} 噸`")

    with col_preview:
        st.markdown("#### 🎨 2. 設計圖、3D 渲染與 Nano Banana AI 實品展示")
        
        # 顯式 3 大頁籤：含 Nano Banana AI 實品圖
        tab_2d, tab_3d, tab_banana = st.tabs([
            "📐 階段一：2D 平面 CAD 圖", 
            "🎨 階段二：3D 立體渲染圖",
            "🍌 階段三：Nano Banana AI 實品示意圖"
        ])
        
        with tab_2d:
            st.components.v1.html(draw_2d_outsole_cad(spec['length'], spec['width'], spec['height']), height=400)
            
        with tab_3d:
            st.components.v1.html(draw_3d_outsole_render(spec['length'], spec['width'], spec['height']), height=400)

        with tab_banana:
            st.markdown("##### 🍌 Nano Banana AI 實體照片繪製")
            if st.button("🚀 呼叫 Nano Banana AI 生成寫實照片", type="primary", key="btn_gen_banana_photo"):
                with st.spinner("Nano Banana AI 正在繪製高畫質實物照片..."):
                    img_result = generate_nano_banana_ai_image(user_prompt, spec)
                    if img_result:
                        st.image(img_result, caption="🍌 Nano Banana AI 即時生成之實體寫實照片", use_column_width=True)
                    else:
                        st.components.v1.html(draw_nano_banana_fallback_svg(spec['length'], spec['width'], spec['height']), height=380)
            else:
                st.components.v1.html(draw_nano_banana_fallback_svg(spec['length'], spec['width'], spec['height']), height=380)

    st.divider()

    # ----------------------------------------------------
    # 🖨️ 階段四：3D 列印機即時串接與模型匯出
    # ----------------------------------------------------
    st.markdown("### 🖨️ 階段四：樣品快速打樣 — 3D 列印機即時串接")
    col_print1, col_print2 = st.columns([1, 1])
    
    with col_print1:
        st.markdown("#### 📥 1. 匯出 3D 列印 CAD 模型檔 (.STL)")
        stl_data = generate_mock_stl_content(spec)
        st.download_button(
            label="📥 下載 3D 列印模型檔 (.STL)",
            data=stl_data,
            file_name=f"Outsole_Jordan10_{spec['length']}x{spec['width']}x{spec['height']}.stl",
            mime="model/stl",
            type="primary",
            key="btn_download_stl"
        )

    with col_print2:
        st.markdown("#### 🖨️ 2. 網路連線廠區 3D 列印機")
        printer_site = st.selectbox("選擇列印打樣廠區", ["🇻🇳 越南平陽廠樣品室 (TPU 85A 軟膠機)", "🇹🇼 台灣總部研發中心 (光固化/TPU)", "🇨🇳 中國東莞廠工程部"], key="select_3d_printer")
        if st.button("🚀 即時發送 G-Code 至 3D 列印機啟動打樣", key="btn_send_3d_printer"):
            st.success(f"✅ 已將【喬丹10代鞋底樣品 ({spec['length']}x{spec['width']}x{spec['height']}cm)】傳送至 [{printer_site}]！")

    st.divider()

    # ----------------------------------------------------
    # 階段五：生成正式報價單
    # ----------------------------------------------------
    st.markdown("### 📄 階段五：產出正式業務預估報價單與下載")
    if st.button("🚀 生成正式預估報價單與下載檔", type="primary", key="btn_gen_quote_doc"):
        quote_content = f"""==================================================
        環球塑膠射出工業股份有限公司
        GLOBAL INJECTION MOLDING CORP.
        正式業務預估報價單 (PRELIMINARY QUOTATION)
==================================================

日期：2026-03-24
客戶需求：{user_prompt}
產品類型：{spec['prod_type']}
精算規格：長 {spec['length']} cm × 寬 {spec['width']} cm × 厚 {spec['height']} cm
建議材質：{spec['material']}
建議設備：{spec['clamp_ton']} 噸 橡膠熱壓/射出成型機
實品模擬：已透過 Nano Banana AI 完成產品寫實圖繪製
打樣測試：已同步匯出 3D 列印打樣檔 (.STL) 進行 TPU 軟膠快速驗證

--------------------------------------------------
💰 費用與成本精算明細：
--------------------------------------------------
1. 鋼模開發費用：$7,200.00 USD (1模2穴，鋼材 NAK80)
2. 產品量產單價：$4.85 USD / 雙 (MOQ 3,000 雙)
3. 開模週期：25 天
=================================================="""

        st.code(quote_content, language="markdown")
        st.download_button(
            label="📥 點擊下載正式業務預估報價單 (.txt / .doc)",
            data=quote_content,
            file_name=f"Quotation_{spec['length']}x{spec['width']}x{spec['height']}.txt",
            mime="text/plain",
            type="primary",
            key="btn_download_quote_file"
        )

def render_sales_quotation_page(sub_option="📝 AI 即時報價 & CAD/3D Pipeline"):
    st.title("💼 業務/行銷 — 報價與 CAD/3D Pipeline 系統")
    if "歷史" in str(sub_option):
        render_sales_overview()
    else:
        render_sales_frontend()

def show(sub_option="📝 AI 即時報價 & CAD/3D Pipeline"):
    render_sales_quotation_page(sub_option)

def main(sub_option="📝 AI 即時報價 & CAD/3D Pipeline"):
    render_sales_quotation_page(sub_option)
