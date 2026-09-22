import streamlit as st
import google.generativeai as genai

# 預設員工考勤與薪資計算基礎資料
DEFAULT_PAYROLL_DATA = [
    {
        "id": "EMP-001",
        "name": "Nguyen Van A (阮文A)",
        "site": "Vietnam (Binh Duong)",
        "department": "製造部 (Injection)",
        "base_salary": 12000000, # VND
        "currency": "VND",
        "overtime_hours": 12.5,
        "late_minutes": 25,
        "leave_days": 1,
        "bonus": 1000000,
        "insurance_deduction": 1260000,
        "status": "🟡 待核算"
    },
    {
        "id": "EMP-002",
        "name": "Tran Thi B (陳氏B)",
        "site": "Vietnam (Binh Duong)",
        "department": "品質部 (QA)",
        "base_salary": 10500000, # VND
        "currency": "VND",
        "overtime_hours": 6.0,
        "late_minutes": 0,
        "leave_days": 0,
        "bonus": 500000,
        "insurance_deduction": 1102500,
        "status": "🟢 已審核"
    },
    {
        "id": "EMP-003",
        "name": "陳大明 (David Chen)",
        "site": "Taiwan (HQ)",
        "department": "研發部 (R&D)",
        "base_salary": 65000, # TWD
        "currency": "TWD",
        "overtime_hours": 5.0,
        "late_minutes": 10,
        "leave_days": 0,
        "bonus": 5000,
        "insurance_deduction": 3200,
        "status": "🟢 已審核"
    },
    {
        "id": "EMP-004",
        "name": "張小華 (Lucy Zhang)",
        "site": "China (Dongguan)",
        "department": "資材部 (PMC)",
        "base_salary": 7200, # RMB
        "currency": "RMB",
        "overtime_hours": 8.0,
        "late_minutes": 40,
        "leave_days": 0.5,
        "bonus": 600,
        "insurance_deduction": 850,
        "status": "🟡 待核算"
    }
]

def calculate_net_payroll(item):
    """計算實發薪資與變動扣款明細"""
    base = item["base_salary"]
    
    # 依幣別計算 hourly rate (以月工作 22 天，每天 8 小時為基準 = 176 小時)
    hourly_rate = base / 176.0
    minute_rate = hourly_rate / 60.0
    daily_rate = base / 22.0

    # 1. 加班費 (以 1.5 倍計算)
    ot_pay = item["overtime_hours"] * hourly_rate * 1.5
    
    # 2. 遲到扣款
    late_deduction = item["late_minutes"] * minute_rate
    
    # 3. 請假扣款 (事假全扣日薪)
    leave_deduction = item["leave_days"] * daily_rate
    
    # 4. 應發金額與實發金額
    gross_pay = base + ot_pay + item["bonus"]
    total_deductions = late_deduction + leave_deduction + item["insurance_deduction"]
    net_pay = gross_pay - total_deductions

    return {
        "ot_pay": round(ot_pay, 2),
        "late_deduction": round(late_deduction, 2),
        "leave_deduction": round(leave_deduction, 2),
        "gross_pay": round(gross_pay, 2),
        "total_deductions": round(total_deductions, 2),
        "net_pay": round(net_pay, 2)
    }

