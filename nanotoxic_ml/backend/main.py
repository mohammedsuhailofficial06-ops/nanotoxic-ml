from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# 1. Professional CORS Configuration
# This is essential for your Flutter Web app to talk to the Render API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Robust Path Handling for Cloud Deployment
# This ensures the model is found regardless of where Render starts the script
BASE_DIR = os.path.dirname(os.path.abspath(_file_))
model_path = os.path.join(BASE_DIR, 'nano_model.pkl')

try:
    model = joblib.load(model_path)
    print("✅ Nano-QSAR Model loaded successfully")
except Exception as e:
    print(f"❌ Critical Error: Could not load model at {model_path}. Error: {e}")

# 3. Scientific Data Schema
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
        "version": "2.0-Research",
        "institution_context": "Karunya Institute of Technology and Sciences"
    }

@app.post("/predict")
def predict_tox(data: NanoData):
    # Ensure the input features match the training dataset exactly
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
    
    # 4. Generate Predictions with Confidence Analytics
    # Uses predict_proba to determine the probability of the assessment
    probs = model.predict_proba(df_input)[0] 
    prediction = model.predict(df_input)[0]
    
    # Probability of the selected class (0: Safe, 1: Toxic)
    confidence = max(probs) * 100
    result = "Toxic" if prediction == 1 else "Safe"
    
    return {
        "prediction": result,
        "confidence": f"{confidence:.2f}%",
        "metadata": {
            "model_type": "Random Forest Classifier",
            "endpoint": "Nanotoxicity (In-Vitro)",
            "descriptors": ["Size", "Zeta Potential", "Dosage", "Core Material"]
        }
    }
if _name_ == "_main_":
    import uvicorn
    # This grabs the port from Render's environment, or uses 10000 as a backup
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)