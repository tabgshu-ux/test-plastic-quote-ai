import streamlit as st
import pandas as pd
import psycopg2
import datetime

def get_db_connection():
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_mes_production(tenant_info, user_perms):
    st.markdown("### 🏭 MES 生產製造與機台 IoT 即時監控中心")
    st.info("💡 *專為製造工廠打造：即時監控射出機桶溫、射出壓力與循環時間，支援工單生產進度追蹤、異常代碼過濾與即時數據搜尋。*")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 IoT 機台即時 Log 與工單總覽", "➕ 新增生產工單與排程", "⚙️ 機台狀態與生產參數維護"])

    # ==================== Tab 1: IoT 機台即時 Log 與工單總覽 ====================
    with tab1:
        st.markdown("#### 🔍 設備 IoT 連線數據與生產即時搜尋")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            keyword = st.text_input("關鍵字搜尋（設備編號或廠區）", placeholder="輸入設備代號...")
        with col_s2:
            status_filter = st.selectbox("依機台狀態篩選", ["全部狀態", "🟢 正常運轉 (RUN)", "🟡 待機中 (IDLE)", "🔴 異常警報 (ALARM)"])
        with col_s3:
            factory_filter = st.selectbox("依廠區篩選", ["全部廠區", "越南平陽廠", "台北總廠"])

        try:
            conn = get_db_connection()
            query = "SELECT id, device_id, factory_id, barrel_temperature, injection_pressure, cycle_time, status_code, logged_at FROM iot_device_logs ORDER BY logged_at DESC"
            df = pd.read_sql(query, conn)
            conn.close()
        except Exception as e:
            df = pd.DataFrame([
                {"id": 1, "device_id": "INJ-MACHINE-01", "factory_id": "越南平陽廠", "barrel_temperature": 210.5, "injection_pressure": 1250.0, "cycle_time": 28.5, "status_code": "🟢 RUN", "logged_at": "2026-10-23 10:30:00"}
            ])

        filtered_df = df.copy()
        if keyword:
            filtered_df = filtered_df[filtered_df['device_id'].str.contains(keyword, case=False, na=False)]
        if status_filter != "全部狀態":
            stat_key = "RUN" if "正常" in status_filter else ("IDLE" if "待機" in status_filter else "ALARM")
            filtered_df = filtered_df[filtered_df['status_code'].str.contains(stat_key, na=False)]
        if factory_filter != "全部廠區":
            f_key = "越南" if "越南" in factory_filter else "台北"
            filtered_df = filtered_df[filtered_df['factory_id'].str.contains(f_key, na=False)]

        st.markdown(f"**符合條件的 IoT 即時數據筆數**：`{len(filtered_df)}` 筆")
        st.dataframe(filtered_df, use_container_width=True)

    # ==================== Tab 2: 新增生產工單與排程 ====================
    with tab2:
        st.markdown("#### ➕ 發布新生產工單與 IoT 參數綁定")
        with st.form("new_mes_form"):
            c1, c2 = st.columns(2)
            with c1:
                device_id = st.text_input("IoT 射出機編號 *", value="INJ-MACHINE-02")
                factory_id = st.selectbox("生產廠區", ["越南平陽廠", "台北總廠"])
                barrel_temp = st.number_input("設定桶溫 (°C)", value=215.0, step=0.5)
                inj_pressure = st.number_input("設定射出壓力 (bar)", value=1300.0, step=10.0)
            with c2:
                cycle_time = st.number_input("預估循環週期 (秒)", value=30.0, step=0.1)
                status_code = st.selectbox("初始機台狀態", ["🟢 正常運轉 (RUN)", "🟡 待機中 (IDLE)", "🔴 異常警報 (ALARM)"])
                note = st.text_area("生產批次備註", placeholder="輸入模具編號或原料批號...")

            if st.form_submit_button("🚀 寫入 IoT 監控日誌至雲端", type="primary", use_container_width=True):
                if device_id:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        insert_sql = """
                            INSERT INTO iot_device_logs (device_id, factory_id, barrel_temperature, injection_pressure, cycle_time, status_code)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        cur.execute(insert_sql, (device_id, factory_id, barrel_temp, inj_pressure, cycle_time, status_code))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 設備 [{device_id}] 即時運行數據已成功寫入 Supabase 資料庫！")
                        st.rerun()
                    except Exception as db_err:
                        st.error(f"❌ 寫入資料庫失敗：{db_err}")
                else:
                    st.warning("請輸入設備編號！")

    # ==================== Tab 3: 機台狀態與生產參數維護 ====================
    with tab3:
        st.markdown("#### ⚙️ 機台維護、狀態重設與資料清理")
        target_log_id = st.text_input("輸入要刪除或維護的 IoT Log ID (數字編號)", placeholder="例: 1")
        
        if target_log_id:
            with st.form("edit_mes_form"):
                st.warning(f"⚠️ 您正在準備刪除編號為 [{target_log_id}] 的 IoT 運行紀錄。")
                submitted_delete = st.form_submit_button("🗑️ 確認刪除此筆 IoT 紀錄", type="secondary", use_container_width=True)

                if submitted_delete:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM iot_device_logs WHERE id = %s", (int(target_log_id),))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🗑️ IoT 紀錄 ID [{target_log_id}] 已自系統中刪除！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗：{e}")
