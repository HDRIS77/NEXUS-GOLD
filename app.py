import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة
st.set_page_config(page_title="NEXUS GOLD TERMINAL PRO", layout="wide")
st_autorefresh(interval=30000, key="nexus_v4_refresh")

# 2. تصميم الواجهة النيون (المربعات المحدثة)
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; }
    h1, h2, h3 { color: #00E5FF !important; text-shadow: 0 0 15px #00E5FF; text-align: center; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; }
    .oracle-box { 
        border: 2px solid #00E5FF; 
        background: rgba(0, 229, 255, 0.05); 
        padding: 20px; 
        border-radius: 15px; 
        min-height: 280px; 
        color: white;
        margin-bottom: 10px;
    }
    .buy-signal { color: #39FF14; font-size: 24px; font-weight: bold; margin-bottom: 10px; }
    .sell-signal { color: #FF007F; font-size: 24px; font-weight: bold; margin-bottom: 10px; }
    .hold-signal { color: #FFD700; font-size: 24px; font-weight: bold; margin-bottom: 10px; }
    p { font-size: 16px; line-height: 1.4; }
    </style>
    """, unsafe_allow_html=True)

# 3. نظام الأمان
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    with st.form("gate"):
        if st.text_input("NEXUS KEY:", type="password") == "neuxs_gold_2024":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 4. التحكم في البيانات
with st.sidebar:
    st.markdown("### 🛠️ إعدادات الصاغة")
    local_21 = st.number_input("سعر عيار 21 (مصر):", value=7020)
    bank_usd = st.number_input("سعر دولار البنك:", value=48.5)
    st.info("💡 التحديث تلقائي كل 30 ثانية.")

# 5. جلب الداتا العالمية
@st.cache_data(ttl=30)
def get_intel():
    df = yf.download("GC=F", period="1mo", interval="1h")
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    return df

try:
    df = get_intel()
    curr_global = float(df['Close'].iloc[-1])
    rsi_val = float(df['RSI'].iloc[-1])
    
    # الحسابات
    fair_21_usd = (curr_global / 31.1035) * (21/24)
    hedging_usd = local_21 / fair_21_usd
    gap_pct = ((hedging_usd - bank_usd) / bank_usd) * 100
    fair_local_price = fair_21_usd * bank_usd

    st.markdown("<h1>⚡ NEXUS INTELLIGENCE TERMINAL ⚡</h1>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GLOBAL SPOT", f"${curr_global:,.2f}")
    c2.metric("HEDGING USD", f"{hedging_usd:.2f} ج.م")
    c3.metric("ARB GAP", f"{gap_pct:.1f}%")
    c4.metric("CONFIDENCE", f"{int(50 + (abs(50-rsi_val)*0.5))}%")

    st.markdown("---")

    # 6. المربعات التحليلية (NEXUS ORACLE) - تم حقن النصوص بالداخل
    col_a, col_b = st.columns(2)
    
    # تحضير رسالة المدى القريب
    if gap_pct < -1:
        short_html = f"<div class='buy-signal'>✅ القرار: اشتري فوراً</div><p><b>السبب:</b> الذهب في مصر لقطة، أرخص من العالمي بـ {abs(gap_pct):.1f}%.<br><b>التوقع:</b> السعر في مصر لازم يشد لـ <b>{fair_local_price:.0f} ج.م</b>.<br><b>نسبة النجاح:</b> 90%</p>"
    elif gap_pct > 12:
        short_html = f"<div class='sell-signal'>❌ القرار: بيع أو انتظر</div><p><b>السبب:</b> فيه فقاعة وسعر عالي وهمي في مصر حالياً.<br><b>التوقع:</b> السعر ممكن يريح لـ <b>{fair_local_price:.0f} ج.م</b>.<br><b>نسبة النجاح:</b> 75%</p>"
    else:
        short_html = "<div class='hold-signal'>🔄 القرار: تفرج (HOLD)</div><p>السعر المحلي والعالمي ماشيين مع بعض بالمليم. مفيش فرصة لربح سريع، استنى فجوة سعرية تظهر.</p>"

    # تحضير رسالة المدى البعيد
    if curr_global > df['EMA_20'].iloc[-1]:
        long_html = f"<div class='buy-signal'>📈 الاتجاه: صعود مستمر</div><p>الذهب عالمياً قوي ومجمع للشراء.<br><b>الهدف:</b> قد نرى مستويات <b>${curr_global * 1.05:.0f}</b> قريباً.</p>"
    else:
        long_html = f"<div class='sell-signal'>📉 الاتجاه: تصحيح هابط</div><p>الذهب بيفقد قوته حالياً، احتمال ينزل لمستويات <b>${curr_global * 0.95:.0f}</b> قبل ما يرتد.</p>"
    long_html += f"<p><b>مؤشر RSI:</b> {int(rsi_val)} (فوق 70 خطر | تحت 30 لقطة)</p>"

    with col_a:
        st.markdown(f"<div class='oracle-box'><h3>📅 المدى القريب</h3>{short_html}</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown(f"<div class='oracle-box'><h3>⏳ المدى البعيد</h3>{long_html}</div>", unsafe_allow_html=True)

    # 7. الشارت
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    increasing_line_color='#39FF14', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Nexus Error: {e}")
