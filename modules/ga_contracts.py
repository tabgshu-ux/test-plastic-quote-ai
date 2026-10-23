import streamlit as st
import pandas as pd
import psycopg2
import datetime

def get_db_connection():
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_ga_contracts(tenant_info, user_perms):
    st.markdown("### 📜 跨國行政公文與合約列管中心")
    st.info("💡 *專為法務與行政打造：管理各類商務合約、廠房租約與公文效期、合約狀態追蹤、即時關鍵字搜尋與憑證維護。*")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 合約總覽與即時搜尋", "➕ 登錄新合約/公文", "⚙️ 合約狀態維護與刪除"])

    # ==================== Tab 1: 合約總覽與即時搜尋 ====================
    with tab1:
        st.markdown("#### 🔍 合約與公文即時搜尋與篩選")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            keyword = st.text_input("關鍵字搜尋（合約編號、標題或相對人）", placeholder="輸入標題或廠商名稱...")
        with col_s2:
            status_filter = st.selectbox("依合約狀態篩選", ["全部狀態", "🟢 有效中", "🟡 即將到期", "🔴 已終止/過期"])

        try:
            conn = get_db_connection()
            query = "SELECT contract_id, doc_type, title, partner_unit, sign_date, end_date, owner, status FROM ga_contracts ORDER BY sign_date DESC"
            df = pd.read_sql(query, conn)
            conn.close()
        except Exception as e:
            df = pd.DataFrame([
                {"contract_id": "CNT-2026-001", "doc_type": "廠房租賃合約", "title": "平陽廠房 A 區長期租賃合約", "partner_unit": "越南工業園區開發股份公司", "sign_date": "2024-01-01", "end_date": "2029-01-01", "owner": "許福村", "status": "🟢 有效中"}
            ])

        filtered_df = df.copy()
        if keyword:
            filtered_df = filtered_df[
                filtered_df['contract_id'].str.contains(keyword, case=False, na=False) |
                filtered_df['title'].str.contains(keyword, case=False, na=False) |
                filtered_df['partner_unit'].str.contains(keyword, case=False, na=False)
            ]
        if status_filter != "全部狀態":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]

        st.markdown(f"**符合條件的合約總數**：`{len(filtered_df)}` 筆")
        st.dataframe(filtered_df, use_container_width=True)

    # ==================== Tab 2: 登錄新合約/公文 ====================
    with tab2:
        st.markdown("#### ➕ 登錄新合約或行政公文")
        with st.form("new_contract_form"):
            c1, c2 = st.columns(2)
            with c1:
                contract_id = st.text_input("合約/公文編號 *", value=f"CNT-{datetime.datetime.now().strftime('%m%d%H%M')}")
                doc_type = st.selectbox("文件類型", ["廠房租賃合約", "設備採購合約", "勞務外包合約", "產學合作協議", "重要行政公文"])
                title = st.markdown = st.text_input("合約標題 / 主旨 *", placeholder="例: 廠房設備維護保養年度合約")
            with c2:
                partner_unit = st.text_input("相對合作單位 / 廠商 *", placeholder="例: 台灣某某科技股份有限公司")
                sign_date = st.date_input("簽訂日期", value=datetime.date.today())
                end_date = st.date_input("到期/效期截止日", value=datetime.date.today() + datetime.timedelta(days=365))
                owner = st.text_input("內部負責人 / 經辦", placeholder="例: 許福村")

            if st.form_submit_button("🚀 確認登錄至雲端合約庫", type="primary", use_container_width=True):
                if contract_id and title:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        insert_sql = """
                            INSERT INTO ga_contracts (contract_id, doc_type, title, partner_unit, sign_date, end_date, owner, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, '🟢 有效中')
                            ON CONFLICT (contract_id) DO UPDATE 
                            SET title = EXCLUDED.title, partner_unit = EXCLUDED.partner_unit, status = EXCLUDED.status;
                        """
                        cur.execute(insert_sql, (contract_id, doc_type, title, partner_unit, sign_date, end_date, owner))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 合約 [{contract_id} - {title}] 已成功寫入 Supabase 雲端資料庫！")
                        st.rerun()
                    except Exception as db_err:
                        st.error(f"❌ 寫入資料庫失敗：{db_err}")
                else:
                    st.warning("請填寫必要的合約編號與標題！")

    # ==================== Tab 3: 合約狀態維護與刪除 ====================
    with tab3:
        st.markdown("#### ⚙️ 合約狀態維護與刪除處理")
        target_contract_id = st.text_input("輸入要處理的合約編號 (Contract ID)", placeholder="例: CNT-2026-001")
        
        if target_contract_id:
            with st.form("edit_contract_form"):
                new_status = st.selectbox("更新合約狀態", ["🟢 有效中", "🟡 即將到期", "🔴 已終止/過期"])
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted_update = st.form_submit_button("💾 更新合約狀態", type="primary", use_container_width=True)
                with col_btn2:
                    submitted_delete = st.form_submit_button("🗑️ 刪除此合約紀錄", type="secondary", use_container_width=True)

                if submitted_update:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("UPDATE ga_contracts SET status = %s WHERE contract_id = %s", (new_status, target_contract_id))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 合約 [{target_contract_id}] 狀態已更新為 [{new_status}]！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"更新失敗：{e}")

                if submitted_delete:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM ga_contracts WHERE contract_id = %s", (target_contract_id,))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🗑️ 合約 [{target_contract_id}] 已自系統中刪除！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗：{e}")
