import os
import pandas as pd
from src.model import train_model, evaluate_model, save_model

# Load dataset
df = pd.read_csv("data/heart_disease_risk_dataset_earlymed.csv")

# Features and target
X = df[
    [
        "Chest_Pain",
        "Shortness_of_Breath",
        "Fatigue",
        "Palpitations",
        "Dizziness",
        "Swelling",
        "Pain_Arms_Jaw_Back",
        "Cold_Sweats_Nausea",
        "High_BP",
        "High_Cholesterol",
        "Diabetes",
        "Smoking",
        "Obesity",
        "Sedentary_Lifestyle",
        "Family_History",
        "Chronic_Stress",
        "Gender",
        "Age"
    ]
]

y = df["Heart_Risk"]

# Train model
model, X_test, y_test = train_model(X, y)

# Evaluate model
metrics = evaluate_model(model, X_test, y_test)
print("Model Performance:")
print(f"Accuracy : {metrics['accuracy']:.4f}")
print(f"Precision: {metrics['precision']:.4f}")
print(f"Recall   : {metrics['recall']:.4f}")

# Create folder
os.makedirs("outputs/models", exist_ok=True)

# Save model
save_model(model, "outputs/models/heart_model.pkl")
print("Model saved successfully.")