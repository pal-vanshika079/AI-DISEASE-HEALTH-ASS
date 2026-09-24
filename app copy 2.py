from flask import Flask, render_template, request, send_file
import pickle
import pandas as pd
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)
latest_report={}

# Load the trained ML model
model_path = "model/disease_model.pkl"

with open(model_path, "rb") as file:
    model = pickle.load(file)


# Home page
@app.route("/")
def home():
    return render_template("index.html")

def create_pdf_report():

    pdf_path = "AI_Health_Assessment_Report.pdf"

    c = canvas.Canvas(pdf_path, pagesize=A4)

    width, height = A4
    y = height - 50

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(
        width / 2,
        y,
        "AI HEALTH ASSESSMENT REPORT"
    )

    y -= 25

    c.setFont("Helvetica", 10)
    c.drawCentredString(
        width / 2,
        y,
        "AI-Based Educational Health Assessment"
    )

    y -= 45

    # Prediction Result
    c.setFont("Helvetica-Bold", 15)
    c.drawString(50, y, "Prediction Result")

    y -= 25

    c.setFont("Helvetica-Bold", 12)
    c.drawString(
        50,
        y,
        f"Most Likely Condition: {latest_report['disease']}"
    )

    y -= 35

    # Selected Symptoms
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Selected Symptoms:")

    y -= 20

    c.setFont("Helvetica", 11)
    c.drawString(
        70,
        y,
        str(latest_report["symptoms"])
    )

    y -= 35

    # Top 3 Predictions
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Top 3 Model Predictions:")

    y -= 22

    c.setFont("Helvetica", 11)

    for name, prob in latest_report["top_predictions"]:
        c.drawString(
            70,
            y,
            f"{name} - {prob}% model score"
        )
        y -= 20

    y -= 20

    # Health Guidance
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Health Guidance:")

    y -= 22

    c.setFont("Helvetica", 11)

    health_text = latest_report["health_tip"]

    c.drawString(
        70,
        y,
        health_text
    )

    y -= 35

    # Report Status
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Report Status:")

    y -= 20

    c.setFont("Helvetica", 11)
    c.drawString(
        70,
        y,
        "Educational AI assessment"
    )

    y -= 35

    # Why this prediction
    c.setFont("Helvetica-Bold", 12)
    c.drawString(
        50,
        y,
        "Why this prediction?"
    )

    y -= 22

    c.setFont("Helvetica", 10)
    c.drawString(
        70,
        y,
        "The model made this prediction based on"
    )

    y -= 16

    c.drawString(
        70,
        y,
        "the symptoms selected by the user."
    )

    y -= 35

    # Red Flag
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Red Flag:")

    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(
        70,
        y,
        "If you have severe breathing difficulty,"
    )

    y -= 16

    c.drawString(
        70,
        y,
        "chest pain, fainting, confusion, or rapidly"
    )

    y -= 16

    c.drawString(
        70,
        y,
        "worsening symptoms, seek urgent medical care."
    )

    y -= 35

    # Important
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Important:")

    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(
        70,
        y,
        "Model scores are not medical probabilities"
    )

    y -= 16

    c.drawString(
        70,
        y,
        "or a medical diagnosis."
    )

    y -= 16

    c.drawString(
        70,
        y,
        "Please consult a qualified healthcare"
    )

    y -= 16

    c.drawString(
        70,
        y,
        "professional for medical advice."
    )

    # Footer
    y = 40

    c.setFont("Helvetica", 8)
    c.drawCentredString(
        width / 2,
        y,
        "AI Disease Health Assistant | Educational Purpose Only"
    )

    c.save()

    return pdf_path 
# Download Report
@app.route("/download-report")
def download_report():

    if not latest_report:
        return "Please run a prediction first."

    report = f"""AI HEALTH ASSESSMENT REPORT

Selected Symptoms:
{latest_report["symptoms"]}

Most Likely Condition:
{latest_report["disease"]}

Top 3 Model Predictions:
"""

    for name, prob in latest_report["top_predictions"]:
        report += f"{name} — {prob}% model score\n"

    report += f"""
Health Guidance:
{latest_report["health_tip"]}

Report Status:
Educational AI assessment

Why this prediction?
The model made this prediction based on the symptoms you selected.

Health Assistant:
Rest, stay hydrated, and follow the health guidance provided above.

Red Flag:
If you have severe breathing difficulty, chest pain, fainting,
confusion, or rapidly worsening symptoms, seek urgent medical care.

Important:
Model scores are not medical probabilities or a medical diagnosis.
Please consult a qualified healthcare professional for medical advice.
"""

    report_path = "health_report.txt"

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report)

    return send_file(
        report_path,
        as_attachment=True,
        download_name="AI_Health_Assessment_Report.txt",
        mimetype="text/plain"
    )
