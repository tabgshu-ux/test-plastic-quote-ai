import streamlit as st
import pandas as pd
import psycopg2

def get_db_connection():
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_org_management(tenant_info, user_perms):
    st.markdown("### 🌐 跨國廠區、組織架構與系統設定中心")
    st.info("💡 *專為系統管理員打造：管理全球廠區主檔、組織部門、使用者帳號權限及多國動態匯率引擎。*")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 廠區與部門總覽", "💱 跨國動態匯率設定", "👤 使用者與權限管理"])

    # ==================== Tab 1: 廠區與部門總覽 ====================
    with tab1:
        st.markdown("#### 🏢 全球廠區與部門架構")
        c_col1, c_col2 = st.columns(2)

        with c_col1:
            st.markdown("##### 🏭 廠區主檔清單")
            try:
                conn = get_db_connection()
                f_df = pd.read_sql("SELECT factory_id, factory_name, country, currency, status FROM factories", conn)
                conn.close()
            except Exception:
                f_df = pd.DataFrame([
                    {"factory_id": "VN-BD01", "factory_name": "越南平陽廠", "country": "Vietnam", "currency": "VND", "status": "營運中"},
                    {"factory_id": "TW-TP01", "factory_name": "台北總公司", "country": "Taiwan", "currency": "TWD", "status": "營運中"}
                ])
            st.dataframe(f_df, use_container_width=True)

        with c_col2:
            st.markdown("##### 📂 部門主檔清單")
            try:
                conn = get_db_connection()
                d_df = pd.read_sql("SELECT dept_id, dept_name, factory_location FROM departments", conn)
                conn.close()
            except Exception:
                d_df = pd.DataFrame([
                    {"dept_id": "DEPT-PROD", "dept_name": "生產製造部", "factory_location": "越南平陽廠"},
                    {"dept_id": "DEPT-IT", "dept_name": "資訊管理部", "factory_location": "台北總公司"}
                ])
            st.dataframe(d_df, use_container_width=True)

    # ==================== Tab 2: 跨國動態匯率設定 ====================
    with tab2:
        st.markdown("#### 💱 跨國即時與歷史匯率檔 (Currency Rates)")
        try:
            conn = get_db_connection()
            rate_df = pd.read_sql("SELECT id, currency_code, rate_to_usd, updated_at FROM currency_rates", conn)
            conn.close()
        except Exception:
            rate_df = pd.DataFrame([
                {"id": 1, "currency_code": "VND", "rate_to_usd": 25000.000000, "updated_at": "2026-10-23"},
                {"id": 2, "currency_code": "TWD", "rate_to_usd": 32.000000, "updated_at": "2026-10-23"},
                {"id": 3, "currency_code": "USD", "rate_to_usd": 1.000000, "updated_at": "2026-10-23"}
            ])

        st.dataframe(rate_df, use_container_width=True)

        with st.form("update_rate_form"):
            st.markdown("##### ➕ 新增或更新匯率 (對 USD)")
            rc1, rc2 = st.columns(2)
            with rc1:
                curr_code = st.text_input("幣別代碼 (例如: VND, TWD)", placeholder="VND")
            with rc2:
                rate_val = st.number_input("對美金匯率 (Rate to USD)", value=25000.0, step=0.000001, format="%.6f")

            if st.form_submit_button("🚀 儲存匯率至雲端", type="primary", use_container_width=True):
                if curr_code:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        sql = """
                            INSERT INTO currency_rates (currency_code, rate_to_usd)
                            VALUES (%s, %s)
                            ON CONFLICT (currency_code) DO UPDATE SET rate_to_usd = EXCLUDED.rate_to_usd, updated_at = CURRENT_TIMESTAMP;
                        """
                        cur.execute(sql, (curr_code.upper(), rate_val))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 幣別 [{curr_code.upper}] 匯率已成功更新！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"更新匯率失敗：{e}")

    # ==================== Tab 3: 使用者與權限管理 ====================
    with tab3:
        st.markdown("#### 👤 系統使用者帳號與權限清單")
        try:
            conn = get_db_connection()
            user_df = pd.read_sql("SELECT user_id, username, full_name, dept_id, role, status FROM users", conn)
            conn.close()
        except Exception:
            user_df = pd.DataFrame([
                {"user_id": 1, "username": "admin", "full_name": "許福村", "dept_id": "DEPT-IT", "role": "Administrator", "status": "Active"}
            ])
        st.dataframe(user_df, use_container_width=True)
