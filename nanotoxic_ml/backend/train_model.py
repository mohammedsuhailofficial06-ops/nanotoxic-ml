import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Load your data
df = pd.read_csv('../data/nanotox_data.csv')

# Use a LabelEncoder so the model remembers the 'materials'
le = LabelEncoder()
df['core_material'] = le.fit_transform(df['core_material'])

X = df[['core_material', 'size_nm', 'zeta_potential_mv', 'dosage_ug_ml']]
y = df['is_toxic']

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X, y)

# SAVE BOTH the model and the encoder
joblib.dump(model, 'nano_model.pkl')
joblib.dump(le, 'material_encoder.pkl')

print("✅ Model & Encoder saved for production!")