import psycopg2
import os

def init_db():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "global_erp"),
        user=os.getenv("DB_USER", "erp_user"),
        password=os.getenv("DB_PASSWORD", "your_password"),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "5432")
    )
    cur = conn.cursor()
    
    # 建表 SQL
    create_tables_sql = """
    CREATE TABLE IF NOT EXISTS assets (
        asset_id VARCHAR(50) PRIMARY KEY,
        asset_name VARCHAR(100) NOT NULL,
        category VARCHAR(50) NOT NULL,
        factory_location VARCHAR(20) NOT NULL,
        status VARCHAR(20) DEFAULT '在用',
        purchase_date DATE,
        purchase_cost NUMERIC(15, 2),
        currency VARCHAR(10) DEFAULT 'USD',
        specifications JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS asset_maintenance (
        id SERIAL PRIMARY KEY,
        asset_id VARCHAR(50) REFERENCES assets(asset_id) ON DELETE CASCADE,
        maintenance_date DATE NOT NULL,
        maintenance_type VARCHAR(30),
        description TEXT,
        cost NUMERIC(12, 2) DEFAULT 0,
        currency VARCHAR(10) DEFAULT 'USD',
        technician VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cur.execute(create_tables_sql)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ 資產管理資料表 Schema 初始化完成！")

if __name__ == "__main__":
    init_db()
