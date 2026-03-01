import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh
import time
import requests

# ==========================================
# 1. إعدادات التنبيهات (حط بياناتك هنا)
# ==========================================
TELEGRAM_TOKEN = "اكتب_هنا_الـ_TOKEN_بتاعك"
CHAT_ID = "اكتب_هنا_رقم_الـ_ID_بتاعك"

def send_telegram_msg(message):
    if "اكتب_هنا" in TELEGRAM_TOKEN: return 
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try: requests.get(url, timeout=5)
    except: pass

# 2. إعدادات الصفحة والتحديث الفائق (كل 10 ثواني)
st.set_page_config(page_title="NEXUS GOLD PRO V7", layout="wide")
st_autorefresh(interval=10000, key="nexus_v7_live")

# 3. واجهة النيون الاحترافية
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; font-size: 35px !important; }
    h1, h2, h3 { color: #00E5FF !important; text-shadow: 0 0 15px #00E5FF; text-align: center; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; padding: 15px; }
    .oracle-box { border: 2px solid #00E5FF; background: rgba(0, 229, 255, 0.05); padding: 25px; border-radius: 15px; min-height: 200px; text-align: center; }
    .trend-up { color: #39FF14; font-weight: bold; }
    .trend-down { color: #FF007F; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 4. نظام الأمان
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    with st.container():
        st.markdown("<h1>🔒 NEXUS SECURITY GATE</h1>", unsafe_allow_html=True)
        with st.form("login_gate"):
            key = st.text_input("NEXUS KEY:", type="password")
            if st.form_submit_button("فتح رادار الذهب") and key == "neuxs_gold_2024":
                st.session_state.auth = True
                st.rerun()
        st.stop()

# 5. شريط التحكم الجانبي
with st.sidebar:
    st.markdown("### 🛠️ تسعير الصاغة اليوم")
    local_21 = st.number_input("سعر عيار 21 في مصر (الآن):", value=7425)
    bank_usd = st.number_input("سعر دولار البنك الرسمي:", value=48.5)
    st.markdown("---")
    st.info("💡 الكود يسحب السعر العالمي المباشر (XAU/USD) لضمان أعلى دقة.")

# 6. محرك سحب البيانات اللحظي (إصلاح مشكلة الثبات)
def get_live_data():
    # نستخدم رمز XAUUSD=X للتحديث الفوري
    ticker = yf.Ticker("XAUUSD=X")
    df = ticker.history(period="1d", interval="1m")
    if df.empty:
        df = yf.download("XAUUSD=X", period="2d", interval="1m", progress=False)
    
    # حساب المؤشرات
    df['RSI'] = ta.rsi(df['Close'], length=14)
    return df

try:
    df = get_live_data()
    curr_global = float(df['Close'].iloc[-1])
    prev_global = float(df['Close'].iloc[-2])
    rsi_val = float(df['RSI'].iloc[-1])
    
    # حساب الفجوة والدولار التحوطي
    fair_21_usd = (curr_global / 31.1035) * (21/24)
    hedging_usd = local_21 / fair_21_usd
    gap_pct = ((hedging_usd - bank_usd) / bank_usd) * 100
    fair_local_price = fair_21_usd * bank_usd

    # إرسال التنبيهات
    if rsi_val > 70 and "high_alert" not in st.session_state:
        send_telegram_msg(f"🚨 تنبيه نكسوس: السعر العالمي طار! RSI: {int(rsi_val)} | العالمي: ${curr_global}")
        st.session_state.high_alert = True
    elif rsi_val < 35 and "low_alert" not in st.session_state:
        send_telegram_msg(f"💰 تنبيه نكسوس: فرصة شراء! RSI: {int(rsi_val)} | السعر المحلي: {local_21}")
        st.session_state.low_alert = True

    # العرض الرئيسي
    st.markdown("<h1>⚡ NEXUS INTELLIGENCE V7 ⚡</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("GLOBAL SPOT (XAU)", f"${curr_global:,.2f}")
    col2.metric("HEDGING USD", f"{hedging_usd:.2f} EGP")
    col3.metric("ARB GAP", f"{gap_pct:.1f}%")

    st.markdown("---")

    # التحليل الذكي
    c_a, c_b = st.columns(2)
    with c_a:
        if gap_pct < 0:
            decision = "<h2 class='trend-up'>✅ قرار: شراء (السعر محروق)</h2>"
            detail = f"الذهب في مصر أرخص من العالمي بـ {abs(gap_pct):.1f}%"
        elif gap_pct > 15:
            decision = "<h2 class='trend-down'>❌ قرار: بيع/انتظار (فقاعة)</h2>"
            detail = "السعر في مصر فيه مغالاة كبيرة جداً."
        else:
            decision = "<h2 style='color:#FFD700;'>🔄 قرار: احتفاظ (استقرار)</h2>"
            detail = "السعر المحلي يتماشى مع البورصة العالمية."
        st.markdown(f"<div class='oracle-box'>{decision}<p>{detail}</p></div>", unsafe_allow_html=True)

    with c_b:
        rsi_stat = "تشبع شرائي (خطر)" if rsi_val > 70 else "تشبع بيعي (فرصة)" if rsi_val < 35 else "تداول مستقر"
        st.markdown(f"<div class='oracle-box'><h3>📈 مؤشر القوة (RSI)</h3><h2>{int(rsi_val)}</h2><p>{rsi_stat}</p></div>", unsafe_allow_html=True)

    # الشارت اللحظي
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    increasing_line_color='#39FF14', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Nexus Error: {e}")
    st.info("جاري محاولة إعادة الاتصال بالسيرفر العالمي...")
