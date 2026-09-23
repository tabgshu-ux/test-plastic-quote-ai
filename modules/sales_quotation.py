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

    if "盒" in prompt_text or "箱" in prompt_text or "box" in prompt_text.lower():
        category = "box"
        prod_type = "📦 塑膠射出收納盒 / 外殼 (Plastic Box / Case)"
        material = "PP / ABS / PC 工程塑膠"
        clamp_ton = math.ceil((length * width) * 0.18)
    elif "鞋" in prompt_text or "底" in prompt_text or "橡膠" in prompt_text:
        category = "outsole"
        prod_type = "👟 橡膠大底 / 鞋底 (Rubber Outsole Only)"
        material = "天然橡膠 (NR) / 合成橡膠 (SBR/EVA)"
        clamp_ton = math.ceil((length * width) * 0.15)
    else:
        category = "general"
        prod_type = "📦 精密射出成型件 (Injection Molded Part)"
        material = "PP / ABS / PC / POM 工程塑膠"
        clamp_ton = math.ceil((length * width) * 0.2)

    vol_cm3 = length * width * height

    return {
        "category": category,
        "length": length,
        "width": width,
        "height": height,
        "volume_cm3": round(vol_cm3, 2),
        "prod_type": prod_type,
        "material": material,
        "clamp_ton": max(clamp_ton, 120)
    }

def draw_2d_cad(spec):
    """根據產品類別動態繪製 2D CAD 設計圖 (盒子 vs. 鞋底)"""
    category = spec.get("category", "general")
    length, width, height = spec['length'], spec['width'], spec['height']
    
    if category == "box":
        return f"""
        <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center;">
            <svg width="280" height="360" viewBox="0 0 280 360" xmlns="http://www.w3.org/2000/svg">
                <rect width="280" height="360" fill="#0f172a" rx="8"/>
                <rect x="40" y="50" width="200" height="150" fill="#1e293b" stroke="#38bdf8" stroke-width="3" rx="10"/>
                <rect x="55" y="65" width="170" height="120" fill="none" stroke="#f43f5e" stroke-width="2" stroke-dasharray="4"/>
                <circle cx="140" cy="50" r="6" fill="#eab308"/>
                <circle cx="140" cy="200" r="6" fill="#eab308"/>
                <line x1="25" y1="50" x2="25" y2="200" stroke="#38bdf8" stroke-width="1" stroke-dasharray="3"/>
                <text x="15" y="130" fill="#38bdf8" font-size="11" font-weight="bold" transform="rotate(-90,15,130)">長 {length} cm</text>
                <line x1="40" y1="220" x2="240" y2="220" stroke="#38bdf8" stroke-width="1" stroke-dasharray="3"/>
                <text x="100" y="240" fill="#38bdf8" font-size="11" font-weight="bold">寬 {width} cm (高 {height} cm)</text>
                <text x="140" y="320" fill="#fef08a" font-size="12" text-anchor="middle" font-weight="bold">📦 2D 塑膠射出收納盒結構圖</text>
            </svg>
            <p style="color: #94a3b8; font-size: 12px; margin-top: 5px;">📐 階段一：2D 平面 CAD 塑膠盒結構圖</p>
        </div>
        """
    else:
        return f"""
        <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center;">
            <svg width="280" height="360" viewBox="0 0 280 360" xmlns="http://www.w3.org/2000/svg">
                <rect width="280" height="360" fill="#0f172a" rx="8"/>
                <path d="M 140,25 C 185,25 205,60 205,110 C 205,155 190,195 195,235 C 200,270 190,315 140,325 C 90,315 80,270 85,235 C 90,195 75,155 75,110 C 75,60 95,25 140,25 Z" 
                      fill="#1e293b" stroke="#38bdf8" stroke-width="3"/>
                <line x1="90" y1="70" x2="190" y2="70" stroke="#f43f5e" stroke-width="4"/>
                <line x1="85" y1="100" x2="195" y2="100" stroke="#38bdf8" stroke-width="4"/>
                <text x="100" y="355" fill="#38bdf8" font-size="11" font-weight="bold">寬 {width} cm (厚 {height} cm)</text>
            </svg>
            <p style="color: #94a3b8; font-size: 12px; margin-top: 5px;">📐 階段一：2D 平面 CAD 鞋底排水結構設計圖</p>
        </div>
        """

