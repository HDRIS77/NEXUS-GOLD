import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
import numpy as np
from streamlit_autorefresh import st_autorefresh

# 1. إعداد الصفحة (أول سطر كود)
st.set_page_config(page_title="NEXUS GOLD TERMINAL", layout="wide")

# تحديث تلقائي كل 30 ثانية
st_autorefresh(interval=30000, key="nexus_refresh")

# 2. تصميم الواجهة نيون أزرق (NEXUS STYLE)
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; }
    h1, h2, h3 { color: #00E5FF !important; text-shadow: 0 0 15px #00E5FF; text-align: center; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; padding: 15px; }
    .oracle-box { border: 2px solid #00E5FF; background: rgba(0, 229, 255, 0.05); padding: 20px; border-radius: 15px; margin-bottom: 20px; }
    .alarm-red { border: 2px solid #FF007F; background: rgba(255, 0, 127, 0.1); padding: 15px; border-radius: 10px; color: #FF007F; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. نظام الأمان
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1>🔐 NEXUS GATE</h1>", unsafe_allow_html=True)
    with st.form("login_gate"):
        pwd = st.text_input("ENTER ACCESS KEY:", type="password")
        if st.form_submit_button("UNLOCK"):
            if pwd == "neuxs_gold_2024":
                st.session_state.auth = True
                st.rerun()
            else: st.error("INVALID KEY")
    st.stop()

# 4. التحكم اليدوي (السوق المصري)
with st.sidebar:
    st.markdown("### ⚙️ إعدادات الصاغة")
    local_21 = st.number_input("سعر جرام 21 الحالي في مصر:", value=3500)
    bank_usd = st.number_input("سعر دولار البنك (الرسمي):", value=48.5)
    st.markdown("---")
    st.info("تحديث هذه الأرقام يحدث 'توقعات النظام' فوراً.")

# 5. محرك البيانات والتحليل
@st.cache_data(ttl=30)
def fetch_data():
    # سحب داتا 60 يوم للتحليل البعيد
    df = yf.download("GC=F", period="60d", interval="1h")
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
    df['EMA_50'] = ta.ema(df['Close'], length=50)
    return df

try:
    df = fetch_data()
    curr_global = float(df['Close'].iloc[-1])
    rsi_val = float(df['RSI'].iloc[-1])
    atr_val = float(df['ATR'].iloc[-1])

    # حسابات "محامي الشيطان" (Arbitrage)
    hedging_usd = (local_21 * 31.1 / curr_global) / (21/24)
    gap_pct = ((hedging_usd - bank_usd) / bank_usd) * 100

    st.markdown("<h1>⚡ NEXUS INTELLIGENCE TERMINAL ⚡</h1>", unsafe_allow_html=True)

    # مؤشر التذبذب
    if atr_val > df['ATR'].mean() * 1.5:
        st.markdown("<div class='alarm-red'>🚨 ALERT: HIGH VOLATILITY - تذبذب عالي | خطر في التنفيذ حالياً</div>", unsafe_allow_html=True)

    # المؤشرات الرئيسية
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GLOBAL SPOT", f"${curr_global:,.2f}")
    c2.metric("HEDGING USD", f"{hedging_usd:.2f} ج.م")
    c3.metric("ARB GAP (فقاعة)", f"{gap_pct:.1f}%")
    conf_score = 50 + (abs(50 - rsi_val) * 0.5)
    c4.metric("CONFIDENCE", f"{int(conf_score)}%")

    st.markdown("---")

    # 6. خانة التوقعات (التي تسميها Oracle)
    st.markdown("### 🔮 NEXUS ANALYTICS: توقعات قريب وبعيد المدى")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
        st.subheader("📅 المدى القريب (أيام)")
        if gap_pct > 15:
            st.error("📉 SELL SIGNAL: الذهب المحلي 'فقاعة' حالياً. ينصح بالبيع (التحوط).")
        elif rsi_val < 35:
            st.success("📈 BUY SIGNAL: تشبع بيعي عالمي. فرصة شراء.")
        else:
            st.warning("🔄 HOLD: السوق مستقر، لا تتخذ قراراً متسرعاً.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
        st.subheader("⏳ المدى البعيد (أسابيع)")
        trend = "ACCUMULATION (تجميع)" if curr_global > df['EMA_50'].iloc[-1] else "DISTRIBUTION (تصريف)"
        st.write(f"**الاتجاه العام (Trend):** {trend}")
        st.write(f"**مؤشر القوة (RSI):** {int(rsi_val)}")
        st.markdown("</div>", unsafe_allow_html=True)

    # 7. الرسم البياني
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    increasing_line_color='#00E5FF', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("NEXUS is calibrating data... Please wait.")
