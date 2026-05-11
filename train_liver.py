import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
import pickle
import os

# 1. Generate Synthetic Liver Dataset
print("Generating synthetic liver dataset...")
np.random.seed(42)
n_samples = 1000

data = {
    'Age': np.random.randint(20, 80, n_samples),
    'Total_Bilirubin': np.random.uniform(0.5, 10.0, n_samples),
    'Alkaline_Phosphotase': np.random.randint(50, 400, n_samples),
    'Alamine_Aminotransferase': np.random.randint(10, 150, n_samples),
    'Aspartate_Aminotransferase': np.random.randint(10, 150, n_samples),
    'Total_Proteins': np.random.uniform(4.0, 9.0, n_samples),
    'Albumin': np.random.uniform(2.0, 5.0, n_samples),
    'Gender': np.random.randint(0, 2, n_samples), # 1 = Male, 0 = Female
}

# Create a logical target based on some thresholds
target = np.zeros(n_samples)
for i in range(n_samples):
    risk_score = 0
    if data['Total_Bilirubin'][i] > 3.0: risk_score += 1
    if data['Alkaline_Phosphotase'][i] > 200: risk_score += 1
    if data['Alamine_Aminotransferase'][i] > 80: risk_score += 1
    if data['Aspartate_Aminotransferase'][i] > 80: risk_score += 1
    if data['Albumin'][i] < 3.0: risk_score += 1
    
    if risk_score >= 2:
        target[i] = 1

data['Liver_Risk'] = target.astype(int)

df = pd.DataFrame(data)

os.makedirs('data', exist_ok=True)
dataset_path = os.path.join('data', 'synthetic_liver_dataset.csv')
df.to_csv(dataset_path, index=False)
print(f"Dataset saved to {dataset_path}")

# 2. Train Model
print("Training RandomForestClassifier...")
X = df.drop('Liver_Risk', axis=1)
y = df['Liver_Risk']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 3. Evaluate Model
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)

print(f"Accuracy: {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall: {rec:.4f}")

# 4. Save Model
os.makedirs(os.path.join('outputs', 'models'), exist_ok=True)
model_path = os.path.join('outputs', 'models', 'liver_model.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
    
print(f"Model successfully saved to {model_path}")
