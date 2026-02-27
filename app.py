import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
import numpy as np
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة
st.set_page_config(page_title="NEXUS GOLD TERMINAL PRO", layout="wide")
st_autorefresh(interval=30000, key="nexus_final_refresh") # تحديث كل 30 ثانية

# 2. تصميم الواجهة النيون المطور
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; }
    h1, h2, h3 { color: #00E5FF !important; text-shadow: 0 0 15px #00E5FF; text-align: center; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; padding: 15px; }
    .oracle-box { border: 2px solid #00E5FF; background: rgba(0, 229, 255, 0.05); padding: 20px; border-radius: 15px; min-height: 200px; }
    .alarm-red { border: 2px solid #FF007F; background: rgba(255, 0, 127, 0.1); padding: 15px; border-radius: 10px; color: #FF007F; text-align: center; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. نظام الأمان
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1>🔐 NEXUS GATE</h1>", unsafe_allow_html=True)
    with st.form("login"):
        pwd = st.text_input("ACCESS KEY:", type="password")
        if st.form_submit_button("UNLOCK"):
            if pwd == "neuxs_gold_2024":
                st.session_state.auth = True
                st.rerun()
            else: st.error("INVALID KEY")
    st.stop()

# 4. التحكم اليدوي (Sidebar) - الحل الأضمن للسوق المصري
with st.sidebar:
    st.markdown("### ⚙️ إعدادات السوق المحلي")
    # السعر اللي بتسمعه في الصاغة
    local_21 = st.number_input("سعر جرام 21 الحالي (مصر):", value=3700, step=5)
    # سعر دولار البنك الرسمي
    bank_usd = st.number_input("سعر دولار البنك الرسمي:", value=48.5, step=0.1)
    st.markdown("---")
    st.info("تغيير هذه الأرقام يحدث تحليل 'الفقاعة' فوراً.")

# 5. محرك جلب البيانات (مُعدل لحل مشكلة الأرقام الخاطئة)
@st.cache_data(ttl=30)
def fetch_gold_intel():
    # سحب داتا 30 يوم فقط لضمان الدقة وتجنب الخلل في التواريخ البعيدة
    df = yf.download("GC=F", period="1mo", interval="1h")
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # حساب المؤشرات الفنية
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    return df

try:
    data = fetch_gold_intel()
    # السعر العالمي اللحظي الحقيقي
    curr_global = float(data['Close'].iloc[-1])
    rsi_val = float(data['RSI'].iloc[-1])
    atr_val = float(data['ATR'].iloc[-1])

    # --- حسابات "محامي الشيطان" وكشف الحقيقة ---
    # الدولار التحوطي: هو السعر اللي التجار مسعرين بيه الدولار جوه الذهب
    # المعادلة: (سعر 21 * 31.1 / السعر العالمي) / (21/24)
    hedging_usd = (local_21 * 31.1 / curr_global) / (21/24)
    
    # الفجوة (Arbitrage Gap): الفرق بين دولار الذهب ودولار البنك
    gap_pct = ((hedging_usd - bank_usd) / bank_usd) * 100

    st.markdown("<h1>⚡ NEXUS INTELLIGENCE TERMINAL ⚡</h1>", unsafe_allow_html=True)

    # مؤشر التذبذب (Volatility Clock)
    if atr_val > data['ATR'].mean() * 1.5:
        st.markdown("<div class='alarm-red'>🚨 ALERT: HIGH VOLATILITY - تذبذب عالي | خطر في التنفيذ حالياً</div>", unsafe_allow_html=True)

    # الكروت الرئيسية
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GLOBAL SPOT", f"${curr_global:,.2f}")
    c2.metric("HEDGING USD", f"{hedging_usd:.2f} EGP")
    c3.metric("ARB GAP (الفقاعة)", f"{gap_pct:.1f}%")
    
    # نسبة الثقة (تعتمد على الفجوة والمؤشرات العالمية)
    conf = 50 + (abs(50 - rsi_val) * 0.4)
    if gap_pct > 20: conf -= 20 # الثقة بتقل لو الفقاعة كبرت
    c4.metric("CONFIDENCE", f"{int(max(10, conf))}%")

    st.markdown("---")

    # 6. NEXUS ORACLE (التحليل الصريح)
    st.markdown("### 🔮 NEXUS ANALYTICS: تحليل المسارات")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
        st.subheader("📅 المدى القريب (أيام)")
        if gap_pct > 15:
            st.error("📉 SELL SIGNAL: السعر المحلي 'منفوخ' بدولار وهمي. خطر الشراء حالياً عالي جداً.")
        elif gap_pct < 5 and rsi_val < 40:
            st.success("📈 BUY SIGNAL: السعر المحلي عادل والعالمي في منطقة شراء.")
        else:
            st.warning("🔄 HOLD: انتظر تصحيح السعر المحلي أو العالمي.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
        st.subheader("⏳ المدى البعيد (أسابيع)")
        trend = "BULLISH (تجميع)" if curr_global > data['EMA_20'].iloc[-1] else "BEARISH (تصريف)"
        st.write(f"الاتجاه العام: **{trend}**")
        st.write(f"مؤشر RSI العالمي: **{int(rsi_val)}**")
        st.write("**نصيحة محامي الشيطان:** لا تنجرف وراء إشاعات السوق، الأرقام لا تكذب.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 7. الشارت النيون
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
                    increasing_line_color='#00E5FF', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("NEXUS is calibrating... Please check your input values.")
