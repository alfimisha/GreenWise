import pandas as pd
import joblib
from flask import Flask, render_template, request, jsonify
from rapidfuzz import process

# Load model, scaler, and columns
model = joblib.load("data/carbon_emissions_model.pkl")
scaler = joblib.load("data/scaler.pkl")
model_columns = joblib.load("data/model_columns.pkl")

# Load dataset for product name correction
df = pd.read_csv("data/PublicTablesForCarbonCatalogueDataDescriptor_v30Oct2021(Product Level Data).csv", encoding="ISO-8859-1")
dataset_product_names = df["Product name (and functional unit)"].dropna().unique().tolist()

# Function to correct product name using fuzzy matching
def get_closest_product_name(scraped_name):
    match, score, _ = process.extractOne(scraped_name, dataset_product_names)
    return match if score > 80 else scraped_name  # Only replace if confidence is high

app = Flask(__name__)

# Route to render the input form (index.html)
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle form submission and make prediction
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Ensure request contains JSON data
        if not request.is_json:
            return jsonify({"error": "Request must be JSON", "success": False}), 415

        # Get JSON data
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Invalid JSON data", "success": False}), 400

        # Check for missing fields
        required_fields = ["year_of_reporting", "product_name", "country"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "success": False
            }), 400

        # Extract and process data
        year_of_reporting = int(data["year_of_reporting"])
        product_name = data["product_name"]
        country = data["country"]

        # Correct product name before prediction
        corrected_product_name = get_closest_product_name(product_name)

        # Data processing
        example_data = {
            "Year of reporting": [year_of_reporting],
            "Product name (and functional unit)": [corrected_product_name],
            "Country (where company is incorporated)": [country]
        }
        example_df = pd.DataFrame(example_data)

        # One-hot encode and standardize the data
        example_encoded = pd.get_dummies(example_df)
        example_encoded = example_encoded.reindex(columns=model_columns, fill_value=0)
        example_scaled = pd.DataFrame(scaler.transform(example_encoded), columns=example_encoded.columns)

        # Make prediction
        predicted_emission = model.predict(example_scaled)[0]
        

        return jsonify({
            "prediction": float(predicted_emission),
            "corrected_product_name": corrected_product_name,
            "success": True,
            "product_name": product_name
        })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

if __name__ == '__main__':
    app.run(debug=True)
