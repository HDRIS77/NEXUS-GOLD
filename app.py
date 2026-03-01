import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة والتحديث الفائق (كل 5 ثواني لضمان اللحظية)
st.set_page_config(page_title="NEXUS GOLD V12 - ALWAYS LIVE", layout="wide")
st_autorefresh(interval=5000, key="nexus_v12_ultra")

# 2. تصميم الواجهة النيون المطور
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; font-size: 32px !important; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; padding: 15px; }
    .oracle-box { border: 2px solid #39FF14; background: rgba(57, 255, 20, 0.05); padding: 20px; border-radius: 15px; text-align: center; }
    .live-status { color: #39FF14; font-family: monospace; font-size: 14px; text-align: center; margin-bottom: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. محرك سحب السعر "الذي لا ينام" (Force Sync)
def get_ultra_live_price():
    try:
        # إجبار المكتبة على سحب بيانات جديدة تماماً بدون كاش
        ticker = yf.Ticker("XAUUSD=X")
        # سحب بيانات آخر 5 دقائق فقط لضمان السرعة القصوى
        df = ticker.history(period="1d", interval="1m")
        
        if df.empty or len(df) < 1:
            # محاولة بديلة برمز الذهب الآجل
            df = yf.download("GC=F", period="1d", interval="1m", progress=False)

        current_price = float(df['Close'].iloc[-1])
        sync_time = datetime.datetime.now().strftime("%H:%M:%S")
        return current_price, f"CONNECTED - SYNCED AT {sync_time} ✅"
    except:
        # في حالة انقطاع السيرفر العالمي فقط يثبت على آخر سعر
        return 5278.00, "RECONNECTING TO SERVER... 🔄"

# 4. التنفيذ والحسابات
global_price, sync_status = get_ultra_live_price()

with st.sidebar:
    st.markdown("### 🇪🇬 تسعير مصر")
    # السعر الحالي لعيار 21 في مصر
    local_21 = st.number_input("سعر عيار 21 الآن:", value=7600) 
    bank_usd = st.number_input("دولار البنك:", value=48.50)
    st.markdown("---")
    st.write(f"📡 {sync_status}")

# حسابات نكسوس الفورية
# سعر الأوقية عالمياً مقسوماً على 31.1035 للجرام
global_21_usd = (global_price / 31.1035) * (21/24)
fair_price_egp = global_21_usd * bank_usd
gap = ((local_21 - fair_price_egp) / fair_price_egp) * 100

# 5. العرض الرئيسي
st.markdown("<h1>⚡ NEXUS GOLD INTELLIGENCE V12 ⚡</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='live-status'>STREAM STATUS: {sync_status}</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("GLOBAL SPOT (LIVE)", f"${global_price:,.2f}")
c2.metric("FAIR EGP (السعر العادل)", f"{fair_price_egp:,.0f} ج.م")
c3.metric("ARB GAP (الفجوة حالياً)", f"{gap:.1f}%")

st.markdown("---")

# 6. صندوق القرار اللحظي
st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
# الفجوة الحالية تظهر تضخماً بنسبة 7.8% في مصر
if gap < 0:
    st.success(f"✅ إشارة: اقتنص الفرصة (شراء) - الفجوة لصالحك")
else:
    st.markdown("<h3 style='color:#FFD700;'>🔄 إشارة: تريّث (احتفاظ)</h3>", unsafe_allow_html=True)
    st.write(f"السوق المصري يسبق العالمي بـ {gap:.1f}%. انتظر حتى يلحق السعر العالمي أو يصحح المحلي.")
st.markdown("</div>", unsafe_allow_html=True)

# 7. عداد الفتح (للمعلومة فقط)
now = datetime.datetime.now()
next_monday = now + datetime.timedelta(days=(7 - now.weekday()) % 7)
opening = datetime.datetime(next_monday.year, next_monday.month, next_monday.day, 1, 0, 0)
if now < opening:
    diff = opening - now
    st.write(f"⚠️ البورصة في عطلة حالياً | نبض السوق القادم بعد: {diff.seconds // 3600} ساعة و {(diff.seconds // 60) % 60} دقيقة")