# Download PDF Report
@app.route("/download-pdf")
def download_pdf():

    if not latest_report:
        return "Please run a prediction first."

    pdf_path = create_pdf_report()

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="AI_Health_Assessment_Report.pdf",
        mimetype="application/pdf"
    )
# Health Assistant
@app.route("/health-assistant", methods=["POST"])
def health_assistant():

    question = request.form.get("question", "").lower()

    if "cough" in question:
        answer = "For cough, stay hydrated, rest, and avoid smoke or other irritants."

    elif "fever" in question:
        answer = "For fever, rest, drink enough fluids, and monitor your temperature."

    elif "headache" in question:
        answer = "For headache, rest, stay hydrated, and avoid known triggers."

    elif "vomiting" in question:
        answer = "After vomiting, take small sips of fluids to help prevent dehydration."

    elif "breathing" in question:
        answer = "Breathing difficulty can require medical attention. If it is severe or worsening, seek urgent medical care."

    else:
        answer = "Please describe your symptoms clearly. This assistant provides general educational guidance only."

    return f"""
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>AI Health Assistant</title>

    <style>

        body {{
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            margin: 0;
            padding: 30px 15px;
        }}

        .container {{
            max-width: 750px;
            margin: auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 25px;
        }}

        .header h1 {{
            margin-bottom: 8px;
        }}

        .header p {{
            color: #666;
        }}

        .card {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        }}

        .question {{
            background: #f7f9fc;
            padding: 15px;
            border-radius: 10px;
        }}

        .guidance {{
            background: #f7f9fc;
            padding: 15px;
            border-radius: 10px;
        }}

        .warning {{
            background: #fff8e1;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
        }}

        .buttons {{
            text-align: center;
            margin-top: 25px;
        }}

        .back {{
            display: inline-block;
            padding: 13px 25px;
            background: #333;
            color: white;
            text-decoration: none;
            border-radius: 8px;
        }}

        .back:hover {{
            background: #555;
        }}

    </style>

</head>

<body>

<div class="container">

    <div class="header">

        <h1>🩺 AI Health Assistant</h1>

        <p>
            AI-Based Educational Health Guidance
        </p>

    </div>


    <div class="card">

        <h3>💬 Your Question</h3>

        <div class="question">
            {question}
        </div>

    </div>


    <div class="card">

        <h3>🩺 Health Guidance</h3>

        <div class="guidance">
            {answer}
        </div>

    </div>


    <div class="card">

        <div class="warning">

            <b>⚠️ Important:</b>

            <br><br>

            This is general educational information
            and not a medical diagnosis.

            <br><br>

            If symptoms are severe or getting worse,
            seek medical care.

        </div>

    </div>


    <div class="buttons">

        <a href="/" class="back">
            ← Go Back
        </a>

    </div>

</div>

</body>

</html>
"""

