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

# 2. إعدادات الصفحة
st.set_page_config(page_title="NEXUS GOLD PRO V8", layout="wide")
st_autorefresh(interval=15000, key="nexus_v8_stable") # تحديث كل 15 ثانية لاستقرار أكتر

# 3. واجهة النيون
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; font-size: 32px !important; }
    h1, h2, h3 { color: #00E5FF !important; text-shadow: 0 0 15px #00E5FF; text-align: center; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; padding: 10px; }
    .oracle-box { border: 2px solid #00E5FF; background: rgba(0, 229, 255, 0.05); padding: 20px; border-radius: 15px; min-height: 180px; text-align: center; }
    .trend-up { color: #39FF14; font-weight: bold; font-size: 18px; }
    .trend-down { color: #FF007F; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# 4. نظام الأمان
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='margin-top:50px;'>🔒 NEXUS SECURITY GATE</h1>", unsafe_allow_html=True)
    with st.form("login_gate"):
        key = st.text_input("NEXUS KEY:", type="password")
        if st.form_submit_button("فتح النظام") and key == "neuxs_gold_2024":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 5. التحكم الجانبي
with st.sidebar:
    st.markdown("### 🛠️ تسعير الصاغة")
    local_21 = st.number_input("سعر عيار 21 (مصر):", value=7425)
    bank_usd = st.number_input("سعر دولار البنك:", value=48.5)
    st.markdown("---")
    st.write("⏱️ التحديث تلقائي كل 15 ثانية")

# 6. محرك سحب البيانات (نسخة ضد الأخطاء)
def get_safe_data():
    try:
        # محاولة أولى: بيانات دقيقة جداً
        df = yf.download("XAUUSD=X", period="1d", interval="1m", progress=False)
        if df.empty or len(df) < 2:
            # محاولة ثانية: بيانات أوسع لو الأولى فشلت
            df = yf.download("GC=F", period="5d", interval="1h", progress=False)
        
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
            
        df['RSI'] = ta.rsi(df['Close'], length=14)
        return df
    except:
        return pd.DataFrame()

try:
    df = get_safe_data()
    if df.empty:
        st.warning("جاري محاولة استعادة الاتصال بالسيرفر العالمي...")
        st.stop()

    curr_global = float(df['Close'].iloc[-1])
    prev_global = float(df['Close'].iloc[-2])
    rsi_val = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50
    
    # حسابات الفجوة
    fair_21_usd = (curr_global / 31.1035) * (21/24)
    hedging_usd = local_21 / fair_21_usd
    gap_pct = ((hedging_usd - bank_usd) / bank_usd) * 100
    fair_local_price = fair_21_usd * bank_usd

    # العرض
    st.markdown("<h1>⚡ NEXUS INTELLIGENCE V8 ⚡</h1>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GLOBAL SPOT", f"${curr_global:,.2f}")
    c2.metric("HEDGING USD", f"{hedging_usd:.2f}")
    c3.metric("ARB GAP", f"{gap_pct:.1f}%")
    c4.metric("RSI Lvl", f"{int(rsi_val)}")

    st.markdown("---")

    # التحليل
    ca, cb = st.columns(2)
    with ca:
        if gap_pct < -0.5:
            msg = f"<div class='trend-up'>✅ شراء فوراً</div><p>السعر في مصر لقطة! المكسب: {fair_local_price - local_21:.0f} ج</p>"
        elif gap_pct > 3:
            msg = "<div class='trend-down'>❌ بيع/انتظار</div><p>السعر في مصر فيه فقاعة حالياً.</p>"
        else:
            msg = "<div style='color:#FFD700;'>🔄 استقرار (HOLD)</div><p>السوق المصري ماشي مع العالمي.</p>"
        st.markdown(f"<div class='oracle-box'><h3>📅 قرار اللحظة</h3>{msg}</div>", unsafe_allow_html=True)

    with cb:
        trend = "صاعد 📈" if curr_global > prev_global else "تصحيح 📉"
        rsi_msg = "خطر (بيع)" if rsi_val > 70 else "فرصة (شراء)" if rsi_val < 35 else "منطقة آمنة"
        st.markdown(f"<div class='oracle-box'><h3>⏳ اتجاه الماركت</h3><p>{trend}</p><p>حالة RSI: {rsi_msg}</p></div>", unsafe_allow_html=True)

    # الشارت
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    increasing_line_color='#39FF14', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("النظام في حالة سكون.. سيتم التحديث خلال ثواني")
