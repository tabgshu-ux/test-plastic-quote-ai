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
    
    create_tables_sql = """
    -- 1. 跨國廠區/分公司動態主檔表 (factories)
    CREATE TABLE IF NOT EXISTS factories (
        factory_id VARCHAR(50) PRIMARY KEY,
        factory_name VARCHAR(100) NOT NULL,
        country VARCHAR(50) NOT NULL,
        currency VARCHAR(10) DEFAULT 'USD',
        status VARCHAR(20) DEFAULT '營運中',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 2. 跨國部門主檔表 (departments)
    CREATE TABLE IF NOT EXISTS departments (
        dept_id VARCHAR(50) PRIMARY KEY,
        dept_name VARCHAR(100) NOT NULL,
        factory_location VARCHAR(20) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 3. 使用者帳號表 (users)
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        dept_id VARCHAR(50) REFERENCES departments(dept_id),
        role VARCHAR(30) DEFAULT 'User',
        status VARCHAR(20) DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 4. 模組與網頁權限表 (module_permissions)
    CREATE TABLE IF NOT EXISTS module_permissions (
        id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
        module_name VARCHAR(100) NOT NULL,
        can_access BOOLEAN DEFAULT TRUE,
        UNIQUE(user_id, module_name)
    );

    -- 5. IoT 設備即時連線 Log 表 (iot_device_logs) - 新增
    CREATE TABLE IF NOT EXISTS iot_device_logs (
        id SERIAL PRIMARY KEY,
        device_id VARCHAR(50) NOT NULL,
        factory_id VARCHAR(50),
        barrel_temperature NUMERIC(5,2),
        injection_pressure NUMERIC(6,2),
        cycle_time NUMERIC(5,2),
        status_code VARCHAR(20),
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 6. 員工資料表 (employees)
    CREATE TABLE IF NOT EXISTS employees (
        employee_id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        factory_location VARCHAR(20) NOT NULL,
        department VARCHAR(50),
        base_salary NUMERIC(12, 2),
        currency VARCHAR(10) DEFAULT 'VND',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 7. 考勤打卡紀錄表 (clock_records)
    CREATE TABLE IF NOT EXISTS clock_records (
        id SERIAL PRIMARY KEY,
        employee_id VARCHAR(50) REFERENCES employees(employee_id),
        clock_time TIMESTAMP NOT NULL,
        device_ip VARCHAR(50),
        factory_location VARCHAR(20)
    );

    -- 8. 業務報價單 (quotations)
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

    -- 9. 電子發票解析表 (invoices)
    CREATE TABLE IF NOT EXISTS invoices (
        invoice_id VARCHAR(50) PRIMARY KEY,
        tax_code_mst VARCHAR(50),
        seller_name VARCHAR(150),
        total_amount NUMERIC(15,2),
        currency VARCHAR(10) DEFAULT 'VND',
        invoice_date DATE,
        xml_filename VARCHAR(255)
    );

    -- 10. 資產與模具主檔 (assets)
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

    -- 11. 資產維修履歷 (asset_maintenance)
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
    print("✅ 全套 AI ERP 資料庫（含 IoT 設備監控、動態廠區、權限管理與財務）Schema 初始化完成！")

if __name__ == "__main__":
    init_db()
