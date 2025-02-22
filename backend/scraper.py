import requests
from bs4 import BeautifulSoup
import json

# Define user-agent to avoid bot detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Function to scrape Amazon product details
def scrape_amazon_product(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raise an error for bad responses

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract product details
        product_name = soup.find(id="productTitle").get_text(strip=True) if soup.find(id="productTitle") else "Unknown Product"
        product_detail = soup.find(id="feature-bullets").get_text(strip=True) if soup.find(id="feature-bullets") else "No details available"
        company = soup.find("a", {"id": "bylineInfo"}).get_text(strip=True) if soup.find("a", {"id": "bylineInfo"}) else "Unknown Company"
        country = "USA"  # Amazon doesn't provide this directly, so set a default or scrape differently
        industry = "Retail"

        # Data formatted for the Flask API
        data = {
            "year_of_reporting": "2024",
            "product_name": product_name,
            "country": country,
    
        }

        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the Amazon page: {e}")
        return None

# Function to send data to Flask backend
def send_to_backend(data):
    api_url = "http://127.0.0.1:5000/predict"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}  # Use form encoding

    try:
        response = requests.post(api_url, data=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        print(f"Carbon Emission Prediction: {result.get('prediction', 'N/A')}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to backend: {e}")


if __name__ == "__main__":
    # Example Amazon product URL (change it as needed)
    amazon_url = "https://www.amazon.com/dp/B08N5WRWNW"
    
    scraped_data = scrape_amazon_product(amazon_url)
    if scraped_data:
        send_to_backend(scraped_data)
