import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="NEXUS GOLD TERMINAL", layout="wide")
st_autorefresh(interval=60000, key="nexus_refresh") # تحديث كل دقيقة لضمان الاستقرار

# 2. تصميم الواجهة نيون (ثابت ومستقر)
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; }
    h1, h2, h3 { color: #00E5FF !important; text-shadow: 0 0 15px #00E5FF; text-align: center; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; padding: 15px; }
    .oracle-box { border: 2px solid #00E5FF; background: rgba(0, 229, 255, 0.05); padding: 20px; border-radius: 15px; min-height: 150px; margin-top: 10px;}
    .status-box { background-color: #1a1a1a; padding: 10px; border-radius: 10px; border-left: 5px solid #00E5FF; }
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

# 4. شريط التحكم الجانبي (Side Panel)
with st.sidebar:
    st.markdown("### ⚙️ إعدادات الصاغة")
    local_21_price = st.number_input("سعر جرام 21 الآن (مصر):", value=3600, step=5)
    official_usd = st.number_input("سعر دولار البنك:", value=48.50, step=0.1)
    st.markdown("---")
    st.write("💡 نصيحة محامي الشيطان: ادخل الأسعار الحقيقية لتكشف الفقاعة.")

# 5. محرك جلب البيانات (تعديل الرمز لضمان الدقة)
@st.cache_data(ttl=60)
def get_clean_data():
    # استخدام GC=F (عقود الذهب) مع التأكد من جلب السعر اللحظي
    ticker = yf.Ticker("GC=F")
    df = ticker.history(period="1mo", interval="1h")
    # إذا فشل، نحاول الرمز البديل لضمان عدم توقف التطبيق
    if df.empty:
        df = yf.download("GC=F", period="1mo", interval="1h")
    
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # حساب المؤشرات
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    return df

try:
    data = get_clean_data()
    # جلب آخر سعر إغلاق صحيح (العالمي)
    global_spot = float(data['Close'].iloc[-1])
    rsi_val = float(data['RSI'].iloc[-1])
    
    # --- الحسابات المنطقية (The Devil's Math) ---
    # السعر العالمي للأونصة تحوله لسعر جرام 24 (قسمة 31.1)
    # ثم تحوله لعيار 21 (ضرب 21/24)
    # ثم تحسب الدولار التحوطي
    hedging_usd = (local_21_price / (global_spot / 31.1 * (21/24)))
    gap_pct = ((hedging_usd - official_usd) / official_usd) * 100

    # 6. الواجهة الرئيسية
    st.markdown("<h1>⚡ NEXUS INTELLIGENCE TERMINAL ⚡</h1>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GLOBAL SPOT", f"${global_spot:,.2f}")
    c2.metric("HEDGING USD", f"{hedging_usd:.2f} EGP")
    c3.metric("ARB GAP (فقاعة)", f"{gap_pct:.1f}%")
    c4.metric("CONFIDENCE", f"{int(50 + (abs(50-rsi_val)*0.5))}%")

    st.markdown("---")

    # 7. التوقعات (Oracle)
    st.markdown("### 🔮 NEXUS ANALYTICS: تحليل المسارات")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
        st.subheader("📅 المدى القريب")
        if gap_pct > 10:
            st.error("📉 SELL / WAIT: فجوة سعرية عالية. السوق المحلي 'منفوخ' ومخاطرة الشراء مرتفعة.")
        elif gap_pct < 2:
            st.success("📈 BUY: السعر المحلي عادل جداً مقارنة بالعالمي.")
        else:
            st.warning("🔄 HOLD: السوق مستقر، لا تندفع في قراراتك.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
        st.subheader("⏳ المدى البعيد")
        trend = "BULLISH (تجميع)" if global_spot > data['EMA_20'].iloc[-1] else "BEARISH (تصريف)"
        st.write(f"الاتجاه الاستراتيجي: **{trend}**")
        st.write(f"مؤشر القوة (RSI): **{int(rsi_val)}**")
        st.markdown("</div>", unsafe_allow_html=True)

    # 8. الشارت
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
                    increasing_line_color='#00E5FF', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"حدث خطأ في جلب البيانات: {e}")
    st.info("حاول تحديث الصفحة أو التأكد من اتصال الإنترنت.")
