import psycopg2
import pandas as pd
import streamlit as st

# Supabase 雲端 PostgreSQL 連線字串
SUPABASE_CONN_STR = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"

def get_db_connection():
    """建立並回傳一個新的 Supabase 資料庫連線"""
    try:
        conn = psycopg2.connect(SUPABASE_CONN_STR)
        return conn
    except Exception as e:
        st.error(f"❌ 資料庫連線失敗：{e}")
        return None

def execute_query(query, params=None):
    """執行寫入、更新或刪除等 SQL 指令"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ 執行 SQL 指令錯誤：{e}")
        if conn:
            conn.close()
        return False

def fetch_data_as_df(query, params=None):
    """執行查詢 SQL 並直接回傳 Pandas DataFrame"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    try:
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ 讀取資料錯誤：{e}")
        if conn:
            conn.close()
        return pd.DataFrame()
