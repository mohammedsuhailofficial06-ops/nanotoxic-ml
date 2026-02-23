from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

]import os
# This finds the absolute path to your model file
model_path = os.path.join(os.path.dirname(_file_), 'nano_model.pkl')
model = joblib.load(model_path)

class NanoData(BaseModel):
    core_material: str
    size_nm: float
    zeta_potential_mv: float
    dosage_ug_ml: float

@app.get("/")
def read_root():
    return {"message": "NanoToxic-ML API is Online", "version": "2.0-Research"}

@app.post("/predict")
def predict_tox(data: NanoData):
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
    
    # NEW: Get probability scores
    probs = model.predict_proba(df_input)[0] 
    prediction = model.predict(df_input)[0]
    
    confidence = max(probs) * 100
    result = "Toxic" if prediction == 1 else "Safe"
    
    return {
        "prediction": result,
        "confidence": f"{confidence:.2f}%",
        "methodology": "Random Forest Classifier (Nano-QSAR)"
    }