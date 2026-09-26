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

    -- 5. IoT 設備即時連線 Log 表 (iot_device_logs)
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
        keeper VARCHAR(100),
        status VARCHAR(20) DEFAULT '🟢 使用中',
        purchase_date DATE,
        scrap_date DATE,
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

    -- ====================================================
    # 🏢 總務部 (GA) 與 簽核中心 (Workflow) 擴充資料表
    -- ====================================================

    -- 12. 總務用品採購與請購單表 (ga_procurements) - 升級多幣別支援
    CREATE TABLE IF NOT EXISTS ga_procurements (
        po_id VARCHAR(50) PRIMARY KEY,
        item_name VARCHAR(150) NOT NULL,
        category VARCHAR(50) NOT NULL,
        quantity INT DEFAULT 1,
        currency VARCHAR(10) DEFAULT 'VND',           -- 🟢 幣別 (VND, TWD, RMB, USD)
        unit_price NUMERIC(15,2) DEFAULT 0.00,        -- 🟢 原幣單價
        estimated_cost NUMERIC(15,2) DEFAULT 0.00,    -- 🟢 當地原幣預估總金額
        estimated_cost_usd NUMERIC(15,2) DEFAULT 0.00,-- 🟢 折合美金總金額 (戰情室專用)
        dept_name VARCHAR(50),
        applicant VARCHAR(100) NOT NULL,
        status VARCHAR(30) DEFAULT '🟡 簽核中',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 13. 零用金與行政費用報銷表 (ga_petty_cash)
    CREATE TABLE IF NOT EXISTS ga_petty_cash (
        pc_id VARCHAR(50) PRIMARY KEY,
        apply_date DATE NOT NULL,
        applicant VARCHAR(100) NOT NULL,
        expense_type VARCHAR(50) NOT NULL,
        amount NUMERIC(12,2) NOT NULL,
        currency VARCHAR(10) DEFAULT 'VND',           -- 預設當地貨幣
        description TEXT,
        status VARCHAR(30) DEFAULT '🟡 簽核中',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 14. 行政公文與合同列管表 (ga_contracts)
    CREATE TABLE IF NOT EXISTS ga_contracts (
        contract_id VARCHAR(50) PRIMARY KEY,
        doc_type VARCHAR(50) NOT NULL,
        title VARCHAR(200) NOT NULL,
        partner_unit VARCHAR(150) NOT NULL,
        sign_date DATE NOT NULL,
        end_date DATE NOT NULL,
        owner VARCHAR(100),
        status VARCHAR(30) DEFAULT '🟢 有效中',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 15. 電子簽核審核中心佇列主檔 (approval_queue)
    CREATE TABLE IF NOT EXISTS approval_queue (
        approval_id VARCHAR(50) PRIMARY KEY,
        source_module VARCHAR(100) NOT NULL,
        applicant VARCHAR(100) NOT NULL,
        item_summary TEXT NOT NULL,
        apply_date DATE DEFAULT CURRENT_DATE,
        current_step VARCHAR(100) DEFAULT '關卡 1：主管審核',
        status VARCHAR(30) DEFAULT '🟡 待簽核',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 16. 電子簽核歷程 Log 明細表 (approval_logs)
    CREATE TABLE IF NOT EXISTS approval_logs (
        id SERIAL PRIMARY KEY,
        approval_id VARCHAR(50) REFERENCES approval_queue(approval_id) ON DELETE CASCADE,
        reviewer VARCHAR(100) NOT NULL,
        reviewer_role VARCHAR(50),
        action VARCHAR(20) NOT NULL, -- '🟢 同意' 或 '🔴 駁回'
        comments TEXT,
        reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 17. 跨國即時與歷史匯率檔 (currency_rates) - 新增
    CREATE TABLE IF NOT EXISTS currency_rates (
        id SERIAL PRIMARY KEY,
        currency_code VARCHAR(10) NOT NULL UNIQUE, -- 如 VND, TWD, RMB, EUR
        rate_to_usd NUMERIC(15, 6) NOT NULL,       -- 對美金匯率 (例如 1 USD = 25420 VND)
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    cur.execute(create_tables_sql)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ 全套 AI ERP 資料庫（含多幣別採購、IoT 設備監控、總務部 GA、電子簽核 Workflow）Schema 初始化完成！")

if __name__ == "__main__":
    init_db()
