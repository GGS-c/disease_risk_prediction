from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import pickle
import os
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Patient, Prediction
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_disease_prediction_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///disease_prediction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ------------------ LOAD MODELS ------------------

HEART_MODEL_PATH = os.path.join("outputs", "models", "heart_model.pkl")
with open(HEART_MODEL_PATH, "rb") as f:
    heart_model = pickle.load(f)

LIVER_MODEL_PATH = os.path.join("outputs", "models", "liver_model.pkl")
with open(LIVER_MODEL_PATH, "rb") as f:
    liver_model = pickle.load(f)


# ------------------ ROUTES ------------------

def get_specialist(disease_type, city):
    doctors = {
        "Nashik": {
            "Heart": [
                {"name": "Dr. Sanjay Wazalwar", "hospital": "Wockhardt Hospitals", "phone": "+91-253-6624444", "address": "Wadala Naka, Nashik"},
                {"name": "Dr. Nitin Bhamre", "hospital": "Apollo Hospital Nashik", "phone": "+91-253-2627000", "address": "Gangapur Road, Nashik"}
            ],
            "Liver": [
                {"name": "Dr. Prasad Bhate", "hospital": "Apollo Hospital Nashik", "phone": "+91-253-2627000", "address": "Gangapur Road, Nashik"},
                {"name": "Dr. Vijay Gite", "hospital": "Six Sigma Hospital", "phone": "+91-253-2313333", "address": "Mahatma Nagar, Nashik"}
            ]
        },
        "Pune": {
            "Heart": [
                {"name": "Dr. Shirish Hiremath", "hospital": "Ruby Hall Clinic", "phone": "+91-20-66455100", "address": "Sassoon Road, Pune"},
                {"name": "Dr. Rituja Kulkarni", "hospital": "Jehangir Hospital", "phone": "+91-20-66811000", "address": "Pune Station Road, Pune"}
            ],
            "Liver": [
                {"name": "Gastroenterology Dept", "hospital": "Dr. D. Y. Patil Hospital", "phone": "+91-20-27805000", "address": "Pimpri, Pune"},
                {"name": "Liver & Gastro Care", "hospital": "Ruby Hall Clinic", "phone": "+91-20-66455100", "address": "Sassoon Road, Pune"}
            ]
        },
        "Jalgaon": {
            "Heart": [
                {"name": "Dr. Sunil Mahajan", "hospital": "Orchid Hospital", "phone": "+91-257-2234455", "address": "Ring Road, Jalgaon"},
                {"name": "Cardiology Dept", "hospital": "Gajanan Heart Hospital", "phone": "+91-257-2223344", "address": "Navi Peth, Jalgaon"}
            ],
            "Liver": [
                {"name": "Gastroenterology Dept", "hospital": "Godavari Hospital", "phone": "+91-257-2255566", "address": "Jilha Peth, Jalgaon"},
                {"name": "Dr. Ramesh Patil", "hospital": "Indo American Hospital", "phone": "+91-257-2266777", "address": "Khandesh Mill Complex, Jalgaon"}
            ]
        },
        "Mumbai": {
            "Heart": [
                {"name": "Dr. Ramakanta Panda", "hospital": "Asian Heart Institute", "phone": "+91-22-66986666", "address": "Bandra Kurla Complex, Mumbai"},
                {"name": "Dr. Brian Pinto", "hospital": "Holy Family Hospital", "phone": "+91-22-61569999", "address": "Bandra West, Mumbai"}
            ],
            "Liver": [
                {"name": "Dr. Aabha Nagral", "hospital": "Jaslok Hospital", "phone": "+91-22-66573333", "address": "Pedder Road, Mumbai"},
                {"name": "Liver Clinic", "hospital": "Global Hospital", "phone": "+91-22-67670101", "address": "Parel, Mumbai"}
            ]
        }
    }
    
    spec_type = "Cardiologist" if disease_type == "Heart" else "Gastroenterologist / Liver Specialist"
    
    if city in doctors and disease_type in doctors[city]:
        results = []
        for doc in doctors[city][disease_type]:
            results.append({
                "type": spec_type,
                "name": doc["name"],
                "hospital": doc["hospital"],
                "phone": doc["phone"],
                "address": doc["address"]
            })
        return results
    else:
        return [{
            "type": spec_type,
            "name": "General Medical Officer",
            "hospital": "City Central Hospital",
            "phone": "104",
            "address": "Medical District"
        }]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/heart")
