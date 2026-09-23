import re
import math
import streamlit as st
import google.generativeai as genai
import os

# ----------------------------------------------------
# 🌐 業務模組多語系字典 (i18n Dictionary for Sales Module)
# ----------------------------------------------------
SALES_I18N = {
    "繁體中文": {
        "page_title": "💼 業務/行銷 — 報價與 CAD/3D Pipeline 系統",
        "sub_title": "💼 全產業 AI 即時報價與 2D/3D/Nano Banana AI 自動化系統",
        "sub_caption": "輸入任意產品描述，由 AI 自動理解語意並即時生成 2D CAD、3D 渲染與 Nano Banana 寫實照片。",
        "section_input": "📝 1. 請客戶說明產品需求與規格",
        "input_label": "請輸入產品描述 (輸入完點擊下方紅鈕或按 Enter)：",
        "input_default": "無人機螺旋槳用馬達",
        "btn_submit": "🚀 提交 AI 語意解析與全自動繪圖 (Enter)",
        "section_ai_parse": "💡 Gemini AI 動態規格精算解析",
        "label_prod_type": "辨識產品類型",
        "label_material": "建議材質",
        "label_dimensions": "精算尺寸",
        "label_volume": "估算體積",
        "label_clamp_ton": "建議機台鎖模力/噸數",
        "section_preview": "🎨 2. 2D CAD、3D 渲染與 Nano Banana AI 寫實生成展示",
        "tab_2d": "📐 階段一：2D CAD 幾何圖",
        "tab_3d": "🎨 階段二：3D 等角立體圖",
        "tab_banana": "🍌 階段三：Nano Banana AI 寫實照片",
        "banana_heading": "🍌 Nano Banana AI 寫實成品照生成",
        "btn_gen_banana": "🚀 呼叫 Nano Banana AI 算圖生成寫實相片",
        "banana_toast": "Nano Banana AI 正在運算 8K 寫實照片...",
        "banana_success": "🎉 已成功生成 8K 寫實成品照片！",
        "section_3dprint": "🖨️ 階段四：樣品快速打樣 — 3D 列印機即時串接",
        "section_3dprint_caption": "將 3D 模型自動匯出為 3D 列印通用檔 (.STL)，並可直接發送指令至廠區 3D 列印機進行快速打樣：",
        "download_stl_title": "📥 1. 匯出通用 3D 列印 CAD 模型檔 (.STL)",
        "btn_download_stl": "📥 下載 3D 列印模型檔 (.STL)",
        "print_connect_title": "🖨️ 2. 網路連線廠區 3D 列印機",
        "select_printer_label": "選擇列印打樣廠區",
        "btn_send_printer": "🚀 即時發送 G-Code 至 3D 列印機啟動打樣",
        "section_quote": "📄 階段五：產出正式業務預估報價單與下載",
        "btn_gen_quote": "🚀 生成正式預估報價單與下載檔",
        "btn_download_quote": "📥 點擊下載正式業務預估報價單 (.txt / .doc)",
        "overview_title": "📊 全產業報價紀錄與客戶資料庫",
        "overview_caption": "即時追蹤不同產業客戶提交之 AI 自動報價單、規格評估與模具開發預算。"
    },
    "Tiếng Việt": {
        "page_title": "💼 Kinh Doanh / Marketing — Hệ thống Báo giá & CAD/3D Pipeline",
        "sub_title": "💼 Báo Giá AI Thời Gian Thực & Tự Động Hóa 2D/3D/Nano Banana AI",
        "sub_caption": "Nhập mô tả sản phẩm bất kỳ, AI sẽ tự động hiểu ngữ nghĩa và tạo bản vẽ 2D CAD, phối cảnh 3D và ảnh thực tế Nano Banana.",
        "section_input": "📝 1. Yêu cầu & Thông số kỹ thuật của khách hàng",
        "input_label": "Nhập mô tả sản phẩm (Bấm nút đỏ hoặc nhấn Enter sau khi nhập):",
        "input_default": "Động cơ mô-tơ cánh quạt Drone",
        "btn_submit": "🚀 Gửi phân tích AI & Tự động vẽ (Enter)",
        "section_ai_parse": "💡 Phân Tích Thông Số Kỹ Thuật AI Gemini",
        "label_prod_type": "Loại sản phẩm nhận diện",
        "label_material": "Vật liệu đề xuất",
        "label_dimensions": "Kích thước chính xác",
        "label_volume": "Thể tích ước tính",
        "label_clamp_ton": "Lực kẹp máy đề xuất",
        "section_preview": "🎨 2. Hiển Thị 2D CAD, 3D Render & Ảnh Thực Tế Nano Banana AI",
        "tab_2d": "📐 Giai đoạn 1: Bản vẽ 2D CAD",
        "tab_3d": "🎨 Giai đoạn 2: Phối cảnh 3D",
        "tab_banana": "🍌 Giai đoạn 3: Ảnh thực tế Nano Banana AI",
        "banana_heading": "🍌 Tạo Ảnh Sản Phẩm Thực Tế Nano Banana AI",
        "btn_gen_banana": "🚀 Gọi Nano Banana AI để tạo ảnh thực tế",
        "banana_toast": "Nano Banana AI đang xử lý ảnh thực tế 8K...",
        "banana_success": "🎉 Đã tạo thành công ảnh sản phẩm thực tế 8K!",
        "section_3dprint": "🖨️ Giai đoạn 4: Tạo mẫu nhanh — Kết nối máy in 3D",
        "section_3dprint_caption": "Tự động xuất mô hình 3D sang tệp .STL và gửi lệnh trực tiếp đến máy in 3D nhà máy:",
        "download_stl_title": "📥 1. Xuất tệp CAD in 3D (.STL)",
        "btn_download_stl": "📥 Tải tệp mô hình 3D (.STL)",
        "print_connect_title": "🖨️ 2. Kết nối máy in 3D nhà máy",
        "select_printer_label": "Chọn khu vực máy in 3D",
        "btn_send_printer": "🚀 Gửi G-Code đến máy in 3D để bắt đầu",
        "section_quote": "📄 Giai đoạn 5: Xuất Báo Giá Bảng Dự Toán Chính Thức",
        "btn_gen_quote": "🚀 Tạo bảng báo giá chính thức & tệp tải về",
        "btn_download_quote": "📥 Tải bảng báo giá chính thức (.txt / .doc)",
        "overview_title": "📊 Quản Lý Lịch Sử Báo Giá & CSDL Khách Hàng",
        "overview_caption": "Theo dõi thời gian thực các báo giá AI, đánh giá thông số và ngân sách phát triển khuôn."
    },
    "English": {
        "page_title": "💼 Sales & Marketing — Quotation & CAD/3D Pipeline System",
        "sub_title": "💼 Multi-Industry AI Instant Quotation & 2D/3D/Nano Banana AI Automation",
        "sub_caption": "Enter any product description; AI automatically understands semantics and generates 2D CAD, 3D renders, and Nano Banana photos.",
        "section_input": "📝 1. Customer Requirements & Specs",
        "input_label": "Enter product description (Click red button or press Enter):",
        "input_default": "Drone propeller brushless motor housing",
        "btn_submit": "🚀 Submit AI Analysis & Auto-Drawing (Enter)",
        "section_ai_parse": "💡 Gemini AI Specs Analysis",
        "label_prod_type": "Identified Product Type",
        "label_material": "Recommended Material",
        "label_dimensions": "Calculated Dimensions",
        "label_volume": "Estimated Volume",
        "label_clamp_ton": "Recommended Clamping Force",
        "section_preview": "🎨 2. 2D CAD, 3D Render & Nano Banana AI Photo Display",
        "tab_2d": "📐 Stage 1: 2D CAD Geometry",
        "tab_3d": "🎨 Stage 2: 3D Isometric View",
        "tab_banana": "🍌 Stage 3: Nano Banana AI Photo",
        "banana_heading": "🍌 Nano Banana AI Photorealistic Rendering",
        "btn_gen_banana": "🚀 Call Nano Banana AI to Generate Photo",
        "banana_toast": "Nano Banana AI is rendering 8K photos...",
        "banana_success": "🎉 Successfully generated 8K photorealistic photo!",
        "section_3dprint": "🖨️ Stage 4: Rapid Prototyping — 3D Printer Connection",
        "section_3dprint_caption": "Export 3D models to standard .STL and send G-Code commands directly to factory 3D printers:",
        "download_stl_title": "📥 1. Export 3D Printing File (.STL)",
        "btn_download_stl": "📥 Download 3D Model File (.STL)",
        "print_connect_title": "🖨️ 2. Connect Factory 3D Printers",
        "select_printer_label": "Select Prototyping Site",
        "btn_send_printer": "🚀 Send G-Code to 3D Printer",
        "section_quote": "📄 Stage 5: Official Quotation Generation",
        "btn_gen_quote": "🚀 Generate Official Quotation Document",
        "btn_download_quote": "📥 Download Official Quotation (.txt / .doc)",
        "overview_title": "📊 Quotation History & Customer Database",
        "overview_caption": "Track AI quotations, specification evaluations, and tooling budgets across industries in real time."
    }
}

