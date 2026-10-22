import streamlit as st

st.set_page_config(page_title="全球多租戶 SaaS AI ERP 平台", layout="wide")

# 初始化 Session State 狀態
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "master_admins" not in st.session_state:
    st.session_state.master_admins = ["admin", "superadmin"]
if "tenant_list" not in st.session_state:
    st.session_state.tenant_list = [
        {
            "tenant_id": "TENANT-001",
            "company_name": "裕豐電機工業 (Reetech Industrial)",
            "tax_id": "0312345678",
            "plan": "🚀 企業旗艦版 (Enterprise Flagship)",
            "pricing_usd": 3000,
            "expiry": "2027-12-31",
            "modules": ["總經理室", "管理部", "工程中心", "ISO品質合規", "ESG碳足跡"],
            "org_chart": {
                "1級：總管理處": ["2級：營運中心", "2級：財務處"],
                "2級：營運中心": ["3級：工程課", "3級：品保課"],
                "3級：工程課": ["4級：機構組", "4級：軟體組"]
            }
        }
    ]
if "pricing_plans" not in st.session_state:
    st.session_state.pricing_plans = {
        "企業旗艦版": 3000,
        "標準正式版": 1500,
        "輕量訂閱版": 600
    }

# ==========================================
# 第一層：總控管理員帳號登入驗證 (Login Gateway)
# ==========================================
def render_login():
    st.markdown("## 🔐 平台總控管理員登入驗證")
    st.markdown("請先通過總控驗證以進入全球 SaaS 管理核心。")
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("管理員帳號", placeholder="請輸入帳號 (預設: admin)")
        password = st.text_input("密碼", type="password", placeholder="請輸入密碼 (預設: admin123)")
        submit = st.form_submit_button("登入總控台")
        
        if submit:
            if username in st.session_state.master_admins and password == "admin123":
                st.session_state.logged_in = True
                st.success("登入成功！正在進入總控管理中心...")
                st.rerun()
            else:
                st.error("帳號或密碼錯誤！(預設帳號: admin / 密碼: admin123)")

