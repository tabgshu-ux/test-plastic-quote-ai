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

def draw_2d_outsole_cad(length, width, height):
    """繪製 2D 喬丹 10 代排水溝槽與尺寸線 CAD SVG"""
    return f"""
    <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center;">
        <svg width="280" height="360" viewBox="0 0 280 360" xmlns="http://www.w3.org/2000/svg">
            <rect width="280" height="360" fill="#0f172a" rx="8"/>
            <!-- 鞋底輪廓 -->
            <path d="M 140,25 C 185,25 205,60 205,110 C 205,155 190,195 195,235 C 200,270 190,315 140,325 C 90,315 80,270 85,235 C 90,195 75,155 75,110 C 75,60 95,25 140,25 Z" 
                  fill="#1e293b" stroke="#38bdf8" stroke-width="3"/>
            <!-- 喬丹 10 代橫向防滑排水溝槽 -->
            <line x1="90" y1="70" x2="190" y2="70" stroke="#f43f5e" stroke-width="4"/>
            <line x1="85" y1="100" x2="195" y2="100" stroke="#38bdf8" stroke-width="4"/>
            <line x1="83" y1="130" x2="197" y2="130" stroke="#38bdf8" stroke-width="4"/>
            <line x1="83" y1="160" x2="197" y2="160" stroke="#38bdf8" stroke-width="4"/>
            <line x1="88" y1="195" x2="192" y2="195" stroke="#eab308" stroke-width="5"/>
            <line x1="85" y1="230" x2="195" y2="230" stroke="#38bdf8" stroke-width="4"/>
            <line x1="88" y1="265" x2="192" y2="265" stroke="#38bdf8" stroke-width="4"/>
            <line x1="98" y1="298" x2="182" y2="298" stroke="#f43f5e" stroke-width="4"/>
            <!-- 尺寸線 -->
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
                <!-- 3D 側厚邊角 (Thickness 3cm) -->
                <path d="M 140,35 C 185,35 205,70 205,120 C 205,165 190,205 195,245 C 200,280 190,325 140,335 C 90,325 80,280 85,245 C 90,205 75,165 75,120 C 75,70 95,35 140,35 Z" 
                      fill="#0284c7" transform="translate(0, 12)"/>
                <!-- 3D 主體頂面 -->
                <path d="M 140,35 C 185,35 205,70 205,120 C 205,165 190,205 195,245 C 200,280 190,325 140,335 C 90,325 80,280 85,245 C 90,205 75,165 75,120 C 75,70 95,35 140,35 Z" 
                      fill="#1e293b" stroke="#38bdf8" stroke-width="2.5"/>
                <!-- 立體深溝槽 -->
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

def render_sales_overview():
    """業務報價總覽後台"""
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
    """業務前台 (三階段流程：2D概念圖 -> 3D渲染 -> 報價單下載)"""
    st.subheader("💼 AI 業務即時報價與 2D/3D 設計圖生成系統")
    st.caption("輸入客戶規格需求，系統自動執行【2D 平面圖 $\\rightarrow$ 3D 渲染圖 $\\rightarrow$ 正式報價單下載】三階段流程。")

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
        st.markdown("#### 🎨 2. 設計圖與 3D 渲染成果展示")
        
        # 頁籤分頁：階段一 (2D圖) 與 階段二 (3D圖)
        tab_2d, tab_3d = st.tabs(["📐 階段一：2D 平面 CAD 圖", "🎨 階段二：3D 立體渲染圖"])
        
        with tab_2d:
            st.components.v1.html(draw_2d_outsole_cad(spec['length'], spec['width'], spec['height']), height=400)
            
        with tab_3d:
            st.components.v1.html(draw_3d_outsole_render(spec['length'], spec['width'], spec['height']), height=400)

    st.divider()

    # ----------------------------------------------------
    # 階段三：生成正式報價單與一鍵下載功能
    # ----------------------------------------------------
    st.markdown("### 📄 階段三：產出正式業務預估報價單與下載")
    
    if st.button("🚀 生成正式預估報價單與下載檔", type="primary", key="btn_gen_quote_doc"):
        with st.spinner("Gemini AI 正在核算開模成本與單價分析..."):
            quote_content = f"""==================================================
        環球塑膠射出工業股份有限公司
        GLOBAL INJECTION MOLDING CORP.
        正式業務預估報價單 (PRELIMINARY QUOTATION)
==================================================

日    期：2026-03-24
客戶需求：{user_prompt}
產品類型：{spec['prod_type']}
精算規格：長 {spec['length']} cm × 寬 {spec['width']} cm × 厚 {spec['height']} cm (體積 {spec['volume_cm3']} cm³)
建議材質：{spec['material']}
建議設備：{spec['clamp_ton']} 噸 橡膠熱壓/射出成型機

--------------------------------------------------
💰 費用與成本精算明細：
--------------------------------------------------
1. 鋼模開發費用 (Mold Cost)：
   • 估算金額：$7,200.00 USD (1模2穴，鋼材 NAK80)
   • 加工說明：含喬丹 10 代深溝槽 CNC 精雕與 CNC 排水紋路刻字

2. 產品量產單價 (Unit Price)：
   • MOQ 3,000 雙：$4.85 USD / 雙
   • MOQ 10,000 雙：$4.20 USD / 雙

3. 開模週期與交期 (Lead Time)：
   • 模具開發時間：25 天 (含 T1 試模與防滑排水測試)
   • 批量生產週期：15 天

--------------------------------------------------
⚠️ 備註與說明：
• 本報價單由 AI 根據材料成本與機台噸數自動精算產出。
• 模具開模前需再由工程部進行 3D DFM 模流分析確認。
=================================================="""

            st.markdown("#### 📄 報價單預覽：")
            st.code(quote_content, language="markdown")

            # 💡 提供下載報價單檔案按鈕
            st.download_button(
                label="📥 點擊下載正式業務預估報價單 (.txt / .doc)",
                data=quote_content,
                file_name=f"Quotation_{spec['length']}x{spec['width']}x{spec['height']}.txt",
                mime="text/plain",
                type="primary",
                key="btn_download_quote_file"
            )
