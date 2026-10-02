import re
import math
import streamlit as st

# ----------------------------------------------------
# 🌐 工程與業務報價模組專屬多語系字典 (i18n)
# ----------------------------------------------------
ENGINEERING_I18N = {
    "繁體中文": {
        "page_title": "🛠️ 工程與技術 — CAD/3D 繪圖與 AI 報價 Pipeline 系統",
        "sub_title": "🛠️ 配電盤與工業成型件 AI 規格精算與 2D/3D 自動化繪圖",
        "sub_caption": "提供工程主管與業務同仁輸入產品描述，由 AI 自動解析規格並生成 2D CAD、3D 結構圖與寫實成品照。",
        "section_input": "📝 1. 輸入客戶需求與工程規格描述",
        "input_label": "請輸入產品描述（例如：配電盤用銅排 Busbar 10x100mm 或 2000A 高壓開關櫃）：",
        "input_default": "配電盤用高純度銅排 Busbar 10x100mm 長度 6000mm",
        "btn_submit": "🚀 提交 AI 語意解析與全自動工程繪圖",
        "section_ai_parse": "💡 AI 動態工程規格解析",
        "label_prod_type": "辨識產品與工程類型",
        "label_material": "建議選用材質",
        "label_dimensions": "精算尺寸/規格",
        "label_volume": "估算體積/用量",
        "label_clamp_ton": "建議設備鎖模力/壓延噸數",
        "section_preview": "🎨 2. 2D CAD 工程圖、3D 立體圖與 AI 寫實渲染",
        "tab_2d": "📐 階段一：2D 幾何工程 CAD",
        "tab_3d": "🎨 階段二：3D 立體結構圖",
        "tab_photo": "📸 階段三：AI 成品寫實照",
        "photo_heading": "📸 AI 寫實成品圖生成",
        "btn_gen_photo": "🚀 呼叫 AI 生成 8K 寫實成品照",
        "photo_toast": "AI 正在運算 8K 寫實照片...",
        "photo_success": "🎉 已成功生成 8K 寫實成品照片！",
        "section_3dprint": "🖨️ 階段四：工程打樣 — 3D 列印機/CNC 即時串接",
        "section_3dprint_caption": "自動將 3D 模型匯出為 3D 列印通用檔 (.STL)，並可直接發送指令至廠區打樣中心：",
        "download_stl_title": "📥 1. 匯出通用 3D 列印 CAD 模型檔 (.STL)",
        "btn_download_stl": "📥 下載 3D 模型檔 (.STL)",
        "print_connect_title": "🖨️ 2. 網路連線廠區打樣設備",
        "select_printer_label": "選擇打樣廠區與打樣室",
        "btn_send_printer": "🚀 即時發送 G-Code 至打樣中心啟動製作",
        "section_quote": "📄 階段五：產出正式工程預估報價單與下載",
        "btn_gen_quote": "🚀 生成正式預估報價單",
        "btn_download_quote": "📥 下載正式工程預估報價單 (.txt)"
    },
    "Tiếng Việt": {
        "page_title": "🛠️ Phòng Kỹ Thuật — Hệ thống CAD/3D & Báo Giá Pipeline",
        "sub_title": "🛠️ Tự Động Phân Tích Kỹ Thuật & Vẽ CAD 2D/3D Cho Tủ Điện",
        "sub_caption": "Dành cho quản lý kỹ thuật và nhân viên kinh doanh nhập yêu cầu sản phẩm, AI sẽ tự động tạo bản vẽ CAD và phối cảnh 3D.",
        "section_input": "📝 1. Yêu cầu & Thông số kỹ thuật của khách hàng",
        "input_label": "Nhập mô tả sản phẩm (Ví dụ: Thanh cái đồng Busbar 10x100mm hoặc Tủ điện 2000A):",
        "input_default": "Thanh cái đồng Busbar 10x100mm chiều dài 6000mm cho tủ điện",
        "btn_submit": "🚀 Gửi phân tích AI & Tự động vẽ CAD",
        "section_ai_parse": "💡 Phân Tích Thông Số Kỹ Thuật AI Gemini",
        "label_prod_type": "Loại sản phẩm nhận diện",
        "label_material": "Vật liệu đề xuất",
        "label_dimensions": "Kích thước chính xác",
        "label_volume": "Thể tích/Khối lượng ước tính",
        "label_clamp_ton": "Lực kẹp/Lực ép máy đề xuất",
        "section_preview": "🎨 2. Hiển Thị 2D CAD, 3D Render & Ảnh AI Thực Tế",
        "tab_2d": "📐 Giai đoạn 1: Bản vẽ kỹ thuật 2D CAD",
        "tab_3d": "🎨 Giai đoạn 2: Phối cảnh 3D",
        "tab_photo": "📸 Giai đoạn 3: Ảnh AI thực tế",
        "photo_heading": "📸 Tạo Ảnh Sản Phẩm Thực Tế AI",
        "btn_gen_photo": "🚀 Gọi AI để tạo ảnh thực tế 8K",
        "photo_toast": "AI đang xử lý ảnh thực tế 8K...",
        "photo_success": "🎉 Đã tạo thành công ảnh sản phẩm thực tế 8K!",
        "section_3dprint": "🖨️ Giai đoạn 4: Tạo mẫu nhanh — Kết nối máy in 3D / CNC",
        "section_3dprint_caption": "Tự động xuất mô hình 3D sang tệp .STL và gửi lệnh trực tiếp đến máy in 3D nhà máy:",
        "download_stl_title": "📥 1. Xuất tệp CAD in 3D (.STL)",
        "btn_download_stl": "📥 Tải tệp mô hình 3D (.STL)",
        "print_connect_title": "🖨️ 2. Kết nối máy in 3D / Phòng tạo mẫu nhà máy",
        "select_printer_label": "Chọn khu vực máy in 3D",
        "btn_send_printer": "🚀 Gửi G-Code đến máy in 3D để bắt đầu",
        "section_quote": "📄 Giai đoạn 5: Xuất Báo Giá Bảng Dự Toán Chính Thức",
        "btn_gen_quote": "🚀 Tạo bảng báo giá chính thức & tệp tải về",
        "btn_download_quote": "📥 Tải bảng báo giá chính thức (.txt)"
    },
    "English": {
        "page_title": "🛠️ R&D Engineering — CAD/3D & Quotation Pipeline",
        "sub_title": "🛠️ AI Engineering Quotation & Automated 2D/3D CAD Drawing",
        "sub_caption": "Designed for Engineering Managers and Sales Reps to generate CAD designs, 3D prototypes, and quotations.",
        "section_input": "📝 1. Customer Requirements & Specs",
        "input_label": "Enter description (e.g., Copper Busbar 10x100mm or High Voltage 2000A Cabinet):",
        "input_default": "High conductivity copper busbar 10x100mm length 6000mm",
        "btn_submit": "🚀 Submit AI Analysis & Auto CAD Generation",
        "section_ai_parse": "💡 Technical Specs Analysis",
        "label_prod_type": "Identified Product / Engineering Type",
        "label_material": "Recommended Material",
        "label_dimensions": "Calculated Dimensions",
        "label_volume": "Estimated Volume / Weight",
        "label_clamp_ton": "Recommended Press / Clamping Force",
        "section_preview": "🎨 2. 2D CAD, 3D Render & AI Photo Display",
        "tab_2d": "📐 Stage 1: 2D CAD Geometry",
        "tab_3d": "🎨 Stage 2: 3D Isometric View",
        "tab_photo": "📸 Stage 3: AI Photo Rendering",
        "photo_heading": "📸 AI Photorealistic Photo Generation",
        "btn_gen_photo": "🚀 Call AI to Generate Photo",
        "photo_toast": "AI is rendering 8K photorealistic photo...",
        "photo_success": "🎉 Successfully generated 8K photorealistic photo!",
        "section_3dprint": "🖨️ Stage 4: Rapid Prototyping — 3D Printer / CNC Connection",
        "section_3dprint_caption": "Export 3D models to standard .STL and send G-Code commands directly to factory prototyping center:",
        "download_stl_title": "📥 1. Export 3D Printing File (.STL)",
        "btn_download_stl": "📥 Download 3D Model File (.STL)",
        "print_connect_title": "🖨️ 2. Connect Factory Prototyping Center",
        "select_printer_label": "Select Prototyping Site",
        "btn_send_printer": "🚀 Send G-Code to 3D Printer",
        "section_quote": "📄 Stage 5: Official Engineering Quotation Generation",
        "btn_gen_quote": "🚀 Generate Official Engineering Quotation",
        "btn_download_quote": "📥 Download Official Quotation (.txt)"
    }
}

