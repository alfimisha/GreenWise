from flask import Flask, jsonify # type: ignore
import pandas as pd
import os

app = Flask(__name__)

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