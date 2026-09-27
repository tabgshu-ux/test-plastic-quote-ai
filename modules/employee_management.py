import datetime
import pandas as pd
import streamlit as st

# ----------------------------------------------------
# 🌐 跨國匯率與幣別配置
# ----------------------------------------------------
EXCHANGE_RATES = {
    "🇻🇳 越南 (Vietnam)": {"symbol": "₫", "code": "VND", "step": 100000.0, "default_sal": 9000000.0},
    "🇹🇼 台灣 (Taiwan)": {"symbol": "NT$", "code": "TWD", "step": 1000.0, "default_sal": 45000.0},
    "🇨🇳 中國 (China)": {"symbol": "¥", "code": "RMB", "step": 500.0, "default_sal": 8000.0},
    "🇮🇩 印尼 (Indonesia)": {"symbol": "Rp", "code": "IDR", "step": 100000.0, "default_sal": 5000000.0},
    "USD (美金)": {"symbol": "$", "code": "USD", "step": 100.0, "default_sal": 1500.0}
}

def render_employee_management(sub_option="📋 員工人事資料表", lang="繁體中文"):
    current_sub_option = sub_option if sub_option else "📋 員工人事資料表"
    
    st.title("📋 員工人事資料表與跨國檔案管理")
    st.caption("支援多國籍員工資料維護（含姓名、地址、電話、起薪）、各國法定保險/稅務提繳計算，並自動同步請假系統與權限後台。")

    # ----------------------------------------------------
    # 🗄️ 1. 初始化 Session State 資料庫
    # ----------------------------------------------------
    if "employee_db" not in st.session_state:
        st.session_state.employee_db = [
            {
                "emp_id": "VN-001", "name": "Nguyễn Văn A", "country": "🇻🇳 越南 (Vietnam)",
                "dept": "生產一課 (射出)", "position": "射出機技術員", "id_number": "038095001234",
                "phone": "0912345678", "address": "Bình Dương, Việt Nam", "currency": "VND", "base_salary": 9000000.0,
                "insurance_deduction": 945000.0, # 10.5%
                "join_date": "2024-03-01", "extra_info": "醫院: Bệnh viện Bình Dương", "role": "User (一般員工)"
            },
            {
                "emp_id": "TW-001", "name": "陳大明", "country": "🇹🇼 台灣 (Taiwan)",
                "dept": "管理部", "position": "行政專員", "id_number": "A123456789",
                "phone": "0912345678", "address": "台北市信義區忠孝東路四段", "currency": "TWD", "base_salary": 45000.0,
                "insurance_deduction": 2480.0, # 勞健保估算
                "join_date": "2023-01-15", "extra_info": "勞保級距: $45,800 | 健保級距: $45,800", "role": "Supervisor (主管)"
            }
        ]

    if "leave_requests" not in st.session_state:
        st.session_state.leave_requests = []

    if "users_permissions" not in st.session_state:
        st.session_state.users_permissions = {}

    # ----------------------------------------------------
    # 📌 2. 建立 3 大跨國功能頁籤
    # ----------------------------------------------------
    tab_emp, tab_leave, tab_perm = st.tabs([
        "👥 跨國員工檔案管理 (Global Profiles)", 
        "🌴 請假系統 (Leave System)", 
        "🔑 權限系統後台 (Permissions System)"
    ])

    # ====================================================
    # TAB 1: 跨國員工檔案管理
    # ====================================================
    with tab_emp:
        with st.expander("➕ 新增跨國員工個人檔案 (Add International Employee Profile)", expanded=True):
            with st.form("add_global_emp_form"):
                st.markdown("##### 📍 步驟 1：基本資訊與選擇員工國籍/廠區")
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    country = st.selectbox("員工國籍 / 所屬廠區 *", [
                        "🇻🇳 越南 (Vietnam)", 
                        "🇹🇼 台灣 (Taiwan)", 
                        "🇨🇳 中國 (China)", 
                        "🇮🇩 印尼 (Indonesia)"
                    ])
                with col_c2:
                    prefix_map = {"🇻🇳 越南 (Vietnam)": "VN", "🇹🇼 台灣 (Taiwan)": "TW", "🇨🇳 中國 (China)": "CN", "🇮🇩 印尼 (Indonesia)": "ID"}
                    prefix = prefix_map.get(country, "EMP")
                    emp_id = st.text_input("員工編號 (Emp ID) *", f"{prefix}-{len(st.session_state.employee_db)+1:03d}")
                with col_c3:
                    emp_name = st.text_input("員工全名 (Full Name) *", "張小華")

                col_b1, col_b2, col_b3 = st.columns(3)
                with col_b1:
                    dept = st.selectbox("所屬部門", ["生產一課 (射出)", "品質保證部 (QA)", "總務行政部 (GA)", "財務部 (Finance)", "研發部 (R&D)"])
                    phone = st.text_input("聯絡電話 (Phone) *", "0912345678")
                with col_b2:
                    emp_position = st.text_input("職位名稱", "射出工程師")
                    address = st.text_input("居住/戶籍地址 (Address) *", "台北市信義區忠孝東路")
                with col_b3:
                    emp_role = st.selectbox("系統權限角色 (Role)", ["User (一般員工)", "Supervisor (主管)", "Admin (系統管理者)"])

                st.markdown("---")
                st.markdown(f"##### 📋 步驟 2：輸入【{country}】專屬身分、起薪與法定保險資訊")

                id_number = ""
                extra_info = ""
                curr_key = "VND (越南盾)"
                default_sal = 9000000.0
                est_ins_deduction = 0.0

                if "越南" in country:
                    curr_key = "VND (越南盾)"
                    col_vn1, col_vn2, col_vn3 = st.columns(3)
                    with col_vn1:
                        id_number = st.text_input("身份證字號 (Số CCCD)", "038095009999")
                    with col_vn2:
                        join_date = st.date_input("入職/到職日期", datetime.date.today())
                        contract_date = st.date_input("合約簽署日期", datetime.date.today())
                    with col_vn3:
                        hospital = st.text_input("醫保指定醫院 (Bệnh viện)", "Bệnh viện Quốc tế Hạnh Phúc")
                        extra_info = f"就醫醫院: {hospital}"

                    col_sal1, col_sal2, col_sal3 = st.columns(3)
                    with col_sal1:
                        base_sal = st.number_input("約定起薪 / 保險底薪 (VND)", min_value=0.0, value=9000000.0, step=100000.0)
                    with col_sal2:
                        est_ins_deduction = base_sal * 0.105
                        st.number_input("每月社醫失保個人扣繳 (10.5% VND)", value=est_ins_deduction, disabled=True)
                    with col_sal3:
                        allowance = st.number_input("各類津貼總計 (VND)", min_value=0.0, value=1530000.0, step=50000.0)

                elif "台灣" in country:
                    curr_key = "TWD (新台幣)"
                    col_tw1, col_tw2, col_tw3 = st.columns(3)
                    with col_tw1:
                        id_number = st.text_input("身分證字號 (ID Number)", "A123456789")
                    with col_tw2:
                        join_date = st.date_input("到職日期", datetime.date.today())
                        labor_level = st.number_input("勞保投保級距 (TWD)", value=45800)
                    with col_tw3:
                        health_level = st.number_input("健保投保級距 (TWD)", value=45800)
                        pension_rate = st.number_input("勞退個人自提比例 (%)", min_value=0, max_value=6, value=0)
                        # 🟢 純文字格式，完全不使用 \vert{}
                       extra_info = f"勞保級距: ${labor_level:,.0f} | 健保級距: ${health_level:,.0f} | 勞退自提: {pension_rate}%"

                    col_sal1, col_sal2, col_sal3 = st.columns(3)
                    with col_sal1:
                        base_sal = st.number_input("約定起薪 / 月薪 (TWD)", min_value=0.0, value=45000.0, step=1000.0)
                    with col_sal2:
                        est_ins_deduction = 1150.0 + 672.0
                        est_ins_deduction = st.number_input("預估每月勞健保自付額 (TWD)", value=est_ins_deduction)
                    with col_sal3:
                        allowance = st.number_input("伙食津貼/其他 (TWD)", min_value=0.0, value=3000.0)

                elif "中國" in country:
                    curr_key = "RMB (人民幣)"
                    col_cn1, col_cn2, col_cn3 = st.columns(3)
                    with col_cn1:
                        id_number = st.text_input("居民身份證號", "441900199001011234")
                    with col_cn2:
                        join_date = st.date_input("入職日期", datetime.date.today())
                        city = st.text_input("參保城市", "廣東東莞")
                    with col_cn3:
                        housing_fund = st.text_input("住房公積金號碼", "100200300")
                        extra_info = f"參保城市: {city} | 公積金號: {housing_fund}"

                    col_sal1, col_sal2, col_sal3 = st.columns(3)
                    with col_sal1:
                        base_sal = st.number_input("約定起薪 / 基本工資 (RMB)", min_value=0.0, value=8000.0, step=500.0)
                    with col_sal2:
                        est_ins_deduction = base_sal * 0.105
                        est_ins_deduction = st.number_input("預估五險一金個人扣款 (RMB)", value=est_ins_deduction)
                    with col_sal3:
                        allowance = st.number_input("職務津貼 (RMB)", min_value=0.0, value=1000.0)

                else: # 印尼
                    curr_key = "IDR (印尼盾)"
                    col_id1, col_id2, col_id3 = st.columns(3)
                    with col_id1:
                        id_number = st.text_input("NIK 身份證號", "3201012345670001")
                    with col_id2:
                        join_date = st.date_input("入職日期 (Tanggal Masuk)", datetime.date.today())
                        bpjs_tk = st.text_input("BPJS Ketenagakerjaan 號碼", "00012345678")
                    with col_id3:
                        bpjs_kes = st.text_input("BPJS Kesehatan 號碼", "00087654321")
                        extra_info = f"BPJS TK: {bpjs_tk} | BPJS Kes: {bpjs_kes}"

                    col_sal1, col_sal2, col_sal3 = st.columns(3)
                    with col_sal1:
                        base_sal = st.number_input("約定起薪 / 基本工資 (IDR)", min_value=0.0, value=5000000.0, step=100000.0)
                    with col_sal2:
                        est_ins_deduction = base_sal * 0.04
                        st.number_input("BPJS 個人提繳估算 (4% IDR)", value=est_ins_deduction, disabled=True)
                    with col_sal3:
                        allowance = st.number_input("交通/伙食津貼 (IDR)", min_value=0.0, value=1000000.0)

                curr_code = EXCHANGE_RATES[curr_key]["code"]

                if st.form_submit_button("✅ 儲存跨國員工檔案 (同步請假與權限)", type="primary"):
                    if not emp_name or not phone or not address:
                        st.error("❌ 請填寫姓名、電話與地址等必填欄位！")
                    else:
                        st.session_state.employee_db.append({
                            "emp_id": emp_id,
                            "name": emp_name,
                            "country": country,
                            "dept": dept,
                            "position": emp_position,
                            "id_number": id_number,
                            "phone": phone,
                            "address": address,
                            "currency": curr_code,
                            "base_salary": base_sal,
                            "insurance_deduction": est_ins_deduction,
                            "join_date": str(join_date),
                            "extra_info": extra_info,
                            "role": emp_role
                        })

                        st.session_state.users_permissions[emp_id] = {
                            "username": emp_id,
                            "full_name": emp_name,
                            "country": country,
                            "role": emp_role.split()[0],
                            "allowed_modules": ["👥 人事/行政", "🌴 請假系統", "🏢 總務管理"]
                        }

                        st.success(f"🎉 成功建立【{country}】員工 `{emp_name}` ({emp_id})！")
                        st.rerun()

        st.divider()
        st.markdown("#### 📋 全球在職員工資料表 (含姓名、電話、地址與起薪)")
        if st.session_state.employee_db:
            global_list = []
            for emp in st.session_state.employee_db:
                global_list.append({
                    "工號": emp["emp_id"],
                    "姓名": emp["name"],
                    "國籍/廠區": emp["country"],
                    "部門": emp["dept"],
                    "職位": emp["position"],
                    "聯絡電話": emp.get("phone", "-"),
                    "居住地址": emp.get("address", "-"),
                    "身分證號": emp["id_number"],
                    "起薪/保險底薪": f"{emp['base_salary']:,.0f} {emp['currency']}",
                    "預估保險扣減額": f"-{emp['insurance_deduction']:,.0f} {emp['currency']}",
                    "到職日期": emp.get("join_date", "-"),
                    "國籍保險與備註": emp["extra_info"]
                })
            st.dataframe(pd.DataFrame(global_list), use_container_width=True)

    # ====================================================
    # TAB 2: 請假系統
    # ====================================================
    with tab_leave:
        st.subheader("🌴 全球員工請假申請與簽核")
        emp_options = [f"{e['emp_id']} - {e['name']} ({e['country']} / {e['dept']})" for e in st.session_state.employee_db]

        with st.expander("➕ 填寫請假申請單", expanded=True):
            with st.form("form_submit_global_leave"):
                col_l1, col_l2 = st.columns(2)
                with col_l1:
                    selected_emp_str = st.selectbox("選擇請假員工", emp_options if emp_options else ["無員工資料"])
                    leave_type = st.selectbox("假別", ["年假/特休 (Annual Leave)", "病假 (Sick Leave)", "事假 (Personal Leave)", "產假/陪產假", "公假"])
                with col_l2:
                    s_date = st.date_input("開始日期", value=datetime.date.today())
                    e_date = st.date_input("結束日期", value=datetime.date.today())
                
                reason = st.text_input("請假事由 / Lý do / Reason", placeholder="請輸入請假事由...")
                btn_leave = st.form_submit_button("🚀 送出假單並發起簽核", type="primary")

                if btn_leave and selected_emp_str != "無員工資料":
                    emp_code = selected_emp_str.split(" - ")[0]
                    emp_name = selected_emp_str.split(" - ")[1].split(" (")[0]
                    days = (e_date - s_date).days + 1

                    lv_id = f"LV-{datetime.date.today().strftime('%Y%m%d')}-{len(st.session_state.leave_requests)+1:02d}"
                    st.session_state.leave_requests.append({
                        "單號": lv_id,
                        "員工編號": emp_code,
                        "姓名": emp_name,
                        "假別": leave_type,
                        "開始日期": str(s_date),
                        "結束日期": str(e_date),
                        "天數": float(days),
                        "事由": reason,
                        "狀態": "🟡 簽核中"
                    })

                    st.success(f"✅ 假單已送出！單號：{lv_id}，天數：{days}天")
                    st.rerun()

        st.markdown("---")
        st.markdown("#### 📋 歷史請假紀錄")
        st.dataframe(pd.DataFrame(st.session_state.leave_requests), use_container_width=True)

    # ====================================================
    # TAB 3: 權限系統後台
    # ====================================================
    with tab_perm:
        st.subheader("🔑 權限系統後台 — 跨國人員帳號與權限清單")
        
        perm_list = []
        for emp_id, info in st.session_state.users_permissions.items():
            perm_list.append({
                "帳號 / 工號": info["username"],
                "員工姓名": info["full_name"],
                "所屬國籍": info.get("country", "未設定"),
                "權限角色": info["role"],
                "開通模組": ", ".join(info["allowed_modules"])
            })
        st.dataframe(pd.DataFrame(perm_list), use_container_width=True)

def show(sub_option="📋 員工人事資料表", lang="繁體中文"):
    render_employee_management(sub_option, lang)

def main(sub_option="📋 員工人事資料表", lang="繁體中文"):
    render_employee_management(sub_option, lang)
