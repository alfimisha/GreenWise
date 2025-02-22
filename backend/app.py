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

    return render_template('index.html', prediction=predicted_emission)

if __name__ == '__main__':
    app.run(debug=True)