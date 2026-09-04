import streamlit as st
from streamlit_option_menu import option_menu

# إعدادات الصفحة
st.set_page_config(page_title="نظام إدارة المقاولات", layout="wide", initial_sidebar_state="collapsed")

# إخفاء القوائم العلوية الافتراضية
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container { padding-bottom: 70px; }
    </style>
""", unsafe_allow_html=True)

# إدارة حالة التطبيق (Session State) للتسلسل الإجباري
if 'selected_specialty' not in st.session_state:
    st.session_state.selected_specialty = None
if 'selected_artisan' not in st.session_state:
    st.session_state.selected_artisan = None

# شريط التنقل السفلي الاحترافي (بديل القائمة العلوية البشعة)
selected = option_menu(
    menu_title=None,
    options=["1. الرئيسية", "2. اختيار المقاول", "3. إنشاء Devis"],
    icons=["house-door", "person-check", "receipt"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#f8f9fa", "border-radius": "8px"},
        "icon": {"color": "#007bff", "font-size": "18px"},
        "nav-link": {"font-size": "15px", "text-align": "center", "margin": "0px", "font-weight": "bold"},
        "nav-link-selected": {"background-color": "#007bff", "color": "white"},
    }
)

st.markdown("---")

# ---------------------------------------------------------
# المحطة الأولى: الصفحة الرئيسية
# ---------------------------------------------------------
if selected == "1. الرئيسية":
    st.title("🏠 النظام الذكي لإدارة المقاولات")
    st.write("مرحباً بك. يضمن هذا النظام تسلسلاً عملياً وصارماً لإدارة مشاريعك وعروض الأسعار.")
    st.info("👈 اضغط على '2. اختيار المقاول' في الشريط بالأعلى لبدء العملية.")

# ---------------------------------------------------------
# المحطة الثانية: اختيار التخصص ثم المقاول (إجباري)
# ---------------------------------------------------------
elif selected == "2. اختيار المقاول":
    st.title("👷‍♂️ تحديد التخصص والمقاول")
    
    # 1. اختيار نوع العمل الأساسي
    specialties = ["الكهرباء (Électricité)", "الترصيص (Plomberie)", "البناء (Bâtiment)", "الطلاء (Peinture)"]
    chosen_specialty = st.selectbox("الخطوة 1: اختر نوع العمل:", specialties)
    
    # قاعدة بيانات المقاولين حسب التخصص
    artisans_db = {
        "الكهرباء (Électricité)": ["أحمد - كهربائي معتمد", "خالد - صيانة كهرباء"],
        "الترصيص (Plomberie)": ["عمر - مرصص", "سعيد - شبكات مياه"],
        "البناء (Bâtiment)": ["علي - مقاول بناء", "مؤسسة النجاح للبناء"],
        "الطلاء (Peinture)": ["يوسف - دهان ديكور", "كريم - طلاء واجهات"]
    }
    
    if chosen_specialty:
        available_artisans = artisans_db.get(chosen_specialty, [])
        chosen_artisan = st.selectbox("الخطوة 2: اختر المقاول التابع للتخصص:", available_artisans)
        
        if st.button("✅ تثبيت الاختيار والانتقال للـ Devis", use_container_width=True):
            st.session_state.selected_specialty = chosen_specialty
            st.session_state.selected_artisan = chosen_artisan
            st.success(f"تم بنجاح! تم ربط العمل بالمقاول: {chosen_artisan}. يمكنك الآن الانتقال إلى '3. إنشاء Devis'.")

# ---------------------------------------------------------
# المحطة الثالثة: إصدار Devis (محمية بشرط الاختيار)
# ---------------------------------------------------------
elif selected == "3. إنشاء Devis":
    st.title("📝 إصدار عرض سعر (Devis)")
    
    # قفل الحماية: التحقق مما إذا تم اختيار المقاول مسبقاً
    if st.session_state.selected_artisan is None:
        st.error("⛔ عذراً، لا يمكنك الوصول إلى هذه الصفحة مباشرة!")
        st.warning("⚠️ يجب عليك العودة إلى محطة **'2. اختيار المقاول'** وتحديد التخصص والمقاول أولاً لفتح هذه الصفحة.")
    else:
        st.success(f"العمل جارٍ لصالح المقاول: **{st.session_state.selected_artisan}** (التخصص: {st.session_state.selected_specialty})")
        
        with st.form("devis_generation_form"):
            col_1, col_2 = st.columns(2)
            with col_1:
                client_name = st.text_input("اسم الزبون:")
                client_phone = st.text_input("رقم هاتف الزبون:")
            with col_2:
                total_amount = st.number_input("المبلغ الإجمالي المقترح (دج):", min_value=0.0, format="%.2f")
                status = st.selectbox("حالة الـ Devis:", ["مسودة", "تم الإرسال للزبون", "مقبول", "مرفوض"])
                
            work_details = st.text_area("تفاصيل وبنود العمل المطلوب إنجازها:")
            
            submitted = st.form_submit_button("💾 حفظ وإصدار الـ Devis", use_container_width=True)
            
            if submitted:
                if not client_name:
                    st.error("الرجاء إدخال اسم الزبون على الأقل.")
                else:
                    st.success("🎉 تم حفظ وتوثيق الـ Devis بنجاح في النظام!")