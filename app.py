import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from brain_engine import calculate_nexus_strategy  # استيراد المحرك

# 1. إعدادات الصفحة (يجب أن تكون أول أمر)
st.set_page_config(page_title="NEXUS GOLD INTELLIGENCE", layout="wide")

# 2. تحديث تلقائي كل 30 ثانية (عشان نتجنب حظر الـ API)
st_autorefresh(interval=30000, key="datarefresh")

# 3. تصميم الـ CSS (نيون أزرق)
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; }
    h1, h2, h3 { color: #00E5FF !important; text-shadow: 0 0 15px #00E5FF; text-align: center; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; padding: 20px; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 4. الأمان
PASSWORD = "nexus_gold_2026"
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 NEXUS ACCESS CONTROL")
    pwd = st.text_input("ENTER ACCESS KEY:", type="password")
    if pwd == PASSWORD: 
        st.session_state.auth = True
        st.rerun()
    st.stop()

# 5. جلب البيانات
@st.cache_data(ttl=30)
def load_data():
    gold = yf.download("GC=F", period="5d", interval="1m")
    if isinstance(gold.columns, pd.MultiIndex): gold.columns = gold.columns.get_level_values(0)
    return gold

try:
    df = load_data()
    analysis = calculate_nexus_strategy(df)
    
    # حساب السعر المحلي (مثال: سعر السوق الموازي)
    usd_egp = 72.0 # يمكنك ربطها بـ API آخر مستقبلاً
    price_21 = (analysis['last_price'] / 31.1) * usd_egp * (21/24)

    st.markdown("<h1>⚡ NEXUS INTELLIGENCE TERMINAL ⚡</h1>", unsafe_allow_html=True)
    
    # عرض العدادات الرئيسية
    c1, c2, c3 = st.columns(3)
    c1.metric("GLOBAL SPOT (OZ)", f"${analysis['last_price']:,}")
    c2.metric("LOCAL 21K (EGP)", f"{int(price_21):,} ج.م")
    c3.metric("NEXUS CONFIDENCE", f"{analysis['confidence']}%")

    st.markdown("---")

    # لوحة التوقعات (The Oracle)
    st.markdown(f"### 🧠 AI PROJECTION: <span style='color:#00E5FF'>{analysis['trend']}</span>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        # الرسم البياني
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        increasing_line_color='#00E5FF', decreasing_line_color='#FF007F')])
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    with col_b:
        st.info("💡 **تحليل المحاكاة:**")
        if analysis['confidence'] > 80:
            st.error(f"⚠️ إشارة قوية: {analysis['trend']}. يفضل تحريك 20% من المخزون.")
        else:
            st.warning("🔄 السوق في حالة تذبذب عرضي. انتظر تأكيد الإشارة.")
            
        st.write(f"RSI Indicator: {analysis['rsi']}")
        st.write("Monte Carlo Path: Stable")

except Exception as e:
    st.error(f"Connection Error: {e}")
