import streamlit as st
import pandas as pd
import os
from recommendation import load_data, recommend_plan
from sentiment import analyze_sentiment
from logger import log_interaction
from reportlab.pdfgen import canvas

# ---- CONFIG ----
st.set_page_config(page_title="Healthcare Recommendation System", layout="wide")

# Load user DB
# ---- USER DB ----
USERS_FILE = "data/users.csv"
if os.path.exists(USERS_FILE):
    users_df = pd.read_csv(USERS_FILE)
else:
    users_df = pd.DataFrame(columns=["username", "password", "role", "age", "gender"])

# Load hospital DB
HOSPITAL_FILE = "data/hospital_list.xlsx"
if os.path.exists(HOSPITAL_FILE):
    hospital_df = pd.read_excel("data/hospital_list.xlsx")
else:
    hospital_df = pd.DataFrame(columns=["speciality", "hospital_name", "location"])

# Session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = ""

# Auth UI
auth_mode = st.sidebar.radio("🔐 Choose Action", ["Login", "Register"])

if not st.session_state.authenticated:
    st.subheader("🔐 User Authentication")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if auth_mode == "Login":
        login_disabled = not (username and password)
        if st.button("Login", disabled=login_disabled):

            user_row = users_df[users_df["username"] == username]
            if not user_row.empty and user_row.iloc[0]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.role = user_row.iloc[0]["role"]
                st.success(f"✅ Welcome, {username.title()}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    elif auth_mode == "Register":
        role = st.selectbox("Choose Role", ["user", "admin"])
        age = st.number_input("Age", min_value=1, max_value=120, step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        register_disabled = not (username and password and age and gender)
        if st.button("Register", disabled=register_disabled): 
            if username in users_df["username"].values:
                st.warning("🚫 Username already exists.")
            else:
                new_user = pd.DataFrame([{
                    "username": username,
                    "password": password,
                    "role": role,
                    "age": age,
                    "gender": gender
                }])
                new_user.to_csv(USERS_FILE, mode="a", header=not os.path.exists(USERS_FILE), index=False)
                st.success("✅ Registration successful! You can now log in.")
    st.stop()

# ---- APP TITLE ----
st.title("🩺 Healthcare Recommendation System")

# ---- SIDEBAR NAV ----
menu_options = {
    "📝 Recommendation": "Recommendation",
    "🤖 Chatbot": "Chatbot",
    "📜 My History": "My History"
}
if st.session_state.role == "admin":
    menu_options["📊 Admin Dashboard"] = "Admin Dashboard"

menu = st.sidebar.radio("📌 Navigate", list(menu_options.keys()))
menu = menu_options[menu]  # Get value from selected emoji+label

st.sidebar.markdown("## 👤 Logged in as")
st.sidebar.markdown(f"**{st.session_state.username.title()}** ({st.session_state.role})")
st.sidebar.markdown("---")

# Logout button
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.pop("chat_history", None)
    st.session_state.pop("symptom_list", None)
    st.success("You have been logged out.")
    st.rerun()

# ---- LOAD DATA ----
df = load_data()

# ---- RECOMMENDATION PAGE ----
if menu == "Recommendation":
    st.subheader("📝 Enter Symptoms")
    symptoms_input = st.text_input("Separate multiple symptoms with commas")

    user_symptoms = []
    recs = []
    sentiment_result = ""

    get_rec_disabled = not symptoms_input.strip()
    if st.button("Get Recommendation", disabled=get_rec_disabled):

        if symptoms_input:
            user_symptoms = [s.strip() for s in symptoms_input.split(",")]
            user_info = users_df[users_df["username"] == st.session_state.username].iloc[0]
            recs = recommend_plan(user_symptoms, df, age=user_info["age"], gender=user_info["gender"])

            st.subheader("🔍 Top Recommendation(s):")
            for i, (rec, score) in enumerate(recs, 1):
                st.markdown(f"**{i}. {rec}**  \n🧠 *Symptom Match Score:* `{score}`")

            # Show hospitals if any match
            matched_specialities = [rec[0] for rec in recs]
            hospital_matches = hospital_df[hospital_df["speciality"].isin(matched_specialities)]

            if not hospital_matches.empty:
                st.markdown("🏥 **Recommended Hospitals**")
                st.dataframe(hospital_matches)

            st.session_state["user_symptoms"] = user_symptoms
            st.session_state["recs"] = recs
        else:
            st.warning("Please enter at least one symptom.")

    st.subheader("🗣️ Optional: Give Feedback")
    feedback = st.text_area("How do you feel about this recommendation?", key="feedback_box")

    if st.button("Submit Feedback"):
        if "user_symptoms" in st.session_state and "recs" in st.session_state:
            sentiment_result = analyze_sentiment(feedback)
            st.success(f"✅ Your feedback has been analyzed. Detected sentiment: **{sentiment_result}**")
            log_interaction(
                st.session_state["user_symptoms"],
                st.session_state["recs"],
                feedback,
                sentiment_result
            )
        else:
            st.warning("Generate a recommendation first.")

    if st.button("📄 Download Report as PDF"):
        os.makedirs("reports", exist_ok=True)
        filename = f"reports/report_{st.session_state.username}.pdf"
        c = canvas.Canvas(filename)
        c.drawString(100, 800, f"User: {st.session_state.username}")
        c.drawString(100, 780, f"Symptoms: {', '.join(st.session_state.get('user_symptoms', []))}")
        c.drawString(100, 760, "Recommendations:")
        for i, (rec, score) in enumerate(st.session_state.get("recs", []), 1):
            c.drawString(120, 740 - i*20, f"{i}. {rec} (Score: {score})")
        if feedback:
            c.drawString(100, 660, f"Feedback: {feedback}")
            c.drawString(100, 640, f"Sentiment: {sentiment_result}")
        c.save()
        with open(filename, "rb") as file:
            st.download_button("Download PDF", file, file_name=filename)

# ---- CHATBOT PAGE ----
# ---- CHATBOT PAGE ----
elif menu == "Chatbot":
    st.subheader("🤖 Chat with MediPal")

    bot_style = "🧠 [Professional MediPal]:" if st.session_state.role == "admin" else "😊 [Friendly MediPal]:"

    if st.button("🧹 Clear Chat History"):
        st.session_state.chat_history = [
            f"{bot_style} Hello {st.session_state.username.title()}! What symptoms are you experiencing today?"
        ]
        st.session_state.symptom_list = []
        st.rerun()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            f"{bot_style} Hello {st.session_state.username.title()}! What symptoms are you experiencing today?"
        ]
        st.session_state.symptom_list = []

    for msg in st.session_state.chat_history:
        st.markdown(msg)

    user_input = st.chat_input("Type your symptoms or questions here...")

    if user_input:
        st.session_state.chat_history.append(f"🗣️ You: {user_input}")
        response = ""

        # Normalize input
        lowered = user_input.lower()
        symptoms = [s.strip() for s in lowered.split(",")]

        if any(word in lowered for word in ["nothing", "no symptoms", "i'm fine", "feeling okay"]):
            response = f"{bot_style} Glad to hear that! Stay hydrated and take care. Let me know if anything changes."
        elif any(word in lowered for word in ["tired", "fatigue", "exhausted"]):
            response = f"{bot_style} You mentioned fatigue — are you sleeping well and staying hydrated?"
        elif any(word in lowered for word in ["pain", "ache", "hurt"]):
            response = f"{bot_style} Noted. Can you describe where the pain is and how severe it feels?"
        elif any(word in lowered for word in ["cold", "flu", "cough", "sneeze", "congestion"]):
            response = f"{bot_style} Sounds like a seasonal infection. Is the weather cold where you are? ❄️"
        elif any(word in lowered for word in ["headache", "migraine"]):
            response = f"{bot_style} Sorry to hear about the headache. Have you had enough water and rest lately?"
        elif any(word in lowered for word in ["fever", "temperature"]):
            response = f"{bot_style} Fever noted. Please monitor your temperature and drink plenty of fluids."

        else:
            # Fallback and Recommendation
            st.session_state.symptom_list.extend(symptoms)
            user_info = users_df[users_df["username"] == st.session_state.username].iloc[0]
            recs = recommend_plan(st.session_state.symptom_list, df, age=user_info["age"], gender=user_info["gender"])

            response = f"{bot_style} Thanks! Based on your inputs, here's what I suggest:"
            st.session_state.chat_history.append(response)

            for i, (rec, score) in enumerate(recs, 1):
                st.session_state.chat_history.append(f"👉 Recommendation {i}: **{rec}** (Score: `{score}`)")

            response = f"{bot_style} Let me know if you experience more symptoms, and I’ll refine the suggestions."

        st.session_state.chat_history.append(response)
        st.rerun()

# ---- MY HISTORY PAGE ----
elif menu == "My History":
    st.subheader("📜 My Recommendation History")
    username = st.session_state.get("username", "guest")
    log_file = f"data/logs_{username}.csv"

    try:
        history_df = pd.read_csv(log_file)
        st.dataframe(history_df, use_container_width=True)
        st.markdown("### 🕑 Most Recent Entries")
        st.dataframe(history_df.tail(5), use_container_width=True)
    except FileNotFoundError:
        st.info("You don't have any history yet.")

# ---- ADMIN DASHBOARD ----
elif menu == "Admin Dashboard":
    st.subheader("📊 Admin Analytics Dashboard")
    import glob
    import plotly.express as px

    all_logs = pd.DataFrame()
    for file in glob.glob("data/logs_*.csv"):
        df = pd.read_csv(file)
        df["user"] = file.split("_")[-1].replace(".csv", "")
        all_logs = pd.concat([all_logs, df], ignore_index=True)

    if all_logs.empty:
        st.info("No feedback logs yet.")
    else:
        st.markdown("### 🧾 All Feedback")
        st.dataframe(all_logs)

        st.markdown("### 🥧 Sentiment Breakdown")
        sentiment_counts = all_logs["sentiment"].value_counts()
        fig = px.pie(
            names=sentiment_counts.index,
            values=sentiment_counts.values,
            title="Sentiment Distribution"
        )
        st.plotly_chart(fig)

        st.markdown("### 🌟 Top Recommended Plans")
        recs_flat = all_logs["recommendations"].dropna().str.split(", ").explode()
        top_recs = recs_flat.value_counts().head(5)
        fig2 = px.bar(
            top_recs,
            x=top_recs.index,
            y=top_recs.values,
            title="Top 5 Recommendations"
        )
        st.plotly_chart(fig2)


