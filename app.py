import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh

# 1. الإعدادات
st.set_page_config(page_title="NEXUS GOLD TERMINAL", layout="wide")
st_autorefresh(interval=30000, key="nexus_final_fix")

# 2. الاستايل
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; }
    .opportunity-box { border: 2px solid #39FF14; background: rgba(57, 255, 20, 0.1); padding: 20px; border-radius: 15px; color: #39FF14; font-weight: bold; text-align: center; }
    .bubble-box { border: 2px solid #FF007F; background: rgba(255, 0, 127, 0.1); padding: 20px; border-radius: 15px; color: #FF007F; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. الأمان
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    with st.form("gate"):
        if st.text_input("KEY:", type="password") == "neuxs_gold_2024":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 4. المدخلات
with st.sidebar:
    local_21 = st.number_input("سعر 21 في مصر:", value=7020)
    bank_usd = st.number_input("دولار البنك:", value=48.5)

# 5. الداتا
@st.cache_data(ttl=30)
def get_gold():
    df = yf.download("GC=F", period="1mo", interval="1h")
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

try:
    data = get_gold()
    global_spot = float(data['Close'].iloc[-1])
    
    # الحسبة الدقيقة
    fair_price_21_usd = (global_spot / 31.1035) * (21/24)
    hedging_usd = local_21 / fair_price_21_usd
    gap_pct = ((hedging_usd - bank_usd) / bank_usd) * 100

    st.markdown("<h1>⚡ NEXUS INTELLIGENCE ⚡</h1>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("GLOBAL SPOT", f"${global_spot:,.2f}")
    c2.metric("HEDGING USD", f"{hedging_usd:.2f} EGP")
    c3.metric("ARB GAP", f"{gap_pct:.1f}%")

    st.markdown("---")

    # 6. تحليل محامي الشيطان
    if gap_pct < 0:
        st.markdown(f"""<div class='opportunity-box'>
        🔥 فرصة شراء ذهبية! <br>
        الذهب في مصر أرخص من السعر العالمي بـ {abs(gap_pct):.1f}%. <br>
        السعر العادل المفروض يكون {fair_price_21_usd * bank_usd:.0f} ج.م.
        </div>""", unsafe_allow_html=True)
    elif gap_pct > 15:
        st.markdown("<div class='bubble-box'>⚠️ تحذير: فقاعة سعرية! الذهب في مصر مسعر بدولار وهمي.</div>", unsafe_allow_html=True)
    else:
        st.info("🔄 السوق المحلي يتبع العالمي بشكل طبيعي حالياً.")

    # الشارت
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e: st.write("Waiting for market signal...")
