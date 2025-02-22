import pandas as pd
import joblib
from flask import Flask, render_template, request

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
    if predicted_emission < 0.000001:
        predicted_emission_text = "less than 1 mg"
    else:
        predicted_emission_text = f"{predicted_emission:.6f} kg"

    return render_template('index.html', prediction=predicted_emission_text)

if __name__ == '__main__':
    app.run(debug=True)
