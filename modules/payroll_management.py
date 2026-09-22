import datetime
import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

def generate_payslip_pdf(pay_record):
    pdf_path = "official_payslip.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    cp = st.session_state.company_profile
    vn_site = cp['sites'].get("Vietnam (Binh Duong)", list(cp['sites'].values())[0])

    story.append(Paragraph(f"<b>{cp['name']} - {vn_site['site_name']}</b>", ParagraphStyle("PTitle", parent=styles["Heading1"], fontSize=13)))
    story.append(Paragraph(f"<b>PHIẾU LƯƠNG HÀNG THÁNG / 每月正式薪資單 ({pay_record['pay_month']})</b>", ParagraphStyle("SubP", fontSize=11, textColor=colors.HexColor("#0284c7"))))
    story.append(Spacer(1, 10))

    pay_table_data = [
        ["Hạng mục / 薪資與扣款項目", "Số tiền / 金額 (VND)"],
        ["Lương cơ bản / 本薪", f"{pay_record['base_salary']:,.0f}"],
        ["Trừ BHXH (10.5%) / 保險自付 (10.5%)", f"-{pay_record['insurance_deduct']:,.0f}"],
        ["LƯƠNG THỰC NHẬN / 當月實領薪資 (NET)", f"{pay_record['net_salary']:,.0f}"]
    ]
    t_ptable = Table(pay_table_data, colWidths=[340, 180])
    t_ptable.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1"))]))
    story.append(t_ptable)
    doc.build(story)
    return pdf_path

def render_payroll_management():
    st.subheader("💵 每月動態薪資發放與變動扣款結算中心")
    if "monthly_payroll_db" not in st.session_state:
        st.session_state.monthly_payroll_db = []

    if st.session_state.get("employee_db"):
        with st.expander("📝 輸入員工【當月變動考勤與借款扣款】", expanded=True):
            with st.form("monthly_payroll_form"):
                pay_month = st.text_input("發薪月份", datetime.date.today().strftime("%Y-%m"))
                emp_sel = st.selectbox("選擇結算員工", [f"{e['emp_id']} - {e['name']}" for e in st.session_state.employee_db])
                tardy_m = st.number_input("當月遲到/早退扣款", value=100000.0)
                leave_m = st.number_input("當月請假扣款", value=300000.0)
                advance_m = st.number_input("當月預支借款扣除", value=1000000.0)

                if st.form_submit_button("✅ 計算並發放此月薪資", type="primary"):
                    target_id = emp_sel.split(" - ")[0]
                    emp_info = next(e for e in st.session_state.employee_db if e["emp_id"] == target_id)
                    ins_105 = emp_info['base_salary'] * 0.105
                    allow_tot = emp_info['meal_allowance'] + emp_info['fuel_allowance'] + emp_info['phone_allowance']
                    net_m = emp_info['base_salary'] + allow_tot - ins_105 - tardy_m - leave_m - advance_m

                    st.session_state.monthly_payroll_db.append({
                        "pay_month": pay_month, "emp_id": emp_info['emp_id'], "emp_name": emp_info['name'],
                        "base_salary": emp_info['base_salary'], "allowance_total": allow_tot,
                        "insurance_deduct": ins_105, "tardy_deduct": tardy_m, "leave_deduct": leave_m,
                        "advance_deduct": advance_m, "net_salary": net_m
                    })
                    st.success(f"🎉 薪資已成功計算！實領薪資: `{net_m:,.0f} VND`")
                    st.rerun()

    if st.session_state.monthly_payroll_db:
        pay_df = pd.DataFrame(st.session_state.monthly_payroll_db)
        st.dataframe(pay_df, use_container_width=True)

# 未來串接網路打卡機 API 的處理邏輯範例
def process_clock_in_data(employee_id, clock_in_time, shift_start_time="08:00:00", grace_minutes=5):
    """
    接受網路打卡機傳入的打卡資料並自動計算遲到時間
    """
    from datetime import datetime
    
    fmt = "%Y-%m-%d %H:%M:%S"
    actual_time = datetime.strptime(clock_in_time, fmt)
    scheduled_time = datetime.strptime(f"{actual_time.strftime('%Y-%m-%d')} {shift_start_time}", fmt)
    
    # 計算時間差（分鐘）
    diff_minutes = (actual_time - scheduled_time).total_seconds() / 60
    
    # 扣除緩衝時間
    late_minutes = max(0, int(diff_minutes - grace_minutes))
    
    return {
        "employee_id": employee_id,
        "clock_in": clock_in_time,
        "is_late": late_minutes > 0,
        "late_minutes": late_minutes,
        "deduction_note": f"遲到 {late_minutes} 分鐘" if late_minutes > 0 else "正常出勤"
    }
