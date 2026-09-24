from flask import Flask, render_template, request, send_file
import pickle
import pandas as pd
import os

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
    <h1>Prediction Result</h1>

    <h2>Most Likely Condition: {disease}</h2>

    <h3>Top 3 Model Predictions:</h3>

    <ol>
        {''.join(
            f"<li>{name} — {prob}% model score</li>"
            for name, prob in top_predictions
        )}
    </ol>
    <hr>

    <h3>📋 AI Health Assessment Report</h3>

    <p>
    <b>Selected Symptoms:</b> {selected_symptoms}
    </p>

    <p>
    <b>Most Likely Condition:</b> {disease}
    </p>

    <p>
    <b>Health Guidance:</b> {health_tip}
    </p>

    <p>
    <b>Report Status:</b> Educational AI assessment
    </p>

    <hr>

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

    <hr>

    <h3>🩺 Health Assistant</h3>

    <p><b>General Guidance:</b></p>

    <p>{health_tip}</p>

    <p>
        <b>⚠️ Red Flag:</b> If you have severe breathing difficulty,
        chest pain, fainting, confusion, or rapidly worsening symptoms,
        seek urgent medical care.
    </p>

    <hr>

    <p>
        <b>⚠️ Important:</b> Model scores are not medical probabilities
        or a medical diagnosis. Please consult a qualified healthcare
        professional for medical advice.
    </p>

    <br>

    <a href="/download-report">
    <button>📥 Download Report</button>
    </a>

    <br><br>

    <a href="/">Go Back</a>
    """


if __name__ == "__main__":
    app.run(debug=True)