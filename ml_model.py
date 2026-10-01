# ml_model.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle
import os

def train_and_save_model():
    # Training data
    data = {
        'magnitude': [5.2, 7.1, 3.5, 6.8, 4.2, 8.0, 6.0],
        'depth': [10, 35, 5, 20, 15, 50, 25],
        'population_density': [500, 1200, 200, 800, 300, 1500, 900],
        'rainfall': [50, 10, 200, 30, 150, 5, 120],
        'type': ['Earthquake', 'Earthquake', 'Flood', 'Earthquake', 'Flood', 'Earthquake', 'Flood']
    }
    df = pd.DataFrame(data)

    X = df.drop('type', axis=1)
    y = df['type']

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y_encoded)

    with open('disaster_model.pkl', 'wb') as f:
        pickle.dump((model, le), f)
    
    print("✅ ML Model trained and saved successfully!")
    return model, le

def load_model():
    if os.path.exists('disaster_model.pkl'):
        with open('disaster_model.pkl', 'rb') as f:
            return pickle.load(f)
    else:
        return train_and_save_model()

# Auto train when imported
model, label_encoder = load_model()