def get_sales_lang_dict():
    """獲取當前語言字典，預設繁體中文"""
    lang = st.session_state.get("lang", "繁體中文")
    return SALES_I18N.get(lang, SALES_I18N["繁體中文"])

def parse_dimensions_and_type(prompt_text):
    """精準動態解析尺寸與全產業產品類型"""
    nums = re.findall(r'\d+(?:\.\d+)?', prompt_text)
    
    length = 12.0
    width = 12.0
    height = 5.0 # 單位: cm
    
    if len(nums) >= 3:
        length = float(nums[0])
        width = float(nums[1])
        height = float(nums[2])
    elif len(nums) == 2:
        length = float(nums[0])
        width = float(nums[1])

    if any(k in prompt_text.lower() for k in ["馬達", "螺旋槳", "無人機", "motor", "propeller", "drone", "động cơ", "cánh quạt"]):
        category = "motor"
        prod_type = "🛸 無人機螺旋槳 / 無刷馬達外殼 (Drone Motor & Propeller)"
        material = "航太鋁合金 (AL6061) / 碳纖維 / PC 工程塑膠"
        clamp_ton = math.ceil((length * width) * 0.15)
    elif any(k in prompt_text.lower() for k in ["盒", "箱", "box", "case", "hộp"]):
        category = "box"
        prod_type = "📦 塑膠射出收納盒 / 外殼 (Plastic Box / Case)"
        material = "PP / ABS / PC 工程塑膠"
        clamp_ton = math.ceil((length * width) * 0.18)
    elif any(k in prompt_text.lower() for k in ["鞋", "底", "橡膠", "sole", "đế giày"]):
        category = "outsole"
        prod_type = "👟 橡膠大底 / 鞋底 (Rubber Outsole Only)"
        material = "天然橡膠 (NR) / 合成橡膠 (SBR/EVA)"
        clamp_ton = math.ceil((length * width) * 0.15)
    else:
        category = "general"
        prod_type = "⚙️ 精密工業成型件 (Precision Industrial Part)"
        material = "PP / ABS / PC / POM / 鋁合金"
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
        "clamp_ton": max(clamp_ton, 80)
    }