# Disease prediction
@app.route("/predict", methods=["POST"])
def predict():

    symptoms = request.form.getlist("symptoms")

    symptom_names = [
        "Fever",
        "Cough",
        "Headache",
        "Tiredness",
        "Nausea",
        "Vomiting",
        "Sore Throat",
        "Difficulty Breathing"
    ]

    symptom_values = []

    for symptom in symptom_names:
        if symptom in symptoms:
            symptom_values.append(1)
        else:
            symptom_values.append(0)

    input_data = pd.DataFrame(
        [symptom_values],
        columns=symptom_names
    )

    prediction = model.predict(input_data)

    disease = prediction[0]
    # Health Assistant guidance
    health_tips = {
    "Flu": "Rest properly, drink enough fluids, and monitor your symptoms.",
    "Common Cold": "Take adequate rest, stay hydrated, and keep yourself comfortable.",
    "Migraine": "Rest in a quiet environment, stay hydrated, and avoid known triggers.",
    "Gastritis": "Eat light meals, stay hydrated, and avoid foods that worsen stomach discomfort.",
    "Bronchitis": "Rest, stay hydrated, and avoid smoke or other respiratory irritants.",
    "Pneumonia": "Seek medical advice promptly, especially if breathing difficulty or high fever is present.",
    "Allergy": "Avoid known triggers and keep your surroundings clean.",
    "Sinusitis": "Stay hydrated, rest, and avoid irritants such as smoke and dust.",
    "Food Poisoning": "Drink fluids to prevent dehydration and seek medical help if symptoms are severe.",
    "Viral Fever": "Rest, stay hydrated, and monitor your temperature and symptoms.",
    "Tonsillitis": "Rest, drink fluids, and seek medical advice if swallowing or breathing becomes difficult.",
    "Typhoid": "Consult a qualified healthcare professional for proper evaluation and treatment."
}

    health_tip = health_tips.get(
    disease,
    "Stay hydrated, take adequate rest, and consult a healthcare professional if symptoms persist."
)
    # Explain the prediction using selected symptoms
    selected_symptoms = ", ".join(symptoms) if symptoms else "None"

    # Get model probabilities
    probabilities = model.predict_proba(input_data)[0]
    classes = model.classes_

    # Get top 3 predictions
    top_indices = probabilities.argsort()[-3:][::-1]

    top_predictions = []
    for i in top_indices:
        top_predictions.append(
        (classes[i], round(probabilities[i] * 100, 2))
    )
        # Save latest prediction for Download Report
    latest_report["symptoms"] = selected_symptoms
    latest_report["disease"] = disease
    latest_report["top_predictions"] = top_predictions
    latest_report["health_tip"] = health_tip

    return f"""
     <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Prediction Result</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            margin: 0;
            padding: 30px 15px;
        }}

        .container {{
            max-width: 750px;
            margin: auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 25px;
        }}

        .header h1 {{
            margin-bottom: 8px;
        }}

        .header p {{
            color: #666;
        }}

        .card {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        }}

        .condition {{
            text-align: center;
        }}

        .condition h2 {{
            margin-bottom: 5px;
        }}

        .condition p {{
            color: #666;
        }}

        .card h3 {{
            margin-top: 0;
        }}

        ol {{
            padding-left: 25px;
        }}

        li {{
            margin: 10px 0;
        }}

        .guidance {{
            background: #f7f9fc;
            padding: 15px;
            border-radius: 10px;
        }}

        .warning {{
            background: #fff8e1;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
        }}

        .important {{
            background: #fff0f0;
            padding: 15px;
            border-radius: 10px;
        }}

        .buttons {{
            text-align: center;
            margin-top: 25px;
        }}

        .download {{
            display: inline-block;
            padding: 13px 25px;
            background: #333;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            margin: 5px;
        }}

        .back {{
            display: inline-block;
            padding: 13px 25px;
            background: white;
            color: #333;
            text-decoration: none;
            border: 1px solid #ccc;
            border-radius: 8px;
            margin: 5px;
        }}
    </style>
</head>

<body>

<div class="container">

    <div class="header">
        <h1>🩺 AI Disease Health Assistant</h1>
        <p>AI-Based Educational Health Assessment</p>
    </div>

    <div class="card condition">
        <h2>Prediction Result</h2>
        <h2>Most Likely Condition: {disease}</h2>
        <p>Based on the symptoms selected by the user.</p>
    </div>

    <div class="card">
        <h3>🔍 Top 3 Model Predictions</h3>

        <ol>
            {''.join(
                f"<li><b>{name}</b> — {prob}% model score</li>"
                for name, prob in top_predictions
            )}
        </ol>
    </div>

    <div class="card">
        <h3>📋 AI Health Assessment Report</h3>

        <p>
            <b>Selected Symptoms:</b> {selected_symptoms}
        </p>

        <p>
            <b>Most Likely Condition:</b> {disease}
        </p>

        <div class="guidance">
            <b>Health Guidance:</b><br><br>
            {health_tip}
        </div>

        <p>
            <b>Report Status:</b> Educational AI assessment
        </p>
    </div>

    <div class="card">
        <h3>🔍 Why this prediction?</h3>

        <p>
            The model made this prediction based on the symptoms you selected.
        </p>

        <p>
            <b>Selected Symptoms:</b> {selected_symptoms}
        </p>

        <p>
            The prediction is generated by a machine-learning model
            trained on the project's disease-symptom dataset.
        </p>
    </div>

    <div class="card">
        <h3>🩺 Health Assistant</h3>

        <p><b>General Guidance:</b></p>

        <p>{health_tip}</p>

        <div class="warning">
            <b>⚠️ Red Flag:</b><br><br>
            If you have severe breathing difficulty, chest pain,
            fainting, confusion, or rapidly worsening symptoms,
            seek urgent medical care.
        </div>
    </div>

    <div class="card important">
        <b>⚠️ Important:</b><br><br>
        Model scores are not medical probabilities or a medical diagnosis.
        Please consult a qualified healthcare professional for medical advice.
    </div>

    <div class="buttons">

        <a href="/download-report" class="download">
            📥 Download Report
        </a>
        <a href="/download-pdf" class="download">
    📄 Download PDF
    </a>

        <a href="/" class="back">
            ← Go Back
        </a>

    </div>

</div>

</body>
</html>
"""


if __name__ == "__main__":
    app.run(debug=True)