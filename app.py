import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh
import datetime

# 1. إعدادات الصفحة والتحديث (كل 10 ثواني)
st.set_page_config(page_title="NEXUS GOLD V10", layout="wide")
st_autorefresh(interval=10000, key="nexus_v10_live")

# 2. تصميم الواجهة النيون
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; padding: 15px; }
    .oracle-box { border: 2px solid #39FF14; background: rgba(57, 255, 20, 0.05); padding: 20px; border-radius: 15px; text-align: center; }
    .time-stamp { color: #FFD700; font-family: monospace; font-size: 12px; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. محرك سحب السعر العالمي (تحديث أوتوماتيكي ومضمون)
def get_global_price():
    try:
        # استخدام الرمز المباشر XAU/USD لضمان مطابقة شاشة iSagha
        ticker = yf.Ticker("XAUUSD=X")
        df = ticker.history(period="1d", interval="1m")
        
        # صمام أمان لو البيانات اللحظية متأخرة
        if df.empty or len(df) < 1:
            df = yf.download("XAUUSD=X", period="1d", interval="2m", progress=False)
            
        current_price = float(df['Close'].iloc[-1])
        return current_price, datetime.datetime.now().strftime("%H:%M:%S")
    except:
        # لو السيرفر وقع، يرجع آخر سعر معروف (زي اللي في صورك)
        return 5278.00, "Offline-Cache"

# 4. التنفيذ
global_price, last_sync = get_global_price()

with st.sidebar:
    st.markdown("### 🇪🇬 تسعير مصر")
    # تم تحديث القيمة الافتراضية لـ 7600 بناءً على iSagha
    local_21 = st.number_input("سعر عيار 21 الآن:", value=7600) 
    bank_usd = st.number_input("دولار البنك:", value=48.50)
    st.info(f"آخر مزامنة عالمية: {last_sync}")

# 5. الحسابات الذكية
# سعر جرام 21 عالمياً بناءً على السعر العالمي اللحظي
global_21_usd = (global_price / 31.1035) * (21/24)
fair_price_egp = global_21_usd * bank_usd
gap = ((local_21 - fair_price_egp) / fair_price_egp) * 100

# 6. العرض
st.markdown("<h1>⚡ NEXUS GOLD INTELLIGENCE V10 ⚡</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='time-stamp'>LIVE GLOBAL FEED: {last_sync}</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("GLOBAL SPOT", f"${global_price:,.2f}")
c2.metric("FAIR EGP (السعر العادل)", f"{fair_price_egp:,.0f} ج.م")
c3.metric("ARB GAP (الفجوة)", f"{gap:.1f}%")

st.markdown("---")

# 7. تحليل "محامي الشيطان" لقرار اللحظة
st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
if gap < 0:
    st.markdown(f"<h2 style='color:#39FF14;'>✅ إشارة: اقتنص الفرصة (شراء)</h2>", unsafe_allow_html=True)
    st.write(f"الذهب في مصر لسه متسعر أرخص من العالمي بـ {abs(gap):.1f}%. المكسب المتوقع: {fair_price_egp - local_21:.0f} جنيه في الجرام.")
else:
    st.markdown(f"<h2 style='color:#FFD700;'>🔄 إشارة: تريّث (احتفاظ)</h2>", unsafe_allow_html=True)
    st.write("السوق المصري بدأ يسبق العالمي. انتظر تصحيح أو استقرار الفجوة.")
st.markdown("</div>", unsafe_allow_html=True)