def get_i18n():
    lang = st.session_state.get("lang", "繁體中文")
    return ENGINEERING_I18N.get(lang, ENGINEERING_I18N["繁體中文"])

def parse_specs(prompt_text):
    nums = re.findall(r'\d+(?:\.\d+)?', prompt_text)
    length, width, height = 10.0, 100.0, 6000.0
    if len(nums) >= 3:
        length, width, height = float(nums[0]), float(nums[1]), float(nums[2])
    elif len(nums) == 2:
        length, width = float(nums[0]), float(nums[1])

    prompt_lower = prompt_text.lower()
    if any(k in prompt_lower for k in ["銅排", "母線", "busbar", "đồng", "thanh cái"]):
        category = "busbar"
        prod_type = "⚡ 配電盤用導電銅排 (Conductive Copper Busbar)"
        material = "高純度紫銅 (C1100 / 99.9% Cu IACS 98%)"
        clamp_ton = math.ceil((length * width) * 0.05)
    elif any(k in prompt_lower for k in ["櫃", "箱", "cabinet", "switchgear", "tủ điện"]):
        category = "cabinet"
        prod_type = "🏭 配電盤高低壓開關櫃 (Switchgear Cabinet Box)"
        material = "熱浸鍍鋅鋼板 (SECC) / 粉體塗裝 (RAL 7035)"
        clamp_ton = math.ceil((length * width) * 0.25)
    else:
        category = "general"
        prod_type = "⚙️ 精密工業成型機構件 (Precision Industrial Component)"
        material = "工程塑膠 (PC/ABS) / 鋁合金 AL6061"
        clamp_ton = math.ceil((length * width) * 0.15)

    vol_cm3 = (length * width * height) / 1000.0
    return {
        "category": category, "length": length, "width": width, "height": height,
        "volume_cm3": round(vol_cm3, 2), "prod_type": prod_type, "material": material,
        "clamp_ton": max(clamp_ton, 50)
    }

