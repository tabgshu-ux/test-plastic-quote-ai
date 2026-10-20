import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

# 1. 頁面基本設定 (Mobile-First & 企業級外觀)
st.set_page_config(
    page_title="SaaS Enterprise Multi-Tenant AI-ERP & Master Hub",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 自定義精緻企業風 CSS 美化 (UI/UX Styling)
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .card-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #1e293b;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 初始化全域定價策略、匯率中樞與多租戶資料庫
if "global_pricing" not in st.session_state:
    st.session_state.global_pricing = {
        "enterprise_base_fee": 150,
        "standard_base_fee": 80,
        "extra_dept_fee": 5
    }

if "global_fx_rates" not in st.session_state:
    st.session_state.global_fx_rates = {
        "USD": 1.0,
        "TWD": 31.50,
        "VND": 25400.00,
        "RMB": 7.20
    }

if "tenants_db" not in st.session_state:
    st.session_state.tenants_db = {
        "tenant_vina_水电": {
            "name": "🇻🇳 越南平陽水電工程有限公司",
            "region": "越南 (Binh Duong, VN)",
            "plan": "旗艦版 (Enterprise)",
            "price_usd": 170,
            "expiry_date": "2027-10-20",
            "org_nodes": [
                {"id": "n_1", "name": "👑 總經理室", "type": "高階決策層", "parent": "無 (頂層)", "modules": ["全球戰情室", "P&L"]},
                {"id": "n_2", "name": "⚙️ 工程部", "type": "營運部門", "parent": "👑 總經理室", "modules": ["工程估驗", "施工日報"]},
                {"id": "n_3", "name": "📦 平陽廠原物料倉庫", "type": "實體據點/庫位", "parent": "👑 總經理室", "modules": ["庫存管理"]}
            ],
            "iot_devices": [{"dev_id": "DEV-01", "name": "平陽廠大門人臉辨識機", "type": "人臉辨識", "ip": "192.168.10.50", "status": "🟢 聯機中"}],
            "ap_invoices": [{"invoice_no": "000123", "supplier": "越南材料行", "items": "PVC管", "qty": "50支", "amount_vnd": "15,000,000", "status": "🔴 待付款"}],
            "staff": [
                {"name": "許福村 (公司老闆)", "email": "fuchun@vina.com", "role": "Tenant Admin (最高權限)"},
                {"name": "阮文安 (越籍會計)", "email": "an.nguyen@vina.com", "role": "財務與會計專員"}
            ],
            "audit_logs": [
                {"time": "2026-10-20 14:10:22", "user": "阮文安 (越籍會計)", "action": "上傳並解析越南紅發票 (編號: 000123)", "ip": "192.168.10.15"}
            ]
        },
        "tenant_taipei_wash": {
            "name": "🇹🇼 台北極速智慧洗車坊",
            "region": "台灣 (Taipei, TW)",
            "plan": "標準版 (Standard)",
            "price_usd": 80,
            "expiry_date": "2026-11-05",
            "org_nodes": [
                {"id": "w_1", "name": "👑 台北總店長室", "type": "高階決策層", "parent": "無 (頂層)", "modules": ["營收戰情"]},
                {"id": "w_2", "name": "🚗 洗車美容部", "type": "營運部門", "parent": "👑 台北總店長室", "modules": ["會員預約", "水刀聯動"]}
            ],
            "iot_devices": [{"dev_id": "W-01", "name": "入口車牌辨識 (ANPR)", "type": "車牌辨識", "ip": "10.0.0.15", "status": "🟢 運作中"}],
            "ap_invoices": [],
            "staff": [{"name": "張店長", "email": "manager@wash.com", "role": "Tenant Admin"}],
            "audit_logs": [{"time": "2026-10-19 10:00:00", "user": "張店長", "action": "初始化台北洗車坊租戶後台", "ip": "1.2.3.4"}]
        }
    }

# 追蹤目前的登入模式："Master" (總控台) 或 具體某個 Tenant Key (租戶後台)
if "current_portal" not in st.session_state:
    st.session_state.current_portal = "Master"

# 4. 側邊欄：乾淨清晰的導覽與身分切換
with st.sidebar:
    st.image("https://img.icons8.com/color/96/company.png", width=64)
    st.markdown("### 🌐 SaaS 多租戶 AI-ERP 平台")
    
    lang = st.selectbox("選擇語系 / Select Language", ["繁體中文", "English", "Tiếng Việt (越南語)", "简体中文"])
    
    st.markdown("---")
    st.markdown("🔒 **[系統身分切換]**")
    
    portal_mode = st.radio(
        "選擇操作視角",
        ["👑 SaaS 平台總控台 (Master Hub)", "🏢 進入客戶租戶公司後台 (Tenant Portal)"]
    )
    
    if portal_mode == "👑 SaaS 平台總控台 (Master Hub)":
        st.session_state.current_portal = "Master"
    else:
        # 下拉選單只在需要進去看個別客戶時使用，平常在總控台用表格搜尋
        selected_t_key = st.selectbox(
            "選擇要模擬進入的公司租戶",
            options=list(st.session_state.tenants_db.keys()),
            format_func=lambda x: st.session_state.tenants_db[x]["name"]
        )
        st.session_state.current_portal = selected_t_key

    is_master = (st.session_state.current_portal == "Master")
    
    st.markdown("---")
    st.markdown("### 📌 系統導覽選單")
    
    if is_master:
        menu_choice = st.radio(
            "選擇總控台模組",
            [
                "🏢 全球租戶動態總覽與搜尋中心 (Tenants Hub)",
                "💱 全球多幣別與即時匯率中樞 (Global FX)",
                "⚙️ 全球定價策略與費率自訂 (Pricing)"
            ]
        )
    else:
        current_t_name = st.session_state.tenants_db[st.session_state.current_portal]["name"]
        menu_choice = st.radio(
            f"內部模組 ({current_t_name})",
            [
                "🖱️ 公司組織與據點自助設定 (超清楚版)",
                "👥 員工帳號與權限角色管理 (RBAC)",
                "🔒 系統資安稽核日誌 (Audit Trail)",
                "🤖 AI 硬體與車牌/人臉辨識掛接",
                "🇻🇳 越南紅發票與應付帳款 (AP)"
            ]
        )
    
    st.markdown("---")
    if st.button("🚪 登出系統", use_container_width=True):
        st.info("已安全登出系統。")

# 5. 主畫面邏輯路由
if is_master:
    # ==================== SaaS 總控台：強大租戶管理與搜尋中心 ====================
    if "全球租戶動態總覽" in menu_choice:
        st.markdown("## 🏢 SaaS 平台總控台：全球企業租戶動態總覽與搜尋中心 (Tenants Management Hub)")
        st.info("💡 *在此處您可以檢視所有已註冊的企業客戶。支援即時關鍵字搜尋，並可依據【價格】、【地區位置】、【使用到期日】進行智慧排序與過濾！*")
        
        # 搜尋與篩選控制面板
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                search_keyword = st.text_input("🔍 搜尋公司名稱或代碼", placeholder="輸入關鍵字...")
            with s2:
                region_filter = st.selectbox("🌍 依地區位置過濾", ["全部地區", "越南 (Binh Duong, VN)", "台灣 (Taipei, TW)"])
            with s3:
                sort_by = st.selectbox("📊 排序依據", ["價格由高到低 (Price)", "使用到期日最近 (Expiry)", "公司名稱筆畫 (Name)"])
            with s4:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("➕ 新增企業客戶租戶", type="primary", use_container_width=True):
                    st.success("🎉 請前往模組市集或發布連結供客戶自助註冊！")
            st.markdown('</div>', unsafe_allow_html=True)

        # 整理租戶資料成 DataFrame
        tenant_list_data = []
        for t_key, t_val in st.session_state.tenants_db.items():
            tenant_list_data.append({
                "租戶代碼": t_key,
                "公司名稱": t_val["name"],
                "地區位置": t_val["region"],
                "訂閱方案": t_val["plan"],
                "每月價格 (USD)": t_val["price_usd"],
                "合約到期日": t_val["expiry_date"],
                "部門數": len(t_val["org_nodes"]),
                "狀態": "🟢 正常營運"
            })
        df_tenants = pd.DataFrame(tenant_list_data)

        # 套用搜尋與過濾邏輯
        if search_keyword:
            df_tenants = df_tenants[df_tenants.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False)).any(axis=1)]
        if region_filter != "全部地區":
            df_tenants = df_tenants[df_tenants["地區位置"] == region_filter]
        
        if "價格由高到低" in sort_by:
            df_tenants = df_tenants.sort_values(by="每月價格 (USD)", ascending=False)
        elif "使用到期日最近" in sort_by:
            df_tenants = df_tenants.sort_values(by="合約到期日", ascending=True)

        # 顯示互動表格
        st.markdown("### 📋 企業租戶列表與管理")
        st.dataframe(df_tenants, use_container_width=True)
        
        # 快速進入租戶管理捷徑
        st.markdown("### 🚀 快速切換至指定客戶租戶後台")
        quick_cols = st.columns(len(st.session_state.tenants_db))
        for idx, (t_key, t_val) in enumerate(st.session_state.tenants_db.items()):
            with quick_cols[idx]:
                if st.button(f"📂 進入：{t_val['name']}", use_container_width=True):
                    st.session_state.current_portal = t_key
                    st.rerun()

    elif "全球多幣別與即時匯率引擎" in menu_choice:
        st.markdown("## 💱 SaaS 平台總控台：全球多幣別與即時匯率引擎 (Global FX Engine)")
        st.info("💡 維護全平台的基準匯率（USD/TWD/VND/RMB）。")
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            with st.form("fx_form"):
                fx = st.session_state.global_fx_rates
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.number_input("美元 (USD)", value=fx["USD"], disabled=True)
                with c2: nt = st.number_input("台幣 (TWD)", value=fx["TWD"], step=0.1)
                with c3: nv = st.number_input("越南盾 (VND)", value=fx["VND"], step=10.0)
                with c4: nr = st.number_input("人民幣 (RMB)", value=fx["RMB"], step=0.01)
                if st.form_submit_button("💾 立即更新全平台即時匯率", type="primary", use_container_width=True):
                    st.session_state.global_fx_rates["TWD"] = nt
                    st.session_state.global_fx_rates["VND"] = nv
                    st.session_state.global_fx_rates["RMB"] = nr
                    st.success("🎉 匯率更新成功！")
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("## ⚙️ SaaS 平台總控台：全球定價策略與費率自訂")
        st.info("設定全平台的方案月費與部門加購價。")

