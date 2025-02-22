import pandas as pd
import joblib
from flask import Flask, render_template, request, jsonify

# Load model, scaler, and columns
model = joblib.load("data/carbon_emissions_model.pkl")
scaler = joblib.load("data/scaler.pkl")
model_columns = joblib.load("data/model_columns.pkl")

app = Flask(__name__)

# Route to render the input form (index.html)
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle form submission and make prediction
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract data from request
        year_of_reporting = int(data['year_of_reporting'])
        product_name = data['product_name']
        country = data['country']

        # Convert to DataFrame and make prediction
        example_data = {
            "Year of reporting": [year_of_reporting],
            "Product name (and functional unit)": [product_name],
            "Country (where company is incorporated)": [country]
        }
        example_df = pd.DataFrame(example_data)

        # One-hot encode and standardize the data
        example_encoded = pd.get_dummies(example_df)
        example_encoded = example_encoded.reindex(columns=model_columns, fill_value=0)
        example_scaled = pd.DataFrame(scaler.transform(example_encoded), columns=example_encoded.columns)

        # Make prediction
        predicted_emission = model.predict(example_scaled)[0]

        return jsonify({"prediction": predicted_emission, "success": True})

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500
if __name__ == '__main__':
    app.run(debug=True)
