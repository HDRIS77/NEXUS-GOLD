import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 1. إعدادات الصفحة (يجب أن يكون أول أمر في الكود) ---
st.set_page_config(page_title="NEXUS GOLD INTELLIGENCE", layout="wide")

# --- 2. نظام الأمان (حل مشكلة عدم الاستجابة لـ Enter) ---
PASSWORD = "neuxs_gold_2024"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #00E5FF; text-shadow: 0 0 15px #00E5FF;'>🔐 NEXUS ACCESS CONTROL</h1>", unsafe_allow_html=True)
    
    # استخدام st.form بيجبر البرنامج يلقط الـ Enter ويرسل البيانات
    with st.form("login_gate"):
        pwd = st.text_input("ENTER ACCESS KEY:", type="password")
        submitted = st.form_submit_button("UNLOCK TERMINAL")
        
        if submitted:
            if pwd == PASSWORD:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ INVALID KEY")
    st.stop()

# --- 3. تصميم الواجهة النيون ---
st_autorefresh(interval=30000, key="nexus_refresh") # تحديث كل 30 ثانية

st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; font-size: 2.5rem; }
    div[data-testid="stMetricLabel"] { color: #ffffff; font-weight: bold; }
    h1, h2, h3 { color: #00E5FF !important; text-shadow: 0 0 15px #00E5FF; text-align: center; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; padding: 25px; border-radius: 15px; box-shadow: 0 0 15px rgba(0, 229, 255, 0.1); }
    hr { border: 1px solid #00E5FF; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. جلب البيانات والحسابات ---
@st.cache_data(ttl=30)
def fetch_gold_data():
    data = yf.download("GC=F", period="5d", interval="1m")
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

try:
    gold_df = fetch_gold_data()
    current_price = float(gold_df['Close'].iloc[-1])
    
    # حسابات السوق المصري (مثال)
    usd_rate = 72.0
    price_21k = (current_price / 31.1) * usd_rate * (21/24)

    st.markdown("<h1>⚡ NEXUS INTELLIGENCE TERMINAL ⚡</h1>", unsafe_allow_html=True)

    # عرض البيانات في كروت نيون
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("GLOBAL SPOT (OZ)", f"${current_price:,.2f}")
    with c2: st.metric("LOCAL 21K (EGP)", f"{int(price_21k):,} ج.م")
    with c3: st.metric("SYSTEM STATUS", "ONLINE", delta="STABLE")

    st.markdown("<hr>", unsafe_allow_html=True)

    # الرسم البياني
    fig = go.Figure(data=[go.Candlestick(x=gold_df.index,
                    open=gold_df['Open'], high=gold_df['High'],
                    low=gold_df['Low'], close=gold_df['Close'],
                    increasing_line_color='#00E5FF', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("Synchronizing with Global Markets...")