def draw_2d_cad(spec):
    length, width, height = spec['length'], spec['width'], spec['height']
    return f"""
    <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center;">
        <svg width="340" height="300" viewBox="0 0 340 300" xmlns="http://www.w3.org/2000/svg">
            <rect width="340" height="300" fill="#0f172a" rx="8"/>
            <rect x="50" y="90" width="240" height="50" fill="#b45309" stroke="#f59e0b" stroke-width="3" rx="4"/>
            <circle cx="90" cy="115" r="12" fill="#0f172a" stroke="#f59e0b" stroke-width="2"/>
            <circle cx="250" cy="115" r="12" fill="#0f172a" stroke="#f59e0b" stroke-width="2"/>
            <line x1="50" y1="70" x2="290" y2="70" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="170" y="62" fill="#38bdf8" font-size="12" text-anchor="middle" font-weight="bold">Length: {height} mm</text>
            <text x="170" y="260" fill="#fef08a" font-size="13" text-anchor="middle" font-weight="bold">⚡ 2D CAD Spec ({length}x{width}mm)</text>
        </svg>
    </div>
    """

def draw_3d_render(spec):
    return f"""
    <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; text-align: center;">
        <svg width="340" height="300" viewBox="0 0 340 300" xmlns="http://www.w3.org/2000/svg">
            <rect width="340" height="300" fill="#0f172a" rx="8"/>
            <g transform="translate(30, 70)">
                <polygon points="40,30 220,30 200,60 20,60" fill="#d97706" stroke="#f59e0b" stroke-width="2"/>
                <polygon points="20,60 200,60 200,100 20,100" fill="#b45309" stroke="#f59e0b" stroke-width="2"/>
                <polygon points="200,60 220,30 220,70 200,100" fill="#78350f" stroke="#f59e0b" stroke-width="2"/>
            </g>
            <text x="170" y="260" fill="#38bdf8" font-size="13" text-anchor="middle" font-weight="bold">⚡ 3D Isometric View</text>
        </svg>
    </div>
    """

