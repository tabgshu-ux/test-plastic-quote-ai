import streamlit as st
import pandas as pd
import psycopg2
import datetime

def get_db_connection():
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_ga_procurements(tenant_info):
    st.markdown("### 📦 總務用品採購與跨國請購管理中心")
    st.info("💡 *支援各廠區總務用品請購、多幣別（VND/TWD/USD）單價與金額計算、折合美金總額換算，並支援進階搜尋與完整生命週期維護。*")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 請購單總覽與進階搜尋", "➕ 提交新請購申請", "⚙️ 請購單修改與維護"])

    # ==================== Tab 1: 請購單總覽與進階搜尋 ====================
    with tab1:
        st.markdown("#### 🔍 請購紀錄即時搜尋與篩選")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            keyword = st.text_input("關鍵字搜尋（品名、單號、申請人）", placeholder="輸入品名或單號...")
        with col_s2:
            category_filter = st.selectbox("依類別篩選", ["全部類別", "辦公耗材", "廠務設備", "IT 軟硬體", "勞安防護具"])
        with col_s3:
            currency_filter = st.selectbox("依幣別篩選", ["全部幣別", "VND (越南盾)", "TWD (新台幣)", "USD (美元)"])

        # 從 Supabase 讀取資料
        try:
            conn = get_db_connection()
            query = "SELECT po_id, item_name, category, quantity, currency, unit_price, estimated_cost, estimated_cost_usd, dept_name, applicant, status FROM ga_procurements ORDER BY created_at DESC"
            df = pd.read_sql(query, conn)
            conn.close()
        except Exception as e:
            df = pd.DataFrame([
                {"po_id": "PO-2026-001", "item_name": "A4 影印紙", "category": "辦公耗材", "quantity": 50, "currency": "VND", "unit_price": 85000, "estimated_cost": 4250000, "estimated_cost_usd": 170.0, "dept_name": "管理部", "applicant": "阮文Ａ", "status": "🟡 簽核中"}
            ])

        # 前端過濾
        filtered_df = df.copy()
        if keyword:
            filtered_df = filtered_df[
                filtered_df['po_id'].str.contains(keyword, case=False, na=False) |
                filtered_df['item_name'].str.contains(keyword, case=False, na=False) |
                filtered_df['applicant'].str.contains(keyword, case=False, na=False)
            ]
        if category_filter != "全部類別":
            filtered_df = filtered_df[filtered_df['category'] == category_filter]
        if currency_filter != "全部幣別":
            curr_code = currency_filter.split(" ")[0]
            filtered_df = filtered_df[filtered_df['currency'] == curr_code]

        st.markdown(f"**符合條件的請購單總數**：`{len(filtered_df)}` 筆")
        st.dataframe(filtered_df, use_container_width=True)

    # ==================== Tab 2: 提交新請購申請 ====================
    with tab2:
        st.markdown("#### ➕ 填寫總務請購單")
        with st.form("new_po_form"):
            c1, c2 = st.columns(2)
            with c1:
                po_id = st.text_input("請購單編號 *", value=f"PO-{datetime.datetime.now().strftime('%m%d%H%M')}")
                item_name = st.text_input("採購品名 / 規格 *", placeholder="例: 工廠專用安全鞋 / 事務機碳粉")
                category = st.selectbox("採購類別", ["辦公耗材", "廠務設備", "IT 軟硬體", "勞安防護具", "其他雜項"])
                quantity = st.number_input("採購數量", value=1, min_value=1, step=1)
            with c2:
                currency = st.selectbox("原幣幣別", ["VND", "TWD", "USD"])
                unit_price = st.number_input("原幣單價", value=100000.0, step=1000.0)
                dept_name = st.text_input("申請部門", placeholder="例: 製造部 / 管理部")
                applicant = st.text_input("申請人姓名 *", placeholder="例: 許福村")

            # 計算總金額
            est_cost = quantity * unit_price
            # 簡易換算美金（可依匯率調整，此處預設範例換算）
            rate_map = {"VND": 25000.0, "TWD": 32.0, "USD": 1.0}
            est_cost_usd = est_cost / rate_map.get(currency, 1.0)

            st.info(f"💡 系統自動計算：原幣總金額 = `{est_cost:,.2f} {currency}` | 折合美金 = `$ {est_cost_usd:,.2f} USD`")

            if st.form_submit_button("🚀 提交請購申請並拋轉至簽核中心", type="primary", use_container_width=True):
                if po_id and item_name and applicant:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        # 1. 寫入 ga_procurements
                        insert_po_sql = """
                            INSERT INTO ga_procurements (po_id, item_name, category, quantity, currency, unit_price, estimated_cost, estimated_cost_usd, dept_name, applicant, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '🟡 簽核中')
                        """
                        cur.execute(insert_po_sql, (po_id, item_name, category, quantity, currency, unit_price, est_cost, est_cost_usd, dept_name, applicant))
                        
                        # 2. 自動拋轉至電子簽核中心佇列 (approval_queue)
                        insert_q_sql = """
                            INSERT INTO approval_queue (approval_id, source_module, applicant, item_summary, current_step, status)
                            VALUES (%s, '總務採購 (GA Procurements)', %s, %s, '關卡 1：部門主管審核', '🟡 待簽核')
                            ON CONFLICT (approval_id) DO NOTHING;
                        """
                        cur.execute(insert_q_sql, (po_id, applicant, f"請購項目: {item_name} (數量: {quantity}, 金額: {est_cost:,.2f} {currency})"))

                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 請購單 [{po_id}] 已成功送出，並自動同步至電子簽核中心！")
                        st.rerun()
                    except Exception as db_err:
                        st.error(f"❌ 寫入資料庫失敗：{db_err}")
                else:
                    st.warning("請填寫必要的單號、品名與申請人！")

    # ==================== Tab 3: 請購單修改與維護 ====================
    with tab3:
        st.markdown("#### ⚙️ 修改或刪除請購單")
        target_po_id = st.text_input("輸入要處理的請購單編號 (PO ID)", placeholder="例: PO-2026-001")
        
        if target_po_id:
            with st.form("edit_po_form"):
                new_po_status = st.selectbox("更新狀態", ["🟡 簽核中", "🟢 已核准採購", "🔴 已駁回"])
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted_po_update = st.form_submit_button("💾 更新採購狀態", type="primary", use_container_width=True)
                with col_btn2:
                    submitted_po_delete = st.form_submit_button("🗑️ 刪除此請購單", type="secondary", use_container_width=True)

                if submitted_po_update:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("UPDATE ga_procurements SET status = %s WHERE po_id = %s", (new_po_status, target_po_id))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 請購單 [{target_po_id}] 狀態已更新為 [{new_po_status}]！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"更新失敗：{e}")

                if submitted_po_delete:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM ga_procurements WHERE po_id = %s", (target_po_id,))
                        cur.execute("DELETE FROM approval_queue WHERE approval_id = %s", (target_po_id,))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🗑️ 請購單 [{target_po_id}] 已自系統及簽核佇列中刪除！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗：{e}")
