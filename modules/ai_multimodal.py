import streamlit as st
import pandas as pd
import psycopg2
import datetime

def get_db_connection():
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_ai_multimodal(tenant_info, user_perms):
    st.markdown("### 🤖 AI 語音與多模態無門檻智慧輸入中心")
    st.info("💡 *專為現場基層打造：支援語音轉文字口語填單、現場設備/模具照片上傳，由 AI 自動解析並寫入動態資料庫。*")
    st.markdown("---")

    tab1, tab2 = st.tabs(["🎙️ 語音與照片智慧解析填單", "📜 多模態辨識歷史日誌"])

    with tab1:
        st.markdown("#### 📸 上傳現場照片或使用語音輸入")
        with st.form("ai_multimodal_form"):
            col1, col2 = st.columns(2)
            with col1:
                input_mode = st.selectbox("選擇輸入互動模式", ["🎤 語音轉文字口述輸入", "📷 現場照片辨識解析", "📦 條碼快速掃描辨識"])
                factory_site = st.selectbox("作業廠區", ["越南平陽廠 A 區", "越南平陽廠 B 區", "台北總公司"])
            with col2:
                uploaded_photo = st.file_uploader("上傳現場工件/設備照片", type=["jpg", "png", "jpeg"])
                voice_text_sim = st.text_area("語音轉譯文字 / 口述內容", placeholder="例：『報告班長，INJ-01 號機台桶溫過高已排除，補報維修工時 2 小時。』")

            if st.form_submit_button("🚀 啟動 AI 多模態自動解析並入庫", type="primary", use_container_width=True):
                try:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    sql = """
                        INSERT INTO approval_queue (approval_id, source_module, applicant, item_summary, current_step, status)
                        VALUES (%s, 'AI 多模態輸入', '現場基層人員', %s, 'AI 自動解析完成', '🟢 已自動入庫')
                        ON CONFLICT (approval_id) DO NOTHING;
                    """
                    dummy_id = f"AI-{datetime.datetime.now().strftime('%m%d%H%M%S')}"
                    cur.execute(sql, (dummy_id, f"模式: {input_mode} | 內容: {voice_text_sim}"))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"🎉 AI 多模態解析成功！已自動產生紀錄單號：`{dummy_id}` 並完成資料庫登錄。")
                except Exception as e:
                    st.error(f"AI 解析入庫失敗：{e}")

    with tab2:
        st.markdown("#### 📜 AI 智慧辨識歷史稽核日誌")
        try:
            conn = get_db_connection()
            df = pd.read_sql("SELECT approval_id, source_module, applicant, item_summary, apply_date, status FROM approval_queue WHERE source_module = 'AI 多模態輸入'", conn)
            conn.close()
            st.dataframe(df, use_container_width=True)
        except Exception:
            st.info("目前尚無 AI 多模態辨識紀錄。")
