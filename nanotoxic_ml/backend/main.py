from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import os

# Initialize the app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 2. ROBUST MODEL LOADING
# Using absolute paths to ensure Render finds your 'nano_model.pkl'.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'nano_model.pkl')

try:
    # Ensure nano_model.pkl is in the same folder as this main.py in GitHub
    model = joblib.load(model_path)
    print("✅ Nano-QSAR Model loaded successfully")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Could not load model file at {model_path}. Error: {e}")
    model = None

# 3. DATA SCHEMA (Matches your Flutter UI)
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
        "author": "Mohammed Suhail A"
    }

@app.post("/predict")
async def predict_tox(data: NanoData):
    # Safety check: If model failed to load, don't let the server crash
    if model is None:
        raise HTTPException(status_code=500, detail="Machine Learning model is not loaded on the server.")

    try:
        # Prepare the input for your Random Forest model
        # The keys must match the feature names used during your training
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
        
        # 4. SCIENTIFIC INFERENCE
        # We use predict_proba to get the statistical confidence for the research score
        probs = model.predict_proba(df_input)[0] 
        prediction = model.predict(df_input)[0]
        
        confidence = max(probs) * 100
        result = "Toxic" if prediction == 1 else "Safe"
        
        return {
            "prediction": result,
            "confidence": f"{confidence:.2f}%",
            "methodology": "Random Forest Classifier (Nano-QSAR)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference Error: {str(e)}")

if _name_ == "_main_":
    import uvicorn
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)