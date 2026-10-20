import streamlit as st
import pandas as pd
from datetime import datetime

# ==============================================================================
# 🧩 SaaS 企業級多租戶 AI-ERP 系統 (含圖形化階層組織樹)
# ==============================================================================

st.set_page_config(
    page_title="SaaS Enterprise Modular AI-ERP & Visual Org Chart",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# 3. 初始化全域資料
if "global_pricing" not in st.session_state:
    st.session_state.global_pricing = {"enterprise_base_fee": 150, "standard_base_fee": 80, "extra_dept_fee": 5}

if "global_fx_rates" not in st.session_state:
    st.session_state.global_fx_rates = {"USD": 1.0, "TWD": 31.50, "VND": 25400.00, "RMB": 7.20}

if "tenants_db" not in st.session_state:
    st.session_state.tenants_db = {
        "tenant_vina_水电": {
            "name": "🇻🇳 越南平陽水電工程有限公司",
            "region": "越南 (Binh Duong, VN)",
            "plan": "旗艦版 (Enterprise)",
            "price_usd": 170,
            "expiry_date": "2027-10-20",
            "org_nodes": [
                {"id": "n_1", "name": "董事長 / 總經理室", "type": "最高決策層", "parent": "無 (頂層)", "modules": ["全球戰情室"]},
                {"id": "n_2", "name": "工程技術部", "type": "營運/行政部門", "parent": "董事長 / 總經理室", "modules": ["工程估驗"]},
                {"id": "n_3", "name": "平陽美福營業所", "type": "營運據點/分店", "parent": "董事長 / 總經理室", "modules": ["門市收發貨"]},
                {"id": "n_4", "name": "財務會計部", "type": "營運/行政部門", "parent": "董事長 / 總經理室", "modules": ["總帳管理"]}
            ],
            "iot_devices": [{"dev_id": "DEV-01", "name": "平陽廠人臉辨識機", "type": "人臉辨識", "ip": "192.168.10.50", "status": "🟢 聯機中"}],
            "ap_invoices": [{"invoice_no": "000123", "supplier": "越南材料行", "items": "PVC管", "amount_vnd": "15,000,000", "status": "🔴 待付款"}],
            "staff": [{"name": "許福村", "email": "fuchun@vina.com", "role": "Tenant Admin"}],
            "audit_logs": [{"time": "2026-10-20 14:10:22", "user": "許福村", "action": "初始化組織樹", "ip": "192.168.10.2"}]
        },
        "tenant_taipei_wash": {
            "name": "🇹🇼 台北極速智慧洗車坊",
            "region": "台灣 (Taipei, TW)",
            "plan": "標準版 (Standard)",
            "price_usd": 80,
            "expiry_date": "2026-11-05",
            "org_nodes": [
                {"id": "w_1", "name": "董事長室", "type": "最高決策層", "parent": "無 (頂層)", "modules": ["營收戰情"]},
                {"id": "w_2", "name": "台北旗艦總店", "type": "營運據點/分店", "parent": "董事長室", "modules": ["會員預約"]},
                {"id": "w_3", "name": "洗車美容作業部", "type": "營運部門", "parent": "台北旗艦總店", "modules": ["水刀聯動"]}
            ],
            "iot_devices": [{"dev_id": "W-01", "name": "車牌辨識 (ANPR)", "type": "車牌辨識", "ip": "10.0.0.15", "status": "🟢 運作中"}],
            "ap_invoices": [],
            "staff": [{"name": "張店長", "email": "manager@wash.com", "role": "Tenant Admin"}],
            "audit_logs": [{"time": "2026-10-19 10:00:00", "user": "張店長", "action": "初始化組織樹", "ip": "1.2.3.4"}]
        }
    }

if "current_portal" not in st.session_state:
    st.session_state.current_portal = "Master"

# 4. 側邊欄導覽
with st.sidebar:
    st.image("https://img.icons8.com/color/96/company.png", width=64)
    st.markdown("### 🌐 SaaS 多租戶 AI-ERP 平台")
    
    lang = st.selectbox("選擇語系 / Select Language", ["繁體中文", "English", "Tiếng Việt (越南語)", "简体中文"])
    
    st.markdown("---")
    
    if st.session_state.current_portal != "Master":
        if st.button("👑 返回 SaaS 平台總控台", type="primary", use_container_width=True):
            st.session_state.current_portal = "Master"
            st.rerun()
        st.markdown(f"🏢 **目前管理租戶**: `{st.session_state.tenants_db[st.session_state.current_portal]['name']}`")
    else:
        st.markdown("👑 **目前身分**: `SaaS 平台總管理員 (Master)`")
    
    st.markdown("---")
    st.markdown("### 📌 系統導覽選單")
    
    if st.session_state.current_portal == "Master":
        menu_choice = st.radio(
            "選擇總控台模組 (Master Hub)",
            [
                "🏢 全球企業租戶動態總覽與管理 (Tenants Hub)",
                "💱 全球多幣別與即時匯率中樞 (Global FX)",
                "⚙️ 全球定價策略與費率自訂 (Pricing)"
            ]
        )
    else:
        current_t_name = st.session_state.tenants_db[st.session_state.current_portal]["name"]
        menu_choice = st.radio(
            f"內部模組 ({current_t_name})",
            [
                "🖱️ 公司組織樹與營業據點管理 (含組織圖與CRUD)",
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
if st.session_state.current_portal == "Master":
    # ==================== SaaS 總控台 ====================
    if "全球企業租戶動態總覽" in menu_choice:
        st.markdown("## 🏢 SaaS 平台總控台：全球企業租戶動態總覽與管理中心")
        st.info("💡 *在此處您可以檢視所有已註冊的企業客戶，並可直接點擊進入該公司的獨立模組後台，隨時協助客戶核對組織圖！*")
        
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                search_keyword = st.text_input("🔍 搜尋公司名稱", placeholder="輸入關鍵字...")
            with s2:
                region_filter = st.selectbox("🌍 依地區位置過濾", ["全部地區", "越南 (Binh Duong, VN)", "台灣 (Taipei, TW)"])
            with s3:
                sort_by = st.selectbox("📊 排序依據", ["價格由高到低", "使用到期日最近", "公司名稱筆畫"])
            with s4:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("➕ 新選企業客戶租戶", type="primary", use_container_width=True):
                    st.success("🎉 請引導客戶透過模組市集自助註冊！")
            st.markdown('</div>', unsafe_allow_html=True)

        tenant_list_data = []
        for t_key, t_val in st.session_state.tenants_db.items():
            tenant_list_data.append({
                "租戶代碼": t_key,
                "公司名稱": t_val["name"],
                "地區位置": t_val["region"],
                "訂閱方案": t_val["plan"],
                "每月價格 (USD)": t_val["price_usd"],
                "合約到期日": t_val["expiry_date"],
                "組織節點數": len(t_val["org_nodes"]),
                "狀態": "🟢 正常營運"
            })
        df_tenants = pd.DataFrame(tenant_list_data)

        if search_keyword:
            df_tenants = df_tenants[df_tenants.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False)).any(axis=1)]
        if region_filter != "全部地區":
            df_tenants = df_tenants[df_tenants["地區位置"] == region_filter]

        st.markdown("### 📋 企業租戶列表")
        st.dataframe(df_tenants, use_container_width=True)
        
        st.markdown("### 🚀 快速進入指定客戶租戶後台與組織圖核對")
        quick_cols = st.columns(len(st.session_state.tenants_db))
        for idx, (t_key, t_val) in enumerate(st.session_state.tenants_db.items()):
            with quick_cols[idx]:
                st.markdown(f"""
                    <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; margin-bottom: 10px;">
                        <b>{t_val['name']}</b><br>
                        <span style="font-size: 12px; color: gray;">{t_val['region']} | ${t_val['price_usd']}/月</span>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"📂 進入並核對組織圖", key=f"btn_{t_key}", use_container_width=True):
                    st.session_state.current_portal = t_key
                    st.rerun()

    elif "全球多幣別與即時匯率引擎" in menu_choice:
        st.markdown("## 💱 SaaS 平台總控台：全球多幣別與即時匯率引擎")
        st.info("💡 維護全平台的基準匯率。")
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
    # ==================== 個別租戶後台：組織樹 CRUD 與標準方塊連線組織圖 ====================
    current_tenant = st.session_state.tenants_db[st.session_state.current_portal]
    
    if "公司組織樹與營業據點管理" in menu_choice:
        st.markdown(f"## 🖱️ {current_tenant['name']}：組織樹與營業據點管理 (含標準組織圖)")
        st.info("💡 *在此處您可以新增、修改或刪除公司內部的組織節點與實體據點。畫面下方會完整呈現像 ProcessOn 那樣、帶有上下級方塊連線的標準組織架構圖！*")
        
        col_set, col_edit = st.columns([1, 1])
        
        with col_set:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### ➕ 新增組織節點或實體據點")
            with st.form("dept_add_form"):
                node_name = st.text_input("名稱*", placeholder="例：財務會計部 / 台北旗艦總店")
                node_type = st.selectbox("屬性分類", [
                    "👑 最高決策層 (Board / CEO)",
                    "📂 營運/行政部門 (Department)", 
                    "🏢 營運據點/分店 (Branch / Store)", 
                    "📦 實體倉庫/庫位 (Warehouse)"
                ])
                existing_parents = [n["name"] for n in current_tenant["org_nodes"]]
                chosen_parent = st.selectbox("指定上級掛載點 (Parent)", existing_parents)
                
                if st.form_submit_button("🧱 確認新增並掛載", type="primary", use_container_width=True):
                    if node_name:
                        current_tenant["org_nodes"].append({
                            "id": f"n_{len(current_tenant['org_nodes'])+1}",
                            "name": node_name,
                            "type": node_type,
                            "parent": chosen_parent,
                            "modules": ["日常作業"]
                        })
                        st.success(f"🎉 成功新增 [{node_name}]！")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_edit:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### ✏️ 修改或刪除現有節點 / 據點")
            if current_tenant["org_nodes"]:
                node_names_list = [n["name"] for n in current_tenant["org_nodes"]]
                target_node_name = st.selectbox("選擇要修改或刪除的節點", node_names_list, key="edit_select")
                
                target_node = next((n for n in current_tenant["org_nodes"] if n["name"] == target_node_name), None)
                
                if target_node:
                    with st.form("edit_node_form"):
                        new_edit_name = st.text_input("修改名稱", value=target_node["name"])
                        new_edit_parent = st.selectbox("修改上級掛載點", existing_parents, index=existing_parents.index(target_node["parent"]) if target_node["parent"] in existing_parents else 0)
                        
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            submitted_update = st.form_submit_button("💾 儲存修改", type="primary", use_container_width=True)
                        with col_e2:
                            submitted_delete = st.form_submit_button("🗑️ 刪除此節點", use_container_width=True)
                            
                        if submitted_update:
                            target_node["name"] = new_edit_name
                            target_node["parent"] = new_edit_parent
                            st.success(f"🎉 節點已成功更新！")
                            st.rerun()
                            
                        if submitted_delete:
                            if target_node["parent"] == "無 (頂層)":
                                st.error("❌ 無法刪除公司頂層最高決策層！")
                            else:
                                current_tenant["org_nodes"] = [n for n in current_tenant["org_nodes"] if n["name"] != target_node_name]
                                st.success(f"🗑️ 節點 [{target_node_name}] 已成功刪除！")
                                st.rerun()
            else:
                st.info("目前尚無組織節點。")
            st.markdown('</div>', unsafe_allow_html=True)

        # ==================== 下方標準方塊連線組織圖 (Graphviz Org Chart) ====================
        st.markdown("---")
        st.markdown("### 📊 貴公司標準階層組織架構圖 (Org Chart Flowchart)")
        st.info("💡 *下方即時透過圖形引擎繪製出如同 ProcessOn 標準方塊與連線的組織架構圖，讓您與租戶一眼看出上下級歸屬是否正確！*")
        
        # 使用 Graphviz 繪製階層組織圖
        try:
            import graphviz
            org_dot = graphviz.Digraph(comment='Enterprise Org Chart', format='png')
            org_dot.attr(rankdir='TB', size='12,12') # 由上往下排列 (Top to Bottom)
            org_dot.attr('node', shape='box', style='filled,rounded', fontname='Microsoft JhengHei', fontsize='12', margin='0.2')
            
            # 依據節點屬性賦予不同顏色方塊
            for node in current_tenant["org_nodes"]:
                n_name = node["name"]
                n_type = node["type"]
                
                if "最高決策層" in n_type:
                    color = "#2563eb" # 寶藍色
                    text_color = "white"
                elif "部門" in n_type:
                    color = "#3b82f6" # 藍色
                    text_color = "white"
                elif "據點" in n_type or "分店" in n_type:
                    color = "#10b981" # 綠色
                    text_color = "white"
                else:
                    color = "#64748b" # 灰色
                    text_color = "white"
                    
                org_dot.node(n_name, label=f"{n_name}\n({n_type})", fillcolor=color, fontcolor=text_color)
                
            # 建立上下級連線關係
            for node in current_tenant["org_nodes"]:
                if node["parent"] != "無 (頂層)" and node["parent"]:
                    org_dot.edge(node["parent"], node["name"], color="#64748b", penwidth="1.5")
                    
            st.graphviz_chart(org_dot)
        except Exception as e:
            st.warning("⚠️ 圖形引擎載入中，若未顯示請重新整理頁面。以下同步提供樹狀檢視：")
            for node in current_tenant["org_nodes"]:
                st.markdown(f"- 📂 **{node['name']}** ({node['type']}) ➔ 上級: `{node['parent']}`")

    elif "員工帳號與權限角色管理" in menu_choice:
        st.markdown(f"## 👥 {current_tenant['name']}：員工帳號與權限角色管理 (RBAC)")
        st.info("💡 建立公司內部員工帳號與職務。")
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
        st.markdown(f"## 🔒 {current_tenant['name']}：系統資安稽核日誌")
        st.info("💡 記錄公司內部員工操作軌跡。")
        st.dataframe(pd.DataFrame(current_tenant["audit_logs"]), use_container_width=True)

    elif "AI 硬體與車牌" in menu_choice:
        st.markdown(f"## 🤖 {current_tenant['name']}：AI 硬體與車牌/人臉辨識自助掛接")
        if current_tenant["iot_devices"]:
            st.dataframe(pd.DataFrame(current_tenant["iot_devices"]), use_container_width=True)

    else:
        st.markdown(f"## 🇻🇳 {current_tenant['name']}：越南紅發票與應付帳款 (AP)")
        if current_tenant["ap_invoices"]:
            st.dataframe(pd.DataFrame(current_tenant["ap_invoices"]), use_container_width=True)
