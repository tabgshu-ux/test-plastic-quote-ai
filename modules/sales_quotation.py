import streamlit as st
import re
import math
import io

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

def generate_pdf_quotation(user_prompt, spec):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#1e293b"), alignment=1, spaceAfter=10
    )
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor("#0284c7"), spaceBefore=8, spaceAfter=4)
    cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor("#334155"), leading=11)
    cell_bold = ParagraphStyle('CellBold', parent=cell_style, fontName='Helvetica-Bold')

    story.append(Paragraph("<b>GLOBAL INJECTION MOLDING CORP.</b>", title_style))
    story.append(Paragraph("<font size=9 color='#64748b'>Official Preliminary Quotation & Technical Evaluation</font>", ParagraphStyle('SubTitle', alignment=1)))
    story.append(Spacer(1, 10))

    info_data = [
        [Paragraph("Date:", cell_bold), Paragraph("2026-03-24", cell_style), Paragraph("Quotation No:", cell_bold), Paragraph(f"QT-{spec['clamp_ton']}-2026", cell_style)],
        [Paragraph("Customer Req:", cell_bold), Paragraph(f"Rubber Outsole L{spec['length']} W{spec['width']} H{spec['height']}", cell_style), Paragraph("Product Type:", cell_bold), Paragraph(spec['prod_type'], cell_style)],
        [Paragraph("Dimensions:", cell_bold), Paragraph(f"{spec['length']} x {spec['width']} x {spec['height']} cm", cell_style), Paragraph("Volume:", cell_bold), Paragraph(f"{spec['volume_cm3']} cm3", cell_style)],
        [Paragraph("Material:", cell_bold), Paragraph(spec['material'], cell_style), Paragraph("Clamp Force:", cell_bold), Paragraph(f"{spec['clamp_ton']} Tons", cell_style)]
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

    cost_data = [
        [Paragraph("Item Description", cell_bold), Paragraph("Specification / Details", cell_bold), Paragraph("Est. Cost (USD)", cell_bold)],
        [Paragraph("Steel Mold Cost", cell_style), Paragraph("1 Mold / 2 Cavities (CNC Deep Groove Engraving)", cell_style), Paragraph("$7,200.00 USD", cell_style)],
        [Paragraph("Unit Price (MOQ 3,000 Pairs)", cell_style), Paragraph("Rubber Injection / Hot Press Molding", cell_style), Paragraph("$4.85 USD / Pair", cell_style)],
        [Paragraph("Unit Price (MOQ 10,000 Pairs)", cell_style), Paragraph("Volume Discount Price", cell_style), Paragraph("$4.20 USD / Pair", cell_style)]
    ]
    t_cost = Table(cost_data, colWidths=[150, 260, 130])
    t_cost.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0284c7")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_cost)
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
            <text x="100" y="355" fill="#38bdf8" font-size="11" font-weight="bold">寬 {width} cm (厚 {height} cm)</text>
        </svg>
    </div>
    """

def render_sales_overview():
    st.subheader("📊 業務報價總覽與資料庫中心")
    if "quotation_db" not in st.session_state:
        st.session_state.quotation_db = [
            {"id": "QT-2026-001", "sales": "Alex Chen", "customer": "Nike Vietnam", "product": "鞋子橡膠大底 (長40寬25厚3)", "price_usd": 4.85, "status": "🟢 已送出報價"},
            {"id": "QT-2026-002", "sales": "David Wang", "customer": "Adidas Taiwan", "product": "足球鞋中底 EVA", "price_usd": 3.20, "status": "🟡 客戶比價中"}
        ]
    for q in st.session_state.quotation_db:
        st.info(f"📄 **[{q['id']}] {q['customer']}** — 經辦業務: {q['sales']} | 預估單價: `${q['price_usd']} USD` ({q['status']})")

def render_sales_frontend():
    st.subheader("💼 AI 業務即時報價與 2D/3D 設計圖/3D列印串接系統")
    col_input, col_preview = st.columns([1, 1])

    with col_input:
        user_prompt = st.text_area("請輸入產品描述與尺寸細節：", value="我需要鞋子橡膠大底長40寬25厚3,底部用喬丹10的排水方式", height=120)
        spec = parse_dimensions_and_type(user_prompt)
        st.success(f"**產品類型**: {spec['prod_type']}")
        st.write(f"• **建議材質**: `{spec['material']}`")
        st.write(f"• **精算尺寸**: `{spec['length']} cm × {spec['width']} cm × {spec['height']} cm`")

    with col_preview:
        st.components.v1.html(draw_2d_outsole_cad(spec['length'], spec['width'], spec['height']), height=400)

    if st.button("🚀 生成正式 PDF 業務預估報價單", type="primary"):
        pdf_bytes = generate_pdf_quotation(user_prompt, spec)
        st.download_button(label="📥 下載正式商務 PDF 報價單 (.pdf)", data=pdf_bytes, file_name="Quotation.pdf", mime="application/pdf")

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
