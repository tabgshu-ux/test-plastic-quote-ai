import streamlit as st
import pandas as pd
import psycopg2

def get_db_connection():
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_approval_center(tenant_info, user_perms):
    st.markdown("### ✍️ 全方位跨部門電子簽核與審核中心")
    st.info("💡 *獨立模組：統一管理來自請假差勤、總務採購等各模組的待審核表單，支援一鍵同意、駁回與歷史簽核軌跡追蹤。*")
    st.markdown("---")

    tab1, tab2 = st.tabs(["📋 待簽核佇列與審核作業", "📜 歷史簽核日誌與軌跡"])

    # ==================== Tab 1: 待簽核佇列與審核作業 ====================
    with tab1:
        st.markdown("#### ⏳ 待主管審核之表單清單")
        
        try:
            conn = get_db_connection()
            query = "SELECT approval_id, source_module, applicant, item_summary, apply_date, current_step, status FROM approval_queue ORDER BY created_at DESC"
            df = pd.read_sql(query, conn)
            conn.close()
        except Exception as e:
            df = pd.DataFrame([
                {"approval_id": "PO-2026-001", "source_module": "總務採購", "applicant": "阮文Ａ", "item_summary": "請購項目: A4 影印紙", "apply_date": "2026-10-23", "current_step": "關卡 1：部門主管審核", "status": "🟡 待簽核"}
            ])

        st.dataframe(df, use_container_width=True)
        st.markdown("---")

        st.markdown("#### ✍️ 執行審核動作")
        with st.form("approval_action_form"):
            target_id = st.text_input("輸入要審核的表單編號 (Approval ID / 單號)", placeholder="例: PO-2026-001 或 LV-001")
            action_choice = st.selectbox("審核決定", ["🟢 同意核准 (Approve)", "🔴 駁回申請 (Reject)"])
            comments = st.text_area("審核意見 / 批示說明", placeholder="請輸入批示內容...")
            reviewer_name = st.text_input("審核主管姓名", value="許福村 (總經理)")

            if st.form_submit_button("🚀 確認送出審核決定", type="primary", use_container_width=True):
                if target_id:
                    final_status = "🟢 已核准" if "同意" in action_choice else "🔴 已駁回"
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        
                        # 1. 更新 approval_queue 狀態
                        cur.execute("UPDATE approval_queue SET status = %s WHERE approval_id = %s", (final_status, target_id))
                        
                        # 2. 同步更新來源表單狀態
                        if target_id.startswith("PO"):
                            cur.execute("UPDATE ga_procurements SET status = %s WHERE po_id = %s", (final_status, target_id))
                        elif target_id.startswith("LV"):
                            cur.execute("UPDATE leaves SET status = %s WHERE leave_id = %s", (final_status, target_id))

                        # 3. 寫入 approval_logs 歷程記錄
                        log_sql = """
                            INSERT INTO approval_logs (approval_id, reviewer, reviewer_role, action, comments)
                            VALUES (%s, %s, '主管/管理員', %s, %s)
                        """
                        cur.execute(log_sql, (target_id, reviewer_name, final_status, comments))

                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 表單 [{target_id}] 審核完成，決定：【{final_status}】！")
                        st.rerun()
                    except Exception as err:
                        st.error(f"❌ 審核處理失敗：{err}")
                else:
                    st.warning("請輸入要審核的表單編號！")

    # ==================== Tab 2: 歷史簽核日誌與軌跡 ====================
    with tab2:
        st.markdown("#### 📜 完整簽核軌跡與稽核日誌 (Audit Trail)")
        try:
            conn = get_db_connection()
            log_query = "SELECT id, approval_id, reviewer, reviewer_role, action, comments, reviewed_at FROM approval_logs ORDER BY reviewed_at DESC"
            log_df = pd.read_sql(log_query, conn)
            conn.close()
            st.dataframe(log_df, use_container_width=True)
        except Exception as e:
            st.info("目前尚無歷史簽核紀錄。")
