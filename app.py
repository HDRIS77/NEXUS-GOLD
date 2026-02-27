import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh # تطلب تثبيت المكتبة في requirements

# --- إعدادات الواجهة النيون ---
st.set_page_config(page_title="NEUXS GOLD TERMINAL", layout="wide")

# تحديث الصفحة تلقائياً كل ثانيتين
st_autorefresh(interval=2000, key="datarefresh")

st.markdown("""
    <style>
    .main { background-color: #050505; }
    .stMetric { background-color: #0f1111; border: 1px solid #00ff41; padding: 15px; border-radius: 10px; box-shadow: 0 0 10px #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; text-shadow: 0 0 10px #00ff41; font-family: 'Courier New', Courier, monospace; }
    .stButton>button { background-color: #00ff41; color: black; border-radius: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_input_with_experimental_code=True)

# --- نظام الأمان ---
PASSWORD = "neuxs_gold_2024"
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    pwd = st.text_input("ENTER NEUXS ACCESS KEY:", type="password")
    if pwd == PASSWORD: 
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- سحب البيانات ---
def fetch_data():
    gold = yf.download("GC=F", period="1d", interval="1m")
    usd_egp = 70.0 # سعر دولار الصاغة (يمكنك تعديله يدوياً هنا)
    return gold, usd_egp

try:
    gold_data, egp_rate = fetch_data()
    current_global_price = float(gold_data['Close'].iloc[-1])
    
    # --- حسابات الذهب في مصر ---
    # الأوقية = 31.1 جرام عيار 24
    price_24_egp = (current_global_price / 31.1) * egp_rate
    price_21_egp = price_24_egp * (21/24)
    price_18_egp = price_24_egp * (18/24)
    
    # هامش محلات الذهب (تقريبي 2%)
    spread = 0.02 

    # --- Header ---
    st.title("⚡ NEUXS GOLD INTELLIGENCE")
    
    # --- العرض العالمي والمحلي ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GLOBAL GOLD (OZ)", f"${current_global_price:,.2f}")
    c2.metric("عيار 24 (مصر)", f"{int(price_24_egp)} EGP")
    c3.metric("عيار 21 (مصر)", f"{int(price_21_egp)} EGP")
    c4.metric("عيار 18 (مصر)", f"{int(price_18_egp)} EGP")

    st.markdown("---")

    # --- جدول البيع والشراء للتجار ---
    st.subheader("🏦 تجارة الصاغة (تقديري):")
    trade_col1, trade_col2 = st.columns(2)
    
    with trade_col1:
        st.success(f"🟢 سعر الشراء (عيار 21): {int(price_21_egp)} EGP")
    with trade_col2:
        st.error(f"🔴 سعر البيع (عيار 21): {int(price_21_egp * (1-spread))} EGP")

    # --- الرسم البياني النيون ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=gold_data.index, y=gold_data['Close'], 
                             line=dict(color='#00ff41', width=3),
                             fill='toself', fillcolor='rgba(0, 255, 65, 0.1)', name="LIVE GOLD"))
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                      plot_bgcolor='rgba(0,0,0,0)', xaxis_showgrid=False, yaxis_showgrid=False)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.write("CONNECTING TO NEUXS CORE...")
