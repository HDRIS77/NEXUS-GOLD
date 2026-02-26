import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- إعدادات الأمان والصفحة ---
st.set_page_config(page_title="NEUXS Gold Terminal", layout="wide")

PASSWORD = "neuxs_gold_2024" 

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        password_input = st.sidebar.text_input("ادخل كلمة السر للدخول:", type="password")
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun() # تحديث الصفحة بعد إدخال الباسورد
        else:
            if password_input: st.error("كلمة السر خطأ")
            st.warning("يرجى إدخال كلمة السر الصحيحة للوصول للنظام.")
            return False
    return True

if check_password():
    st.title("🏆 نظام تداول الذهب الذكي :NEUXS")
    st.sidebar.header("لوحة التحكم")

    @st.cache_data(ttl=300) 
    def load_data():
        gold = yf.download("GC=F", period="5d", interval="15m")
        usd = yf.download("DX-Y.NYB", period="5d", interval="15m")
        return gold, usd

    try:
        gold_df, usd_df = load_data()
        
        if isinstance(gold_df.columns, pd.MultiIndex):
            gold_df.columns = gold_df.columns.get_level_values(0)
        if isinstance(usd_df.columns, pd.MultiIndex):
            usd_df.columns = usd_df.columns.get_level_values(0)
            
        gold_df = gold_df.reset_index()

        # حساب المؤشرات
        delta = gold_df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        gold_df['RSI'] = 100 - (100 / (1 + rs))
        gold_df['EMA20'] = gold_df['Close'].ewm(span=20, adjust=False).mean()

        # استخراج القيم كأرقام بسيطة (التعديل هنا لحل المشكلة)
        current_price = float(gold_df['Close'].iloc[-1])
        last_rsi = float(gold_df['RSI'].iloc[-1])
        current_usd = float(usd_df['Close'].iloc[-1])
        prev_price = float(gold_df['Close'].iloc[-2])
        change = current_price - prev_price

        # --- عرض المؤشرات العلوية ---
        m1, m2, m3 = st.columns(3)
        m1.metric("سعر أوقية الذهب", f"${current_price:,.2f}", f"{change:.2f}")
        m2.metric("مؤشر القوة RSI", f"{last_rsi:.2f}")
        m3.metric("اتجاه الدولار", f"{current_usd:.2f}")

        st.markdown("---")

        # --- التوصية ---
        st.subheader("📢 توصية نيكسس الحالية:")
        if last_rsi > 70:
            st.error("🔴 إشارة: بيع (SELL) - تشبع شراء")
        elif last_rsi < 30:
            st.success("🟢 إشارة: شراء (BUY) - تشبع بيع")
        else:
            st.warning("🟡 إشارة: انتظار (HOLD) - منطقة محايدة")

        # --- الرسم البياني ---
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=gold_df['Datetime' if 'Datetime' in gold_df.columns else 'Date'],
                                     open=gold_df['Open'], high=gold_df['High'],
                                     low=gold_df['Low'], close=gold_df['Close'], name="السعر"))
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"حدث خطأ في عرض البيانات: {e}")
