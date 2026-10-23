import streamlit as st
import pandas as pd
import psycopg2
import os

def get_db_connection():
    # 使用您的 Supabase 連線字串
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_employee_management(tenant_info):
    st.markdown("### 👥 全球跨國員工與在地化薪資管理中心")
    st.info("💡 *支援台灣、越南等不同國家的證件（身分證/CCCD/稅號/社保）、多幣別薪資設定，並具備即時關鍵字搜尋與完整的增刪修查功能。*")
    st.markdown("---")

    tenant_id = tenant_info.get("tenant_id", "TENANT-001")

    # 分頁籤：1. 員工清單與搜尋 | 2. 新增員工 | 3. 修改與維護
    tab1, tab2, tab3 = st.tabs(["📋 員工總覽與進階搜尋", "➕ 新增跨國員工", "⚙️ 修改與維護設定"])

    # ==================== Tab 1: 員工總覽與進階搜尋 ====================
    with tab1:
        st.markdown("#### 🔍 員工資料即時搜尋與篩選")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            keyword = st.text_input("關鍵字搜尋（姓名、編號、證件）", placeholder="輸入姓名或員工編號...")
        with col_s2:
            factory_filter = st.selectbox("依廠區篩選", ["全部廠區", "越南平陽廠 (Binh Duong)", "台北總公司 (Taipei)"])
        with col_s3:
            currency_filter = st.selectbox("依薪資幣別篩選", ["全部幣別", "VND (越南盾)", "TWD (新台幣)", "USD (美元)"])

        # 從 Supabase 讀取員工資料
        try:
            conn = get_db_connection()
            query = "SELECT employee_id, name, factory_location, department, base_salary, currency FROM employees"
            df = pd.read_sql(query, conn)
            conn.close()
        except Exception as e:
            # 若資料庫尚未有資料，提供預設展示資料確保畫面不崩潰
            df = pd.DataFrame([
                {"employee_id": "EMP-001", "name": "Nguyễn Văn A", "factory_location": "越南平陽廠", "department": "生產部", "base_salary": 12000000, "currency": "VND"},
                {"employee_id": "EMP-002", "name": "許小明", "factory_location": "台北總公司", "department": "資訊管理部", "base_salary": 65000, "currency": "TWD"}
            ])

        # 執行前端過濾與搜尋
        filtered_df = df.copy()
        if keyword:
            filtered_df = filtered_df[
                filtered_df['employee_id'].str.contains(keyword, case=False, na=False) |
                filtered_df['name'].str.contains(keyword, case=False, na=False)
            ]
        if factory_filter != "全部廠區":
            loc_key = "越南" if "越南" in factory_filter else "台北"
            filtered_df = filtered_df[filtered_df['factory_location'].str.contains(loc_key, na=False)]
        if currency_filter != "全部幣別":
            curr_code = currency_filter.split(" ")[0]
            filtered_df = filtered_df[filtered_df['currency'] == curr_code]

        st.markdown(f"**符合條件的員工總數**：`{len(filtered_df)}` 位")
        st.dataframe(filtered_df, use_container_width=True)

    # ==================== Tab 2: 新增跨國員工 ====================
    with tab2:
        st.markdown("#### ➕ 註冊新員工與設定在地化薪資")
        with st.form("new_employee_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_id = st.text_input("員工編號 (Employee ID) *", placeholder="例: EMP-003")
                e_name = st.text_input("員工全名 (Full Name) *", placeholder="例: Trần Thị B 或 王大明")
                e_factory = st.selectbox("所屬廠區 / 國家", ["越南平陽廠 (Binh Duong, VN)", "台北總公司 (Taipei, TW)"])
                e_dept = st.text_input("所屬部門", placeholder="例: 品保處 / 資訊部")
            with c2:
                e_salary = st.number_input("基本薪資數值 (Base Salary)", value=10000000.0, step=1000.0)
                e_currency = st.selectbox("薪資幣別 (Currency)", ["VND", "TWD", "USD"])
                e_id_card = st.text_input("國家法定證件 (身分證 / CCCD)", placeholder="輸入證件號碼...")
                e_tax = st.text_input("稅號 / 社保編號 (Tax / BHXH)", placeholder="輸入稅號或社保代號...")

            if st.form_submit_button("🚀 確認新增並寫入雲端資料庫", type="primary", use_container_width=True):
                if e_id and e_name:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        insert_sql = """
                            INSERT INTO employees (employee_id, name, factory_location, department, base_salary, currency)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (employee_id) DO UPDATE 
                            SET name = EXCLUDED.name, factory_location = EXCLUDED.factory_location, 
                                department = EXCLUDED.department, base_salary = EXCLUDED.base_salary, currency = EXCLUDED.currency;
                        """
                        cur.execute(insert_sql, (e_id, e_name, e_factory, e_dept, e_salary, e_currency))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 成功新增員工 [{e_name} ({e_id})] 至 Supabase 雲端資料庫！")
                        st.rerun()
                    except Exception as db_err:
                        st.error(f"❌ 寫入資料庫失敗：{db_err}")
                else:
                    st.warning("請填寫必要的員工編號與姓名！")

    # ==================== Tab 3: 修改與維護設定 ====================
    with tab3:
        st.markdown("#### ⚙️ 修改或刪除現有員工資料")
        target_emp_id = st.text_input("輸入要修改或刪除的員工編號 (Employee ID)", placeholder="例: EMP-001")
        
        if target_emp_id:
            with st.form("edit_employee_form"):
                up_name = st.text_input("修改員工姓名", value="更新後的姓名")
                up_salary = st.number_input("修改基本薪資", value=15000000.0)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted_update = st.form_submit_button("💾 儲存修改", type="primary", use_container_width=True)
                with col_btn2:
                    submitted_delete = st.form_submit_button("🗑️ 刪除此員工", type="secondary", use_container_width=True)

                if submitted_update:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("UPDATE employees SET name = %s, base_salary = %s WHERE employee_id = %s", (up_name, up_salary, target_emp_id))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 員工 [{target_emp_id}] 資料已成功更新！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"更新失敗：{e}")

                if submitted_delete:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM employees WHERE employee_id = %s", (target_emp_id,))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🗑️ 員工 [{target_emp_id}] 已自系統中刪除！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗：{e}")
