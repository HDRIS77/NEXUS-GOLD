import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh
import time
import requests

# ==========================================
# إعدادات التنبيهات (حط بياناتك هنا)
# ==========================================
TELEGRAM_TOKEN = "اكتب_هنا_الـ_TOKEN_بتاعك"
CHAT_ID = "اكتب_هنا_رقم_الـ_ID_بتاعك"

def send_telegram_msg(message):
    if "اكتب_هنا" in TELEGRAM_TOKEN: return # تخطي لو البيانات لسه ما دخلتش
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        requests.get(url, timeout=5)
    except:
        pass

# 1. إعدادات الصفحة والتحديث الفائق (كل 10 ثواني)
st.set_page_config(page_title="NEXUS GOLD TERMINAL PRO V6", layout="wide")
st_autorefresh(interval=10000, key="nexus_final_v6")

# 2. تصميم الواجهة النيون المتقدمة
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
    .rsi-hot { color: #FF007F; font-weight: bold; text-shadow: 0 0 5px #FF007F; }
    .rsi-cool { color: #39FF14; font-weight: bold; text-shadow: 0 0 5px #39FF14; }
    </style>
    """, unsafe_allow_html=True)

# 3. إدارة الجلسة والأمان
if "last_update" not in st.session_state: st.session_state.last_update = time.time()
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    with st.form("gate"):
        if st.text_input("NEXUS KEY:", type="password") == "neuxs_gold_2024":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 4. شريط التحكم الجانبي
with st.sidebar:
    st.markdown("### 🛠️ إعدادات الصاغة")
    local_21 = st.number_input("سعر عيار 21 (مصر):", value=7020)
    bank_usd = st.number_input("سعر دولار البنك:", value=48.5)
    st.markdown("---")
    if st.button("🔄 تحديث إجباري"):
        st.session_state.last_update = time.time()
        st.rerun()
    st.info("💡 التنبيهات تعمل تلقائياً عند وصول RSI لـ 70 أو 35.")

# 5. محرك البيانات
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
    
    # منطق الـ RSI والتنبيهات
    if rsi_val > 70:
        rsi_html = f"<span class='rsi-hot'>⚠️ {int(rsi_val)} (خطر - بيع)</span>"
        if "alert_high" not in st.session_state:
            send_telegram_msg(f"🚨 NEXUS ALERT: الذهب في منطقة خطر! RSI: {int(rsi_val)}. السعر: ${curr_global}")
            st.session_state.alert_high = True
    elif rsi_val < 35:
        rsi_html = f"<span class='rsi-cool'>✅ {int(rsi_val)} (لقطة - شراء)</span>"
        if "alert_low" not in st.session_state:
            send_telegram_msg(f"💰 NEXUS ALERT: فرصة شراء لقطة! RSI: {int(rsi_val)}. السعر المحلي: {local_21}")
            st.session_state.alert_low = True
    else:
        rsi_html = f"<span style='color: #00E5FF;'>{int(rsi_val)} (منطقة آمنة)</span>"
        st.session_state.pop("alert_high", None)
        st.session_state.pop("alert_low", None)

    # الحسابات
    seconds_ago = int(time.time() - st.session_state.last_update)
    fair_21_usd = (curr_global / 31.1035) * (21/24)
    hedging_usd = local_21 / fair_21_usd
    gap_pct = ((hedging_usd - bank_usd) / bank_usd) * 100
    fair_local_price = fair_21_usd * bank_usd

    st.markdown("<h1>⚡ NEXUS INTELLIGENCE TERMINAL ⚡</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='timer-text'>⏱️ تحديث منذ {seconds_ago} ثانية | {trend_arrow}</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GLOBAL SPOT", f"${curr_global:,.2f}")
    c2.metric("HEDGING USD", f"{hedging_usd:.2f} ج.م")
    c3.metric("ARB GAP", f"{gap_pct:.1f}%")
    c4.metric("CONFIDENCE", f"{int(50 + (abs(50-rsi_val)*0.5))}%")

    st.markdown("---")

    # 6. المربعات التحليلية
    col_a, col_b = st.columns(2)
    
    with col_a:
        if gap_pct < -1:
            short_msg = f"<div style='color:#39FF14; font-size:20px;'>✅ القرار: اشتري فوراً</div><p>السعر المحلي أرخص بـ {abs(gap_pct):.1f}%.<br>مكسبك المتوقع: <b>{fair_local_price - local_21:.0f} جنيه/جرام</b>.</p>"
        elif gap_pct > 10:
            short_msg = "<div style='color:#FF007F; font-size:20px;'>❌ القرار: بيع/انتظر</div><p>فقاعة سعرية في مصر. العالمي أرخص بكتير.</p>"
        else:
            short_msg = "<div style='color:#FFD700; font-size:20px;'>🔄 القرار: تفرج (HOLD)</div><p>السوق متزن جداً حالياً.</p>"
        st.markdown(f"<div class='oracle-box'><h3>📅 المدى القريب</h3>{short_msg}</div>", unsafe_allow_html=True)

    with col_b:
        trend_long = "صاعد 📈" if curr_global > df['EMA_20'].iloc[-1] else "هابط 📉"
        long_msg = f"<div style='color:#00E5FF; font-size:20px;'>الاتجاه العام: {trend_long}</div>"
        long_msg += f"<p>مؤشر القوة: {rsi_html}<br>لو الـ RSI كسر الـ 70، جني أرباحك فوراً.</p>"
        st.markdown(f"<div class='oracle-box'><h3>⏳ المدى البعيد</h3>{long_msg}</div>", unsafe_allow_html=True)

    # 7. الشارت
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    increasing_line_color='#39FF14', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("Nexus is calibrating...")
