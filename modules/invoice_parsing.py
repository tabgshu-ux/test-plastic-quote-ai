import streamlit as st
import pandas as pd
import psycopg2
import datetime

def get_db_connection():
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_invoice_parsing(tenant_info, user_perms):
    st.markdown("### 🧾 跨國電子發票解析與稅務管理中心")
    st.info("💡 *專為會計與稅務打造：管理各國電子發票（含越南稅號 MST 與 XML 檔名）、多幣別總金額統計、即時關鍵字搜尋與憑證維護。*")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 電子發票總覽與即時搜尋", "➕ 上傳/登錄新電子發票", "⚙️ 發票狀態維護與刪除"])

    # ==================== Tab 1: 電子發票總覽與即時搜尋 ====================
    with tab1:
        st.markdown("#### 🔍 電子發票即時搜尋與篩選")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            keyword = st.text_input("關鍵字搜尋（發票號碼、稅號或供應商）", placeholder="輸入發票號碼或名稱...")
        with col_s2:
            currency_filter = st.selectbox("依幣別篩選", ["全部幣別", "VND", "USD", "TWD"])

        try:
            conn = get_db_connection()
            query = "SELECT invoice_id, tax_code_mst, seller_name, total_amount, currency, invoice_date, xml_filename FROM invoices ORDER BY invoice_date DESC"
            df = pd.read_sql(query, conn)
            conn.close()
        except Exception as e:
            df = pd.DataFrame([
                {"invoice_id": "INV-2026-001", "tax_code_mst": "0312345678", "seller_name": "越南電力公司 (EVN)", "total_amount": 15000000.0, "currency": "VND", "invoice_date": "2026-10-20", "xml_filename": "invoice_0312345678.xml"}
            ])

        filtered_df = df.copy()
        if keyword:
            filtered_df = filtered_df[
                filtered_df['invoice_id'].str.contains(keyword, case=False, na=False) |
                filtered_df['tax_code_mst'].str.contains(keyword, case=False, na=False) |
                filtered_df['seller_name'].str.contains(keyword, case=False, na=False)
            ]
        if currency_filter != "全部幣別":
            filtered_df = filtered_df[filtered_df['currency'] == currency_filter]

        st.markdown(f"**符合條件的電子發票總數**：`{len(filtered_df)}` 筆")
        st.dataframe(filtered_df, use_container_width=True)

    # ==================== Tab 2: 上傳/登錄新電子發票 ====================
    with tab2:
        st.markdown("#### ➕ 登錄新電子發票與 XML 憑證綁定")
        with st.form("new_invoice_form"):
            c1, c2 = st.columns(2)
            with c1:
                invoice_id = st.text_input("發票號碼 (Invoice ID) *", value=f"INV-{datetime.datetime.now().strftime('%m%d%H%M')}")
                tax_code = st.text_input("供應商稅號 (MST / 統編) *", placeholder="例: 0312345678")
                seller_name = st.text_input("供應商名稱 (Seller Name) *", placeholder="例: 越南某某工業材料行")
            with c2:
                total_amount = st.number_input("發票總金額", value=5000000.0, step=1000.0)
                currency = st.selectbox("發票幣別", ["VND", "USD", "TWD"])
                invoice_date = st.date_input("發票日期", value=datetime.date.today())
                xml_file = st.text_input("XML 檔案名稱", value="invoice_data.xml")

            if st.form_submit_button("🚀 確認登錄至雲端發票庫", type="primary", use_container_width=True):
                if invoice_id and seller_name:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        insert_sql = """
                            INSERT INTO invoices (invoice_id, tax_code_mst, seller_name, total_amount, currency, invoice_date, xml_filename)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (invoice_id) DO UPDATE 
                            SET seller_name = EXCLUDED.seller_name, total_amount = EXCLUDED.total_amount, currency = EXCLUDED.currency;
                        """
                        cur.execute(insert_sql, (invoice_id, tax_code, seller_name, total_amount, currency, invoice_date, xml_file))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 電子發票 [{invoice_id} - {seller_name}] 已成功寫入 Supabase 雲端資料庫！")
                        st.rerun()
                    except Exception as db_err:
                        st.error(f"❌ 寫入資料庫失敗：{db_err}")
                else:
                    st.warning("請填寫必要的發票號碼與供應商名稱！")

    # ==================== Tab 3: 發票狀態維護與刪除 ====================
    with tab3:
        st.markdown("#### ⚙️ 電子發票維護與刪除處理")
        target_invoice_id = st.text_input("輸入要刪除或處理的發票號碼 (Invoice ID)", placeholder="例: INV-2026-001")
        
        if target_invoice_id:
            with st.form("edit_invoice_form"):
                st.warning(f"⚠️ 您正在準備刪除發票號碼 [{target_invoice_id}]。")
                submitted_delete = st.form_submit_button("🗑️ 確認刪除此筆發票紀錄", type="secondary", use_container_width=True)

                if submitted_delete:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM invoices WHERE invoice_id = %s", (target_invoice_id,))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🗑️ 電子發票 [{target_invoice_id}] 已自系統中刪除！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗：{e}")
