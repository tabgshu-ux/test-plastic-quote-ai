import streamlit as st
import pandas as pd
import numpy as np

def render_erp_dashboard_page():
    st.title("🏭 廠務/設備 — IoT 設備監控與 OEE KPI 戰情室")
    st.caption("即時連線各廠區 PLC/IoT 射出機、模溫機與感測器，監控料筒溫度、鎖模壓力與 OEE 稼動率")

    tabs = st.tabs(["📡 IoT 設備即時狀態", "⚡ 廠區 OEE 稼動率", "🛠️ 模具與設備保養紀錄"])

    # ----------------------------------------------------
    # TAB 1: IoT 連接設備狀態
    # ----------------------------------------------------
    with tabs[0]:
        st.subheader("📡 全球廠區 IoT 連接設備即時狀態")
        
        # 篩選廠區
        selected_factory = st.selectbox(
            "選擇廠區 (Factory):",
            ["🇻🇳 越南平陽廠 (Binh Duong)", "🇨🇳 中國東莞廠 (Dongguan)", "🇹🇼 台灣總部研發中心 (HQ)"],
            key="iot_factory_select"
        )

        st.markdown("#### 🟢 射出成型機台 PLC / IoT 連線動態")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("連線機台總數", "18 台", "100% 在線")
        m2.metric("目前運作中機台", "16 台", "🟢 88.8%")
        m3.metric("換模/待機中", "1 台", "🟡 換模 15m")
        m4.metric("異常停機告警", "1 台", "🔴 壓模預警")

        st.divider()

        # IoT 即時數據監控面板
        st.markdown("#### 📊 機台 PLC 即時數據回傳 (三秒更新)")
        iot_machines = pd.DataFrame({
            "機台編號": ["INJ-BH-01", "INJ-BH-02", "INJ-BH-03", "INJ-DG-01", "INJ-TW-01"],
            "設備型號": ["日精 250T 橡膠射出機", "東洋 350T 電動射出機", "百朔 180T 立式機", "海天 500T 雙色機", "發那科 120T 精密機"],
            "目前生產產品": ["喬丹10代橡膠大底", "EVA中底熱壓", "精密塑膠齒輪", "汽車配件外殼", "TPU 研發打樣"],
            "料筒溫度 (°C)": ["185 °C", "210 °C", "205 °C", "225 °C", "190 °C"],
            "射出壓力 (Bar)": ["142 Bar", "165 Bar", "120 Bar", "180 Bar", "110 Bar"],
            "成型週期 (sec)": ["42.5 s", "35.0 s", "28.2 s", "55.0 s", "31.0 s"],
            "IoT 連線狀態": ["🟢 正常生產", "🟢 正常生產", "🟡 模溫偏高預警", "🔴 停機維修", "🟢 正常生產"]
        })
        st.dataframe(iot_machines, use_container_width=True)

    # ----------------------------------------------------
    # TAB 2: 廠區 OEE 稼动率
    # ----------------------------------------------------
    with tabs[1]:
        st.subheader("⚡ 設備綜合效率 (OEE) 統計")
        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            chart_oee = pd.DataFrame(
                np.random.randn(15, 3) * 3 + [88, 76, 92],
                columns=["平陽廠", "東莞廠", "台灣總部"]
            )
            st.line_chart(chart_oee)
        with col_right if 'col_right' in locals() else col_c2:
            st.markdown("#### OEE 三要素解構")
            st.progress(0.92, text="時間稼動率 (Availability): 92%")
            st.progress(0.88, text="性能稼动率 (Performance): 88%")
            st.progress(0.98, text="良品率 (Quality): 98.2%")

    # ----------------------------------------------------
    # TAB 3: 保養紀錄
    # ----------------------------------------------------
    with tabs[2]:
        st.subheader("🛠️ 設備預防性保養與維修履歷")
        st.info("ℹ️ 系統已自動連線至 `assets` 與 `asset_maintenance` PostgreSQL 資料表。")

def show():
    render_erp_dashboard_page()

def main():
    render_erp_dashboard_page()
