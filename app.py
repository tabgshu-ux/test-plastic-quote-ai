import streamlit as st

# 匯入各個獨立的樂高拼圖模組
from modules.org_management import render_org_management
from modules.employee_management import render_employee_management
from modules.leave_attendance import render_leave_attendance
from modules.ga_procurements import render_ga_procurements
from modules.approval_center import render_approval_center
from modules.finance_ap import render_finance_ap
from modules.asset_management import render_asset_management
from modules.mes_production import render_mes_production
from modules.supply_chain import render_supply_chain
from modules.invoice_parsing import render_invoice_parsing
from modules.ga_contracts import render_ga_contracts
from modules.ai_multimodal import render_ai_multimodal
from modules.tax_ledger import render_tax_ledger
from modules.inventory_wms import render_inventory_wms
from modules.dashboard_bi import render_dashboard_bi
from modules.api_gateway_config import render_api_gateway_config

# 設定頁面配置
st.set_page_config(
    page_title="Global Multi-Tenant SaaS AI ERP",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # 租戶與使用者權限模擬上下文
    tenant_info = {
        "tenant_id": "TENANT-001",
        "company_name": "裕豐電機工業 (Reetech Industrial)",
        "current_factory": "越南平陽廠"
    }
    user_perms = ["admin", "finance", "mes", "ga"]

    st.sidebar.markdown("### 🌐 全球多租戶 SaaS AI ERP")
    st.sidebar.info(f"🏢 當前租戶：**{tenant_info['company_name']}**\n\n📍 廠區：{tenant_info['current_factory']}")
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("#### 🧩 樂高模組市集 (App Marketplace)")

    # 側邊欄模組導航選單
    module_choice = st.sidebar.radio(
        "選擇要執行的功能模組：",
        [
            "📈 企業戰情室與 BI 分析",
            "🌐 組織架構與匯率設定",
            "👤 員工與薪資管理",
            "⏱️ 請假與差勤管理",
            "📦 總務採購與請購單",
            "✍️ 全方位電子簽核中心",
            "💰 跨國應付帳款 (Finance AP)",
            "🏷️ 固定資產與模具防混淆",
            "🏭 MES 生產製造與 IoT 監控",
            "📊 供應鏈與業務報價",
            "🧾 跨國電子發票解析",
            "📜 行政公文與合約列管",
            "🤖 AI 多模態無門檻輸入",
            "📊 多國動態稅制與總帳",
            "📦 全球供應鏈倉儲 (WMS)",
            "🔌 第三方 API 閘道器配置"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("© 2026 Global SaaS AI ERP Architecture. All rights reserved.")

    # 路由分發與模組動態渲染
    if "企業戰情室" in module_choice:
        render_dashboard_bi(tenant_info, user_perms)
    elif "組織架構" in module_choice:
        render_org_management(tenant_info, user_perms)
    elif "員工與薪資" in module_choice:
        render_employee_management(tenant_info)
    elif "請假與差勤" in module_choice:
        render_leave_attendance(tenant_info)
    elif "總務採購" in module_choice:
        render_ga_procurements(tenant_info)
    elif "電子簽核" in module_choice:
        render_approval_center(tenant_info, user_perms)
    elif "跨國應付帳款" in module_choice:
        render_finance_ap(tenant_info, user_perms)
    elif "固定資產" in module_choice:
        render_asset_management(tenant_info, user_perms)
    elif "MES 生產製造" in module_choice:
        render_mes_production(tenant_info, user_perms)
    elif "供應鏈與業務報價" in module_choice:
        render_supply_chain(tenant_info, user_perms)
    elif "跨國電子發票" in module_choice:
        render_invoice_parsing(tenant_info, user_perms)
    elif "行政公文" in module_choice:
        render_ga_contracts(tenant_info, user_perms)
    elif "AI 多模態" in module_choice:
        render_ai_multimodal(tenant_info, user_perms)
    elif "多國動態稅制" in module_choice:
        render_tax_ledger(tenant_info, user_perms)
    elif "全球供應鏈倉儲" in module_choice:
        render_inventory_wms(tenant_info, user_perms)
    elif "第三方 API" in module_choice:
        render_api_gateway_config(tenant_info, user_perms)

if __name__ == "__main__":
    main()