def draw_2d_cad(spec):
    """根據產品類別動態繪製 2D CAD 設計圖"""
    category = spec.get("category", "general")
    length, width, height = spec['length'], spec['width'], spec['height']
    
    if category == "motor":
        return f"""
        <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center;">
            <svg width="280" height="340" viewBox="0 0 280 340" xmlns="http://www.w3.org/2000/svg">
                <rect width="280" height="340" fill="#0f172a" rx="8"/>
                <circle cx="140" cy="140" r="45" fill="#1e293b" stroke="#38bdf8" stroke-width="3"/>
                <circle cx="140" cy="140" r="15" fill="#0284c7" stroke="#eab308" stroke-width="2"/>
                <path d="M 140,125 C 160,70 180,40 140,20 C 120,40 130,70 140,125 Z" fill="#0369a1" stroke="#38bdf8" stroke-width="2"/>
                <path d="M 152,148 C 195,180 230,200 240,160 C 215,140 180,145 152,148 Z" fill="#0369a1" stroke="#38bdf8" stroke-width="2"/>
                <path d="M 128,148 C 85,180 50,200 40,160 C 65,140 100,145 128,148 Z" fill="#0369a1" stroke="#38bdf8" stroke-width="2"/>
                <line x1="20" y1="20" x2="20" y2="260" stroke="#38bdf8" stroke-width="1" stroke-dasharray="3"/>
                <text x="12" y="150" fill="#38bdf8" font-size="11" font-weight="bold" transform="rotate(-90,12,150)">Dia {length} cm</text>
                <text x="140" y="310" fill="#fef08a" font-size="12" text-anchor="middle" font-weight="bold">🛸 2D Motor & Propeller CAD</text>
            </svg>
        </div>
        """
    else:
        return f"""
        <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center;">
            <svg width="280" height="340" viewBox="0 0 280 340" xmlns="http://www.w3.org/2000/svg">
                <rect width="280" height="340" fill="#0f172a" rx="8"/>
                <rect x="40" y="50" width="200" height="150" fill="#1e293b" stroke="#38bdf8" stroke-width="3" rx="10"/>
                <text x="140" y="310" fill="#fef08a" font-size="12" text-anchor="middle" font-weight="bold">📦 2D Part Structure CAD</text>
            </svg>
        </div>
        """

