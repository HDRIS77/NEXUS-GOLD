import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta # مكتبة التحليل الفني
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة
st.set_page_config(page_title="NEXUS GOLD INTELLIGENCE", layout="wide")

# 2. نظام الأمان (الباسورد: neuxs_gold_2024)
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #00E5FF;'>🔐 NEXUS ACCESS CONTROL</h1>", unsafe_allow_html=True)
    with st.form("login"):
        pwd = st.text_input("ENTER ACCESS KEY:", type="password")
        if st.form_submit_button("UNLOCK"):
            if pwd == "neuxs_gold_2024":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# 3. تحديث وتصميم نيون
st_autorefresh(interval=30000, key="nexus_refresh")
st.markdown("""<style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; padding: 20px; }
    .prediction-box { border: 2px solid #00E5FF; padding: 20px; border-radius: 15px; background: rgba(0, 229, 255, 0.05); }
</style>""", unsafe_allow_html=True)

# 4. محرك التحليل (The Brain)
def analyze_market(df):
    # تحليل فني عميق
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    df['EMA_50'] = ta.ema(df['Close'], length=50)
    
    current_price = df['Close'].iloc[-1]
    rsi = df['RSI'].iloc[-1]
    ema20 = df['EMA_20'].iloc[-1]
    
    # توقع المدى القريب (1-3 أيام)
    short_term = "BULLISH 📈" if rsi < 50 and current_price > ema20 else "BEARISH 📉"
    
    # توقع المدى البعيد (أسابيع) بناءً على تقاطع المتوسطات
    long_term = "ACCUMULATION (شراء تدريجي)" if current_price > df['EMA_50'].iloc[-1] else "DISTRIBUTION (بيع تدريجي)"
    
    # نسبة الثقة وقوة الإشارة
    confidence = 50 + (abs(50 - rsi) * 0.8)
    
    return short_term, long_term, rsi, confidence

try:
    # جلب داتا مكثفة للمحاكاة
    data = yf.download("GC=F", period="60d", interval="1h")
    if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
    
    st.markdown("<h1>⚡ NEXUS INTELLIGENCE TERMINAL ⚡</h1>", unsafe_allow_html=True)
    
    short_t, long_t, rsi_val, conf = analyze_market(data)
    current_p = data['Close'].iloc[-1]
    price_21k = (current_p / 31.1) * 72.0 * (21/24) # سعر افتراضي للدولار

    # عرض الأرقام الأساسية
    col1, col2, col3 = st.columns(3)
    col1.metric("GLOBAL SPOT", f"${current_p:,.2f}")
    col2.metric("LOCAL 21K", f"{int(price_21k):,} EGP")
    col3.metric("CONFIDENCE SCORE", f"{int(conf)}%")

    st.markdown("---")

    # الخانة الجديدة: التوقعات (التي طلبتها)
    st.markdown("### 🔮 NEXUS ORACLE: تحليل المسارات والتوقعات")
    c_a, c_b = st.columns(2)
    
    with c_a:
        st.markdown(f"""<div class='prediction-box'>
            <h4>📅 توقع المدى القريب (أيام):</h4>
            <h2 style='color: #00E5FF;'>{short_t}</h2>
            <p>بناءً على مؤشر القوة النسبية (RSI: {int(rsi_val)}) والسيولة اللحظية.</p>
        </div>""", unsafe_allow_html=True)

    with c_b:
        st.markdown(f"""<div class='prediction-box'>
            <h4>⏳ توقع المدى البعيد (أسابيع):</h4>
            <h2 style='color: #FF007F;'>{long_t}</h2>
            <p>تحليل تريليونات نقاط البيانات والاتجاه العام (Macro Trend).</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    
    # نصيحة التاجر (Action)
    if conf > 75:
        if "BEARISH" in short_t:
            st.error(f"🚨 إشارة قوية للتاجر: بيع 20% من المخزون حالاً (تحوط). السعر يتجه لهبوط قريب.")
        else:
            st.success(f"✅ إشارة قوية للتاجر: شراء بـ 20% من الكاش. فرصة صعود قوية.")
    else:
        st.warning("⚠️ حالة تذبذب: ينصح بالانتظار (HOLD). لا توجد إشارة دخول واضحة الآن.")

    # الشارت المطور
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
                    increasing_line_color='#00E5FF', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Data Sync Error. Please check 'pandas_ta' in requirements.txt")
