import os
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# 1. UNIVERSAL CORS (Allows Vercel to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. DYNAMIC MODEL SEARCH
# This searches both the current folder AND the subfolder for nano_model.pkl
model = None
possible_paths = [
    os.path.join(os.getcwd(), "nano_model.pkl"),
    os.path.join(os.getcwd(), "nanotoxic_ml", "backend", "nano_model.pkl"),
    os.path.join(os.path.dirname(__file__), "nano_model.pkl")
]

for path in possible_paths:
    if os.path.exists(path):
        try:
            model = joblib.load(path)
            print(f"✅ SUCCESS: Loaded model from {path}")
            break
        except Exception as e:
            print(f"❌ Error loading {path}: {e}")

class NanoData(BaseModel):
    core_material: str
    size_nm: float
    zeta_potential_mv: float
    dosage_ug_ml: float

@app.post("/predict")
async def predict_tox(data: NanoData):
    if model is None:
        raise HTTPException(status_code=500, detail="Model file not found on server paths.")

    try:
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
        df = pd.DataFrame(input_dict)
        prediction = model.predict(df)[0]
        probs = model.predict_proba(df)[0]
        
        return {
            "prediction": "Toxic" if prediction == 1 else "Safe",
            "confidence": f"{(max(probs) * 100):.2f}%"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))