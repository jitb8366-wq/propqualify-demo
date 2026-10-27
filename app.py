import streamlit as st
import google.generativeai as genai

st.set_page_config(
    page_title="PropQualify AI | Real Estate Lead Engine",
    page_icon="🏢",
    layout="centered"
)

st.title("🏢 PropQualify AI")
st.caption("Automated 24/7 Buyer Qualification Assistant for Guwahati Real Estate")

with st.sidebar:
    st.header("⚙️ Broker Controls")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    agency_name = st.text_input("Agency / Builder Name", value="Guwahati Prime Realty")
    st.markdown("---")
    st.subheader("📋 Active Lead Dossier")

if not api_key:
    st.warning("Please enter your free Gemini API Key in the sidebar to start the engine.")
    st.stop()

genai.configure(api_key=api_key)

SYSTEM_PROMPT = f"""
You are the Senior Property Assistant for {agency_name}, operating in Guwahati, Assam. 
Your objective is to warmly greet prospective property buyers, answer simple queries briefly, and naturally collect these 4 qualification details:
1. Desired Configuration (e.g., 2BHK, 3BHK, Commercial Space, Plot)
2. Preferred Location in Guwahati (e.g., GS Road, Zoo Road, Dispur, Six Mile)
3. Total Budget Range (e.g., ₹45 Lakhs - ₹80 Lakhs)
4. Site Visit Readiness & Timeline (e.g., this Saturday, ready to purchase within 30 days)

Rules:
- Be polite, professional, and concise (maximum 2 sentences per response).
- Do not invent property prices. If asked, say: "Exact floor pricing varies; our senior broker will share the precise price sheet during your site visit."
- Once all 4 data points are collected, conclude with: "Thank you! I have registered your requirement. Our senior property manager will call you shortly to confirm your site visit."
- At the end of every response where new buyer data is identified, output an internal summary tag formatted strictly as:
[DOSSIER: Config: <value> | Location: <value> | Budget: <value> | Visit: <value>]
"""

if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.messages = [
        {"role": "assistant", "content": f"Hello! Welcome to {agency_name}. Are you looking for a residential flat, a commercial space, or a plot in Guwahati today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_prompt := st.chat_input("Type your requirement here (e.g., Looking for a 3BHK flat near GS Road)..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    try:
        response = st.session_state.chat_session.send_message(user_prompt)
        full_text = response.text
        
        dossier_text = None
        clean_text = full_text
        if "[DOSSIER:" in full_text:
            parts = full_text.split("[DOSSIER:")
            clean_text = parts[0].strip()
            dossier_text = parts[1].replace("]", "").strip()

        st.session_state.messages.append({"role": "assistant", "content": clean_text})
        with st.chat_message("assistant"):
            st.write(clean_text)

        if dossier_text:
            with st.sidebar:
                st.success(f"🔥 Hot Lead Detected:\n{dossier_text}")

    except Exception as e:
        st.error(f"Error connecting to AI: {str(e)}")