else:
    # ==================== 個別租戶後台 (超清楚、區塊化設定介面) ====================
    current_tenant = st.session_state.tenants_db[st.session_state.current_portal]
    
    if "組織與據點自助設定" in menu_choice:
        st.markdown(f"## 🖱️ {current_tenant['name']}：組織樹與實體據點自助設定")
        st.info("💡 *極致清晰的區塊化設定！您可以直接新增部門或實體倉庫，系統會即時在右側呈現最新的組織與據點樹狀圖。*")
        
        col_set, col_view = st.columns([1, 1])
        
        with col_set:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### ➕ 新增部門或實體據點")
            with st.form("dept_add_form"):
                new_dept = st.text_input("部門或倉庫名稱*", placeholder="例：平陽廠維修中心 / 會計部")
                dept_type = st.selectbox("屬性分類", ["營運/行政部門 (Department)", "實體據點/倉庫 (Location/Warehouse)"])
                existing_parents = [n["name"] for n in current_tenant["org_nodes"]]
                chosen_parent = st.selectbox("指定上級掛載點 (Parent)", existing_parents)
                
                submitted_dept = st.form_submit_button("🧱 確認新增並掛載", type="primary", use_container_width=True)
                if submitted_dept:
                    if new_dept:
                        current_tenant["org_nodes"].append({
                            "id": f"n_{len(current_tenant['org_nodes'])+1}",
                            "name": new_dept,
                            "type": dept_type,
                            "parent": chosen_parent,
                            "modules": ["日常作業"]
                        })
                        current_tenant["audit_logs"].insert(0, {
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "user": current_tenant["staff"][0]["name"],
                            "action": f"新增{dept_type}：{new_dept} (掛載於 {chosen_parent})",
                            "ip": "192.168.10.5"
                        })
                        st.success(f"🎉 成功新增 [{new_dept}] 並完成掛載！")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_view:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 🌳 貴公司目前的組織與據點樹狀圖")
            for node in current_tenant["org_nodes"]:
                is_loc = "實體據點" in node['type'] or "倉庫" in node['name']
                indent = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;┗ 📦 " if is_loc else ("&nbsp;&nbsp;&nbsp;&nbsp;┗ 📂 " if node["parent"] != "無 (頂層)" else "👑 ")
                border_color = "#10b981" if is_loc else "#3b82f6"
                st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 10px; border-radius: 6px; margin-bottom: 8px; border-left: 4px solid {border_color};">
                        <b>{indent}{node['name']}</b> <span style="font-size: 11px; color: gray;">({node['type']})</span><br>
                        <span style="font-size: 11px; color: #0f766e;">📌 上級掛載：{node['parent']}</span>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    elif "員工帳號與權限角色管理" in menu_choice:
        st.markdown(f"## 👥 {current_tenant['name']}：企業內部員工帳號與權限角色管理 (RBAC)")
        st.info("💡 在此處建立公司內部的員工帳號與指派職務。")
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            with st.form("staff_form"):
                s_name = st.text_input("員工姓名*", placeholder="例：陳大為")
                s_email = st.text_input("電子郵件 (登入帳號)*", placeholder="例：david@company.com")
                s_role = st.selectbox("指派權限角色", ["財務與會計專員", "現場工地主任", "總務與人事專員", "採購專員", "租戶系統管理員"])
                if st.form_submit_button("👤 建立員工帳號", type="primary", use_container_width=True):
                    if s_name and s_email:
                        current_tenant["staff"].append({"name": s_name, "email": s_email, "role": s_role})
                        st.success(f"🎉 成功建立員工 [{s_name}]！")
            st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(current_tenant["staff"]), use_container_width=True)

    elif "資安稽核日誌" in menu_choice:
        st.markdown(f"## 🔒 {current_tenant['name']}：系統資安稽核日誌與操作軌跡追蹤")
        st.info("💡 記錄公司內部所有員工的操作軌跡。")
        st.dataframe(pd.DataFrame(current_tenant["audit_logs"]), use_container_width=True)

    elif "AI 硬體與車牌" in menu_choice:
        st.markdown(f"## 🤖 {current_tenant['name']}：AI 硬體與車牌/人臉辨識自助掛接")
        if current_tenant["iot_devices"]:
            st.dataframe(pd.DataFrame(current_tenant["iot_devices"]), use_container_width=True)

    else:
        st.markdown(f"## 🇻🇳 {current_tenant['name']}：越南紅發票與應付帳款 (AP)")
        if current_tenant["ap_invoices"]:
            st.dataframe(pd.DataFrame(current_tenant["ap_invoices"]), use_container_width=True)