def draw_3d_render(spec):
    """根據產品類別動態繪製 3D 立體渲染圖"""
    category = spec.get("category", "general")
    if category == "motor":
        return f"""
        <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center;">
            <svg width="280" height="340" viewBox="0 0 280 340" xmlns="http://www.w3.org/2000/svg">
                <rect width="280" height="340" fill="#0f172a" rx="8"/>
                <g transform="translate(40, 60)">
                    <ellipse cx="100" cy="50" rx="70" ry="25" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
                    <path d="M 30,50 L 30,130 A 70 25 0 0 0 170 130 L 170,50 Z" fill="#0369a1" stroke="#38bdf8" stroke-width="2"/>
                    <ellipse cx="100" cy="50" rx="25" ry="10" fill="#eab308"/>
                    <path d="M 100,50 C 130,10 170,-10 180,20 Z" fill="#7dd3fc" opacity="0.9"/>
                </g>
                <text x="140" y="300" fill="#38bdf8" font-size="12" text-anchor="middle" font-weight="bold">🛸 3D Motor Render</text>
            </svg>
        </div>
        """
    else:
        return f"""
        <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center;">
            <svg width="280" height="340" viewBox="0 0 280 340" xmlns="http://www.w3.org/2000/svg">
                <rect width="280" height="340" fill="#0f172a" rx="8"/>
                <g transform="translate(40, 70)">
                    <polygon points="60,20 180,20 140,60 20,60" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
                    <polygon points="20,60 140,60 140,160 20,160" fill="#0369a1" stroke="#38bdf8" stroke-width="2"/>
                </g>
                <text x="140" y="300" fill="#38bdf8" font-size="12" text-anchor="middle" font-weight="bold">🎨 3D Isometric View</text>
            </svg>
        </div>
        """

def get_nano_banana_photo_url(spec):
    category = spec.get("category", "general")
    if category == "motor":
        return "https://images.unsplash.com/photo-1527977966376-1c8408f9f108?w=800&auto=format&fit=crop&q=80"
    elif category == "box":
        return "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&auto=format&fit=crop&q=80"
    else:
        return "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800&auto=format&fit=crop&q=80"

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
    L = get_sales_lang_dict()
    st.subheader(L["overview_title"])
    st.caption(L["overview_caption"])
    
    if "quotation_db" not in st.session_state:
        st.session_state.quotation_db = [
            {"id": "QT-2026-001", "sales": "Alex Chen", "customer": "Drone Tech Corp", "product": "Drone Motor Housing", "material": "AL6061 Aluminum", "price_usd": 18.50, "status": "🟢 Quoted"},
            {"id": "QT-2026-002", "sales": "David Wang", "customer": "Plastic Box Co.", "product": "Storage Box 10*5*10", "material": "PP Plastic", "price_usd": 1.25, "status": "🟡 Reviewing"}
        ]

    for q in st.session_state.quotation_db:
        st.info(f"📄 **[{q['id']}] {q['customer']}** — Sales: {q['sales']} | Unit Price: `${q['price_usd']} USD` ({q['status']})")
        st.write(f"• **Product**: {q['product']} | **Material**: {q['material']}")