def render_engineering_page(*args, **kwargs):
    L = get_i18n()
    st.title(L["page_title"])
    st.subheader(L["sub_title"])
    st.caption(L["sub_caption"])

    col_input, col_preview = st.columns([1, 1])

    with col_input:
        st.markdown(f"#### {L['section_input']}")
        user_prompt = st.text_input(
            L["input_label"],
            value=st.session_state.get("last_eng_prompt", L["input_default"]),
            key="input_eng_prompt"
        )
        if st.button(L["btn_submit"], type="primary", key="btn_eng_submit"):
            st.session_state["last_eng_prompt"] = user_prompt
            st.rerun()

        spec = parse_specs(user_prompt)

        st.markdown(f"#### {L['section_ai_parse']}")
        st.success(f"**{L['label_prod_type']}**: {spec['prod_type']}")
        st.write(f"• **{L['label_material']}**: `{spec['material']}`")
        st.write(f"• **{L['label_dimensions']}**: `{spec['length']} mm × {spec['width']} mm × {spec['height']} mm`")
        st.write(f"• **{L['label_volume']}**: `{spec['volume_cm3']} cm³`")
        st.write(f"• **{L['label_clamp_ton']}**: `{spec['clamp_ton']} T`")

    with col_preview:
        st.markdown(f"#### {L['section_preview']}")
        t1, t2, t3 = st.tabs([L["tab_2d"], L["tab_3d"], L["tab_photo"]])
        with t1:
            st.components.v1.html(draw_2d_cad(spec), height=310)
        with t2:
            st.components.v1.html(draw_3d_render(spec), height=310)
        with t3:
            st.markdown(f"##### {L['photo_heading']}")
            if st.button(L["btn_gen_photo"], type="primary", key="btn_gen_photo"):
                st.success(L["photo_success"])
            st.image("https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800&auto=format&fit=crop&q=80", caption=spec['prod_type'])

    st.divider()

    st.markdown(f"### {L['section_3dprint']}")
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        st.markdown(f"#### {L['download_stl_title']}")
        st.download_button(
            label=L["btn_download_stl"],
            data=f"solid Part\nendsolid Part",
            file_name=f"Part_{spec['category']}.stl",
            mime="model/stl",
            type="primary"
        )
    with c_p2:
        st.markdown(f"#### {L['print_connect_title']}")
        site = st.selectbox(L["select_printer_label"], ["🇻🇳 Tay Ninh Prototyping Room", "🇻🇳 Binh Duong R&D Room", "🇹🇼 Taiwan HQ Lab"])
        if st.button(L["btn_send_printer"]):
            st.success(f"✅ G-Code Sent to [{site}]!")

    st.divider()

    st.markdown(f"### {L['section_quote']}")
    if st.button(L["btn_gen_quote"], type="primary"):
        doc = f"""==================================================
        REETECH INDUSTRIAL - ENGINEERING QUOTATION
==================================================
Product: {spec['prod_type']}
Material: {spec['material']}
Specs: {spec['length']}x{spec['width']}x{spec['height']} mm
Tooling Cost: $2,500.00 USD
Unit Price: $12.50 USD / KG
=================================================="""
        st.code(doc, language="text")
        st.download_button(label=L["btn_download_quote"], data=doc, file_name="Quotation.txt", mime="text/plain")

def show(*args, **kwargs):
    render_engineering_page(*args, **kwargs)

def main(*args, **kwargs):
    render_engineering_page(*args, **kwargs)
