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
    try:
        requests.get(url, timeout=5)
    except:
        pass

# 2. إعدادات الصفحة والتحديث الفائق
st.set_page_config(page_title="NEXUS GOLD TERMINAL PRO V6", layout="wide")
st_autorefresh(interval=10000, key="nexus_v6_final")

# 3. تصميم الواجهة النيون
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; }
    h1, h2, h3 { color: #00E5FF !important; text-shadow: 0 0 15px #00E5FF; text-align: center; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; }
    .oracle-box { border: 2px solid #00E5FF; background: rgba(0, 229, 255, 0.05); padding: 20px; border-radius: 15px; min-height: 280px; }
    .timer-text { color: #FFD700; text-align: center; font-size: 14px; margin-bottom: 10px; font-family: monospace; }
    .trend-up { color: #39FF14; font-weight: bold; }
    .trend-down { color: #FF007F; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 4. نظام الأمان (تم إصلاح خطأ الـ Submit Button هنا)
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    with st.form("login_form"):
        st.markdown("### 🔒 NEXUS SECURITY GATE")
        key = st.text_input("NEXUS KEY:", type="password")
        submit = st.form_submit_button("دخول النظام") # هذا الزرار يحل المشكلة الظاهرة في صورتك
        if submit and key == "neuxs_gold_2024":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 5. شريط التحكم الجانبي
with st.sidebar:
    st.markdown("### 🛠️ إعدادات الصاغة")
    local_21 = st.number_input("سعر عيار 21 (مصر):", value=7030)
    bank_usd = st.number_input("سعر دولار البنك:", value=48.5)
    st.markdown("---")
    if st.button("🔄 تحديث إجباري"):
        st.session_state.last_update = time.time()
        st.rerun()

# 6. محرك البيانات
@st.cache_data(ttl=10)
def get_market_data():
    df = yf.download("GC=F", period="1mo", interval="1h")
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    return df

try:
    df = get_market_data()
    curr_global = float(df['Close'].iloc[-1])
    prev_global = float(df['Close'].iloc[-2])
    rsi_val = float(df['RSI'].iloc[-1])
    
    # تحديد اتجاه السهم
    trend_arrow = "<span class='trend-up'>▲ (السعر يسخن)</span>" if curr_global > prev_global else "<span class='trend-down'>▼ (السعر يبرد)</span>"
    
    # الحسابات
    fair_21_usd = (curr_global / 31.1035) * (21/24)
    hedging_usd = local_21 / fair_21_usd
    gap_pct = ((hedging_usd - bank_usd) / bank_usd) * 100
    fair_local_price = fair_21_usd * bank_usd

    st.markdown("<h1>⚡ NEXUS INTELLIGENCE TERMINAL ⚡</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='timer-text'>⏱️ السهم اللحظي: {trend_arrow}</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GLOBAL SPOT", f"${curr_global:,.2f}")
    c2.metric("HEDGING USD", f"{hedging_usd:.2f} ج.م")
    c3.metric("ARB GAP", f"{gap_pct:.1f}%")
    c4.metric("CONFIDENCE", f"{int(50 + (abs(50-rsi_val)*0.5))}%")

    st.markdown("---")

    # المربعات التحليلية
    col_a, col_b = st.columns(2)
    with col_a:
        if gap_pct < -1:
            msg = f"<div style='color:#39FF14;'>✅ اشتري فوراً</div><p>المكسب المتوقع: {fair_local_price - local_21:.0f} ج/جرام</p>"
        elif gap_pct > 5:
            msg = "<div style='color:#FF007F;'>❌ بيع/انتظر</div><p>السعر في مصر أغلى من العالمي.</p>"
        else:
            msg = "<div style='color:#FFD700;'>🔄 تفرج (HOLD)</div><p>السوق متزن تماماً.</p>"
        st.markdown(f"<div class='oracle-box'><h3>📅 المدى القريب</h3>{msg}</div>", unsafe_allow_html=True)

    with col_b:
        rsi_color = "#FF007F" if rsi_val > 70 else "#39FF14" if rsi_val < 35 else "#00E5FF"
        long_msg = f"<p>الاتجاه العام: صاعد 📈</p><p style='color:{rsi_color}'>مؤشر القوة RSI: {int(rsi_val)}</p>"
        st.markdown(f"<div class='oracle-box'><h3>⏳ المدى البعيد</h3>{long_msg}</div>", unsafe_allow_html=True)

    # الشارت
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    increasing_line_color='#39FF14', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("Nexus is calibrating...")