def heart():
    return render_template("heart.html")



@app.route("/liver")
def liver():
    return render_template("liver.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


# ------------------ AUTHENTICATION & DASHBOARD ------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        mobile = request.form.get("mobile")
        age = request.form.get("age")
        gender = request.form.get("gender")
        password = request.form.get("password")
        
        # Check if email exists
        user = Patient.query.filter_by(email=email).first()
        if user:
            flash("Email address already exists", "danger")
            return redirect(url_for('register'))
            
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_patient = Patient(name=name, email=email, mobile=mobile, age=age, gender=gender, password=hashed_pw)
        
        db.session.add(new_patient)
        db.session.commit()
        
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))
        
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = Patient.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['patient_id'] = user.id
            session['patient_name'] = user.name
            flash("Logged in successfully", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password", "danger")
            
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop('patient_id', None)
    session.pop('patient_name', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


@app.route("/dashboard")
def dashboard():
    if 'patient_id' not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('login'))
        
    patient_id = session['patient_id']
    patient = Patient.query.get(patient_id)
    predictions = Prediction.query.filter_by(patient_id=patient_id).order_by(Prediction.created_at.desc()).limit(5).all()
    total_predictions = Prediction.query.filter_by(patient_id=patient_id).count()
    
    return render_template("dashboard.html", patient=patient, predictions=predictions, total_predictions=total_predictions)


@app.route("/profile")
def profile():
    if 'patient_id' not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('login'))
        
    patient_id = session['patient_id']
    patient = Patient.query.get(patient_id)
    predictions = Prediction.query.filter_by(patient_id=patient_id).order_by(Prediction.created_at.desc()).all()
    
    return render_template("profile.html", patient=patient, predictions=predictions)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email == "admin@gmail.com" and password == "admin123":
            session['admin_logged_in'] = True
            flash("Admin logged in successfully", "success")
            return redirect(url_for('admin'))
        else:
            flash("Invalid Admin Credentials", "danger")
            
    if not session.get('admin_logged_in'):
        return render_template("admin_login.html")
        
    patients = Patient.query.all()
    predictions = Prediction.query.order_by(Prediction.created_at.desc()).all()
    return render_template("admin.html", patients=patients, predictions=predictions)

@app.route("/admin_logout")
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Admin logged out", "info")
    return redirect(url_for('home'))

# ------------------ HEART PREDICTION ------------------