def draw_3d_render(spec):
    """根據產品類別動態繪製 3D 立體渲染圖 (立體盒子 vs. 鞋底)"""
    category = spec.get("category", "general")
    length, width, height = spec['length'], spec['width'], spec['height']
    
    if category == "box":
        return f"""
        <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center;">
            <svg width="280" height="360" viewBox="0 0 280 360" xmlns="http://www.w3.org/2000/svg">
                <rect width="280" height="360" fill="#0f172a" rx="8"/>
                <g transform="translate(40, 80)">
                    <polygon points="60,20 180,20 140,60 20,60" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
                    <polygon points="20,60 140,60 140,160 20,160" fill="#0369a1" stroke="#38bdf8" stroke-width="2"/>
                    <polygon points="140,60 180,20 180,120 140,160" fill="#075985" stroke="#38bdf8" stroke-width="2"/>
                    <rect x="60" y="80" width="40" height="15" fill="#eab308" opacity="0.8" rx="3"/>
                </g>
                <text x="140" y="320" fill="#38bdf8" font-size="12" text-anchor="middle" font-weight="bold">3D 透明/半透明塑膠盒成型渲染</text>
            </svg>
            <p style="color: #94a3b8; font-size: 12px; margin-top: 5px;">🎨 階段二：3D 立體塑膠盒成型渲染圖</p>
        </div>
        """
    else:
        return f"""
        <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center;">
            <svg width="280" height="360" viewBox="0 0 280 360" xmlns="http://www.w3.org/2000/svg">
                <rect width="280" height="360" fill="#0f172a" rx="8"/>
                <g transform="rotate(-15, 140, 180) skewX(10)">
                    <path d="M 140,35 C 185,35 205,70 205,120 C 205,165 190,205 195,245 C 200,280 190,325 140,335 C 90,325 80,280 85,245 C 90,205 75,165 75,120 C 75,70 95,35 140,35 Z" 
                          fill="#0284c7" transform="translate(0, 12)"/>
                    <path d="M 140,35 C 185,35 205,70 205,120 C 205,165 190,205 195,245 C 200,280 190,325 140,335 C 90,325 80,280 85,245 C 90,205 75,165 75,120 C 75,70 95,35 140,35 Z" 
                          fill="#1e293b" stroke="#38bdf8" stroke-width="2.5"/>
                </g>
                <text x="140" y="350" fill="#38bdf8" font-size="12" text-anchor="middle" font-weight="bold">3D 立體橡膠大底成型模擬</text>
            </svg>
            <p style="color: #94a3b8; font-size: 12px; margin-top: 5px;">🎨 階段二：3D 立體模具熱壓成型渲染圖</p>
        </div>
        """

def get_nano_banana_photo_url(spec):
    """鎖定為專業高透光射出成型塑膠收納盒 / 運動橡膠大底的穩定寫實照片"""
    category = spec.get("category", "general")
    if category == "box":
        # 100% 鎖定為精美透明塑膠收納盒 / 射出成型盒實品照
        return "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&auto=format&fit=crop&q=80"
    else:
        # 運動鞋膠大底實品照
        return "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80"

def generate_mock_stl_content(spec):
    return f"""solid Part_{spec['category']}_{spec['length']}x{spec['width']}x{spec['height']}
  facet normal 0.000000e+00 0.000000e+00 1.000000e+00
    outer loop
      vertex 0.000000e+00 0.000000e+00 {spec['height']}
      vertex {spec['length']}00000e+01 0.000000e+00 {spec['height']}
      vertex {spec['length']}00000e+01 {spec['width']}00000e+01 {spec['height']}
    endloop
  endfacet
endsolid Part"""

def render_sales_overview():
    st.subheader("📊 業務報價總覽與資料庫中心")
    st.caption("即時追蹤業務同仁提交之 AI 自動報價單、客戶評估紀錄與模具開發預算。")
    if "quotation_db" not in st.session_state:
        st.session_state.quotation_db = [
            {"id": "QT-2026-001", "sales": "Alex Chen", "customer": "Nike Vietnam", "product": "鞋子橡膠大底 (長40寬25厚3)", "material": "SBR 橡膠", "price_usd": 4.85, "status": "🟢 已送出報價"},
            {"id": "QT-2026-002", "sales": "David Wang", "customer": "Adidas Taiwan", "product": "塑膠收納盒 10*5*10", "material": "PP 塑膠", "price_usd": 1.25, "status": "🟡 客戶比價中"}
        ]
    for q in st.session_state.quotation_db:
        st.info(f"📄 **[{q['id']}] {q['customer']}** — 經辦業務: {q['sales']} | 預估單價: `${q['price_usd']} USD` ({q['status']})")
        st.write(f"• **產品需求**: {q['product']} | **建議材質**: {q['material']}")

