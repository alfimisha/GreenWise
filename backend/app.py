from flask import Flask, request, jsonify # type: ignore
import pandas as pd
import os
import pickle
import numpy as np
import joblib

with open("data/carbon_emissions_model.pkl", "rb") as f:
    model = joblib.load(f)

print("Model loaded successfully")

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json['features']  # Expecting {"features": [val1, val2, ...]}
        features = np.array(data).reshape(1, -1)  # Reshape for prediction
        prediction = model.predict(features)  # Get prediction
        return jsonify({"prediction": prediction.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)})

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

df = pd.read_csv('data/PublicTablesForCarbonCatalogueDataDescriptor_v30Oct2021(Product Level Data).csv', encoding = 'ISO-8859-1')

@app.route('/')
def home():
    return "Hello from GreenWise!"

@app.route('/carbon-data')
def get_carbon_data():
    data_records = df.to_dict(orient='records')
    return jsonify(data_records)

#error handling for 404
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Page not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)