from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import joblib
import pandas as pd
import os

app = FastAPI()

# 1. THE "FORCE-BYPASS" MIDDLEWARE
# This manually injects CORS headers into EVERY response, even if the app crashes.
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    if request.method == "OPTIONS":
        response = JSONResponse(content="OK")
    else:
        response = await call_next(request)
    
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE, PUT"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    return response

# 2. STANDARD CORS (Safety Backup)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. ROBUST MODEL LOADING
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'nano_model.pkl')

try:
    # Ensure nano_model.pkl is in the same folder as this main.py
    model = joblib.load(model_path)
    print("✅ Nano-QSAR Model loaded successfully")
except Exception as e:
    print(f"❌ Model Error: {e}")
    model = None

class NanoData(BaseModel):
    core_material: str
    size_nm: float
    zeta_potential_mv: float
    dosage_ug_ml: float

@app.get("/")
def read_root():
    return {"status": "Online", "system": "NanoToxic-ML Predictive Portal"}

@app.post("/predict")
async def predict_tox(data: NanoData):
    if model is None:
        return JSONResponse(
            status_code=500, 
            content={"error": "Model not loaded on server"},
            headers={"Access-Control-Allow-Origin": "*"}
        )

    try:
        # Prepare input for Random Forest
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
        probs = model.predict_proba(df_input)[0] 
        prediction = model.predict(df_input)[0]
        
        return JSONResponse(
            content={
                "prediction": "Toxic" if prediction == 1 else "Safe",
                "confidence": f"{(max(probs) * 100):.2f}%",
                "methodology": "Random Forest Classifier"
            },
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"error": str(e)},
            headers={"Access-Control-Allow-Origin": "*"}
        )

if _name_ == "_main_":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)