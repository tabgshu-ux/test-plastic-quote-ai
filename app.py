import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# ==============================================================================
# 🧩 SaaS 企業級多租戶 AI-ERP 系統 (唯一 ID 識別與階層縮排組織圖)
# ==============================================================================

st.set_page_config(
    page_title="SaaS Enterprise Modular AI-ERP & Unique ID Org",
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
        width: 100%;
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
                {"id": "node_root", "name": "董事長室", "type": "👑 董事會 / 董事長室", "parent": "無 (頂層)"},
                {"id": "node_eng", "name": "工程技術部", "type": "⚙️ 工程技術部", "parent": "董事長室"},
                {"id": "node_store", "name": "平陽美福營業所", "type": "🏢 門市 / 營業所", "parent": "董事長室"}
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
                {"id": "w_root", "name": "董事長室", "type": "👑 董事會 / 董事長室", "parent": "無 (頂層)"},
                {"id": "w_branch", "name": "台北旗艦總店", "type": "🏢 營運據點 / 總店", "parent": "董事長室"},
                {"id": "w_dept", "name": "洗車美容作業部", "type": "🏭 生產製造廠務部", "parent": "台北旗艦總店"}
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
                "🖱️ 拼圖式組織與據點一鍵掛載 (唯一ID管理)",
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
        st.info("💡 *在此處檢視所有企業客戶，並可直接點擊進入該公司後台協助核對組織圖！*")
        
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
                if st.button("➕ 新增企業客戶租戶", type="primary", use_container_width=True):
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
    # ==================== 個別租戶後台：唯一 ID 組織管理與階層樹狀圖 ====================
    current_tenant = st.session_state.tenants_db[st.session_state.current_portal]
    
    if "拼圖式組織與據點一鍵掛載" in menu_choice:
        st.markdown(f"## 🖱️ {current_tenant['name']}：拼圖式組織與營業據點一鍵掛載")
        st.info("💡 *滑鼠點擊下方積木按鈕即可一鍵新增部門並掛載至指定上級！下方即時呈現具備精準階層縮排的組織樹狀圖，修改與刪除均採用獨立 ID 識別，絕不重複或混淆。*")
        
        existing_parents = [n["name"] for n in current_tenant["org_nodes"]]
        selected_parent_target = st.selectbox("📌 步驟一：請先選擇要將新部門掛載在哪個上級下方 (Parent Target)", existing_parents)
        
        st.markdown("---")
        st.markdown("### 🧩 步驟二：用滑鼠直接點擊積木按鈕一鍵新增部門/據點")
        
        p1, p2, p3, p4 = st.columns(4)
        
        with p1:
            st.markdown("#### 👑 決策與高階管理")
            if st.button("➕ 加入：董事長室 / 董事會"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "董事長室", "type": "👑 董事會 / 董事長室", "parent": selected_parent_target})
                st.success("🎉 成功新增 [董事長室]！")
                st.rerun()
            if st.button("➕ 加入：總經理室 / CEO"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "總經理室", "type": "👑 總經理室 / 執行長室", "parent": selected_parent_target})
                st.success("🎉 成功新增 [總經理室]！")
                st.rerun()
            if st.button("➕ 加入：副總經理室"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "副總經理室", "type": "👑 副總經理室", "parent": selected_parent_target})
                st.success("🎉 成功新增 [副總經理室]！")
                st.rerun()
                
        with p2:
            st.markdown("#### 💰 財務與行政後勤")
            if st.button("➕ 加入：財務部"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "財務部", "type": "💰 財務部", "parent": selected_parent_target})
                st.success("🎉 成功新增 [財務部]！")
                st.rerun()
            if st.button("➕ 加入：會計部"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "會計部", "type": "💰 會計部", "parent": selected_parent_target})
                st.success("🎉 成功新增 [會計部]！")
                st.rerun()
            if st.button("➕ 加入：人力資源部 (HR)"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "人力資源部", "type": "👥 人力資源部", "parent": selected_parent_target})
                st.success("🎉 成功新增 [人力資源部]！")
                st.rerun()
            if st.button("➕ 加入：總務行政部"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "總務行政部", "type": "👥 總務行政部", "parent": selected_parent_target})
                st.success("🎉 成功新增 [總務行政部]！")
                st.rerun()
                
        with p3:
            st.markdown("#### ⚙️ 工程、研發與生產")
            if st.button("➕ 加入：工程技術部"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "工程技術部", "type": "⚙️ 工程技術部", "parent": selected_parent_target})
                st.success("🎉 成功新增 [工程技術部]！")
                st.rerun()
            if st.button("➕ 加入：研發設計中心"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "研發設計中心", "type": "⚙️ 研發設計中心", "parent": selected_parent_target})
                st.success("🎉 成功新增 [研發設計中心]！")
                st.rerun()
            if st.button("➕ 加入：生產製造廠務部"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "生產製造廠務部", "type": "🏭 生產製造廠務部", "parent": selected_parent_target})
                st.success("🎉 成功新增 [生產製造廠務部]！")
                st.rerun()
            if st.button("➕ 加入：供應鏈與採購部"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "供應鏈與採購部", "type": "🛒 供應鏈與全球採購部", "parent": selected_parent_target})
                st.success("🎉 成功新增 [供應鏈與採購部]！")
                st.rerun()
                
        with p4:
            st.markdown("#### 🏢 實體據點與倉庫")
            if st.button("➕ 加入：營運據點/旗艦總店"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "台北旗艦總店", "type": "🏢 營運據點 / 總店", "parent": selected_parent_target})
                st.success("🎉 成功新增 [台北旗艦總店]！")
                st.rerun()
            if st.button("➕ 加入：海外分公司/辦事處"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "海外分公司", "type": "🏢 分公司 / 辦事處", "parent": selected_parent_target})
                st.success("🎉 成功新增 [海外分公司]！")
                st.rerun()
            if st.button("➕ 加入：廠內原物料倉庫"):
                current_tenant["org_nodes"].append({"id": f"node_{uuid.uuid4().hex[:8]}", "name": "廠內原物料倉庫", "type": "📦 實體原物料倉庫", "parent": selected_parent_target})
                st.success("🎉 成功新增 [廠內原物料倉庫]！")
                st.rerun()

        # 採用【唯一 UUID】進行精準修改與刪除
        st.markdown("---")
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### ✏️ 管理現有部門與據點 (透過唯一 ID 精準修改或刪除)")
            if current_tenant["org_nodes"]:
                # 建立對應字典：顯示名稱 (ID) -> 節點物件
                node_options = {f"{n['name']} ({n['type']}) [ID: {n.get('id', 'N/A')}]": n for n in current_tenant["org_nodes"]}
                selected_label = st.selectbox("選擇要管理的特定節點", list(node_options.keys()), key="uuid_edit_select")
                target_node = node_options[selected_label]
                
                if target_node:
                    with st.form("edit_uuid_node"):
                        up_name = st.text_input("修改名稱", value=target_node["name"])
                        up_parent = st.selectbox("修改上級掛載點", existing_parents, index=existing_parents.index(target_node["parent"]) if target_node["parent"] in existing_parents else 0)
                        
                        col_bt1, col_bt2 = st.columns(2)
                        with col_bt1:
                            sub_up = st.form_submit_button("💾 儲存變更", type="primary", use_container_width=True)
                        with col_bt2:
                            sub_del = st.form_submit_button("🗑️ 刪除此節點", use_container_width=True)
                            
                        if sub_up:
                            target_node["name"] = up_name
                            target_node["parent"] = up_parent
                            st.success(f"🎉 節點更新成功！")
                            st.rerun()
                        if sub_del:
                            if target_node["parent"] == "無 (頂層)":
                                st.error("❌ 無法刪除公司頂層最高決策層節點！")
                            else:
                                current_tenant["org_nodes"] = [n for n in current_tenant["org_nodes"] if n["id"] != target_node["id"]]
                                st.success("🗑️ 該節點已成功刪除！")
                                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ==================== 下方超清晰的階層縮排組織圖 (Indented Org Tree) ====================
        st.markdown("---")
        st.markdown("### 📊 貴公司階層組織架構與上下級歸屬總覽 (Indented Org Tree)")
        st.info("💡 *下方以清晰的縮排樹狀結構呈現，讓您與租戶一眼看出每個部門精準掛載在哪個上級底下！*")
        
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            
            # 找出頂層節點 (parent == "無 (頂層)")
            roots = [n for n in current_tenant["org_nodes"] if n["parent"] == "無 (頂層)"]
            others = [n for n in current_tenant["org_nodes"] if n["parent"] != "無 (頂層)"]
            
            def render_tree(parent_name, level=0):
                children = [n for n in others if n["parent"] == parent_name]
                for child in children:
                    indent_space = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" * level
                    badge_color = "#10b981" if "據點" in child['type'] or "倉庫" in child['type'] else "#3b82f6"
                    st.markdown(f"""
                        <div style="background: #f8f9fa; padding: 10px; border-radius: 6px; margin-bottom: 6px; border-left: 4px solid {badge_color}; margin-left: {level * 25}px;">
                            <b>{child['name']}</b> <span style="font-size: 11px; color: gray;">({child['type']})</span><br>
                            <span style="font-size: 11px; color: #0f766e;">📌 上級掛載：<b>{child['parent']}</b></span>
                        </div>
                    """, unsafe_allow_html=True)
                    # 遞迴渲染子節點
                    render_tree(child["name"], level + 1)

            # 先渲染頂層
            for r in roots:
                st.markdown(f"""
                    <div style="background: #eff6ff; padding: 12px; border-radius: 6px; margin-bottom: 8px; border-left: 5px solid #2563eb;">
                        <b>👑 {r['name']}</b> <span style="font-size: 11px; color: gray;">({r['type']})</span><br>
                        <span style="font-size: 11px; color: #1e40af;">📌 企業最高決策層 (頂層)</span>
                    </div>
                """, unsafe_allow_html=True)
                render_tree(r["name"], level=1)
                
            st.markdown('</div>', unsafe_allow_html=True)

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
