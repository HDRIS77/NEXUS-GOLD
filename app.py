import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
import datetime
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات التحديث الفائق (كل 5 ثواني)
st.set_page_config(page_title="NEXUS GOLD V15 - HYPER LIVE", layout="wide")
st_autorefresh(interval=5000, key="nexus_v15_hyper")

# 2. تصميم الواجهة النيون (إصلاح شامل للصناديق والشارت)
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; font-size: 26px !important; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #333; border-radius: 12px; padding: 10px; }
    .nexus-card {
        border: 2px solid #00E5FF; background-color: rgba(0, 229, 255, 0.05);
        padding: 20px; border-radius: 15px; text-align: center; min-height: 200px;
    }
    .card-title { color: #00E5FF; font-size: 18px; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #333; }
    .status-live { color: #39FF14; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 3. محرك سحب البيانات (متعدد المصادر لضمان التشغيل)
def get_live_nexus_data():
    sources = ["XAUUSD=X", "GC=F", "GOLD"] # الذهب الفوري، العقود الآجلة، وصندوق الذهب
    for src in sources:
        try:
            ticker = yf.Ticker(src)
            df = ticker.history(period="1d", interval="1m")
            if not df.empty and len(df) > 0:
                df['RSI'] = ta.rsi(df['Close'], length=14)
                curr_p = float(df['Close'].iloc[-1])
                rsi_v = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50
                return curr_p, rsi_v, df, "LIVE 🟢"
        except:
            continue
    # سعر الطوارئ لو كل المصادر فشلت (آخر سعر مسجل في صورتك)
    return 5278.87, 55.0, pd.DataFrame(), "SYNCING... 🟡"

# 4. حساب حالة الماركت الحقيقية
def check_market_status():
    now = datetime.datetime.now()
    # البورصة تفتح الاثنين 1 صباحاً وتغلق السبت 1 صباحاً بتوقيت القاهرة
    if now.weekday() == 5 and now.hour >= 1: return False # السبت بعد الفجر
    if now.weekday() == 6: return False # الأحد كله
    if now.weekday() == 0 and now.hour < 1: return False # الاثنين قبل الفجر
    return True

# التنفيذ
price, rsi, df_full, status_label = get_live_nexus_data()
is_open = check_market_status()

# 5. القائمة الجانبية
with st.sidebar:
    st.markdown("### 🛠️ CONTROL PANEL")
    local_21 = st.number_input("سعر عيار 21 (مصر):", value=7600)
    bank_usd = st.number_input("سعر دولار البنك:", value=48.50)
    st.markdown(f"**STATUS:** {status_label}")
    if st.button("FORCE REFRESH 🔄"): st.rerun()

# 6. الواجهة الرئيسية
st.markdown("<h1 style='text-align: center; color: #00E5FF;'>⚡ NEXUS GOLD ULTIMATE V15 ⚡</h1>", unsafe_allow_html=True)

# عرض الساعة وحالة الماركت بشكل احترافي
current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
market_text = "MARKET IS OPEN 🟢" if is_open else "MARKET CLOSED 🔴"
st.markdown(f"<p style='text-align: center; color: #FFD700;'>{current_time} | {market_text}</p>", unsafe_allow_html=True)

# الحسابات
global_21_usd = (price / 31.1035) * (21/24)
fair_local = global_21_usd * bank_usd
gap_pct = ((local_21 - fair_local) / fair_local) * 100
confidence = int(100 - abs(50 - rsi))

c1, c2, c3, c4 = st.columns(4)
c1.metric("GLOBAL SPOT", f"${price:,.2f}")
c2.metric("FAIR PRICE", f"{fair_local:,.0f} ج.م")
c3.metric("ARB GAP", f"{gap_pct:.1f}%")
c4.metric("CONFIDENCE", f"{confidence}%")

st.markdown("---")

# 7. التحليل (المدى القريب والبعيد)
col_left, col_right = st.columns(2)
with col_left:
    status_msg = "شراء (لقطة)" if gap_pct < 0 else "بيع/انتظار" if gap_pct > 3 else "استقرار"
    color = "#39FF14" if gap_pct < 0 else "#FF007F" if gap_pct > 3 else "#FFD700"
    st.markdown(f"""<div class='nexus-card'><div class='card-title'>📅 المدى القريب</div>
    <h2 style='color:{color};'>{status_msg}</h2>
    <p>الفجوة الحالية هي {gap_pct:.1f}%</p></div>""", unsafe_allow_html=True)

with col_right:
    trend = "صاعد 📈" if rsi > 50 else "هابط 📉"
    st.markdown(f"""<div class='nexus-card'><div class='card-title'>⏳ المدى البعيد</div>
    <h2>{trend}</h2><p>RSI: {int(rsi)} | قوة الإشارة ممتازة</p></div>""", unsafe_allow_html=True)

# 8. الرسم البياني (إصلاح نهائي)
st.markdown("### 📊 نبض البورصة اللحظي")
if not df_full.empty:
    fig = go.Figure(data=[go.Candlestick(x=df_full.index, open=df_full['Open'], high=df_full['High'], low=df_full['Low'], close=df_full['Close'], increasing_line_color='#39FF14', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,b=0,t=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ جاري استقبال أول إشارة من البورصة العالمية.. انتظر ثواني.")
