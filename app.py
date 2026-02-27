import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة
st.set_page_config(page_title="NEXUS GOLD TERMINAL PRO", layout="wide")
st_autorefresh(interval=30000, key="nexus_v3_refresh")

# 2. تصميم الواجهة النيون
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; }
    h1, h2, h3 { color: #00E5FF !important; text-shadow: 0 0 15px #00E5FF; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; }
    .oracle-box { border: 2px solid #00E5FF; background: rgba(0, 229, 255, 0.05); padding: 25px; border-radius: 15px; min-height: 250px; line-height: 1.6; }
    .buy-signal { color: #39FF14; font-weight: bold; border-left: 5px solid #39FF14; padding-left: 10px; }
    .sell-signal { color: #FF007F; font-weight: bold; border-left: 5px solid #FF007F; padding-left: 10px; }
    .hold-signal { color: #FFD700; font-weight: bold; border-left: 5px solid #FFD700; padding-left: 10px; }
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
    st.info("💡 نصيحة: لو البرنامج وقف، اتأكد إن السعر العالمي مش مهنج.")

# 5. جلب الداتا
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

    # 6. المربعات التحليلية (NEXUS ORACLE)
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
        st.subheader("📅 المدى القريب (قرارات اليوم)")
        
        if gap_pct < -1:
            st.markdown("<div class='buy-signal'>✅ القرار: اشتري فوراً</div>", unsafe_allow_html=True)
            st.write(f"**السبب:** الذهب في مصر أرخص من العالمي بـ {abs(gap_pct):.1f}%.")
            st.write(f"**التوقع:** السعر في مصر لازم يطلع لـ **{fair_local_price:.0f} ج.م** عشان يلحق العالمي.")
            st.write(f"**نسبة النجاح:** 90% (لو السعر العالمي ثبت).")
        elif gap_pct > 12:
            st.markdown("<div class='sell-signal'>❌ القرار: بيع أو انتظر</div>", unsafe_allow_html=True)
            st.write(f"**السبب:** الذهب في مصر أغلى من قيمته الحقيقية (فقاعة).")
            st.write(f"**التوقع:** السعر ممكن ينزل لـ **{fair_local_price:.0f} ج.م** لو السوق هدي.")
            st.write(f"**نسبة النجاح:** 75%.")
        else:
            st.markdown("<div class='hold-signal'>🔄 القرار: تفرج فقط</div>", unsafe_allow_html=True)
            st.write("**السبب:** السعر المحلي ماشي مع العالمي بالمليم، مفيش فرصة ربح سريعة.")
            st.write("**نصيحة:** لا تدخل الآن، انتظر حدوث فجوة سعرية.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
        st.subheader("⏳ المدى البعيد (نظرة استراتيجية)")
        
        if curr_global > df['EMA_20'].iloc[-1]:
            st.markdown("<div class='buy-signal'>📈 الاتجاه: صعود مستمر</div>", unsafe_allow_html=True)
            target = curr_global * 1.05
            st.write(f"**التحليل:** الذهب عالمياً فوق متوسط الـ 20 ساعة، ده معناه 'تجميع' للشراء.")
            st.write(f"**الهدف القادم:** قد يلامس العالمي مستويات **${target:.0f}**.")
        else:
            st.markdown("<div class='sell-signal'>📉 الاتجاه: تصحيح هابط</div>", unsafe_allow_html=True)
            target = curr_global * 0.95
            st.write(f"**التحليل:** الذهب بيفقد قوته عالمياً، احتمال ينزل لمستويات **${target:.0f}** قبل ما يرتد.")
            
        st.write(f"**مؤشر RSI:** {int(rsi_val)} (لو فوق 70 يبقى خطر، لو تحت 30 يبقى لقطة).")
        st.markdown("</div>", unsafe_allow_html=True)

    # 7. الشارت
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    increasing_line_color='#39FF14', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Nexus Error: {e}")
