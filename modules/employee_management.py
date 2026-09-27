import datetime
import pandas as pd
import streamlit as st

def render_employee_management():
    st.subheader("📋 越南廠人事檔案與職位管理 (整合請假與權限同步)")
    st.caption("維護員工個人資料、職位、合規日期（入職/簽約/離職）、醫療保險、每月固定保險額 (10.5%)，並自動同步請假與權限系統。")

    # ----------------------------------------------------
    # 🗄️ 1. 初始化 Session State (人事、請假、權限資料庫)
    # ----------------------------------------------------
    # (1) 員工主檔資料庫
    if "employee_db" not in st.session_state:
        st.session_state.employee_db = [
            {
                "emp_id": "VN-001", "name": "Nguyễn Văn A", "position": "射出機技術員 (Kỹ thuật viên)",
                "cccd": "038095001234", "phone": "0912345678", "temp_address": "Bình Dương",
                "perm_address": "Sóc Trăng", "hospital_name": "Bệnh viện Đa khoa Tỉnh Bình Dương",
                "hospital_address": "Bình Dương", "join_date": "2024-03-01", "contract_date": "2024-03-05",
                "leave_date": "-", "base_salary": 9000000.0, "meal_allowance": 730000.0,
                "fuel_allowance": 500000.0, "phone_allowance": 300000.0, "role": "User (一般員工)"
            }
        ]

    # (2) 請假系統紀錄資料庫
    if "leave_requests" not in st.session_state:
        st.session_state.leave_requests = [
            {
                "單號": "LV-20260901-01", "員工編號": "VN-001", "姓名": "Nguyễn Văn A",
                "假別": "年假 (Annual Leave)", "開始日期": "2026-10-01", "結束日期": "2026-10-03",
                "天數": 3.0, "事由": "返鄉探親 (Thăm quê)", "狀態": "🟢 已核准"
            }
        ]

    # (3) 權限系統使用者資料庫
    if "users_permissions" not in st.session_state:
        st.session_state.users_permissions = {
            "VN-001": {
                "username": "VN-001", "full_name": "Nguyễn Văn A",
                "role": "User", "allowed_modules": ["👥 人事管理", "🌴 請假系統", "🏢 總務管理"]
            }
        }

    # ----------------------------------------------------
    # 📌 2. 建立 3 大功能頁籤 (人事檔案 / 請假系統 / 權限後台)
    # ----------------------------------------------------
    tab_emp, tab_leave, tab_perm = st.tabs([
        "👥 員工檔案管理 (Employee Profiles)", 
        "🌴 請假系統 (Leave System)", 
        "🔑 權限系統後台 (Permissions System)"
    ])

    # ====================================================
    # TAB 1: 員工檔案管理與新增 (含自動同步邏輯)
    # ====================================================
    with tab_emp:
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
                    emp_role = st.selectbox("系統權限角色 (Role)", ["User (一般員工)", "Supervisor (主管)", "Admin (系統管理者)"])
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

                # 提交按鈕與同步邏輯
                if st.form_submit_button("✅ 儲存員工人事檔案 (同步請假與權限)", type="primary"):
                    # 1️⃣ 寫入人事主檔
                    st.session_state.employee_db.append({
                        "emp_id": emp_id, "name": emp_name, "position": emp_position, "cccd": emp_cccd,
                        "phone": emp_phone, "temp_address": emp_temp_addr, "perm_address": emp_perm_addr,
                        "hospital_name": emp_hosp_name, "hospital_address": emp_hosp_addr,
                        "join_date": str(emp_join_date), "contract_date": str(emp_contract_date),
                        "leave_date": emp_leave_date_str, "base_salary": base_sal,
                        "meal_allowance": meal_allow, "fuel_allowance": fuel_allow, "phone_allowance": phone_allow,
                        "role": emp_role
                    })

                    # 2️⃣ 同步至「權限系統後台」
                    st.session_state.users_permissions[emp_id] = {
                        "username": emp_id,
                        "full_name": emp_name,
                        "role": emp_role.split()[0],
                        "allowed_modules": ["👥 人事管理", "🌴 請假系統", "🏢 總務管理"]
                    }

                    st.success(f"🎉 員工 `{emp_name}` ({emp_id}) 人事檔案已建立！")
                    st.info("✅ 已自動於【請假系統】開通人員選項，並在【權限系統後台】建立預設登入帳號！")
                    st.rerun()

        st.divider()
        st.markdown("#### 📋 在職員工檔案與固定保險扣額清單")
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

    # ====================================================
    # TAB 2: 請假系統 (連動最新員工清單與簽核)
    # ====================================================
    with tab_leave:
        st.subheader("🌴 員工請假申請與簽核")
        
        # 動態連動所有新增的員工
        emp_options = [f"{e['emp_id']} - {e['name']} ({e.get('position', '員工')})" for e in st.session_state.employee_db]

        with st.expander("➕ 填寫請假申請單", expanded=True):
            with st.form("form_submit_leave_emp"):
                col_l1, col_l2 = st.columns(2)
                with col_l1:
                    selected_emp_str = st.selectbox("選擇請假員工", emp_options if emp_options else ["無員工資料"])
                    leave_type = st.selectbox("假別", ["年假/特休 (Annual Leave)", "病假 (Sick Leave)", "事假 (Personal Leave)", "婚/喪假", "公假"])
                with col_l2:
                    s_date = st.date_input("開始日期", value=datetime.date.today())
                    e_date = st.date_input("結束日期", value=datetime.date.today())
                
                reason = st.text_input("請假事由 / Lý do xin nghỉ", placeholder="例如：個人私事 / 身體不適就醫")
                btn_leave = st.form_submit_button("🚀 送出假單並發起簽核", type="primary")

                if btn_leave and selected_emp_str != "無員工資料":
                    emp_code = selected_emp_str.split(" - ")[0]
                    emp_name = selected_emp_str.split(" - ")[1].split(" (")[0]
                    days = (e_date - s_date).days + 1

                    lv_id = f"LV-{datetime.date.today().strftime('%Y%m%d')}-{len(st.session_state.leave_requests)+1:02d}"
                    new_leave = {
                        "單號": lv_id,
                        "員工編號": emp_code,
                        "姓名": emp_name,
                        "假別": leave_type,
                        "開始日期": str(s_date),
                        "結束日期": str(e_date),
                        "天數": float(days),
                        "事由": reason,
                        "狀態": "🟡 簽核中"
                    }
                    st.session_state.leave_requests.append(new_leave)

                    # 自動發起至電子簽核中心 (若有)
                    if "approval_queue" in st.session_state:
                        st.session_state.approval_queue.append({
                            "簽核單號": f"APV-{lv_id}",
                            "來源模組": "🌴 請假申請",
                            "申請人": emp_name,
                            "申請項目": f"{leave_type} {days} 天 ({reason})",
                            "申請日期": str(datetime.date.today()),
                            "當前關卡": "關卡 1：部門主管審核",
                            "狀態": "🟡 待簽核",
                            "簽核歷程": []
                        })

                    st.success(f"✅ 假單已成功送出！單號：{lv_id}，請假天數：{days} 天")
                    st.rerun()

        st.markdown("---")
        st.markdown("#### 📋 歷史請假紀錄")
        st.dataframe(pd.DataFrame(st.session_state.leave_requests), use_container_width=True)

    # ====================================================
    # TAB 3: 權限系統後台 (檢視與管理同步之帳號)
    # ====================================================
    with tab_perm:
        st.subheader("🔑 權限系統後台 — 人員帳號與權限清單")
        st.info("💡 當新增員工時，系統會自動同步建立帳號並開通模組權限。")

        perm_list = []
        for emp_id, info in st.session_state.users_permissions.items():
            perm_list.append({
                "員工編號 / 帳號": info["username"],
                "員工姓名": info["full_name"],
                "權限角色": info["role"],
                "可存取模組清單": ", ".join(info["allowed_modules"])
            })
        st.dataframe(pd.DataFrame(perm_list), use_container_width=True)
