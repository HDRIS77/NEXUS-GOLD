# استيراد العقل الجديد
from brain_engine import calculate_nexus_strategy

# تعديل الـ CSS للأزرق النيون
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] { color: #00E5FF; text-shadow: 0 0 15px #00E5FF; }
    .stMetric { border: 1px solid #00E5FF; box-shadow: 0 0 20px rgba(0, 229, 255, 0.2); }
    h1, h2, h3 { color: #00E5FF !important; text-shadow: 0 0 15px #00E5FF; }
    </style>
    """, unsafe_allow_html=True)

# داخل الجزء الخاص بالبيانات بعد حساب الأسعار:
decision = calculate_nexus_strategy(gold_df)

# إضافة قسم التوقعات (The Oracle)
st.markdown("## 🧠 NEXUS ORACLE (AI PROJECTIONS)")
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("Short-Term (7D)")
    st.write(f"Trend: **{decision['trend']}**")
with c2:
    st.subheader("Confidence Score")
    st.progress(decision['confidence'] / 100)
    st.write(f"{decision['confidence']}%")
with c3:
    st.subheader("Recommended Action")
    action = "HOLD"
    if decision['confidence'] > 80 and decision['trend'] == "BEARISH": action = "SELL 20%"
    elif decision['confidence'] > 80 and decision['trend'] == "BULLISH": action = "BUY 20%"
    st.warning(f"⚠️ {action}")