# ==========================================
# 第二層：總控管理中心 (Master Control Panel)
# ==========================================
def render_master_control():
    st.sidebar.markdown("### 🛠️ 總控導覽選單")
    st.sidebar.info("目前身分：**平台總控管理員 (Master Admin)**")
    if st.sidebar.button("🚪 登出總控系統"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown("## 🏢 平台總控台 - 商業授權與租戶管理中心")
    st.markdown("在此管理所有企業租戶、設定方案定價與拼圖模組，並可進入個別租戶環境。")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 企業租戶總覽與快速進入", "💰 商業方案與拼圖模組設定", "⚙️ 總控台帳號權限管理"])

    # 1. 租戶總覽與新增
    with tab1:
        st.markdown("### 📋 現有企業租戶清單")
        search = st.text_input("🔍 快速搜尋租戶（輸入公司名稱或編號）", placeholder="例如：裕豐 或 TENANT-001")
        
        for t in st.session_state.tenant_list:
            if search and search.lower() not in t["company_name"].lower() and search.lower() not in t["tenant_id"].lower():
                continue
            
            with st.container():
                col_info, col_btn = st.columns([3, 1])
                with col_info:
                    st.markdown(f"#### 🏢 {t['company_name']} (`{t['tenant_id']}`)")
                    st.write(f"• **方案**：{t['plan']} | **年費**：$ {t['pricing_usd']} USD")
                    st.write(f"• **已開通模組**：{', '.join(t['modules'])}")
                with col_btn:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(f"🚀 進入租戶管理", key=f"enter_{t['tenant_id']}"):
                        st.session_state.active_tenant = t['tenant_id']
                        st.rerun()
                st.markdown("---")

        with st.form("add_tenant_form"):
            st.markdown("#### ➕ 新增企業租戶合約")
            new_id = st.text_input("租戶代號", value=f"TENANT-00{len(st.session_state.tenant_list)+1}")
            new_name = st.text_input("公司名稱", placeholder="例如：台灣精密工業股份有限公司")
            new_tax = st.text_input("統一編號", placeholder="87654321")
            new_plan = st.selectbox("選擇商業授權方案", list(st.session_state.pricing_plans.keys()))
            
            if st.form_submit_button("確認建立新租戶"):
                st.session_state.tenant_list.append({
                    "tenant_id": new_id,
                    "company_name": new_name,
                    "tax_id": new_tax,
                    "plan": new_plan,
                    "pricing_usd": st.session_state.pricing_plans[new_plan],
                    "expiry": "2027-12-31",
                    "modules": ["總經理室", "管理部"],
                    "org_chart": {"1級：總管理處": ["2級：管理部"]}
                })
                st.success(f"成功新增租戶：{new_name}！")
                st.rerun()

    # 2. 商業方案與定價設定
    with tab2:
        st.markdown("### 💰 商業方案與拼圖式模組點選設定")
        st.write("在此管理 SaaS 平台的標準授權方案與定價：")
        
        for plan_name, price in st.session_state.pricing_plans.items():
            st.info(f"📌 **{plan_name}** — 年費定價：$ {price} USD")
            
        with st.form("update_price_form"):
            st.markdown("#### 調整方案定價")
            target_plan = st.selectbox("選擇要修改的方案", list(st.session_state.pricing_plans.keys()))
            new_price = st.number_input("新價格 (USD)", value=st.session_state.pricing_plans[target_plan])
            if st.form_submit_button("更新定價"):
                st.session_state.pricing_plans[target_plan] = new_price
                st.success(f"方案 {target_plan} 定價已更新為 $ {new_price} USD！")
                st.rerun()

    # 3. 總控台管理權限新增
    with tab3:
        st.markdown("### ⚙️ 總控台管理員權限設定")
        st.write("目前擁有總控權限的管理員清單：")
        for admin in st.session_state.master_admins:
            st.code(admin)
            
        with st.form("add_admin_form"):
            new_admin_user = st.text_input("新增總控管理員帳號")
            if st.form_submit_button("授予總控權限"):
                if new_admin_user and new_admin_user not in st.session_state.master_admins:
                    st.session_state.master_admins.append(new_admin_user)
                    st.success(f"成功新增總控管理員：{new_admin_user}")
                    st.rerun()

# ==========================================
# 第三層：租戶管理功能 (Tenant Management Hub)
# ==========================================
def render_tenant_management():
    t_id = st.session_state.active_tenant
    tenant = next((t for t in st.session_state.tenant_list if t["tenant_id"] == t_id), None)
    
    if not tenant:
        st.error("找不到此租戶資料！")
        if st.button("返回總控台"):
            del st.session_state.active_tenant
            st.rerun()
        return

    st.sidebar.markdown(f"### 🏢 當前租戶工作區")
    st.sidebar.success(f"**{tenant['company_name']}**")
    if st.sidebar.button("⬅️ 返回平台總控台"):
        del st.session_state.active_tenant
        st.rerun()

    st.markdown(f"## 📊 租戶管理中心 — {tenant['company_name']} (`{tenant['tenant_id']}`)")
    st.markdown("在此檢視租戶費用、勾選拼圖模組，並管理 1~4 級動態組織圖。")
    st.markdown("---")

    tab_fee, tab_mods, tab_org = st.tabs(["💵 租戶費用與合約檢視", "🧩 拼圖式功能模組點選", "🌳 1~4 級租戶組織圖管理"])

    # 1. 租戶費用與方案檢視
    with tab_fee:
        st.markdown("### 💵 財務費用與授權狀態")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"• **統一編號**：{tenant['tax_id']}")
            st.write(f"• **購買商業方案**：{tenant['plan']}")
        with col2:
            st.write(f"• **年度應付費用**：$ {tenant['pricing_usd']} USD")
            st.write(f"• **合約到期日**：{tenant['expiry']}")

    # 2. 拼圖式功能模組點選
    with tab_mods:
        st.markdown("### 🧩 拼圖式功能模組開通管理")
        st.write("勾選該租戶可使用的功能模組：")
        
        all_modules = [
            "總經理室", "管理部", "工程中心", "ISO品質合規", 
            "ESG碳足跡", "國防軍公合規", "財務應付帳款", "智慧倉儲", "數位簽核"
        ]
        
        selected_modules = st.multiselect("已啟用的拼圖模組", all_modules, default=tenant["modules"])
        if st.button("儲存模組變更"):
            tenant["modules"] = selected_modules
            st.success("租戶拼圖模組已成功更新！")
            st.rerun()

    # 3. 租戶組織圖管理 (1~4 級)
    with tab_org:
        st.markdown("### 🌳 1~4 級動態組織架構圖")
        st.write("自由配置該租戶內部的處、部、課、組階層：")
        
        for parent, children in tenant["org_chart"].items():
            st.markdown(f"**📂 {parent}**")
            for child in children:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;┗━ 📄 {child}")
                
        with st.form("org_form"):
            st.markdown("#### 新增組織節點")
            parent_node = st.selectbox("選擇上級節點", list(tenant["org_chart"].keys()))
            new_child = st.text_input("新增下級節點 (例: 3級：品保課 / 4級：檢驗組)")
            if st.form_submit_button("新增組織節點"):
                if new_child:
                    tenant["org_chart"][parent_node].append(new_child)
                    st.success("組織架構更新成功！")
                    st.rerun()

# ==========================================
# 主路由分流邏輯
# ==========================================
if __name__ == "__main__":
    if not st.session_state.logged_in:
        render_login()
    else:
        if "active_tenant" not in st.session_state:
            render_master_control()
        else:
            render_tenant_management()
