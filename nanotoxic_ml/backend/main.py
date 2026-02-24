from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# 1. CORS HANDSHAKE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. DEFINE DATA SCHEMA
class NanoData(BaseModel):
    core_material: str
    size_nm: float
    zeta_potential_mv: float
    dosage_ug_ml: float

# 3. GLOBAL MODEL INITIALIZATION 
# This ensures line 61 always has a 'model' variable to talk to.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'nano_model.pkl')

# We initialize it as None first
model = None

if os.path.exists(model_path):
    try:
        model = joblib.load(model_path)
        print("✅ Nano-QSAR Random Forest Model Loaded Successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
else:
    print(f"❌ CRITICAL: {model_path} NOT FOUND. Ensure the .pkl file is in the backend folder.")

@app.get("/")
def read_root():
    return {"status": "Online", "model_loaded": model is not None}

@app.post("/predict")
async def predict_tox(data: NanoData):
    # This check prevents the NameError you were seeing
    if model is None:
        raise HTTPException(status_code=500, detail="The ML model is not loaded on the server. Check backend logs.")

    try:
        # Prepare input for the Random Forest model
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
        
        # Line 61: Now 'model' is guaranteed to be defined
        prediction = model.predict(df_input)[0]
        probs = model.predict_proba(df_input)[0]
        
        return {
            "prediction": "Toxic" if prediction == 1 else "Safe",
            "confidence": f"{(max(probs) * 100):.2f}%",
            "analysis": "Random Forest Classification"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference Error: {str(e)}")