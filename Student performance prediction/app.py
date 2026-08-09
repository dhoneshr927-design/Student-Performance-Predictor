import streamlit as st
import pandas as pd
import numpy as np
import joblib
import sqlite3
import datetime
from fpdf import FPDF



def generate_pdf(score, student_class, study_hours, attendance, recommendations):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Banner
    pdf.set_fill_color(30, 58, 138) # Dark Navy Blue
    pdf.rect(0, 0, 210, 30, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 8, txt="Student Performance & AI Report", ln=True, align='C')
    
    pdf.set_font("Arial", size=9)
    pdf.cell(0, 5, txt=f"Generated Date: {datetime.date.today().strftime('%B %d, %Y')}", ln=True, align='C')
    pdf.ln(10)
    
    # Summary Section Table
    pdf.set_text_color(30, 58, 138)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 7, txt="Summary Input & Prediction Result", ln=True)
    pdf.set_draw_color(59, 130, 246)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    # Table Grid
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(30, 41, 59)
    
    data = [
        ("Class Level", str(student_class)),
        ("Daily Study Hours", f"{study_hours} hrs"),
        ("Attendance", f"{attendance}%"),
        ("Predicted Score", f"{score:.2f}%")
    ]
    
    for label, val in data:
        pdf.set_fill_color(241, 245, 249)
        pdf.cell(90, 7, txt=f"  {label}", border=1, fill=True)
        pdf.set_fill_color(255, 255, 255)
        pdf.cell(90, 7, txt=f"  {val}", border=1, fill=True, ln=True)
    
    pdf.ln(6)
    
    # AI Recommendations Section
    pdf.set_text_color(30, 58, 138)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 7, txt="AI Suggestions & Recommendations", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(51, 65, 85)
    
    for rec in recommendations:
        start_y = pdf.get_y()
        pdf.set_fill_color(239, 246, 255)
        pdf.set_draw_color(147, 197, 253)
        
        pdf.rect(10, start_y, 190, 10, 'DF')
        pdf.set_xy(12, start_y + 2.5)
        pdf.multi_cell(185, 4.5, txt=f"> {rec}")
        pdf.set_y(start_y + 12)
        
  
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 8, txt="Developed by DhaneshAI |© 2026 All Rights Reserved", align='C', ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# Page Configuration
st.set_page_config(page_title="Student Performance Predictor", page_icon="🎓", layout="centered")

# --- Sidebar & Database Controls ---

conn = sqlite3.connect("predictions.db", check_same_thread=False)


with st.sidebar:
    st.title("👨‍🎓 Student Panel")
    st.caption("Student Performance Predictor")
    st.write("---")
    
    if st.button("🗑️ Clear History"):
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prediction_history")
            conn.commit()
            st.success("Clean Successfully!")
            st.rerun()
        except Exception as e:
            st.error("Not Clean.try again!")


# 1. Database Connection & Table Creation
conn = sqlite3.connect('predictions.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS prediction_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction REAL,
        performance TEXT,
        date TEXT,
        time TEXT
    )
