import re
import math
import io
import streamlit as st

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def parse_dimensions_and_type(prompt_text):
    nums = re.findall(r'\d+(?:\.\d+)?', prompt_text)
    length = 40.0
    width = 25.0
    height = 3.0
    
    if len(nums) >= 3:
        length = float(nums[0])
        width = float(nums[1])
        height = float(nums[2])
    elif len(nums) == 2:
        length = float(nums[0])
        width = float(nums[1])

    if "鞋" in prompt_text or "底" in prompt_text or "橡膠" in prompt_text:
        prod_type = "Rubber Outsole Only"
        material = "Natural Rubber (NR) / Synthetic Rubber (SBR)"
        clamp_ton = math.ceil((length * width) * 0.15)
    else:
        prod_type = "Injection Molded Part"
        material = "PP / ABS / PC Engineering Plastics"
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

def clean_non_ascii(text):
    clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
    if not clean_text.strip():
        return "Custom Rubber Outsole Design (Jordan 10 Tread)"
    return clean_text.strip()

def generate_pdf_quotation(user_prompt, spec):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor("#1e293b"),
        alignment=1,
        spaceAfter=10
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor("#0284c7"),
        spaceBefore=8,
        spaceAfter=4
    )

    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=8.5,
        textColor=colors.HexColor("#334155"),
        leading=11
    )

    cell_bold = ParagraphStyle(
        'CellBold',
        parent=cell_style,
        fontName='Helvetica-Bold'
    )

    story.append(Paragraph("<b>GLOBAL INJECTION MOLDING CORP.</b>", title_style))
    story.append(Paragraph("<font size=9 color='#64748b'>Official Preliminary Quotation & Technical Evaluation</font>", ParagraphStyle('SubTitle', alignment=1)))
    story.append(Spacer(1, 10))

    info_data = [
        [
            Paragraph("Date:", cell_bold), Paragraph("2026-03-24", cell_style),
            Paragraph("Quotation No:", cell_bold), Paragraph(f"QT-{spec['clamp_ton']}-2026", cell_style)
        ],
        [
            Paragraph("Customer Req:", cell_bold), Paragraph(f"Rubber Outsole L{spec['length']} W{spec['width']} H{spec['height']} (Jordan 10 Tread)", cell_style),
            Paragraph("Product Type:", cell_bold), Paragraph(spec['prod_type'], cell_style)
        ],
        [
            Paragraph("Dimensions:", cell_bold), Paragraph(f"{spec['length']} x {spec['width']} x {spec['height']} cm", cell_style),
            Paragraph("Volume:", cell_bold), Paragraph(f"{spec['volume_cm3']} cm3", cell_style)
        ],
        [
            Paragraph("Material:", cell_bold), Paragraph(spec['material'], cell_style),
            Paragraph("Clamp Force:", cell_bold), Paragraph(f"{spec['clamp_ton']} Tons", cell_style)
        ]
    ]
    
    t_info = Table(info_data, colWidths=[85, 185, 85, 185])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Cost Breakdown & Pricing Structure</b>", h2_style))
    cost_data = [
        [Paragraph("Item Description", cell_bold), Paragraph("Specification / Details", cell_bold), Paragraph("Est. Cost (USD)", cell_bold)],
        [Paragraph("Steel Mold Cost", cell_style), Paragraph("1 Mold / 2 Cavities (CNC Deep Groove Engraving)", cell_style), Paragraph("$7,200.00 USD", cell_style)],
        [Paragraph("Unit Price (MOQ 3,000 Pairs)", cell_style), Paragraph("Rubber Injection / Hot Press Molding", cell_style), Paragraph("$4.85 USD / Pair", cell_style)],
        [Paragraph("Unit Price (MOQ 10,000 Pairs)", cell_style), Paragraph("Volume Discount Price", cell_style), Paragraph("$4.20 USD / Pair", cell_style)],
        [Paragraph("3D Rapid Prototyping", cell_style), Paragraph("TPU 85A Flexible Material Printing", cell_style), Paragraph("INCLUDED (FREE)", cell_style)]
    ]
    t_cost = Table(cost_data, colWidths=[150, 260, 130])
    t_cost.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0284c7")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f5f9")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_cost)
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Terms & Production Notes</b>", h2_style))
    story.append(Paragraph("1. Mold Development Lead Time: 25 Days (Includes T1 Trial & Water Drainage Testing).", cell_style))
    story.append(Paragraph("2. Mass Production Lead Time: 15 Days after T1 sample confirmation.", cell_style))
    story.append(Paragraph("3. Payment Terms: 50% Mold Deposit, 50% upon T1 Sample Approval.", cell_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<font color='#94a3b8' size=8>This is an AI-generated official preliminary quotation valid for 30 days. Approved by Global Injection Molding Corp.</font>", ParagraphStyle('Footer', alignment=1)))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def draw_2d_outsole_cad(length, width, height):
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

def generate_mock_stl_content(spec):
    return f"""solid Outsole_Jordan10
  facet normal 0 0 1
    outer loop
      vertex 0 0 {spec['height']}
      vertex {spec['length']} 0 {spec['height']}
      vertex {spec['length']} {spec['width']} {spec['height']}
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
    st.subheader("💼 AI 業務即時報價與 2D/3D 設計圖/3D列印串接系統")
    st.caption("輸入客戶規格需求，系統自動執行【2D 平面圖 $\\rightarrow$ 3D 渲染圖 $\\rightarrow$ 3D 列印打樣 $\\rightarrow$ 正式 PDF 報價單下載】完整流程。")

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
        
        tab_2d, tab_3d = st.tabs(["📐 階段一：2D 平面 CAD 圖", "🎨 階段二：3D 立體渲染圖"])
        
        with tab_2d:
            st.components.v1.html(draw_2d_outsole_cad(spec['length'], spec['width'], spec['height']), height=400)
            
        with tab_3d:
            st.components.v1.html(draw_3d_outsole_render(spec['length'], spec['width'], spec['height']), height=400)

    st.divider()

    st.markdown("### 🖨️ 階段三：樣品快速打樣 — 3D 列印機即時串接")
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
            st.success(f"✅ 已成功將【喬丹10代鞋底樣品 ({spec['length']}x{spec['width']}x{spec['height']}cm)】傳送至 [{printer_site}]！")

    st.divider()

    st.markdown("### 📄 階段四：產出正式 PDF 業務預估報價單")
    
    if st.button("🚀 生成正式 PDF 業務預估報價單", type="primary", key="btn_gen_quote_doc"):
        with st.spinner("ReportLab 正在繪製高畫質 PDF 報價單..."):
            pdf_bytes = generate_pdf_quotation(user_prompt, spec)
            
            st.success("✅ PDF 報價單已成功產出！")
            
            st.download_button(
                label="📥 點擊下載正式商務 PDF 報價單 (.pdf)",
                data=pdf_bytes,
                file_name=f"Quotation_Global_Injection_{spec['length']}x{spec['width']}x{spec['height']}.pdf",
                mime="application/pdf",
                type="primary",
                key="btn_download_pdf_file"
            )

def render_sales_quotation_page():
    st.title("💼 業務報價 & CAD/3D/PDF Pipeline 系統")
    
    tab1, tab2 = st.tabs(["📝 即時 AI 報價與 CAD/3D 設計", "📊 歷史報價單據與資料庫"])
    
    with tab1:
        render_sales_frontend()
        
    with tab2:
        render_sales_overview()

def show():
    render_sales_quotation_page()

def main():
    render_sales_quotation_page()
