import streamlit as st
import pandas as pd
from streamlit_mic_recorder import mic_recorder
import google.generativeai as genai

# --- 1. SETTINGS & AI SETUP ---
st.set_page_config(page_title="AgriBridge AI", page_icon="🌾", layout="wide")

# PASTE YOUR GEMINI API KEY HERE
genai.configure(api_key="AIzaSyAnt3znjrUfPKVS3eIU9G4CSQdYlYqFZBE")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. DATABASE (Memory) ---
if 'labor_posts' not in st.session_state: st.session_state.labor_posts = []
if 'farmer_jobs' not in st.session_state: st.session_state.farmer_jobs = []
if 'market_items' not in st.session_state: st.session_state.market_items = []
if 'equip_items' not in st.session_state: st.session_state.equip_items = []

# --- 3. TRANSLATIONS ---
LANG_DATA = {
    "English": {
        "home": "Home", "farmer_tab": "Hire Labor", "labor_tab": "Find Work", "market_tab": "Marketplace", "rent_tab": "Rent Equipment",
        "name": "Owner Name", "loc": "Village/Location", "phone": "Phone", "crop": "Crop/Skill", "price": "Price", "qty": "Quantity",
        "submit": "Post Details", "call": "Call Now", "remove": "Remove", "near_me": "Search Village (Near Me)",
        "equip_name": "Equipment Name", "rent_price": "Rent/Day", "days": "Days Needed", "deadline": "Last Date",
        "live_price": "Today's Live Market Prices (per Quintal)"
    },
    "Telugu (తెలుగు)": {
        "home": "హోమ్", "farmer_tab": "కూలీల కోసం", "labor_tab": "పని కోసం", "market_tab": "మార్కెట్", "rent_tab": "యంత్రాల అద్దె",
        "name": "యజమాని పేరు", "loc": "గ్రామం", "phone": "ఫోన్", "crop": "పంట", "price": "ధర", "qty": "పరిమాణం",
        "submit": "సమర్పించు", "call": "కాల్ చేయండి", "remove": "తొలగించు", "near_me": "గ్రామం పేరుతో వెతకండి",
        "equip_name": "యంత్రం పేరు", "rent_price": "రోజువారీ అద్దె", "days": "పని దినాలు", "deadline": "చివరి తేదీ",
        "live_price": "నేటి మార్కెట్ ధరలు (క్వింటాల్‌కి)"
    },
    "Hindi (हिंदी)": {
        "home": "होम", "farmer_tab": "मजदूर खोजें", "labor_tab": "काम खोजें", "market_tab": "बाजार", "rent_tab": "उपकरण किराया",
        "name": "मालिक का नाम", "loc": "गांव", "phone": "फोन", "crop": "फसल", "price": "कीमत", "qty": "मात्रा",
        "submit": "जमा करें", "call": "कॉल करें", "remove": "हटाएं", "near_me": "गांव के नाम से खोजें",
        "equip_name": "उपकरण का नाम", "rent_price": "किराया/दिन", "days": "दिनों की संख्या", "deadline": "अंतिम तिथि",
        "live_price": "आज का बाजार भाव (प्रति क्विंटल)"
    }
}

selected_lang = st.sidebar.selectbox("Language / భాష / भाषा", ["English", "Hindi (हिंदी)", "Telugu (తెలుగు)"])
T = LANG_DATA[selected_lang]

# --- 4. NAVIGATION & FILTER ---
menu = st.sidebar.radio("Navigate", [T["home"], T["farmer_tab"], T["labor_tab"], T["market_tab"], T["rent_tab"]])
st.sidebar.write("---")
search_query = st.sidebar.text_input(f"🔍 {T['near_me']}", placeholder="e.g. Mandya").lower()

# --- 5. GLOBAL VOICE ASSISTANT ---
with st.sidebar.expander("✨ AI Voice Assistant"):
    st.write("Speak your need:")
    audio = mic_recorder(start_prompt="⏺ Start Recording", stop_prompt="⏹ Stop", key='voice_ai')
    if audio:
        st.success("✅ Voice Received! AI is processing...")

# --- 6. HOME PAGE ---
if menu == T["home"]:
    st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>🌾 AgriBridge</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; margin-top: 0px;'>Connecting Farmers, Laborers & Equipment</p>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&w=1000&q=80", use_container_width=True)

