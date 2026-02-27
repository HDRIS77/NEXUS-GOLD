import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh
import time

# 1. إعدادات الصفحة
st.set_page_config(page_title="NEXUS GOLD TERMINAL PRO", layout="wide")
# تحديث تلقائي كل 10 ثواني لضمان أقصى دقة
st_autorefresh(interval=10000, key="nexus_ultra_refresh")

# 2. تصميم الواجهة النيون
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; }
    h1, h2, h3 { color: #00E5FF !important; text-shadow: 0 0 15px #00E5FF; text-align: center; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; }
    .oracle-box { border: 2px solid #00E5FF; background: rgba(0, 229, 255, 0.05); padding: 20px; border-radius: 15px; min-height: 280px; }
    .timer-text { color: #FFD700; text-align: center; font-size: 14px; margin-bottom: 20px; font-family: monospace; }
    .buy-signal { color: #39FF14; font-size: 24px; font-weight: bold; }
    .sell-signal { color: #FF007F; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. إدارة وقت التحديث
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

# 4. التحكم في البيانات
with st.sidebar:
    st.markdown("### 🛠️ إعدادات الصاغة")
    local_21 = st.number_input("سعر عيار 21 (مصر):", value=7020)
    bank_usd = st.number_input("سعر دولار البنك:", value=48.5)
    st.markdown("---")
    if st.button("تحديث يدوي الآن"):
        st.session_state.last_update = time.time()
        st.rerun()

# 5. جلب الداتا العالمية
@st.cache_data(ttl=10)
def get_intel():
    df = yf.download("GC=F", period="1mo", interval="1h")
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    return df

try:
    df = get_intel()
    curr_global = float(df['Close'].iloc[-1])
    rsi_val = float(df['RSI'].iloc[-1])
    
    # حساب الثواني المنقضية
    seconds_ago = int(time.time() - st.session_state.last_update)
    
    # الحسابات الاقتصادية
    fair_21_usd = (curr_global / 31.1035) * (21/24)
    hedging_usd = local_21 / fair_21_usd
    gap_pct = ((hedging_usd - bank_usd) / bank_usd) * 100
    fair_local_price = fair_21_usd * bank_usd

    st.markdown("<h1>⚡ NEXUS INTELLIGENCE TERMINAL ⚡</h1>", unsafe_allow_html=True)
    
    # عرض عداد الثواني
    st.markdown(f"<div class='timer-text'>⏱️ آخر تحديث للسعر العالمي: منذ {seconds_ago} ثانية</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GLOBAL SPOT", f"${curr_global:,.2f}")
    c2.metric("HEDGING USD", f"{hedging_usd:.2f} ج.م")
    c3.metric("ARB GAP", f"{gap_pct:.1f}%")
    c4.metric("CONFIDENCE", f"{int(50 + (abs(50-rsi_val)*0.5))}%")

    st.markdown("---")

    # 6. المربعات التحليلية
    col_a, col_b = st.columns(2)
    
    if gap_pct < -1:
        short_html = f"<div class='buy-signal'>✅ القرار: اشتري فوراً</div><p><b>التحليل:</b> الذهب في مصر أرخص من العالمي بـ {abs(gap_pct):.1f}%.<br><b>السعر العادل:</b> {fair_local_price:.0f} ج.م.<br><b>الفرصة:</b> ربح {fair_local_price - local_21:.0f} جنيه في كل جرام عند التصحيح.</p>"
    elif gap_pct > 12:
        short_html = f"<div class='sell-signal'>❌ القرار: بيع/انتظر</div><p><b>التحليل:</b> السعر في مصر سابق العالمي بفقاعة {gap_pct:.1f}%.<br><b>المخاطرة:</b> عالية جداً لو العالمي ثبت.</p>"
    else:
        short_html = "<div class='hold-signal'>🔄 القرار: تفرج (HOLD)</div><p>السوق متزن تماماً بين مصر وبورصة نيويورك.</p>"

    long_html = f"<div class='buy-signal'>📈 المدى البعيد: صاعد</div>" if curr_global > df['EMA_20'].iloc[-1] else f"<div class='sell-signal'>📉 المدى البعيد: هابط</div>"
    long_html += f"<p><b>المستوى القادم:</b> ${curr_global * 1.05:.0f}<br><b>مؤشر القوة (RSI):</b> {int(rsi_val)}</p>"

    with col_a:
        st.markdown(f"<div class='oracle-box'><h3>📅 المدى القريب</h3>{short_html}</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"<div class='oracle-box'><h3>⏳ المدى البعيد</h3>{long_html}</div>", unsafe_allow_html=True)

    # 7. الشارت
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    increasing_line_color='#39FF14', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Nexus Sync Error: {e}")
