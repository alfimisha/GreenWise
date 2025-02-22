import pandas as pd
import joblib 
from flask import Flask, render_template, request, jsonify

# Load model, scaler, and columns
model = joblib.load("data/carbon_emissions_model.pkl")
scaler = joblib.load("data/scaler.pkl")
model_columns = joblib.load("data/model_columns.pkl")
print("Model loaded successfully")

app = Flask(__name__)

df = pd.read_csv('data/PublicTablesForCarbonCatalogueDataDescriptor_v30Oct2021(Product Level Data).csv', encoding = 'ISO-8859-1')
print("Columns in CSV:", df.columns)

# Route to render the input form (index.html)
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle form submission and make prediction
@app.route('/predict', methods=['POST'])
def predict():
    try: 
        # Get form data
        year_of_reporting = request.form['year_of_reporting']
        product_name = request.form['product_name']
        product_detail = request.form['product_detail']
        company = request.form['company']
        country = request.form['country']
        industry = request.form['industry']

        # Convert to DataFrame
        example_data = {
            "Year of reporting": [year_of_reporting],
            "Product name (and functional unit)": [product_name],
            "Product detail": [product_detail],
            "Company": [company],
            "Country (where company is incorporated)": [country],
            "Company's GICS Industry": [industry]
        }
        example_df = pd.DataFrame(example_data)

        # One-hot encode categorical features
        example_encoded = pd.get_dummies(example_df)

        # Ensure the new data matches the columns from training data
        example_encoded = example_encoded.reindex(columns=model_columns, fill_value=0)

        # Standardize using the same scaler
        example_scaled = pd.DataFrame(scaler.transform(example_encoded), columns=example_encoded.columns)

        # Make prediction
        predicted_emission = model.predict(example_scaled)[0]

    # Format predicted_emission_text
    if abs(predicted_emission) < 0.000001:
        predicted_emission_text = "less than 1 mg"
    else:
        predicted_emission_text = f"{predicted_emission:.6f} kg"

        #return render_template('index.html', prediction=predicted_emission_text)

# GET endpoint to retrieve the entire carbon data from the CSV
@app.route('/carbon-data')
def get_carbon_data():
    data_records = df.to_dict(orient='records')
    return jsonify(data_records)


# GET endpoint to retrieve a specific product's carbon emission
@app.route('/product-carbon', methods=['GET'])
def product_carbon():
    product_name = request.args.get('name')
    if not product_name:
        return jsonify({
            'error': 'Please provide a product name using the "name" query parameter.'
        }), 400

    # Filter data using the column "Product name (and functional unit)"
    filtered = df[df['Product name (and functional unit)'].str.contains(product_name, case=False, na=False)]
    if filtered.empty:
        return jsonify({
            'error': f'No product found matching "{product_name}"'
        }), 404

    data_records = filtered.to_dict(orient='records')
    return jsonify(data_records)
        return jsonify({"prediction": predicted_emission})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)