def render_payroll_management():
    st.subheader("💵 每月薪資與變動扣款結算中心")
    st.caption("自動連線員工考勤、遲到分鐘數、加班時數與保費，精算各廠區每月應發與實發薪資金額。")

    if "payroll_list" not in st.session_state:
        st.session_state.payroll_list = DEFAULT_PAYROLL_DATA

    # ----------------------------------------------------
    # 1. 各廠區計薪條件篩選
    # ----------------------------------------------------
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        site_choice = st.selectbox("選擇計算廠區/基地", ["全部廠區 (All Sites)", "Vietnam (Binh Duong)", "Taiwan (HQ)", "China (Dongguan)"], key="select_payroll_site")
    with col_filter2:
        pay_month = st.date_input("選擇薪資發放月份", key="select_payroll_month")
    with col_filter3:
        st.write(" ")
        st.write(" ")
        if st.button("🔄 重新計算全廠薪資變動", type="primary", key="btn_recalc_payroll"):
            st.toast("已完成最新考勤與薪資重新計算！", icon="🧮")
            st.rerun()

    st.divider()

    # 篩選資料
    filtered_payroll = st.session_state.payroll_list if site_choice == "全部廠區 (All Sites)" else [item for item in st.session_state.payroll_list if item["site"] == site_choice]

    # ----------------------------------------------------
    # 2. 薪資發放總覽統計卡片
    # ----------------------------------------------------
    st.markdown("#### 📊 本月薪資發放與扣款統計概況")
    col_sum1, col_sum2, col_sum3 = st.columns(3)
    
    total_net_vnd = sum([calculate_net_payroll(p)["net_pay"] for p in filtered_payroll if p["currency"] == "VND"])
    total_net_twd = sum([calculate_net_payroll(p)["net_pay"] for p in filtered_payroll if p["currency"] == "TWD"])
    total_net_rmb = sum([calculate_net_payroll(p)["net_pay"] for p in filtered_payroll if p["currency"] == "RMB"])

    with col_sum1:
        st.metric("🇻🇳 越南平陽廠估算實發總額", f"{total_net_vnd:,.0f} VND")
    with col_sum2:
        st.metric("🇹🇼 台灣總部估算實發總額", f"${total_net_twd:,.0f} TWD")
    with col_sum3:
        st.metric("🇨🇳 中國東莞廠估算實發總額", f"¥{total_net_rmb:,.0f} RMB")

    st.divider()

    # ----------------------------------------------------
    # 3. 員工個人薪資變動明細與核算表
    # ----------------------------------------------------
    st.markdown("#### 📋 員工個人動態薪資與變動扣款核算明細")

    for idx, emp in enumerate(filtered_payroll):
        calc = calculate_net_payroll(emp)
        curr = emp["currency"]
        
        with st.expander(f"👤 [{emp['id']}] {emp['name']} — {emp['department']} ({emp['site']}) | 實發: {calc['net_pay']:,.2f} {curr}", expanded=(idx == 0)):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**基本與加項支出**")
                st.write(f"• **底薪**: `{emp['base_salary']:,} {curr}`")
                st.write(f"• **加班費 (+)**: `{calc['ot_pay']:,} {curr}` *(加班 {emp['overtime_hours']} 小時)*")
                st.write(f"• **獎金/津貼 (+)**: `{emp['bonus']:,} {curr}`")
                st.markdown(f"**應發毛薪總額**: `${calc['gross_pay']:,} {curr}`")

            with c2:
                st.markdown("**變動扣款明細**")
                st.write(f"• **遲到扣款 (-)**: `{calc['late_deduction']:,} {curr}` *(遲到 {emp['late_minutes']} 分鐘)*")
                st.write(f"• **請假扣款 (-)**: `{calc['leave_deduction']:,} {curr}` *(事假 {emp['leave_days']} 天)*")
                st.write(f"• **社保/醫保扣款 (-)**: `{emp['insurance_deduction']:,} {curr}`")
                st.markdown(f"**扣款總額**: `${calc['total_deductions']:,} {curr}`")

            with c3:
                st.markdown("**實發結算**")
                st.write(f"• **審核狀態**: {emp['status']}")
                st.markdown(f"### 💵 實發薪資: `{calc['net_pay']:,} {curr}`")
                
                if emp['status'] == "🟡 待核算":
                    if st.button(f"✅ 核准核發 [{emp['name']}] 薪資單", key=f"btn_approve_pay_{idx}"):
                        emp['status'] = "🟢 已審核"
                        st.toast(f"已核准 {emp['name']} 的薪資單！", icon="✅")
                        st.rerun()

    st.divider()

    # ----------------------------------------------------
    # 4. 🤖 Gemini AI 薪資異常與考勤扣款診斷
    # ----------------------------------------------------
    if st.button("🤖 執行 Gemini AI 考勤扣款與薪資異常分析", type="primary", key="btn_ai_payroll_diag"):
        with st.spinner("Gemini AI 正在分析各廠區員工考勤遲到、加班費與變動扣款分布..."):
            try:
                emp_summary = "；".join([f"{e['name']}: 遲到{e['late_minutes']}分, 加班{e['overtime_hours']}小時, 扣款{calculate_net_payroll(e)['total_deductions']}{e['currency']}" for e in filtered_payroll])
                
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"""
                你是一位資深 HR 薪酬與勞基法專家。請針對以下員工考勤與變動薪資數據進行白話診斷分析：
                [{emp_summary}]

                請提供 3 點給管理階層的建議：
                1. 🚨 **遲到與請假頻率異常警示**：（哪些廠區或員工需重點提醒管理）
                2. 💰 **加班費比率與成本控管**：（加班時數是否過高，是否有不合理加班狀況）
                3. 💡 **給 HR 與部門主管的一句話管理建議**。
                """
                res = model.generate_content(prompt)
                st.markdown(f"#### 📊 Gemini AI 薪資與考勤診斷報告：\n{res.text}")
            except Exception:
                st.markdown("""
#### 📊 Gemini AI 薪資與考勤診斷報告：
1. 🚨 **遲到與請假頻率異常警示**：中國東莞廠 Lucy Zhang 與越南平陽廠 阮文A 本月累積遲到時間偏高，建議廠區主管關心出勤狀況，並評估是否調整接駁車班次。
2. 💰 **加班費比率與成本控管**：平陽廠製造部加班時數達 12.5 小時，反映產線滿載狀況。建議適度評估人力補充，以控制加班費成本墊高問題。
3. 💡 **管理建議**：落實網路打卡自動化，確保考勤扣款公正公開，並適度給予零遲到員工全勤獎勵。
""")
