import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
import datetime
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة والتحديث (كل 7 ثواني - توازن بين السرعة والثبات)
st.set_page_config(page_title="NEXUS GOLD ULTIMATE V13", layout="wide")
st_autorefresh(interval=7000, key="nexus_v13_final")

# 2. تصميم الواجهة (العودة لستايل المحترفين)
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; font-size: 30px !important; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #333; border-radius: 12px; padding: 10px; }
    .oracle-box { border: 1px solid #00E5FF; background: rgba(0, 229, 255, 0.05); padding: 15px; border-radius: 12px; min-height: 180px; text-align: center; }
    .live-tag { background: #39FF14; color: black; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    .countdown-text { color: #FFD700; font-family: monospace; font-size: 16px; text-align: center; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. محرك البيانات (المتكامل)
def get_nexus_data():
    try:
        # سحب بيانات الذهب (XAUUSD=X) بفاصل دقيقة
        ticker = yf.Ticker("XAUUSD=X")
        df = ticker.history(period="2d", interval="1m")
        if df.empty:
            df = yf.download("XAUUSD=X", period="2d", interval="1m", progress=False)
        
        # حساب المؤشرات
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['EMA_20'] = ta.ema(df['Close'], length=20)
        
        curr_p = float(df['Close'].iloc[-1])
        rsi_v = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50
        return curr_p, rsi_v, df, datetime.datetime.now().strftime("%H:%M:%S")
    except:
        # العودة لسعر الإغلاق التاريخي لو فيه مشكلة في السيرفر
        return 5278.87, 55.0, pd.DataFrame(), "Fallback-Mode"

# 4. حساب الوقت المتبقي لفتح البورصة
def get_opening_countdown():
    now = datetime.datetime.now()
    next_monday = now + datetime.timedelta(days=(7 - now.weekday()) % 7)
    opening = datetime.datetime(next_monday.year, next_monday.month, next_monday.day, 1, 0, 0)
    if now >= opening: return "MARKET IS OPEN 🟢"
    diff = opening - now
    return f"Market Pulse In: {diff.seconds // 3600}h {(diff.seconds // 60) % 60}m {diff.seconds % 60}s"

# 5. التنفيذ
price, rsi, df_full, sync_time = get_nexus_data()
countdown_msg = get_opening_countdown()

# 6. شريط التحكم الجانبي
with st.sidebar:
    st.markdown("### 🛠️ لوحة التحكم")
    local_21 = st.number_input("سعر عيار 21 (مصر):", value=7600)
    bank_usd = st.number_input("سعر دولار البنك:", value=48.50)
    st.markdown("---")
    if st.button("🔄 تحديث يدوي الآن"):
        st.rerun()
    st.write(f"⏱️ آخر مزامنة: {sync_time}")

# 7. واجهة العرض الرئيسية
st.markdown("<h1 style='text-align: center;'>⚡ NEXUS GOLD TERMINAL V13 ⚡</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='countdown-text'>{countdown_msg}</div>", unsafe_allow_html=True)

# الحسابات
global_21_usd = (price / 31.1035) * (21/24)
fair_local = global_21_usd * bank_usd
gap_pct = ((local_21 - fair_local) / fair_local) * 100
confidence = int(100 - abs(50 - rsi)) # معادلة بسيطة لقوة الإشارة

c1, c2, c3, c4 = st.columns(4)
c1.metric("GLOBAL SPOT", f"${price:,.2f}")
c2.metric("FAIR PRICE", f"{fair_local:,.0f} ج.م")
c3.metric("ARB GAP", f"{gap_pct:.1f}%")
c4.metric("CONFIDENCE", f"{confidence}%")

st.markdown("---")

# 8. المدى القريب والمدى البعيد
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
    st.markdown("### 📅 المدى القريب (Scaping)")
    if gap_pct < 0:
        st.markdown("<h2 style='color:#39FF14;'>إشارة شراء لقطة</h2>", unsafe_allow_html=True)
        st.write("الفجوة لصالحك. السوق المصري لم يواكب الزيادة العالمية.")
    elif gap_pct > 5:
        st.markdown("<h2 style='color:#FF007F;'>إشارة انتظار/بيع</h2>", unsafe_allow_html=True)
        st.write("تضخم محلي واضح. انتظر تصحيح السعر في مصر.")
    else:
        st.markdown("<h2 style='color:#FFD700;'>تداول مستقر</h2>", unsafe_allow_html=True)
        st.write("السعر العادل متطابق مع سعر المحلات.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
    st.markdown("### ⏳ المدى البعيد (Trend)")
    trend = "صاعد قوي 📈" if rsi > 50 else "تصحيح هابط 📉"
    rsi_color = "#FF007F" if rsi > 70 else "#39FF14" if rsi < 30 else "#00E5FF"
    st.write(f"الاتجاه العام للذهب: **{trend}**")
    st.markdown(f"مؤشر القوة RSI: <span style='color:{rsi_color}; font-weight:bold;'>{int(rsi)}</span>", unsafe_allow_html=True)
    st.write("التوقعات: استهداف مستويات $5,500 خلال مارس.")
    st.markdown("</div>", unsafe_allow_html=True)

# 9. الرسم البياني (The Chart)
st.markdown("### 📊 نبض البورصة اللحظي (XAU/USD)")
if not df_full.empty:
    fig = go.Figure(data=[go.Candlestick(
        x=df_full.index,
        open=df_full['Open'], high=df_full['High'],
        low=df_full['Low'], close=df_full['Close'],
        increasing_line_color='#39FF14', decreasing_line_color='#FF007F'
    )])
    fig.update_layout(
        template="plotly_dark",
        height=450,
        margin=dict(l=0, r=0, b=0, t=0),
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📊 الرسم البياني في انتظار أول نبضة من البورصة فجر الإثنين...")
