# 🩺 Healthcare Recommendation System

A Streamlit-based web application that provides personalized healthcare recommendations based on user symptoms. The system also analyzes user feedback sentiment, generates PDF reports, and includes an admin dashboard for insights.

---

## 🚀 Features

- 🔐 **User Authentication** (Login/Register)
- 📝 **Symptom-based Health Recommendations**
- 📍 **Nearby Hospital Suggestions** (based on specialty)
- 💬 **Feedback with Sentiment Analysis**
- 📄 **Downloadable PDF Reports**
- 🧠 **Interactive Chatbot** interface
- 📜 **User History Logs**
- 📊 **Admin Analytics Dashboard**

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Backend Logic:** Python
- **Data Analysis:** Pandas
- **Visualization:** Plotly
- **NLP / Sentiment Analysis:** TextBlob (uses NLTK internally)
- **PDF Generation:** ReportLab
- **Authentication:** Local CSV (basic prototype)

---

## 🧪 How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/healthcare-recommendation-system.git
   cd healthcare-recommendation-system

2. **Install dependencies**
       pip install -r requirements.txt

3. **Run the app**
    streamlit run app.py

📂 Project Structure
 .
├── app.py                       # Main application
├── recommendation.py           # Recommendation logic
├── sentiment.py                # Sentiment analysis logic
├── logger.py                   # Interaction logging
├── data/
│   ├── users.csv               # User database
│   ├── hospital_list.xlsx      # Hospital data
│   └── logs_*.csv              # User logs
├── reports/                    # Generated PDFs
├── requirements.txt
└── README.md

-----

## Requirements.txt
   streamlit
pandas
reportlab
textblob
plotly
openpyxl