@app.route("/predict", methods=["POST"])
def predict():
    try:
        input_data = {
            "Chest_Pain": float(request.form["Chest_Pain"]),
            "Shortness_of_Breath": float(request.form["Shortness_of_Breath"]),
            "Fatigue": float(request.form["Fatigue"]),
            "Palpitations": float(request.form["Palpitations"]),
            "Dizziness": float(request.form["Dizziness"]),
            "Swelling": float(request.form["Swelling"]),
            "Pain_Arms_Jaw_Back": float(request.form["Pain_Arms_Jaw_Back"]),
            "Cold_Sweats_Nausea": float(request.form["Cold_Sweats_Nausea"]),
            "High_BP": float(request.form["High_BP"]),
            "High_Cholesterol": float(request.form["High_Cholesterol"]),
            "Diabetes": float(request.form["Diabetes"]),
            "Smoking": float(request.form["Smoking"]),
            "Obesity": float(request.form["Obesity"]),
            "Sedentary_Lifestyle": float(request.form["Sedentary_Lifestyle"]),
            "Family_History": float(request.form["Family_History"]),
            "Chronic_Stress": float(request.form["Chronic_Stress"]),
            "Gender": float(request.form["Gender"]),
            "Age": float(request.form["Age"])
        }

        features = pd.DataFrame([input_data])

        prediction = heart_model.predict(features)[0]

        probability = None
        if hasattr(heart_model, "predict_proba"):
            probability = heart_model.predict_proba(features)[0][1] * 100

        patient_age = int(input_data["Age"])
        gender_str = "Male" if input_data["Gender"] == 1.0 else "Female"
        city = request.form.get("City", "Not Provided")
        
        patient_name = "Guest Patient"
        mobile_num = "Not Provided"
        
        if 'patient_id' in session:
            patient_name = session.get('patient_name', 'Guest Patient')
            patient_obj = Patient.query.get(session['patient_id'])
            if patient_obj:
                mobile_num = patient_obj.mobile

        current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

        patient_info = {
            "name": patient_name,
            "age": patient_age,
            "gender": gender_str,
            "mobile": mobile_num,
            "city": city,
            "date": current_time
        }

        # 3-Tier Risk Logic
        prob_val = probability if probability else (100.0 if prediction == 1 else 0.0)
        
        if prob_val >= 75.0:
            risk_level = "HIGH RISK"
            result_class = "danger"
            clinical_obs = [
                "Elevated cardiovascular risk indicators detected.",
                "Lifestyle and stress-related factors observed.",
                "Blood pressure and other markers suggest immediate attention is required."
            ]
            causes = ["Smoking", "High Blood Pressure", "High Cholesterol", "Chronic Stress", "Obesity"]
            lifestyle_recs = ["Strictly avoid smoking and alcohol", "Adopt a low-sodium, heart-healthy diet", "Avoid strenuous unsanctioned activities"]
            medical_recs = ["Consult a cardiologist immediately", "Perform a comprehensive ECG/Echo", "Monitor BP and lipids regularly"]
        elif prob_val >= 50.0:
            risk_level = "MODERATE RISK"
            result_class = "warning"
            clinical_obs = [
                "Moderate cardiovascular risk indicators detected.",
                "Early signs of lifestyle-induced stress observed.",
                "Preventative measures and close monitoring are highly recommended."
            ]
            causes = ["Borderline Blood Pressure", "Moderate stress levels", "Lack of optimal physical activity"]
            lifestyle_recs = ["Increase daily physical activity like walking", "Improve dietary habits (reduce processed foods)", "Practice stress management"]
            medical_recs = ["Schedule a routine cardiology checkup", "Review current medications", "Monitor vitals periodically"]
        else:
            risk_level = "LOW RISK"
            result_class = "success"
            clinical_obs = [
                "No significant cardiovascular risk indicators detected.",
                "Vitals and lifestyle factors appear within normal baseline limits."
            ]
            causes = ["Maintained healthy lifestyle", "Absence of critical cardiovascular risk factors"]
            lifestyle_recs = ["Continue regular exercise routines", "Maintain a balanced diet", "Ensure adequate hydration and sleep"]
            medical_recs = ["Continue annual routine checkups", "No immediate specialized screening required"]

        doctor_info = get_specialist("Heart", city)

        # Save prediction if user is logged in
        if 'patient_id' in session:
            new_prediction = Prediction(
                patient_id=session['patient_id'],
                disease_type="Heart",
                risk_result=risk_level,
                probability=round(prob_val, 2),
                city=city
            )
            db.session.add(new_prediction)
            db.session.commit()

        return render_template(
            "result.html",
            disease_type="Heart Disease",
            prediction=risk_level,
            probability=round(prob_val, 2),
            result_class=result_class,
            patient_info=patient_info,
            clinical_obs=clinical_obs,
            causes=causes,
            lifestyle_recs=lifestyle_recs,
            medical_recs=medical_recs,
            doctor_info=doctor_info
        )

    except Exception as e:
        return render_template(
            "result.html",
            prediction="Prediction Error",
            advice=str(e),
            probability=None,
            result_class="danger"
        )

