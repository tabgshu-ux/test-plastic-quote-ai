import streamlit as st
import pandas as pd
import psycopg2
import datetime

def get_db_connection():
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_leave_attendance(tenant_info):
    st.markdown("### ⏱️ 全球跨國請假與考勤打卡管理中心")
    st.info("💡 *支援各國員工請假申請（年假、病假、事假等）、天數計算、簽核狀態追蹤，以及完整的即時搜尋與紀錄維護。*")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 請假總覽與進階搜尋", "➕ 提交請假申請", "⚙️ 請假審核與紀錄維護"])

    # ==================== Tab 1: 請假總覽與進階搜尋 ====================
    with tab1:
        st.markdown("#### 🔍 請假紀錄即時搜尋與篩選")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            keyword = st.text_input("關鍵字搜尋（員工姓名或編號）", placeholder="輸入姓名或員工編號...")
        with col_s2:
            leave_type_filter = st.selectbox("依假別篩選", ["全部假別", "年假 (Annual)", "病假 (Sick)", "事假 (Personal)", "公假 (Official)"])
        with col_s3:
            status_filter = st.selectbox("依簽核狀態篩選", ["全部狀態", "🟡 待簽核", "🟢 已核准", "🔴 已駁回"])

        # 從 Supabase 讀取請假資料
        try:
            conn = get_db_connection()
            query = "SELECT leave_id, employee_id, employee_name, leave_type, start_date, end_date, days_count, reason, status FROM leaves ORDER BY created_at DESC"
            df = pd.read_sql(query, conn)
            conn.close()
        except Exception as e:
            # 預設展示資料確保畫面流暢
            df = pd.DataFrame([
                {"leave_id": "LV-001", "employee_id": "EMP-001", "employee_name": "Nguyễn Văn A", "leave_type": "年假 (Annual)", "start_date": "2026-10-25", "end_date": "2026-10-26", "days_count": 2.0, "reason": "家庭聚會", "status": "🟡 待簽核"}
            ])

        # 前端條件過濾
        filtered_df = df.copy()
        if keyword:
            filtered_df = filtered_df[
                filtered_df['employee_id'].str.contains(keyword, case=False, na=False) |
                filtered_df['employee_name'].str.contains(keyword, case=False, na=False)
            ]
        if leave_type_filter != "全部假別":
            type_key = leave_type_filter.split(" ")[0]
            filtered_df = filtered_df[filtered_df['leave_type'].str.contains(type_key, na=False)]
        if status_filter != "全部狀態":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]

        st.markdown(f"**符合條件的請假申請總數**：`{len(filtered_df)}` 筆")
        st.dataframe(filtered_df, use_container_width=True)

    # ==================== Tab 2: 提交請假申請 ====================
    with tab2:
        st.markdown("#### ➕ 填寫新請假單")
        with st.form("new_leave_form"):
            c1, c2 = st.columns(2)
            with c1:
                l_id = st.text_input("請假單編號 *", value=f"LV-{datetime.datetime.now().strftime('%m%d%H%M')}")
                emp_id = st.text_input("員工編號 *", placeholder="例: EMP-001")
                emp_name = st.text_input("員工姓名 *", placeholder="例: Nguyễn Văn A")
                l_type = st.selectbox("假別選擇", ["年假 (Annual)", "病假 (Sick)", "事假 (Personal)", "公假 (Official)", "產假/婚喪假"])
            with c2:
                start_dt = st.date_input("開始日期", value=datetime.date.today())
                end_dt = st.date_input("結束日期", value=datetime.date.today())
                days_cnt = st.number_input("請假天數", value=1.0, step=0.5)
                l_reason = st.text_area("請假事由說明", placeholder="請輸入請假原因...")

            if st.form_submit_button("🚀 提交請假申請至雲端", type="primary", use_container_width=True):
                if emp_id and emp_name:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        insert_sql = """
                            INSERT INTO leaves (leave_id, employee_id, employee_name, leave_type, start_date, end_date, days_count, reason, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '🟡 待簽核')
                        """
                        cur.execute(insert_sql, (l_id, emp_id, emp_name, l_type, start_dt, end_dt, days_cnt, l_reason))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 成功送出員工 [{emp_name}] 的請假申請，單號：`{l_id}`！")
                        st.rerun()
                    except Exception as db_err:
                        st.error(f"❌ 寫入資料庫失敗：{db_err}")
                else:
                    st.warning("請填寫員工編號與姓名！")

    # ==================== Tab 3: 請假審核與紀錄維護 ====================
    with tab3:
        st.markdown("#### ⚙️ 請假審核、修改與刪除")
        target_leave_id = st.text_input("輸入要處理的請假單編號 (Leave ID)", placeholder="例: LV-001")
        
        if target_leave_id:
            with st.form("edit_leave_form"):
                new_status = st.selectbox("更新簽核狀態", ["🟡 待簽核", "🟢 已核准", "🔴 已駁回"])
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted_status = st.form_submit_button("💾 更新簽核狀態", type="primary", use_container_width=True)
                with col_btn2:
                    submitted_delete = st.form_submit_button("🗑️ 刪除此請假單", type="secondary", use_container_width=True)

                if submitted_status:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("UPDATE leaves SET status = %s WHERE leave_id = %s", (new_status, target_leave_id))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 請假單 [{target_leave_id}] 狀態已更新為 [{new_status}]！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"更新狀態失敗：{e}")

                if submitted_delete:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM leaves WHERE leave_id = %s", (target_leave_id,))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🗑️ 請假單 [{target_leave_id}] 已自系統中刪除！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗：{e}")
