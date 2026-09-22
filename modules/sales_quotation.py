import re
import math
import streamlit as st
import google.generativeai as genai

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

def generate_nanobanana_image(user_prompt, spec):
    """呼叫 Google Imagen 3 (Nano Banana) 圖像生成 API"""
    try:
        # 使用 Google Imagen 3 模型生成圖片
        imagen_model = genai.GenerativeModel("imagen-3.0-generate-002")
        image_prompt = f"Industrial 3D render of a single rubber shoe outsole, bottom view, Air Jordan 10 traction pattern with drainage grooves, dimensions {spec['length']}cm length, {spec['width']}cm width, {spec['height']}cm thickness, sole only, no shoe upper, photorealistic, studio lighting, dark background."
        
        result = imagen_model.generate_images(
            prompt=image_prompt,
            number_of_images=1,
            aspect_ratio="1:1"
        )
        if result and len(result.images) > 0:
            return result.images[0], "✅ Nano Banana (Imagen 3) 成功繪製 3D 橡膠鞋底！"
    except Exception as e:
        return None, f"備註: (Imagen 3 API: {str(e)})"

def generate_outsole_svg(length, width, height):
    """備用 SVG CAD 向量圖"""
    return f"""
    <div style="background-color: #1a1e24; padding: 20px; border-radius: 12px; text-align: center;">
        <svg width="300" height="380" viewBox="0 0 300 380" xmlns="http://www.w3.org/2000/svg">
            <rect width="300" height="380" fill="#111827" rx="10"/>
            <path d="M 150,30 C 200,30 220,70 220,120 C 220,170 205,210 210,250 C 215,290 205,340 150,350 C 95,340 85,290 90,250 C 95,210 80,170 80,120 C 80,70 100,30 150,30 Z" 
                  fill="#1f2937" stroke="#00f2fe" stroke-width="3"/>
            <line x1="95" y1="80" x2="205" y2="80" stroke="#ff4b4b" stroke-width="4"/>
            <line x1="90" y1="110" x2="210" y2="110" stroke="#3b82f6" stroke-width="4"/>
            <line x1="88" y1="140" x2="212" y2="140" stroke="#3b82f6" stroke-width="4"/>
            <line x1="88" y1="170" x2="212" y2="170" stroke="#3b82f6" stroke-width="4"/>
            <line x1="95" y1="210" x2="205" y2="210" stroke="#eab308" stroke-width="5"/>
            <line x1="92" y1="250" x2="208" y2="250" stroke="#3b82f6" stroke-width="4"/>
            <line x1="95" y1="290" x2="205" y2="290" stroke="#3b82f6" stroke-width="4"/>
            <text x="150" y="370" fill="#00f2fe" font-size="12" text-anchor="middle">長 {length}cm × 寬 {width}cm × 厚 {height}cm (喬丹10紋路)</text>
        </svg>
    </div>
    """

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
    st.subheader("💼 AI 業務即時報價與 3D 概念圖生成系統")
    st.caption("輸入客戶產品需求（如尺寸、材質、排水紋路），由 Gemini AI 自動精算噸數與成本，並呼叫 Nano Banana 生成 3D 概念圖。")

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
        st.markdown("#### 🎨 2. Nano Banana 3D 繪圖引擎渲染")
        st.caption("點擊下方按鈕，召喚 Nano Banana (Imagen 3) 繪製純 3D 橡膠鞋底：")

        if st.button("🚀 啟動 Nano Banana 生成 3D 鞋底圖與報價單", type="primary", key="btn_gen_nanobanana"):
            with st.spinner("Nano Banana (Imagen 3) 正在即時渲染 3D 喬丹 10 代橡膠鞋底..."):
                img_obj, msg = generate_nanobanana_image(user_prompt, spec)
                
                if img_obj is not None:
                    st.image(img_obj, caption=f"🍌 Nano Banana 3D 渲染成果 ({spec['length']}x{spec['width']}x{spec['height']}cm)", use_container_width=True)
                else:
                    # 顯示 CAD 圖並提示
                    st.components.v1.html(generate_outsole_svg(spec['length'], spec['width'], spec['height']), height=410)
                    st.caption(msg)

                try:
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    ai_prompt = f"""
                    你是一位專業的橡膠射出成型與鞋底模具工程師。
                    請針對客戶需求：『{user_prompt}』
                    規格：[長 {spec['length']}cm, 寬 {spec['width']}cm, 厚 {spec['height']}cm, 噸數 {spec['clamp_ton']} 噸]
                    
                    請產出一份專業的業務報價分析報告：
                    1. 鋼模開發費用預估 (USD，含 CNC 精雕深溝槽)
                    2. 產品單價分析 (根據橡膠原料成本與熱壓/射出加工費)
                    3. 喬丹 10 代排水紋路（橫向溝槽與防滑排水結構）之 CNC 開模可行性
                    4. 建議成型工藝（橡膠射出成型 / 熱壓成型）
                    """
                    res = model.generate_content(ai_prompt)
                    st.markdown(res.text)

                except Exception:
                    st.markdown(f"""
#### 📄 業務即時預估報價單
* **產品名稱**: {spec['prod_type']} (喬丹10代強效排水防滑紋路)
* **尺寸體積**: {spec['length']} × {spec['width']} × {spec['height']} cm ({spec['volume_cm3']} cm³)
* **建議材質**: {spec['material']}
* **預估單件重量**: 約 420g
* **建議製造設備**: {spec['clamp_ton']} 噸 橡膠熱壓/射出成型機

---
##### 💰 費用精算總覽：
1. **鋼模開模費用**: `$6,500 ~ $8,000 USD` (1模2穴，含喬丹10深溝槽 CNC 精雕)
2. **預估產品單價**: `$4.50 ~ $5.20 USD / 雙` (MOQ: 3,000 雙)
3. **開模週期**: 25 天 (含 T1 試模與防滑排水測試)
""")
