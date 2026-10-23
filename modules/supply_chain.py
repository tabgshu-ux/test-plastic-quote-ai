import streamlit as st
import pandas as pd
import psycopg2

def get_db_connection():
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_supply_chain(tenant_info, user_perms):
    st.markdown("### 📊 全球供應鏈與業務報價管理中心")
    st.info("💡 *專為業務與供應鏈打造：管理客戶報價單、依尺寸與鎖模力計算總金額，支援多幣別（USD/TWD/VND）與即時搜尋及維護。*")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 報價單總覽與即時搜尋", "➕ 建立新客戶報價單", "⚙️ 報價單狀態維護與刪除"])

    # ==================== Tab 1: 報價單總覽與即時搜尋 ====================
    with tab1:
        st.markdown("#### 🔍 業務報價單即時搜尋與篩選")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            keyword = st.text_input("關鍵字搜尋（報價單號或客戶名稱）", placeholder="輸入客戶名稱...")
        with col_s2:
            currency_filter = st.selectbox("依幣別篩選", ["全部幣別", "USD", "TWD", "VND"])

        try:
            conn = get_db_connection()
            query = "SELECT quote_id, customer_name, part_length, part_width, part_thickness, clamping_force_tons, total_amount, currency FROM quotations ORDER BY created_at DESC"
            df = pd.read_sql(query, conn)
            conn.close()
        except Exception as e:
            df = pd.DataFrame([
                {"quote_id": "QT-2026-001", "customer_name": "越南宏福實業", "part_length": 150.0, "part_width": 100.0, "part_thickness": 3.5, "clamping_force_tons": 250.0, "total_amount": 12500.0, "currency": "USD"}
            ])

        filtered_df = df.copy()
        if keyword:
            filtered_df = filtered_df[
                filtered_df['quote_id'].str.contains(keyword, case=False, na=False) |
                filtered_df['customer_name'].str.contains(keyword, case=False, na=False)
            ]
        if currency_filter != "全部幣別":
            filtered_df = filtered_df[filtered_df['currency'] == currency_filter]

        st.markdown(f"**符合條件的報價單總數**：`{len(filtered_df)}` 筆")
        st.dataframe(filtered_df, use_container_width=True)

    # ==================== Tab 2: 建立新客戶報價單 ====================
    with tab2:
        st.markdown("#### ➕ 建立新業務報價單與成本計算")
        with st.form("new_quote_form"):
            c1, c2 = st.columns(2)
            with c1:
                quote_id = st.text_input("報價單編號 *", value="QT-2026-002")
                customer_name = st.text_input("客戶名稱 *", placeholder="例: 越南三星電子 / 台灣車燈大廠")
                part_length = st.number_input("產品長度 (mm)", value=100.0, step=1.0)
                part_width = st.number_input("產品寬度 (mm)", value=80.0, step=1.0)
            with c2:
                part_thickness = st.number_input("產品厚度 (mm)", value=3.0, step=0.1)
                clamping_force = st.number_input("建議鎖模力 (Tons)", value=200.0, step=10.0)
                currency = st.selectbox("報價幣別", ["USD", "TWD", "VND"])
                total_amount = st.number_input("報價總金額", value=8500.0, step=100.0)

            if st.form_submit_button("🚀 確認建立並寫入雲端報價庫", type="primary", use_container_width=True):
                if quote_id and customer_name:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        insert_sql = """
                            INSERT INTO quotations (quote_id, customer_name, part_length, part_width, part_thickness, clamping_force_tons, total_amount, currency)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (quote_id) DO UPDATE 
                            SET customer_name = EXCLUDED.customer_name, total_amount = EXCLUDED.total_amount, currency = EXCLUDED.currency;
                        """
                        cur.execute(insert_sql, (quote_id, customer_name, part_length, part_width, part_thickness, clamping_force, total_amount, currency))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 報價單 [{quote_id} - {customer_name}] 已成功寫入 Supabase 雲端資料庫！")
                        st.rerun()
                    except Exception as db_err:
                        st.error(f"❌ 寫入資料庫失敗：{db_err}")
                else:
                    st.warning("請填寫必要的報價單編號與客戶名稱！")

    # ==================== Tab 3: 報價單狀態維護與刪除 ====================
    with tab3:
        st.markdown("#### ⚙️ 報價單維護與刪除處理")
        target_quote_id = st.text_input("輸入要刪除或處理的報價單編號 (Quote ID)", placeholder="例: QT-2026-001")
        
        if target_quote_id:
            with st.form("edit_quote_form"):
                st.warning(f"⚠️ 您正在準備刪除報價單編號 [{target_quote_id}]。")
                submitted_delete = st.form_submit_button("🗑️ 確認刪除此筆報價單", type="secondary", use_container_width=True)

                if submitted_delete:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM quotations WHERE quote_id = %s", (target_quote_id,))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🗑️ 報價單 [{target_quote_id}] 已自系統中刪除！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗：{e}")
