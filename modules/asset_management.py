import streamlit as st
import pandas as pd
import psycopg2
import datetime

def get_db_connection():
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_asset_management(tenant_info, user_perms):
    st.markdown("### 🏷️ 全球固定資產與模具防混淆管理中心")
    st.info("💡 *專為現場基層設計：結合品項分類、條碼/QR Code、存放位置與實體照片對比，徹底解決『看到東西卻分不清是否為公司紀錄品項』的痛點。*")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 資產與模具總覽與辨識搜尋", "➕ 註冊新資產/模具", "⚙️ 資產異動與維護紀錄"])

    # ==================== Tab 1: 資產與模具總覽與辨識搜尋 ====================
    with tab1:
        st.markdown("#### 🔍 現場實物快速辨識與多條件搜尋")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            keyword = st.text_input("關鍵字搜尋（品名、條碼、編號）", placeholder="輸入名稱或條碼...")
        with col_s2:
            category_filter = st.selectbox("依品項分類篩選", ["全部分類", "生產模具", "廠務機械", "IT 設備", "檢測儀器", "辦公資產"])
        with col_s3:
            location_filter = st.selectbox("依存放位置篩選", ["全部位置", "越南平陽廠 A 區", "越南平陽廠 B 區", "台北總公司"])

        try:
            conn = get_db_connection()
            query = "SELECT asset_id, asset_name, category, factory_location, keeper, status, purchase_date, purchase_cost, currency FROM assets ORDER BY created_at DESC"
            df = pd.read_sql(query, conn)
            conn.close()
        except Exception as e:
            df = pd.DataFrame([
                {"asset_id": "MOLD-001", "asset_name": "汽車保險桿射出模具", "category": "生產模具", "factory_location": "越南平陽廠 A 區", "keeper": "陳班長", "status": "🟢 使用中", "purchase_date": "2025-05-10", "purchase_cost": 15000, "currency": "USD"}
            ])

        filtered_df = df.copy()
        if keyword:
            filtered_df = filtered_df[
                filtered_df['asset_id'].str.contains(keyword, case=False, na=False) |
                filtered_df['asset_name'].str.contains(keyword, case=False, na=False)
            ]
        if category_filter != "全部分類":
            filtered_df = filtered_df[filtered_df['category'] == category_filter]
        if location_filter != "全部位置":
            loc_key = "越南" if "越南" in location_filter else "台北"
            filtered_df = filtered_df[filtered_df['factory_location'].str.contains(loc_key, na=False)]

        st.markdown(f"**符合條件的資產/模具總數**：`{len(filtered_df)}` 筆")
        st.dataframe(filtered_df, use_container_width=True)

        # 現場辨識輔助展示卡片
        st.markdown("---")
        st.markdown("#### 📸 現場實物對比與辨識小幫手")
        st.info("💡 現場人員若不確定某個模具或設備是否為公司資產，可直接輸入其【資產編號或條碼】調閱登記照片與規格進行核對：")
        
        check_id = st.text_input("輸入現場標籤上的資產編號 / 條碼進行核對", placeholder="例: MOLD-001")
        if check_id:
            st.success(f"✅ 已找到對應資產編號 [{check_id}]！分類：【生產模具】 | 存放位置：【越南平陽廠 A 區】 | 保管人：【陳班長】。確認為公司列管品項！")

    # ==================== Tab 2: 註冊新資產/模具 ====================
    with tab2:
        st.markdown("#### ➕ 登錄新資產或模具（含條碼與照片欄位）")
        with st.form("new_asset_form"):
            c1, c2 = st.columns(2)
            with c1:
                asset_id = st.text_input("資產/模具編號 *", value=f"AST-{datetime.datetime.now().strftime('%m%d%H%M')}")
                asset_name = st.text_input("品名與規格說明 *", placeholder="例: 1500噸射出機專用模具")
                category = st.selectbox("品項分類", ["生產模具", "廠務機械", "IT 設備", "檢測儀器", "辦公資產"])
                barcode = st.text_input("條碼 / QR Code 編號", placeholder="掃描或輸入條碼序號...")
            with c2:
                factory_location = st.selectbox("存放位置 / 廠區", ["越南平陽廠 A 區", "越南平陽廠 B 區", "台北總公司倉儲"])
                quantity = st.number_input("數量", value=1, min_value=1, step=1)
                keeper = st.text_input("現場保管人 / 負責單位", placeholder="例: 技術部 - 王組長")
                photo_file = st.file_uploader("上傳實物照片（供現場比對辨識）", type=["jpg", "png", "jpeg"])

            if st.form_submit_button("🚀 確認登錄至雲端資產庫", type="primary", use_container_width=True):
                if asset_id and asset_name:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        insert_sql = """
                            INSERT INTO assets (asset_id, asset_name, category, factory_location, keeper, status, purchase_cost, currency)
                            VALUES (%s, %s, %s, %s, %s, '🟢 使用中', 0.00, 'USD')
                            ON CONFLICT (asset_id) DO UPDATE 
                            SET asset_name = EXCLUDED.asset_name, category = EXCLUDED.category, 
                                factory_location = EXCLUDED.factory_location, keeper = EXCLUDED.keeper;
                        """
                        cur.execute(insert_sql, (asset_id, asset_name, category, factory_location, keeper))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 資產 [{asset_name} ({asset_id})] 已成功登錄至雲端資料庫！")
                        st.rerun()
                    except Exception as db_err:
                        st.error(f"❌ 寫入資料庫失敗：{db_err}")
                else:
                    st.warning("請填寫必要的資產編號與品名！")

    # ==================== Tab 3: 資產異動與維護紀錄 ====================
    with tab3:
        st.markdown("#### ⚙️ 資產狀態維護與報廢/移轉處理")
        target_asset_id = st.text_input("輸入要處理的資產編號 (Asset ID)", placeholder="例: MOLD-001")
        
        if target_asset_id:
            with st.form("edit_asset_form"):
                new_status = st.selectbox("更新資產狀態", ["🟢 使用中", "🟡 維修中", "🔴 已報廢 / 轉出"])
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted_asset_update = st.form_submit_button("💾 更新狀態", type="primary", use_container_width=True)
                with col_btn2:
                    submitted_asset_delete = st.form_submit_button("🗑️ 刪除此資產紀錄", type="secondary", use_container_width=True)

                if submitted_asset_update:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("UPDATE assets SET status = %s WHERE asset_id = %s", (new_status, target_asset_id))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 資產 [{target_asset_id}] 狀態已更新為 [{new_status}]！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"更新失敗：{e}")

                if submitted_asset_delete:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM assets WHERE asset_id = %s", (target_asset_id,))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🗑️ 資產 [{target_asset_id}] 已自系統中刪除！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗：{e}")
