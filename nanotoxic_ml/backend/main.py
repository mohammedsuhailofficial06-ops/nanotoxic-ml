from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize the App
app = FastAPI()

# 2. Enable CORS (This allows your Flutter Web app to talk to this Python server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Change this to False
    allow_methods=["*"],
    allow_headers=["*"],
)
# 3. Load the AI Brain
model = joblib.load('nano_model.pkl')

# 4. Define the input structure
class NanoData(BaseModel):
    core_material: str
    size_nm: float
    zeta_potential_mv: float
    dosage_ug_ml: float

@app.get("/")
def read_root():
    return {"message": "NanoToxic-ML API is Online"}

@app.post("/predict")
def predict_tox(data: NanoData):
    # This prepares the data exactly like the training CSV
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
    prediction = model.predict(df_input)
    
    return {"prediction": "Toxic" if prediction[0] == 1 else "Safe"}