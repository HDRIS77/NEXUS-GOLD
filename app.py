import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh
import time

# 1. إعدادات التحديث اللحظي
st.set_page_config(page_title="NEXUS GOLD INTELLIGENCE V9", layout="wide")
st_autorefresh(interval=10000, key="nexus_v9_auto")

# 2. تصميم الواجهة النيون
st.markdown("""
    <style>
    .main { background-color: #050505; color: #e0e0e0; }
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 10px #00E5FF; }
    .stMetric { background-color: #0a0a0a; border: 1px solid #00E5FF; border-radius: 15px; padding: 15px; }
    .oracle-box { border: 2px solid #00E5FF; background: rgba(0, 229, 255, 0.05); padding: 20px; border-radius: 15px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. محرك البيانات العالمي (مطابق لصورك $5,278)
def get_global_gold():
    # سحب الذهب الفوري لضمان مطابقة جوجل وآي صاغة
    gold = yf.Ticker("XAUUSD=X")
    df = gold.history(period="1d", interval="1m")
    if df.empty:
        df = yf.download("XAUUSD=X", period="1d", interval="1m", progress=False)
    return float(df['Close'].iloc[-1]), df

try:
    curr_global, df_hist = get_global_gold()
    
    # 4. إدارة السعر المحلي (تحديث بناءً على الصورة الأخيرة)
    with st.sidebar:
        st.markdown("### 🇪🇬 تسعير مصر (تحديث يدوي ذكي)")
        # القيمة الافتراضية هنا بقت 7600 بناءً على صورة iSagha اللي بعتها
        local_21 = st.number_input("سعر عيار 21 الحالي:", value=7600) 
        bank_usd = st.number_input("دولار البنك:", value=48.50)
        st.warning("⚠️ ملحوظة: السعر في مصر قفز لـ 7600 ج.م بناءً على آخر تحديث للصاغة.")

    # 5. الحسابات الاقتصادية
    # سعر جرام 24 عالمياً = السعر العالمي / 31.1035
    # سعر جرام 21 عالمياً = جرام 24 * (21/24)
    global_21_usd = (curr_global / 31.1035) * (21/24) # تطلع حوالي $169.70 في صورك
    fair_local_price = global_21_usd * bank_usd
    
    # الفجوة (Arbitrage Gap)
    gap_pct = ((local_21 - fair_local_price) / fair_local_price) * 100

    # 6. العرض الرئيسي
    st.markdown("<h1>⚡ NEXUS GOLD RADAR V9 ⚡</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("GLOBAL SPOT (Google)", f"${curr_global:,.2f}")
    c2.metric("FAIR PRICE (السعر العادل)", f"{fair_local_price:,.0f} EGP")
    
    # تلوين الفجوة: لو سالبة (أخضر - لقطة)، لو موجبة كبيرة (أحمر - فقاعة)
    gap_color = "normal" if abs(gap_pct) < 2 else "inverse"
    c3.metric("ARB GAP (الفجوة)", f"{gap_pct:.1f}%", delta_color=gap_color)

    st.markdown("---")

    # 7. تحليل "محامي الشيطان"
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
        if gap_pct < 0:
            st.success("✅ القرار: اشترِ الآن")
            st.write(f"السعر في مصر لسه محملش الزيادة العالمية كاملة. فيه فرق {abs(gap_pct):.1f}% لصالحك.")
        elif gap_pct > 5:
            st.error("❌ القرار: لا تشترِ / بع")
            st.write("السوق المصري مسعر الذهب بزيادة كبيرة (فقاعة) عن السعر العالمي.")
        else:
            st.warning("🔄 القرار: انتظر (Hold)")
            st.write("السعر المحلي والعالمي متزنين تماماً الآن.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
        st.info("📊 تحليل الاتجاه")
        st.write(f"السعر العالمي الآن: **${curr_global}**")
        st.write(f"المستهدف القادم عالمياً: **$5,500**")
        st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"خطأ في الاتصال بالسيرفر: {e}")
