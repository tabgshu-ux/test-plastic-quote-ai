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
    
    # 建立全系統 PostgreSQL 核心資料表 Schema
    create_tables_sql = """
    -- 1. 跨國部門主檔表 (departments)
    CREATE TABLE IF NOT EXISTS departments (
        dept_id VARCHAR(50) PRIMARY KEY,
        dept_name VARCHAR(100) NOT NULL,
        factory_location VARCHAR(20) NOT NULL, -- 'TW', 'DG', 'BH'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 2. 使用者帳號表 (users)
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        dept_id VARCHAR(50) REFERENCES departments(dept_id),
        role VARCHAR(30) DEFAULT 'User', -- 'Admin', 'Manager', 'User'
        status VARCHAR(20) DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 3. 模組頁面授權權限表 (module_permissions)
    CREATE TABLE IF NOT EXISTS module_permissions (
        id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
        module_name VARCHAR(100) NOT NULL, -- 如: '營運戰情室', '財務', '業務/行銷'
        can_access BOOLEAN DEFAULT TRUE,
        UNIQUE(user_id, module_name)
    );

    -- 4. 員工基本資料表 (employees)
    CREATE TABLE IF NOT EXISTS employees (
        employee_id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        factory_location VARCHAR(20) NOT NULL,
        department VARCHAR(50),
        base_salary NUMERIC(12, 2),
        currency VARCHAR(10) DEFAULT 'VND',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 5. 考勤打卡紀錄表 (clock_records)
    CREATE TABLE IF NOT EXISTS clock_records (
        id SERIAL PRIMARY KEY,
        employee_id VARCHAR(50) REFERENCES employees(employee_id),
        clock_time TIMESTAMP NOT NULL,
        device_ip VARCHAR(50),
        factory_location VARCHAR(20)
    );

    -- 6. 業務報價單主檔 (quotations)
    CREATE TABLE IF NOT EXISTS quotations (
        quote_id VARCHAR(50) PRIMARY KEY,
        customer_name VARCHAR(100),
        part_length NUMERIC(8,2),
        part_width NUMERIC(8,2),
        part_thickness NUMERIC(8,2),
        clamping_force_tons NUMERIC(8,2),
        total_amount NUMERIC(12,2),
        currency VARCHAR(10) DEFAULT 'USD',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 7. 通用信箱發票解析表 (invoices)
    CREATE TABLE IF NOT EXISTS invoices (
        invoice_id VARCHAR(50) PRIMARY KEY,
        tax_code_mst VARCHAR(50),
        seller_name VARCHAR(150),
        total_amount NUMERIC(15,2),
        currency VARCHAR(10) DEFAULT 'VND',
        invoice_date DATE,
        xml_filename VARCHAR(255)
    );

    -- 8. 資產與模具主檔 (assets)
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

    -- 9. 資產與模具維修履歷 (asset_maintenance)
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
    print("✅ 全套 AI ERP 資料庫（含權限管理、薪資發票、報價與資產）Schema 初始化完成！")

if __name__ == "__main__":
    init_db()