# --- 7. FARMER: HIRE LABOR ---
elif menu == T["farmer_tab"]:
    st.header(f"👨‍🌾 {T['farmer_tab']}")
    col1, col2 = st.columns(2)
    with col1:
        with st.form("f_form", clear_on_submit=True):
            name = st.text_input(T["name"]); crop = st.text_input(T["crop"]); loc = st.text_input(T["loc"])
            days = st.number_input(T["days"], min_value=1); deadline = st.date_input(T["deadline"]); phone = st.text_input(T["phone"])
            if st.form_submit_button(T["submit"]):
                st.session_state.farmer_jobs.append({"name": name, "crop": crop, "loc": loc, "days": days, "deadline": str(deadline), "phone": phone})
                st.rerun()
    with col2:
        for idx, p in enumerate(st.session_state.labor_posts):
            if search_query in p['loc'].lower():
                with st.container(border=True):
                    st.write(f"👷 **{p['name']}** | 📍 {p['loc']} | 🌾 {p['crop']}")
                    st.link_button(T["call"], f"tel:{p['phone']}")
                    if st.button(T["remove"], key=f"rl_{idx}"): st.session_state.labor_posts.pop(idx); st.rerun()

# --- 8. LABORER: FIND WORK ---
elif menu == T["labor_tab"]:
    st.header(f"👷 {T['labor_tab']}")
    col1, col2 = st.columns(2)
    with col1:
        with st.form("l_form", clear_on_submit=True):
            name = st.text_input(T["name"]); crop = st.text_input(T["crop"]); loc = st.text_input(T["loc"]); phone = st.text_input(T["phone"])
            if st.form_submit_button(T["submit"]):
                st.session_state.labor_posts.append({"name": name, "crop": crop, "loc": loc, "phone": phone})
                st.rerun()
    with col2:
        for idx, j in enumerate(st.session_state.farmer_jobs):
            if search_query in j['loc'].lower():
                with st.container(border=True):
                    st.write(f"🌾 **{j['crop']}** | 📍 {j['loc']} | 📅 {j['days']} Days")
                    st.link_button(T["call"], f"tel:{j['phone']}")
                    if st.button(T["remove"], key=f"rf_{idx}"): st.session_state.farmer_jobs.pop(idx); st.rerun()

# --- 9. MARKETPLACE (With Live Prices) ---
elif menu == T["market_tab"]:
    st.header(f"🛒 {T['market_tab']}")
    st.subheader(f"📈 {T['live_price']}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Paddy (వరి)", "₹2,183", "↑ 50"); c2.metric("Cotton (ప్రత్తి)", "₹7,020", "↑ 100"); c3.metric("Maize (మొక్కజొన్న)", "₹1,962", "-10")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.form("m_form", clear_on_submit=True):
            name = st.text_input(T["name"]); crop = st.text_input(T["crop"]); qty = st.text_input(T["qty"])
            price = st.text_input(T["price"]); loc = st.text_input(T["loc"]); phone = st.text_input(T["phone"])
            if st.form_submit_button(T["submit"]):
                st.session_state.market_items.append({"name": name, "crop": crop, "qty": qty, "price": price, "loc": loc, "phone": phone})
                st.rerun()
    with col2:
        for idx, i in enumerate(st.session_state.market_items):
            if search_query in i['loc'].lower():
                with st.container(border=True):
                    st.write(f"🌾 **{i['crop']}** ({i['qty']}) | 💰 {i['price']} | 📍 {i['loc']}")
                    st.link_button(T["call"], f"tel:{i['phone']}")
                    if st.button(T["remove"], key=f"rm_{idx}"): st.session_state.market_items.pop(idx); st.rerun()

# --- 10. EQUIPMENT RENTAL (With Owner Name) ---
elif menu == T["rent_tab"]:
    st.header(f"🚜 {T['rent_tab']}")
    col1, col2 = st.columns(2)
    with col1:
        with st.form("e_form", clear_on_submit=True):
            owner = st.text_input(T["name"]) # OWNER NAME ADDED
            e_name = st.text_input(T["equip_name"]); loc = st.text_input(T["loc"]); price = st.text_input(T["rent_price"]); phone = st.text_input(T["phone"])
            if st.form_submit_button(T["submit"]):
                st.session_state.equip_items.append({"owner": owner, "name": e_name, "loc": loc, "price": price, "phone": phone})
                st.rerun()
    with col2:
        for idx, e in enumerate(st.session_state.equip_items):
            if search_query in e['loc'].lower():
                with st.container(border=True):
                    st.write(f"🚜 **{e['name']}** | 📍 {e['loc']}")
                    st.write(f"👤 Owner: {e['owner']} | 💰 {e['price']}") # DISPLAY OWNER
                    st.link_button(T["call"], f"tel:{e['phone']}")
                    if st.button(T["remove"], key=f"re_{idx}"): st.session_state.equip_items.pop(idx); st.rerun()