def render_sales_frontend():
    L = get_sales_lang_dict()
    st.subheader(L["sub_title"])
    st.caption(L["sub_caption"])

    col_input, col_preview = st.columns([1, 1])

    with col_input:
        st.markdown(f"#### {L['section_input']}")
        
        user_prompt = st.text_input(
            L["input_label"],
            value=st.session_state.get("last_sales_prompt", L["input_default"]),
            key="input_sales_prompt_single"
        )
        
        if st.button(L["btn_submit"], type="primary", key="btn_submit_prompt"):
            st.session_state["last_sales_prompt"] = user_prompt
            st.rerun()

        spec = parse_dimensions_and_type(user_prompt)

        st.markdown(f"#### {L['section_ai_parse']}")
        st.success(f"**{L['label_prod_type']}**: {spec['prod_type']}")
        st.write(f"• **{L['label_material']}**: `{spec['material']}`")
        st.write(f"• **{L['label_dimensions']}**: `{spec['length']} cm × {spec['width']} cm × {spec['height']} cm`")
        st.write(f"• **{L['label_volume']}**: `{spec['volume_cm3']} cm³`")
        st.write(f"• **{L['label_clamp_ton']}**: `{spec['clamp_ton']} T`")

    with col_preview:
        st.markdown(f"#### {L['section_preview']}")
        
        tab_2d, tab_3d, tab_banana = st.tabs([L["tab_2d"], L["tab_3d"], L["tab_banana"]])
        
        with tab_2d:
            st.components.v1.html(draw_2d_cad(spec), height=360)
            
        with tab_3d:
            st.components.v1.html(draw_3d_render(spec), height=360)

        with tab_banana:
            st.markdown(f"##### {L['banana_heading']}")
            
            if st.button(L["btn_gen_banana"], type="primary", key="btn_gen_banana_photo"):
                with st.spinner(L["banana_toast"]):
                    st.success(L["banana_success"])
            
            photo_url = get_nano_banana_photo_url(spec)
            st.image(photo_url, caption=f"🍌 Nano Banana AI ({spec['prod_type']})")

    st.divider()

    # ----------------------------------------------------
    # 🖨️ 階段四：3D 列印機即時串接與模型匯出
    # ----------------------------------------------------
    st.markdown(f"### {L['section_3dprint']}")
    st.caption(L["section_3dprint_caption"])
    
    col_print1, col_print2 = st.columns([1, 1])
    
    with col_print1:
        st.markdown(f"#### {L['download_stl_title']}")
        stl_data = generate_mock_stl_content(spec)
        st.download_button(
            label=L["btn_download_stl"],
            data=stl_data,
            file_name=f"Part_{spec['category']}_{spec['length']}x{spec['width']}x{spec['height']}.stl",
            mime="model/stl",
            type="primary",
            key="btn_download_stl"
        )

    with col_print2:
        st.markdown(f"#### {L['print_connect_title']}")
        printer_site = st.selectbox(L["select_printer_label"], ["🇻🇳 Binh Duong Factory Prototyping Room", "🇹🇼 Taiwan HQ R&D Center", "🇨🇳 Dongguan Plant Engineering Dept"], key="select_3d_printer")
        if st.button(L["btn_send_printer"], key="btn_send_3d_printer"):
            st.success(f"✅ G-Code sent to [{printer_site}] for [{spec['prod_type']}]!")

    st.divider()

    # ----------------------------------------------------
    # 階段五：生成正式報價單
    # ----------------------------------------------------
    st.markdown(f"### {L['section_quote']}")
    if st.button(L["btn_gen_quote"], type="primary", key="btn_gen_quote_doc"):
        quote_content = f"""==================================================
        GLOBAL MANUFACTURING CORP.
        PRELIMINARY QUOTATION
==================================================

Date: 2026-03-24
Customer Requirement: {user_prompt}
Product Type: {spec['prod_type']}
Calculated Specs: {spec['length']} cm (L) × {spec['width']} cm (W) × {spec['height']} cm (H)
Recommended Material: {spec['material']}
Recommended Equipment: {spec['clamp_ton']} T Molding Machine
Nano Banana AI Photo: Generated
3D Printing Prototype: Exported (.STL)

--------------------------------------------------
💰 Cost & Pricing Breakdown:
--------------------------------------------------
1. Tooling / Mold Development: $8,500.00 USD
2. Estimated Unit Price: $18.50 USD / PC (MOQ 500 PCS)
3. Lead Time: 25 Days
=================================================="""

        st.code(quote_content, language="markdown")
        st.download_button(
            label=L["btn_download_quote"],
            data=quote_content,
            file_name=f"Quotation_{spec['category']}_{spec['length']}x{spec['width']}x{spec['height']}.txt",
            mime="text/plain",
            type="primary",
            key="btn_download_quote_file"
        )

def render_sales_quotation_page(sub_option=None):
    L = get_sales_lang_dict()
    st.title(L["page_title"])
    if sub_option and any(k in str(sub_option).lower() for k in ["歷史", "lịch sử", "history"]):
        render_sales_overview()
    else:
        render_sales_frontend()

def show(sub_option=None):
    render_sales_quotation_page(sub_option)

def main(sub_option=None):
    render_sales_quotation_page(sub_option)
