import datetime
import pandas as pd
import streamlit as st

def render_employee_management():
    st.subheader("📋 越南廠人事檔案與職位管理")
    st.caption("維護員工個人資料、職位、合規日期（入職/簽約/離職）、醫療保險與每月固定保險額 (10.5%)。")

    if "employee_db" not in st.session_state:
        st.session_state.employee_db = [
            {
                "emp_id": "VN-001", "name": "Nguyễn Văn A", "position": "射出機技術員 (Kỹ thuật viên)",
                "cccd": "038095001234", "phone": "0912345678", "temp_address": "Bình Dương",
                "perm_address": "Sóc Trăng", "hospital_name": "Bệnh viện Đa khoa Tỉnh Bình Dương",
                "hospital_address": "Bình Dương", "join_date": "2024-03-01", "contract_date": "2024-03-05",
                "leave_date": "-", "base_salary": 9000000.0, "meal_allowance": 730000.0,
                "fuel_allowance": 500000.0, "phone_allowance": 300000.0,
            }
        ]

    with st.expander("➕ 新增員工個人檔案 (Add Employee Profile)", expanded=True):
        with st.form("add_static_emp_form"):
            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1:
                emp_id = st.text_input("員工編號 (Mã NV)", f"VN-{len(st.session_state.employee_db)+1:03d}")
                emp_name = st.text_input("員工全名 (Họ và Tên)", "Trần Thị B")
                emp_position = st.text_input("職位名稱 (Chức vụ)", "射出機技術員")
                emp_cccd = st.text_input("身份證字號 (Số CCCD)", "038095009999")
                emp_phone = st.text_input("聯絡電話", "0987654321")
            with col_e2:
                emp_join_date = st.date_input("入職日期 (Ngày vào làm)", datetime.date(2024, 3, 1))
                emp_contract_date = st.date_input("合約簽署日期 (Ngày ký HĐLĐ)", datetime.date(2024, 3, 5))
                emp_leave_date_str = st.text_input("離職日期 (若仍在庫請填 -)", "-")
            with col_e3:
                emp_temp_addr = st.text_input("暫住地址", "Thuận An, Bình Dương")
                emp_perm_addr = st.text_input("戶籍地址", "Tiền Giang")
                emp_hosp_name = st.text_input("保險就醫醫院", "Bệnh viện Quốc tế Hạnh Phúc")
                emp_hosp_addr = st.text_input("醫院地址", "Thuận An, Bình Dương")

            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1: base_sal = st.number_input("本薪 / 保險底薪 (VND)", min_value=0.0, value=8500000.0, step=100000.0)
            with col_s2: meal_allow = st.number_input("餐費補助", min_value=0.0, value=730000.0)
            with col_s3: fuel_allow = st.number_input("油費補助", min_value=0.0, value=500000.0)
            with col_s4: phone_allow = st.number_input("電話補助", min_value=0.0, value=300000.0)

            if st.form_submit_button("✅ 儲存員工人事檔案", type="primary"):
                st.session_state.employee_db.append({
                    "emp_id": emp_id, "name": emp_name, "position": emp_position, "cccd": emp_cccd,
                    "phone": emp_phone, "temp_address": emp_temp_addr, "perm_address": emp_perm_addr,
                    "hospital_name": emp_hosp_name, "hospital_address": emp_hosp_addr,
                    "join_date": str(emp_join_date), "contract_date": str(emp_contract_date),
                    "leave_date": emp_leave_date_str, "base_salary": base_sal,
                    "meal_allowance": meal_allow, "fuel_allowance": fuel_allow, "phone_allowance": phone_allow,
                })
                st.success(f"🎉 員工 `{emp_name}` 人事檔案已建立！")
                st.rerun()

    st.divider()
    if st.session_state.employee_db:
        static_list = []
        for emp in st.session_state.employee_db:
            ins_deduct = emp["base_salary"] * 0.105
            static_list.append({
                "工號": emp["emp_id"], "姓名": emp["name"], "職位": emp.get("position", "員工"),
                "CCCD": emp["cccd"], "電話": emp["phone"], "本薪 (VND)": f"{emp['base_salary']:,.0f}",
                "每月固定保險自付 (10.5%)": f"-{ins_deduct:,.0f}"
            })
        st.dataframe(pd.DataFrame(static_list), use_container_width=True)