''')
conn.commit()

# 2. Model Loading Function
@st.cache_resource
def load_model():
    try:
        # Model Name 
        return joblib.load("student_performance_model.pkl") 
    except Exception as e:
        st.error(f"Model file 'model.pkl' পাওয়া যায়নি: {e}")
        return None

model = load_model()

# 3. Function to Save Prediction
def save_prediction(score):
    if score >= 80:
        level = "Excellent"
    elif score >= 60:
        level = "Good"
    elif score >= 40:
        level = "Average"
    else:
        level = "Poor"

    today = str(datetime.date.today())
    now = datetime.datetime.now().strftime("%H:%M:%S")

    cursor.execute("""
        INSERT INTO prediction_history (prediction, performance, date, time)
        VALUES (?, ?, ?, ?)
    """, (score, level, today, now))
    
    conn.commit()

# 4. Streamlit UI Design
st.title("🎓 Student Performance Predictor")
st.write("Student Performance Predictor below.")

# User Inputs Form
with st.form("student_form"):
    col1, col2 = st.columns(2)

    with col1:
        gender = st.selectbox("Gender", ["Male", "Female"])
        age = st.number_input("Age", min_value=10, max_value=30, value=16)
        student_class = st.selectbox("Class", ["10th Grade", "11th Grade", "12th Grade"])
        study_hours = st.number_input("Study Hours Per Day", min_value=0.0, max_value=24.0, value=4.0)
        attendance = st.number_input("Attendance Percentage", min_value=0.0, max_value=100.0, value=85.0)

    with col2:
        parent_edu = st.selectbox("Parental Education", ["High School", "intermediate", "Bachelor's", "Master's", "PHD"])
        internet = st.selectbox("Internet Access", ["Yes", "No"])
        activity = st.selectbox("Extracurricular Activities", ["Yes", "No"])
        previous_score = st.number_input("Previous Year Score (%)", min_value=0.0, max_value=100.0, value=75.0)
        performance_level = st.slider("Performance Level", min_value=0.0, max_value=100.0, value=40.0)
        pass_fail = st.selectbox("Pass/Fail Status", ["Pass", "Fail"])

    
    submit_button = st.form_submit_button("Predict Performance")


# Form Submit হওয়ার পর Mappings, Prediction এবং History দেখাবে
if submit_button:
    # ১. ম্যাপিং
    gender_map = {"Male": 1, "Female": 0}
    class_map = {"10th Grade": 0, "11th Grade": 1, "12th Grade": 2}
    parent_edu_map = {"High School": 0, "intermediate": 1, "Bachelor's": 2, "Master's": 3, "PHD": 4}
    internet_map = {"Yes": 1, "No": 0}
    activity_map = {"Yes": 1, "No": 0}
    pass_fail_map = {"Pass": 1, "Fail": 0}

    # ২. DataFrame তৈরি
    input_data = pd.DataFrame({
        'Age': [age],
        'Gender': [gender_map[gender]],
        'Class': [class_map[student_class]],
        'Study_Hours_Per_Day': [study_hours],
        'Attendance_Percentage': [attendance],
        'Parental_Education': [parent_edu_map[parent_edu]],
        'Internet_Access': [internet_map[internet]],
        'Extracurricular_Activities': [activity_map[activity]],
        'Previous_Year_Score': [previous_score],
        'Performance_Level': [performance_level],
        'Pass_Fail': [pass_fail_map[pass_fail]]
    })

    
    prediction = model.predict(input_data)
    score = prediction[0]
    save_prediction(score)


    col1, col2, col3 = st.columns(3)
    col1.metric(label="Predicted Score", value=f"{score:.2f}%")
    col2.metric(label="Attendance Level", value=f"{attendance}%")
    col3.metric(label="Status", value="Pass" if score >= 40 else "Fail")

    st.success(f"Predicted Score: {score:.2f}")

    st.write("---")
    st.subheader("📈 Score Progression")
    
    try:
        history_df = pd.read_sql_query("SELECT * FROM prediction_history ORDER BY id ASC", conn)
        if not history_df.empty:
            st.line_chart(history_df.set_index('id')['prediction'])
    except Exception as e:
        pass
  

    # ২. AI Recommendation Logic
    st.write("---")
    st.subheader("💡 AI Recommendations for Improvement")
    
    recommendations = []
    if score >= 80:
        recommendations = [
            "Excellent performance! Focus on competitive exam preparation and peer mentoring.",
            "Maintain your current study routine and take leadership in study groups."
        ]
    elif score >= 60:
        recommendations = [
            "Good progress! Try increasing daily study hours by 1-2 hours for higher marks.",
            "Focus more on weaker subjects identified in previous assessments."
        ]
    elif score >= 40:
        recommendations = [
            "Average result. Try boosting overall attendance above 85%.",
            "Follow a strict daily study timetable and clear basic concepts."
        ]
    else:
        recommendations = [
            "Immediate intervention needed. Create a structured fundamental study plan.",
            "Minimize distractions and track weekly progress with teachers or mentors."
        ]

    for rec in recommendations:
        st.info(f"👉 {rec}")

    # ৩. Download PDF Button
    pdf_bytes = generate_pdf(score, student_class, study_hours, attendance, recommendations)
    st.download_button(
        label="📄 Download Prediction PDF Report",
        data=pdf_bytes,
        file_name=f"Performance_Report_{datetime.date.today()}.pdf",
        mime="application/pdf"
    )


    st.write("---")
    st.subheader("📜 Prediction History")
    
    try:
        history_df = pd.read_sql_query("SELECT * FROM prediction_history ORDER BY id DESC", conn)
        st.dataframe(history_df, use_container_width=True)
    except Exception as e:
        st.error("ইতিহাস লোড করতে সমস্যা হচ্ছে।")


    st.write("---")
    st.caption("Developed by DhaneshAI | © 2026 All Rights Reserved")
