import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة والتحديث (كل 10 ثواني)
st.set_page_config(page_title="NEXUS GOLD V11 - LIVE", layout="wide")
st_autorefresh(interval=10000, key="nexus_v11_final")

# 2. تصميم الواجهة النيون
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; font-size: 32px !important; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; padding: 15px; }
    .oracle-box { border: 2px solid #39FF14; background: rgba(57, 255, 20, 0.05); padding: 20px; border-radius: 15px; text-align: center; }
    .countdown-box { color: #FFD700; border: 1px dashed #FFD700; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# 3. دالة حساب الوقت المتبقي لفتح البورصة (فجر الإثنين 1 صباحاً)
def get_market_countdown():
    now = datetime.datetime.now()
    # موعد الفتح: الإثنين القادم الساعة 1 صباحاً
    next_monday = now + datetime.timedelta(days=(7 - now.weekday()) % 7)
    opening_time = datetime.datetime(next_monday.year, next_monday.month, next_monday.day, 1, 0, 0)
    
    if now >= opening_time:
        return "Market is OPEN! 🟢"
    
    diff = opening_time - now
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"Market Opens In: {diff.days}d {hours}h {minutes}m {seconds}s ⏳"

# 4. محرك سحب السعر العالمي المطور
def get_global_price():
    try:
        # رمز الذهب الفوري (مطابق لجوجل وآي صاغة)
        ticker = yf.Ticker("XAUUSD=X")
        df = ticker.history(period="1d", interval="1m")
        
        if df.empty:
            # سعر الإغلاق التاريخي لو البورصة قافلة (زي اللي في صورتك)
            return 5278.00, "OFFLINE (Weekend)"
            
        current_price = float(df['Close'].iloc[-1])
        return current_price, datetime.datetime.now().strftime("%H:%M:%S")
    except:
        return 5278.00, "Syncing..."

# 5. التنفيذ والحسابات
global_price, last_sync = get_global_price()
countdown_msg = get_market_countdown()

with st.sidebar:
    st.markdown("### 🇪🇬 تسعير مصر")
    local_21 = st.number_input("سعر عيار 21 الآن:", value=7600) 
    bank_usd = st.number_input("دولار البنك:", value=48.50)
    st.markdown("---")
    st.write(f"🌍 Global Status: {last_sync}")

# حسابات نكسوس
global_21_usd = (global_price / 31.1035) * (21/24)
fair_price_egp = global_21_usd * bank_usd
gap = ((local_21 - fair_price_egp) / fair_price_egp) * 100

# 6. العرض الرئيسي
st.markdown("<h1>⚡ NEXUS GOLD INTELLIGENCE V11 ⚡</h1>", unsafe_allow_html=True)

# عرض العداد التنازلي
st.markdown(f"<div class='countdown-box'>{countdown_msg}</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("GLOBAL SPOT", f"${global_price:,.2f}")
c2.metric("FAIR EGP (العادل)", f"{fair_price_egp:,.0f} ج.م")
c3.metric("ARB GAP (الفجوة)", f"{gap:.1f}%")

st.markdown("---")

# 7. صندوق القرار
st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
if "Market Opens" in countdown_msg:
    st.markdown("<h3 style='color:#FFD700;'>⏸️ وضع الانتظار (عطلة البورصة)</h3>", unsafe_allow_html=True)
    st.write(f"السعر العالمي ثابت عند إغلاق الأسبوع (${global_price}). القرار يعتمد على دولار السوق الموازي حالياً.")
else:
    if gap < 0:
        st.success(f"✅ إشارة: شراء (الفجوة لصالحك بـ {abs(gap):.1f}%)")
    else:
        st.warning("🔄 إشارة: احتفاظ (السوق المصري متضخم)")
st.markdown("</div>", unsafe_allow_html=True)