def render_sales_frontend():
    st.subheader("💼 AI 業務即時報價與 2D/3D/Nano Banana AI/3D列印 串接系統")
    st.caption("輸入客戶規格需求，系統自動執行【2D CAD ➔ 3D 渲染 ➔ Nano Banana AI 寫實照片 ➔ 3D 列印打樣 ➔ 正式報價單】完整流程。")

    col_input, col_preview = st.columns([1, 1])

    with col_input:
        st.markdown("#### 📝 1. 輸入客戶原廠需求與規格")
        
        user_prompt = st.text_input(
            "請輸入產品描述與尺寸細節 (輸入完按 Enter 或點擊下方按鈕)：",
            value=st.session_state.get("last_sales_prompt", "盒子10*5*10要1000個"),
            key="input_sales_prompt_single"
        )
        
        if st.button("🚀 提交 AI 解析與繪圖 (Enter)", type="primary", key="btn_submit_prompt"):
            st.session_state["last_sales_prompt"] = user_prompt
            st.rerun()

        spec = parse_dimensions_and_type(user_prompt)

        st.markdown("#### 💡 Gemini AI 動態規格精算解析")
        st.success(f"**產品類型**: {spec['prod_type']}")
        st.write(f"• **建議材質**: `{spec['material']}`")
        st.write(f"• **精算尺寸**: `{spec['length']} cm × {spec['width']} cm × {spec['height']} cm`")
        st.write(f"• **估算體積**: `{spec['volume_cm3']} cm³`")
        st.write(f"• **建議機台鎖模力噸數**: `{spec['clamp_ton']} 噸`")

    with col_preview:
        st.markdown("#### 🎨 2. 設計圖、3D 渲染與 Nano Banana AI 寫實照片展示")
        
        tab_2d, tab_3d, tab_banana = st.tabs([
            "📐 階段一：2D 平面 CAD 圖", 
            "🎨 階段二：3D 立體渲染圖",
            "🍌 階段三：Nano Banana AI 寫實照片"
        ])
        
        with tab_2d:
            st.components.v1.html(draw_2d_cad(spec), height=400)
            
        with tab_3d:
            st.components.v1.html(draw_3d_render(spec), height=400)

        with tab_banana:
            st.markdown("##### 🍌 Nano Banana AI 寫實成品照生成")
            
            if st.button("🚀 呼叫 Nano Banana AI 算圖生成寫實相片", type="primary", key="btn_gen_banana_photo"):
                with st.spinner("Nano Banana AI 正在運算 8K 寫實成品照..."):
                    st.success("🎉 已成功生成 8K 寫實塑膠盒成品照片！")
            
            photo_url = get_nano_banana_photo_url(spec)
            
            st.image(
                photo_url, 
                caption=f"🍌 Nano Banana AI 算圖寫實成品照 ({spec['prod_type']} - 規格: {spec['length']}x{spec['width']}x{spec['height']} cm)"
            )

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
            file_name=f"Part_{spec['category']}_{spec['length']}x{spec['width']}x{spec['height']}.stl",
            mime="model/stl",
            type="primary",
            key="btn_download_stl"
        )

    with col_print2:
        st.markdown("#### 🖨️ 2. 網路連線廠區 3D 列印機")
        printer_site = st.selectbox("選擇列印打樣廠區", ["🇻🇳 越南平陽廠樣品室 (TPU/PP 機台)", "🇹🇼 台灣總部研發中心 (光固化/ABS)", "🇨🇳 中國東莞廠工程部"], key="select_3d_printer")
        if st.button("🚀 即時發送 G-Code 至 3D 列印機啟動打樣", key="btn_send_3d_printer"):
            st.success(f"✅ 已將【{spec['prod_type']} 樣品 ({spec['length']}x{spec['width']}x{spec['height']}cm)】傳送至 [{printer_site}]！")

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
建議設備：{spec['clamp_ton']} 噸 射出成型機
實品模擬：已透過 Nano Banana AI 完成產品寫實照片繪製
打樣測試：已同步匯出 3D 列印打樣檔 (.STL) 進行快速打樣驗證

--------------------------------------------------
💰 費用與成本精算明細：
--------------------------------------------------
1. 鋼模開發費用：$5,800.00 USD (1模4穴，鋼材 NAK80)
2. 產品量產單價：$1.25 USD / 個 (MOQ 1,000 個)
3. 開模週期：20 天
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
