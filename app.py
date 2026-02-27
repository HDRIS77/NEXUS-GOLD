import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة (يجب أن يكون أول أمر)
st.set_page_config(page_title="NEXUS GOLD INTELLIGENCE", layout="wide")

# 2. التحديث التلقائي (تحديث كامل للنظام كل 30 ثانية لضمان دقة البيانات)
st_autorefresh(interval=30000, key="nexus_global_refresh")

# 3. تصميم الواجهة (نيون أزرق احترافي)
st.markdown("""
    <style>
    .main { background-color: #050505; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; }
    h1, h2, h3 { color: #00E5FF !important; text-shadow: 0 0 15px #00E5FF; text-align: center; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; padding: 20px; border-radius: 15px; }
    .prediction-box { border: 2px solid #00E5FF; padding: 20px; border-radius: 15px; background: rgba(0, 229, 255, 0.05); margin-bottom: 20px; }
    .price-card { border: 1px solid #333; padding: 15px; border-radius: 10px; text-align: center; background: #0e0e0e; }
    </style>
    """, unsafe_allow_html=True)

# 4. نظام الأمان (الباسورد: neuxs_gold_2024)
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1>🔐 NEXUS ACCESS CONTROL</h1>", unsafe_allow_html=True)
    with st.form("login_gate"):
        pwd = st.text_input("ENTER ACCESS KEY:", type="password")
        if st.form_submit_button("UNLOCK TERMINAL"):
            if pwd == "neuxs_gold_2024":
                st.session_state.auth = True
                st.rerun()
            else: st.error("❌ INVALID KEY")
    st.stop()

# 5. محرك جلب البيانات والتحليل
@st.cache_data(ttl=30)
def get_nexus_data():
    # جلب بيانات 60 يوم لضمان دقة التحليل بعيد المدى
    df = yf.download("GC=F", period="60d", interval="1h")
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # حساب المؤشرات الفنية (المخ التحليلي)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    df['EMA_50'] = ta.ema(df['Close'], length=50)
    return df

try:
    data = get_nexus_data()
    current_p = float(data['Close'].iloc[-1])
    rsi_val = float(data['RSI'].iloc[-1])
    
    # --- حسابات التسعير المصري (NEXUS Pricing Engine) ---
    usd_rate = 72.0  # سعر دولار الصاغة
    price_24k = (current_p / 31.1) * usd_rate
    
    # مصفوفة الأعيرة (شراء وبيع بفرق 1% للتحوط)
    prices = {
        "24K": {"buy": price_24k, "sell": price_24k * 0.99},
        "21K": {"buy": price_24k * (21/24), "sell": (price_24k * 0.99) * (21/24)},
        "18K": {"buy": price_24k * (18/24), "sell": (price_24k * 0.99) * (18/24)}
    }

    # --- الواجهة الرئيسية ---
    st.markdown("<h1>⚡ NEXUS INTELLIGENCE TERMINAL ⚡</h1>", unsafe_allow_html=True)
    
    # ملخص سريع
    c1, c2, c3 = st.columns(3)
    c1.metric("GLOBAL SPOT", f"${current_p:,.2f}")
    c2.metric("LOCAL 21K (BUY)", f"{int(prices['21K']['buy']):,} EGP")
    
    # حساب قوة الإشارة (Confidence)
    conf = 50 + (abs(50 - rsi_val) * 0.9)
    c3.metric("CONFIDENCE SCORE", f"{int(conf)}%")

    st.markdown("---")

    # 6. خانة التوقعات (The Oracle) - تحديث أوتوماتيك
    st.markdown("### 🔮 NEXUS ORACLE: تحليل المسارات")
    t_short = "BULLISH 📈" if rsi_val < 50 else "BEARISH 📉"
    t_long = "ACCUMULATION (تجميع)" if current_p > data['EMA_50'].iloc[-1] else "DISTRIBUTION (تصريف)"
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"<div class='prediction-box'><h4>📅 المدى القريب (أيام)</h4><h2 style='color:#00E5FF'>{t_short}</h2></div>", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"<div class='prediction-box'><h4>⏳ المدى البعيد (أسابيع)</h4><h2 style='color:#FF007F'>{t_long}</h2></div>", unsafe_allow_html=True)

    # 7. جدول أسعار البيع والشراء في مصر
    st.markdown("### 🇪🇬 تسعير الصاغة المصرية (شراء وبيع)")
    gc1, gc2, gc3 = st.columns(3)
    
    for col, (grade, val) in zip([gc1, gc2, gc3], prices.items()):
        with col:
            st.markdown(f"""
                <div class='price-card'>
                    <h3 style='margin:0;'>عيار {grade}</h3>
                    <p style='color:#00E5FF; font-size:1.2rem; margin:5px;'>شراء المحل: <b>{int(val['buy']):,}</b></p>
                    <p style='color:#FF007F; font-size:1.2rem; margin:5px;'>بيع للمحل: <b>{int(val['sell']):,}</b></p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # 8. نصيحة التحوط الذكية
    if conf > 80:
        if "BEARISH" in t_short:
            st.error(f"🚨 تنبيه NEXUS: إشارة هبوط قوية. يُنصح التاجر ببيع 20% من المخزون حالاً للتحوط.")
        else:
            st.success(f"✅ تنبيه NEXUS: إشارة صعود قوية. يُنصح التاجر باستخدام الكاش لشراء 20% ذهب زيادة.")
    else:
        st.warning("⚠️ حالة تذبذب عرضي: يُنصح بالانتظار (HOLD) وعدم اتخاذ قرارات كبيرة الآن.")

    # 9. الرسم البياني
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
                    increasing_line_color='#00E5FF', decreasing_line_color='#FF007F')])
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("Nexus is synchronizing data... Please wait a few seconds.")