# ------------------ LIVER PREDICTION ------------------
@app.route("/predict_liver", methods=["POST"])
def predict_liver():
    try:
        input_data = {
            "Age": float(request.form["Age"]),
            "Total_Bilirubin": float(request.form["Total_Bilirubin"]),
            "Alkaline_Phosphotase": float(request.form["Alkaline_Phosphotase"]),
            "Alamine_Aminotransferase": float(request.form["Alamine_Aminotransferase"]),
            "Aspartate_Aminotransferase": float(request.form["Aspartate_Aminotransferase"]),
            "Total_Proteins": float(request.form["Total_Proteins"]),
            "Albumin": float(request.form["Albumin"]),
            "Gender": float(request.form["Gender"])
        }

        features = pd.DataFrame([input_data])

        prediction = liver_model.predict(features)[0]

        probability = None
        if hasattr(liver_model, "predict_proba"):
            probability = liver_model.predict_proba(features)[0][1] * 100

        patient_age = int(input_data["Age"])
        gender_str = "Male" if input_data["Gender"] == 1.0 else "Female"
        city = request.form.get("City", "Not Provided")
        
        patient_name = "Guest Patient"
        mobile_num = "Not Provided"
        
        if 'patient_id' in session:
            patient_name = session.get('patient_name', 'Guest Patient')
            patient_obj = Patient.query.get(session['patient_id'])
            if patient_obj:
                mobile_num = patient_obj.mobile

        current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

        patient_info = {
            "name": patient_name,
            "age": patient_age,
            "gender": gender_str,
            "mobile": mobile_num,
            "city": city,
            "date": current_time
        }

        # 3-Tier Risk Logic
        prob_val = probability if probability else (100.0 if prediction == 1 else 0.0)
        
        if prob_val >= 75.0:
            risk_level = "HIGH RISK"
            result_class = "danger"
            clinical_obs = [
                "Abnormal liver enzyme patterns observed.",
                "Elevated bilirubin-related indicators detected.",
                "Possible severe liver stress markers identified."
            ]
            causes = ["Alcohol intake", "Fatty food consumption", "Poor liver enzyme levels", "Obesity"]
            lifestyle_recs = ["Completely avoid alcohol", "Adopt a strict liver-friendly diet", "Increase water intake significantly"]
            medical_recs = ["Consult a liver specialist immediately", "Perform a complete Liver Function Test (LFT)", "Schedule an abdominal ultrasound"]
        elif prob_val >= 50.0:
            risk_level = "MODERATE RISK"
            result_class = "warning"
            clinical_obs = [
                "Borderline liver enzyme patterns observed.",
                "Mild indicators of liver stress detected.",
                "Preventative monitoring is advised."
            ]
            causes = ["Moderate alcohol consumption", "Irregular dietary habits", "Potential medication side-effects"]
            lifestyle_recs = ["Reduce alcohol intake", "Limit processed foods and sugars", "Maintain regular hydration"]
            medical_recs = ["Schedule a routine gastroenterology checkup", "Monitor LFTs in 3-6 months"]
        else:
            risk_level = "LOW RISK"
            result_class = "success"
            clinical_obs = [
                "Liver enzymes and markers appear within normal limits.",
                "No significant indicators of hepatic stress detected."
            ]
            causes = ["Healthy dietary habits", "Low or no alcohol consumption"]
            lifestyle_recs = ["Maintain current healthy diet", "Continue regular physical activity"]
            medical_recs = ["Continue annual routine blood work", "No immediate specialized screening required"]

        doctor_info = get_specialist("Liver", city)

        # Save prediction
        if 'patient_id' in session:
            new_prediction = Prediction(
                patient_id=session['patient_id'],
                disease_type="Liver",
                risk_result=risk_level,
                probability=round(prob_val, 2),
                city=city
            )

            db.session.add(new_prediction)
            db.session.commit()

        return render_template(
            "result.html",
            disease_type="Liver Disease",
            prediction=risk_level,
            probability=round(prob_val, 2),
            result_class=result_class,
            patient_info=patient_info,
            clinical_obs=clinical_obs,
            causes=causes,
            lifestyle_recs=lifestyle_recs,
            medical_recs=medical_recs,
            doctor_info=doctor_info
        )

    except Exception as e:
        return render_template(
            "result.html",
            prediction="Prediction Error",
            advice=str(e),
            probability=None,
            result_class="danger"
        )
# ------------------ RUN ------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)