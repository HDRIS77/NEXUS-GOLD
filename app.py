import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- إعدادات الواجهة النيون ---
st.set_page_config(page_title="NEUXS GOLD INTELLIGENCE", layout="wide")

# تحديث الصفحة تلقائياً كل ثانية واحدة
st_autorefresh(interval=1000, key="datarefresh")

# تصميم CSS مخصص للواجهة النيون
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stMetricValue"] { color: #00ff41; text-shadow: 0 0 10px #00ff41; font-size: 2rem; }
    div[data-testid="stMetricLabel"] { color: #ffffff; font-weight: bold; }
    h1, h2, h3 { color: #00ff41 !important; text-shadow: 0 0 15px #00ff41; text-align: center; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00ff41; padding: 20px; border-radius: 15px; box-shadow: 0 0 20px rgba(0, 255, 65, 0.2); }
    hr { border: 1px solid #00ff41; }
    </style>
    """, unsafe_allow_html=True)

# --- نظام الأمان ---
PASSWORD = "neuxs_gold_2024"
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 NEUXS ACCESS CONTROL")
    pwd = st.text_input("ENTER ACCESS KEY:", type="password")
    if pwd == PASSWORD: 
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- محرك البيانات والحسابات ---
def get_live_data():
    # سحب الذهب العالمي
    gold = yf.download("GC=F", period="1d", interval="1m")
    # سعر دولار الصاغة (تقدر تعدله يدوياً حسب السوق السوداء)
    usd_egp_blackmarket = 72.0 
    return gold, usd_egp_blackmarket

try:
    gold_df, egp_rate = get_live_data()
    
    # تنظيف الداتا
    if isinstance(gold_df.columns, pd.MultiIndex): gold_df.columns = gold_df.columns.get_level_values(0)
    
    current_global = float(gold_df['Close'].iloc[-1])
    prev_close = float(gold_df['Open'].iloc[-1])
    change = current_global - prev_close

    # حسابات مصر (الأوقية 31.1 جرام)
    price_24 = (current_global / 31.1) * egp_rate
    price_21 = price_24 * (21/24)
    price_18 = price_24 * (18/24)
    
    # هامش تجاري (Spread) 1%
    buy_price_21 = price_21
    sell_price_21 = price_21 * 0.98

    # --- الواجهة الرئيسية ---
    st.markdown("<h1>⚡ NEUXS GOLD TERMINAL ⚡</h1>", unsafe_allow_html=True)
    
    # الصف الأول: الأسعار العالمية والمحلية
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("GLOBAL GOLD (OZ)", f"${current_global:,.2f}", f"{change:+.2f}")
    col2.metric("عيار 24 (مصر)", f"{int(price_24):,} EGP")
    col3.metric("عيار 21 (مصر)", f"{int(price_21):,} EGP")
    col4.metric("عيار 18 (مصر)", f"{int(price_18):,} EGP")

    st.markdown("<hr>", unsafe_allow_html=True)

    # الصف الثاني: قرار البيع والشراء للتجار
    t1, t2 = st.columns(2)
    with t1:
        st.success(f"🟢 سعر شراء المحل (21): {int(buy_price_21):,} ج.م")
    with t2:
        st.error(f"🔴 سعر بيع المحل (21): {int(sell_price_21):,} ج.م")

    # الرسم البياني النيون المشع
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=gold_df.index, y=gold_df['Close'], 
                             line=dict(color='#00ff41', width=4),
                             fill='toself', fillcolor='rgba(0, 255, 65, 0.1)',
                             name="LIVE PRICE"))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#1a1a1a')
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("... جاري الاتصال بنظام نيكسس وتحديث البيانات")
