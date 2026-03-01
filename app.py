import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
import datetime
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات التحديث (كل 7 ثواني)
st.set_page_config(page_title="NEXUS GOLD ULTIMATE V14", layout="wide")
st_autorefresh(interval=7000, key="nexus_v14_fix")

# 2. تصميم الواجهة (إصلاح الصناديق)
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; font-size: 28px !important; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #333; border-radius: 12px; padding: 10px; }
    
    /* ستايل الصندوق الموحد */
    .nexus-card {
        border: 2px solid #00E5FF;
        background-color: rgba(0, 229, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        min-height: 220px;
        margin-bottom: 20px;
    }
    .card-title { color: #00E5FF; font-size: 20px; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px; }
    .card-content { color: #ffffff; font-size: 16px; line-height: 1.6; }
    .highlight-green { color: #39FF14; font-weight: bold; font-size: 22px; }
    .highlight-red { color: #FF007F; font-weight: bold; font-size: 22px; }
    .highlight-gold { color: #FFD700; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

# 3. محرك البيانات
def get_nexus_data():
    try:
        ticker = yf.Ticker("XAUUSD=X")
        df = ticker.history(period="2d", interval="1m")
        if df.empty:
            df = yf.download("XAUUSD=X", period="2d", interval="1m", progress=False)
        
        df['RSI'] = ta.rsi(df['Close'], length=14)
        curr_p = float(df['Close'].iloc[-1])
        rsi_v = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50
        return curr_p, rsi_v, df, datetime.datetime.now().strftime("%H:%M:%S")
    except:
        return 5278.87, 55.0, pd.DataFrame(), "Offline"

# 4. العداد الزمني
def get_opening_countdown():
    now = datetime.datetime.now()
    next_monday = now + datetime.timedelta(days=(7 - now.weekday()) % 7)
    opening = datetime.datetime(next_monday.year, next_monday.month, next_monday.day, 1, 0, 0)
    if now >= opening: return "MARKET IS OPEN 🟢"
    diff = opening - now
    return f"Market Pulse In: {diff.seconds // 3600}h {(diff.seconds // 60) % 60}m {diff.seconds % 60}s ⏳"

# التنفيذ
price, rsi, df_full, sync_time = get_nexus_data()
countdown_msg = get_opening_countdown()

# 5. التحكم الجانبي
with st.sidebar:
    st.markdown("### 🛠️ لوحة التحكم")
    local_21 = st.number_input("سعر عيار 21 (مصر):", value=7600)
    bank_usd = st.number_input("سعر دولار البنك:", value=48.50)
    st.markdown("---")
    if st.button("🔄 تحديث يدوي الآن"): st.rerun()
    st.write(f"⏱️ آخر مزامنة: {sync_time}")

# 6. الواجهة الرئيسية
st.markdown("<h1 style='text-align: center; color: #00E5FF;'>⚡ NEXUS GOLD TERMINAL V14 ⚡</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #FFD700; font-family: monospace;'>{countdown_msg}</p>", unsafe_allow_html=True)

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

# 7. المدى القريب والبعيد (إصلاح ظهور الكلام داخل المربع)
col_left, col_right = st.columns(2)

with col_left:
    if gap_pct < 0:
        status_html = f"<div class='highlight-green'>إشارة شراء لقطة</div><p>المكسب المتوقع: {fair_local - local_21:.0f} ج/جرام</p>"
    elif gap_pct > 5:
        status_html = "<div class='highlight-red'>إشارة انتظار/بيع</div><p>السوق المصري متضخم حالياً.</p>"
    else:
        status_html = "<div class='highlight-gold'>تداول مستقر</div><p>السعر العادل متطابق مع الصاغة.</p>"
    
    st.markdown(f"""
        <div class='nexus-card'>
            <div class='card-title'>📅 المدى القريب (Scaping)</div>
            <div class='card-content'>{status_html}</div>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    trend_text = "صاعد قوي 📈" if rsi > 50 else "تصحيح هابط 📉"
    rsi_color = "#39FF14" if rsi < 40 else "#FF007F" if rsi > 60 else "#00E5FF"
    
    st.markdown(f"""
        <div class='nexus-card'>
            <div class='card-title'>⏳ المدى البعيد (Trend)</div>
            <div class='card-content'>
                الاتجاه العام: <b>{trend_text}</b><br>
                مؤشر القوة RSI: <span style='color:{rsi_color}; font-weight:bold;'>{int(rsi)}</span><br><br>
                التوقعات: استهداف <b>$5,500</b> قريباً.
            </div>
        </div>
    """, unsafe_allow_html=True)

# 8. الرسم البياني
st.markdown("### 📊 نبض البورصة اللحظي (XAU/USD)")
if not df_full.empty:
    fig = go.Figure(data=[go.Candlestick(
        x=df_full.index, open=df_full['Open'], high=df_full['High'],
        low=df_full['Low'], close=df_full['Close'],
        increasing_line_color='#39FF14', decreasing_line_color='#FF007F'
    )])
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0, r=0, b=0, t=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📊 الرسم البياني في وضع الاستعداد (البورصة مغلقة حالياً)")
