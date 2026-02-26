import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- إعدادات الأمان والصفحة ---
st.set_page_config(page_title="NEUXS Gold Terminal", layout="wide")

# كلمة سر بسيطة لحماية موقعك
PASSWORD = "neuxs_gold_2024" 

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        password_input = st.sidebar.text_input("ادخل كلمة السر للدخول:", type="password")
        if password_input == PASSWORD:
            st.session_state.authenticated = True
        else:
            st.warning("يرجى إدخال كلمة السر الصحيحة للوصول للنظام.")
            return False
    return True

if check_password():
    st.title("🏆 NEUXS: نظام تداول الذهب الذكي")
    st.sidebar.header("لوحة التحكم")

    # --- سحب البيانات من البورصة العالمية ---
    @st.cache_data(ttl=300) # تحديث كل 5 دقائق
    def load_data():
        # GC=F هو سعر أوقية الذهب العالمي
        gold = yf.download("GC=F", period="5d", interval="15m")
        # DX-Y.NYB هو مؤشر الدولار
        usd = yf.download("DX-Y.NYB", period="5d", interval="15m")
        return gold, usd

    try:
        gold_df, usd_df = load_data()
        
        # تنظيف الداتا
        if isinstance(gold_df.columns, pd.MultiIndex):
            gold_df.columns = gold_df.columns.get_level_values(0)
        gold_df = gold_df.reset_index()

        # --- حساب المؤشرات الفنية (عقل الماكينة) ---
        # 1. حساب RSI
        delta = gold_df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        gold_df['RSI'] = 100 - (100 / (1 + rs))
        
        # 2. المتوسط المتحرك 20 (EMA)
        gold_df['EMA20'] = gold_df['Close'].ewm(span=20, adjust=False).mean()

        # القيم الحالية
        current_price = float(gold_df['Close'].iloc[-1])
        last_rsi = float(gold_df['RSI'].iloc[-1])
        last_ema = float(gold_df['EMA20'].iloc[-1])
        prev_price = float(gold_df['Close'].iloc[-2])

        # --- عرض المؤشرات العلوية ---
        m1, m2, m3 = st.columns(3)
        m1.metric("سعر أوقية الذهب", f"${current_price:,.2f}", f"{current_price - prev_price:.2f}")
        m2.metric("مؤشر القوة RSI", f"{last_rsi:.2f}")
        m3.metric("اتجاه الدولار", f"{usd_df.iloc[-1]['Close']:.2f}")

        st.markdown("---")

        # --- منطق الإشارة (The Signal Logic) ---
        st.subheader("📢 توصية نيكسس الحالية:")
        
        col_signal, col_advice = st.columns([1, 2])

        if last_rsi > 70:
            col_signal.error("🔴 إشارة: بيع (SELL)")
            col_advice.info("الذهب في منطقة 'تشبع شراء'. يفضل تسييل 20% من المخزون قبل الهبوط المتوقع.")
        elif last_rsi < 30:
            col_signal.success("🟢 إشارة: شراء (BUY)")
            col_advice.info("الذهب في منطقة 'تشبع بيع'. فرصة ممتازة لإعادة الشراء بالكاش المتوفر.")
        else:
            col_signal.warning("🟡 إشارة: انتظار (HOLD)")
            col_advice.write("السعر في منطقة محايدة. لا تقم بأي حركة بيع أو شراء حالياً.")

        # --- الرسم البياني ---
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=gold_df['Date'], open=gold_df['Open'], 
                                     high=gold_df['High'], low=gold_df['Low'], 
                                     close=gold_df['Close'], name="سعر الذهب"))
        fig.add_trace(go.Scatter(x=gold_df['Date'], y=gold_df['EMA20'], name="متوسط EMA20", line=dict(color='orange')))
        fig.update_layout(template="plotly_dark", height=500)
        st.plotly_chart(fig, use_container_width=True)

        st.caption("ملاحظة: البيانات تتحدث تلقائياً كل 5 دقائق من البورصة العالمية.")

    except Exception as e:
        st.error(f"حدث خطأ في جلب البيانات: {e}")
