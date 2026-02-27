# --- نظام الأمان المطور ---
PASSWORD = "neuxs_gold_2024"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1>🔐 NEXUS ACCESS CONTROL</h1>", unsafe_allow_html=True)
    
    # استخدام form بيخلي زرار Enter يشتغل تلقائياً
    with st.form("login_form"):
        pwd = st.text_input("ENTER ACCESS KEY:", type="password")
        submit = st.form_submit_button("LOGIN")
        
        if submit:
            if pwd == PASSWORD:
                st.session_state.auth = True
                st.rerun()  # إعادة تحميل الصفحة للدخول
            else:
                st.error("❌ ACCESS DENIED: INVALID KEY")
    st.stop() # يمنع ظهور باقي الصفحة إلا بعد الدخول
