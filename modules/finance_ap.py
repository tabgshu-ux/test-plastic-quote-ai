import streamlit as st
import pandas as pd
import psycopg2
import datetime

def get_db_connection():
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_finance_ap(tenant_info, user_perms):
    st.markdown("### 💰 跨國應付帳款與多幣別財務管理 (Finance AP)")
    st.info("💡 *處理各廠區應付帳款、零用金報銷審核、多幣別（VND/TWD/USD）動態匯率換算及財務傳票登載。*")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 零用金與費用報銷總覽", "➕ 提交財務請款與報銷", "⚙️ 帳款狀態維護與付訖處理"])

    # ==================== Tab 1: 零用金與費用報銷總覽 ====================
    with tab1:
        st.markdown("#### 🔍 財務報銷與應付帳款即時搜尋")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            keyword = st.text_input("關鍵字搜尋（單號或申請人）", placeholder="輸入單號或姓名...")
        with col_s2:
            expense_filter = st.selectbox("依費用類型篩選", ["全部類型", "差旅費", "辦公雜費", "廠務修繕", "交際費"])
        with col_s3:
            status_filter = st.selectbox("依撥款狀態篩選", ["全部狀態", "🟡 待審核", "🟢 已撥款/付訖", "🔴 已退件"])

        try:
            conn = get_db_connection()
            query = "SELECT pc_id, apply_date, applicant, expense_type, amount, currency, description, status FROM ga_petty_cash ORDER BY created_at DESC"
            df = pd.read_sql(query, conn)
            conn.close()
        except Exception as e:
            df = pd.DataFrame([
                {"pc_id": "PC-2026-001", "apply_date": "2026-10-23", "applicant": "阮文Ａ", "expense_type": "廠務修繕", "amount": 1500000, "currency": "VND", "description": "廠房水電急修", "status": "🟡 待審核"}
            ])

        filtered_df = df.copy()
        if keyword:
            filtered_df = filtered_df[
                filtered_df['pc_id'].str.contains(keyword, case=False, na=False) |
                filtered_df['applicant'].str.contains(keyword, case=False, na=False)
            ]
        if expense_filter != "全部類型":
            filtered_df = filtered_df[filtered_df['expense_type'] == expense_filter]
        if status_filter != "全部狀態":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]

        st.markdown(f"**符合條件的財務請款單總數**：`{len(filtered_df)}` 筆")
        st.dataframe(filtered_df, use_container_width=True)

    # ==================== Tab 2: 提交財務請款與報銷 ====================
    with tab2:
        st.markdown("#### ➕ 填寫零用金與行政費用報銷單")
        with st.form("new_petty_form"):
            c1, c2 = st.columns(2)
            with c1:
                pc_id = st.text_input("報銷單編號 *", value=f"PC-{datetime.datetime.now().strftime('%m%d%H%M')}")
                apply_date = st.date_input("申請日期", value=datetime.date.today())
                applicant = st.text_input("申請人姓名 *", placeholder="例: 許福村")
                expense_type = st.selectbox("費用類型", ["差旅費", "辦公雜費", "廠務修繕", "交際費", "其他雜項"])
            with c2:
                amount = st.number_input("請款金額", value=500000.0, step=1000.0)
                currency = st.selectbox("幣別", ["VND", "TWD", "USD"])
                description = st.text_area("費用說明與備註", placeholder="請輸入詳細支出說明...")

            if st.form_submit_button("🚀 提交財務請款單並同步至簽核中心", type="primary", use_container_width=True):
                if pc_id and applicant:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        
                        # 1. 寫入 ga_petty_cash
                        insert_pc_sql = """
                            INSERT INTO ga_petty_cash (pc_id, apply_date, applicant, expense_type, amount, currency, description, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, '🟡 待審核')
                        """
                        cur.execute(insert_pc_sql, (pc_id, apply_date, applicant, expense_type, amount, currency, description))
                        
                        # 2. 自動拋轉至簽核中心佇列
                        insert_q_sql = """
                            INSERT INTO approval_queue (approval_id, source_module, applicant, item_summary, current_step, status)
                            VALUES (%s, '財務應付與零用金 (Finance AP)', %s, %s, '關卡 2：財務主管複核', '🟡 待簽核')
                            ON CONFLICT (approval_id) DO NOTHING;
                        """
                        cur.execute(insert_q_sql, (pc_id, applicant, f"費用報銷: {expense_type} (金額: {amount:,.2f} {currency})"))

                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 財務請款單 [{pc_id}] 已成功送出並同步至電子簽核中心！")
                        st.rerun()
                    except Exception as db_err:
                        st.error(f"❌ 寫入資料庫失敗：{db_err}")
                else:
                    st.warning("請填寫必要的單號與申請人姓名！")

    # ==================== Tab 3: 帳款狀態維護與付訖處理 ====================
    with tab3:
        st.markdown("#### ⚙️ 更新撥款狀態與資料維護")
        target_pc_id = st.text_input("輸入要處理的報銷單編號 (PC ID)", placeholder="例: PC-2026-001")
        
        if target_pc_id:
            with st.form("edit_pc_form"):
                new_pc_status = st.selectbox("更新撥款/審核狀態", ["🟡 待審核", "🟢 已撥款/付訖", "🔴 已退件"])
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted_pc_update = st.form_submit_button("💾 更新狀態", type="primary", use_container_width=True)
                with col_btn2:
                    submitted_pc_delete = st.form_submit_button("🗑️ 刪除此單據", type="secondary", use_container_width=True)

                if submitted_pc_update:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("UPDATE ga_petty_cash SET status = %s WHERE pc_id = %s", (new_pc_status, target_pc_id))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 報銷單 [{target_pc_id}] 狀態已更新為 [{new_pc_status}]！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"更新失敗：{e}")

                if submitted_pc_delete:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM ga_petty_cash WHERE pc_id = %s", (target_pc_id,))
                        cur.execute("DELETE FROM approval_queue WHERE approval_id = %s", (target_pc_id,))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🗑️ 報銷單 [{target_pc_id}] 已自系統及簽核佇列中刪除！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗：{e}")
