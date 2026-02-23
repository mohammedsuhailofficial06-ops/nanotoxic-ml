from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# 1. Enable CORS: Allows your Flutter Web app to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Professional Path Handling: Ensures Render finds the model file in the cloud
# It looks for 'nano_model.pkl' in the same folder as this script
model_path = os.path.join(os.path.dirname(_file_), 'nano_model.pkl')

try:
    model = joblib.load(model_path)
    print("✅ Nano-QSAR Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# 3. Define the Input Data Structure
class NanoData(BaseModel):
    core_material: str
    size_nm: float
    zeta_potential_mv: float
    dosage_ug_ml: float

@app.get("/")
def read_root():
    return {
        "status": "Online",
        "system": "NanoToxic-ML Predictive Portal",
        "version": "2.0-Research"
    }

@app.post("/predict")
def predict_tox(data: NanoData):
    # Prepare the data exactly as the model was trained
    input_dict = {
        'size_nm': [data.size_nm],
        'zeta_potential_mv': [data.zeta_potential_mv],
        'dosage_ug_ml': [data.dosage_ug_ml],
        'core_material_Gold': [1 if data.core_material == 'Gold' else 0],
        'core_material_IronOxide': [1 if data.core_material == 'IronOxide' else 0],
        'core_material_Silica': [1 if data.core_material == 'Silica' else 0],
        'core_material_Silver': [1 if data.core_material == 'Silver' else 0],
        'core_material_ZincOxide': [1 if data.core_material == 'ZincOxide' else 0],
    }
    
    df_input = pd.DataFrame(input_dict)
    
    # 4. Generate Predictions with Confidence Scores
    # predict_proba gives the probability for [Safe, Toxic]
    probs = model.predict_proba(df_input)[0] 
    prediction = model.predict(df_input)[0]
    
    confidence = max(probs) * 100
    result = "Toxic" if prediction == 1 else "Safe"
    
    return {
        "prediction": result,
        "confidence": f"{confidence:.2f}%",
        "parameters": {
            "material": data.core_material,
            "size": f"{data.size_nm}nm"
        },
        "methodology": "Random Forest Classifier (Nano-QSAR)"
    }