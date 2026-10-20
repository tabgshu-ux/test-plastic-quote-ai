import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# ==============================================================================
# 🧩 SaaS 企業級多租戶 AI-ERP 系統 (多層級組織樹與部門專屬功能自動掛載)
# ==============================================================================

st.set_page_config(
    page_title="SaaS Enterprise Modular AI-ERP & Multi-Level Org",
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
    .org-root-card {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
        display: inline-block;
        margin-bottom: 15px;
    }
    .org-level1-card {
        background: #ffffff;
        border: 2px solid #2563eb;
        color: #1e293b;
        padding: 12px 18px;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 5px;
        min-width: 180px;
    }
    .org-level2-card {
        background: #f8fafc;
        border: 2px solid #0284c7;
        color: #0369a1;
        padding: 10px 15px;
        border-radius: 6px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin: 4px;
        min-width: 150px;
        font-size: 13px;
    }
    .org-level3-card {
        background: #f0fdf4;
        border: 2px solid #10b981;
        color: #065f46;
        padding: 8px 12px;
        border-radius: 6px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin: 3px;
        min-width: 130px;
        font-size: 12px;
    }
    .tree-connector {
        width: 2px;
        height: 25px;
        background-color: #94a3b8;
        margin: 0 auto;
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
                {"id": "node_root", "name": "董事長室", "type": "👑 頂層 (Board)", "parent": "無 (頂層)", "modules": ["全球戰情室", "高階決策審核"]},
                {"id": "node_gen", "name": "總經理室", "type": "👑 一級部門 (CEO)", "parent": "董事長室", "modules": ["營運總控台", "跨部門協調"]},
                {"id": "node_fin", "name": "財務會計部", "type": "💰 二級部門 (Finance)", "parent": "總經理室", "modules": ["總帳管理", "應付帳款(AP)", "多幣別與匯率"]},
                {"id": "node_eng", "name": "工程技術部", "type": "⚙️ 二級部門 (Engineering)", "parent": "總經理室", "modules": ["專案與工項預算", "工程估驗與計價"]},
                {"id": "node_sub_site", "name": "平陽美福工地現場", "type": "📦 三級部門 (Site/Store)", "parent": "工程技術部", "modules": ["工地點工點料", "現場日報表"]}
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
                {"id": "w_root", "name": "董事長室", "type": "👑 頂層 (Board)", "parent": "無 (頂層)", "modules": ["營收戰情"]},
                {"id": "w_branch", "name": "台北旗艦總店", "type": "🏢 一級據點 (Branch)", "parent": "董事長室", "modules": ["門市收發貨", "會員預約"]},
                {"id": "w_dept", "name": "洗車美容作業部", "type": "🏭 二級部門 (Operation)", "parent": "台北旗艦總店", "modules": ["水刀聯動控制", "車牌辨識(ANPR)"]}
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
                "🖱️ 拼圖式多層級組織與部門功能掛載",
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
    # ==================== 個別租戶後台：拼圖式多層級部門與功能掛載 ====================
    current_tenant = st.session_state.tenants_db[st.session_state.current_portal]
    
    if "拼圖式組織與部門功能掛載" in menu_choice:
        st.markdown(f"## 🖱️ {current_tenant['name']}：拼圖式多層級組織與部門功能掛載")
        st.info("💡 *點擊下方豐富的企業部門積木按鈕，選擇階層（一級/二級/三級部門）並掛載至指定上級，系統會自動帶入該部門專屬的 ERP 功能模組！*")
        
        existing_parents = [n["name"] for n in current_tenant["org_nodes"]]
        
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 🧩 步驟一：設定掛載層級與上級主管，並一鍵點擊新增部門")
            
            c_lvl, c_par = st.columns(2)
            with c_lvl:
                dept_level = st.selectbox("選擇部門組織層級", ["👑 頂層 (Board / 董事會)", "👑 一級部門 (Headquarters / 總經理與高管室)", "💰 二級部門 (Functional Dept / 財務、工程、生產、採購等)", "📦 三級部門 (Site / Branch / 現場工務所、倉庫、分店)"])
            with c_par:
                selected_parent_target = st.selectbox("指定上級掛載點 (Parent)", existing_parents)
                
            st.markdown("#### 請選擇要加入的企業部門積木：")
            
            # 定義各部門專屬的預設功能模組對應表
            dept_default_modules = {
                "董事長室": ["全球戰情室", "高階決策審核"],
                "總經理室": ["營運總控台", "跨部門協調"],
                "副總經理室": ["督導管理", "績效考核"],
                "財務部": ["總帳管理", "應付帳款(AP)", "多幣別與匯率"],
                "會計部": ["會計傳票", "稅務報表"],
                "人力資源部": ["人事考勤", "薪資計算"],
                "總務行政部": ["總務採購", "辦公資產管理"],
                "工程技術部": ["專案與工項預算", "工程估驗與計價"],
                "研發設計中心": ["BOM表管理", "研發專案追蹤"],
                "生產製造廠務部": ["MES報工系統", "產線排程管理"],
                "供應鏈與採購部": ["採購單(PR/PO)", "供應商管理"],
                "品保與安衛部": ["QA/QC檢驗", "工安環安追蹤"],
                "營業據點/旗艦總店": ["門市收發貨", "會員預約系統"],
                "海外分公司": ["海外業務管理", "跨國多幣別報表"],
                "廠內原物料倉庫": ["PDA條碼庫存", "出入庫管理"],
                "現場工務所": ["工地點工點料", "現場施工日報表"]
            }
            
            d1, d2, d3, d4 = st.columns(4)
            
            def add_dept_node(name, dept_type_str):
                mods = dept_default_modules.get(name, ["一般日常作業"])
                current_tenant["org_nodes"].append({
                    "id": f"node_{uuid.uuid4().hex[:8]}",
                    "name": name,
                    "type": dept_type_str,
                    "parent": selected_parent_target,
                    "modules": mods
                })
                st.success(f"🎉 成功新增 [{name}] 並自動掛載專屬功能：{', '.join(mods)}")
                st.rerun()

            with d1:
                st.markdown("**👑 決策與高管**")
                if st.button("➕ 董事長室"): add_dept_node("董事長室", dept_level)
                if st.button("➕ 總經理室"): add_dept_node("總經理室", dept_level)
                if st.button("➕ 副總經理室"): add_dept_node("副總經理室", dept_level)
            with d2:
                st.markdown("**💰 財務與行政**")
                if st.button("➕ 財務部"): add_dept_node("財務部", dept_level)
                if st.button("➕ 會計部"): add_dept_node("會計部", dept_level)
                if st.button("➕ 人力資源部"): add_dept_node("人力資源部", dept_level)
                if st.button("➕ 總務行政部"): add_dept_node("總務行政部", dept_level)
            with d3:
                st.markdown("**⚙️ 工程與生產**")
                if st.button("➕ 工程技術部"): add_dept_node("工程技術部", dept_level)
                if st.button("➕ 研發設計中心"): add_dept_node("研發設計中心", dept_level)
                if st.button("➕ 生產製造廠務部"): add_dept_node("生產製造廠務部", dept_level)
                if st.button("➕ 供應鏈與採購部"): add_dept_node("供應鏈與採購部", dept_level)
            with d4:
                st.markdown("**🏢 據點與現場**")
                if st.button("➕ 營業據點/總店"): add_dept_node("營業據點/旗艦總店", dept_level)
                if st.button("➕ 海外分公司"): add_dept_node("海外分公司", dept_level)
                if st.button("➕ 原物料倉庫"): add_dept_node("廠內原物料倉庫", dept_level)
                if st.button("➕ 現場工務所"): add_dept_node("現場工務所", dept_level)
                
            st.markdown('</div>', unsafe_allow_html=True)

        # 現有部門管理與功能自訂修改區塊
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### ✏️ 管理現有部門與專屬功能模組 (修改名稱、掛載點或自訂功能)")
            if current_tenant["org_nodes"]:
                node_options = {f"{n['name']} ({n['type']}) [ID: {n['id']}]": n for n in current_tenant["org_nodes"]}
                selected_label = st.selectbox("選擇要管理的特定部門節點", list(node_options.keys()))
                target_node = node_options[selected_label]
                
                if target_node:
                    with st.form("edit_node_form"):
                        up_name = st.text_input("修改部門名稱", value=target_node["name"])
                        up_parent = st.selectbox("修改上級掛載點", existing_parents, index=existing_parents.index(target_node["parent"]) if target_node["parent"] in existing_parents else 0)
                        
                        st.markdown("#### 🛠️ 該部門啟用的 ERP 功能模組 (可自由勾選調整)")
                        all_possible_modules = [
                            "全球戰情室", "高階決策審核", "營運總控台", "跨部門協調", "督導管理", "績效考核",
                            "總帳管理", "應付帳款(AP)", "多幣別與匯率", "會計傳票", "稅務報表",
                            "人事考勤", "薪資計算", "總務採購", "辦公資產管理",
                            "專案與工項預算", "工程估驗與計價", "工地點工點料", "現場施工日報表",
                            "BOM表管理", "研發專案追蹤", "MES報工系統", "產線排程管理",
                            "採購單(PR/PO)", "供應商管理", "QA/QC檢驗", "工安環安追蹤",
                            "門市收發貨", "會員預約系統", "海外業務管理", "跨國多幣別報表", "PDA條碼庫存"
                        ]
                        current_assigned = target_node.get("modules", [])
                        selected_mods = st.multiselect("勾選此部門所擁有的系統功能", all_possible_modules, default=[m for m in current_assigned if m in all_possible_modules])
                        
                        col_bt1, col_bt2 = st.columns(2)
                        with col_bt1:
                            sub_up = st.form_submit_button("💾 儲存變更", type="primary", use_container_width=True)
                        with col_bt2:
                            sub_del = st.form_submit_button("🗑️ 刪除此部門", use_container_width=True)
                            
                        if sub_up:
                            target_node["name"] = up_name
                            target_node["parent"] = up_parent
                            target_node["modules"] = selected_mods
                            st.success("🎉 部門與專屬功能更新成功！")
                            st.rerun()
                        if sub_del:
                            if target_node["parent"] == "無 (頂層)":
                                st.error("❌ 無法刪除頂層最高決策層！")
                            else:
                                current_tenant["org_nodes"] = [n for n in current_tenant["org_nodes"] if n["id"] != target_node["id"]]
                                st.success("🗑️ 該部門已刪除！")
                                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ==================== 下方多層級標準方塊組織樹 (一、二、三級展開與功能展示) ====================
        st.markdown("---")
        st.markdown("### 📊 貴公司多層級組織架構與專屬功能總覽 (Multi-Level Org Tree)")
        st.info("💡 *下方即時呈現一級、二級、三級部門層級樹狀圖，並清楚標示每個部門所擁有的 ERP 功能模組！*")
        
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            
            roots = [n for n in current_tenant["org_nodes"] if n["parent"] == "無 (頂層)"]
            others = [n for n in current_tenant["org_nodes"] if n["parent"] != "無 (頂層)"]
            
            for r in roots:
                r_mods = ", ".join(r.get("modules", []))
                st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="org-root-card">
                            👑 {r['name']} <span style="font-size: 12px; font-weight: normal;">({r['type']})</span><br>
                            <span style="font-size: 11px; font-weight: normal; opacity: 0.9;">📦 專屬功能：{r_mods}</span>
                        </div>
                    </div>
                    <div class="tree-connector"></div>
                """, unsafe_allow_html=True)
                
                # 一級部門
                level1_children = [n for n in others if n["parent"] == r["name"]]
                if level1_children:
                    cols1 = st.columns(len(level1_children))
                    for idx1, l1 in enumerate(level1_children):
                        with cols1[idx1]:
                            l1_mods = ", ".join(l1.get("modules", []))
                            st.markdown(f"""
                                <div style="text-align: center;">
                                    <div class="org-level1-card">
                                        <b>{l1['name']}</b><br>
                                        <span style="font-size: 11px; color: gray;">{l1['type']}</span><br>
                                        <span style="font-size: 10px; color: #2563eb;">📌 功能：{l1_mods}</span>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # 二級部門
                            level2_children = [n for n in others if n["parent"] == l1["name"]]
                            if level2_children:
                                st.markdown('<div class="tree-connector" style="height: 15px;"></div>', unsafe_allow_html=True)
                                for l2 in level2_children:
                                    l2_mods = ", ".join(l2.get("modules", []))
                                    st.markdown(f"""
                                        <div style="text-align: center;">
                                            <div class="org-level2-card">
                                                <b>{l2['name']}</b><br>
                                                <span style="font-size: 10px; color: gray;">{l2['type']}</span><br>
                                                <span style="font-size: 9px; color: #0284c7;">📌 功能：{l2_mods}</span>
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # 三級部門
                                    level3_children = [n for n in others if n["parent"] == l2["name"]]
                                    if level3_children:
                                        st.markdown('<div class="tree-connector" style="height: 10px;"></div>', unsafe_allow_html=True)
                                        for l3 in level3_children:
                                            l3_mods = ", ".join(l3.get("modules", []))
                                            st.markdown(f"""
                                                <div style="text-align: center;">
                                                    <div class="org-level3-card">
                                                        <b>{l3['name']}</b><br>
                                                        <span style="font-size: 9px; color: gray;">{l3['type']}</span><br>
                                                        <span style="font-size: 8px; color: #059669;">📌 功能：{l3_mods}</span>
                                                    </div>
                                                </div>
                                            """, unsafe_allow_html=True)
                                            
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
