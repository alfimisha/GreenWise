import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def scrape_amazon_product(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        product_name = soup.find(id="productTitle")
        product_name = product_name.get_text(strip=True) if product_name else "Unknown Product"  # Correct Python syntax

        # product_detail = soup.find(id="feature-bullets")  # Not used in your Flask API
        # product_detail = product_detail.get_text(strip=True) if product_detail else "No details available"

        company = soup.find("a", {"id": "bylineInfo"})
        company = company.get_text(strip=True) if company else "Unknown Company"  # Correct Python syntax

        country = "USA"

        data = {
            "year_of_reporting": "2024",
            "product_name": product_name,
            "country": country,
        }

        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the Amazon page: {e}")
        return None
    except AttributeError as e:  # Handle cases where elements are not found
        print(f"Error parsing page (element not found): {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def send_to_backend(data):
    api_url = "http://127.0.0.1:5000/predict"
    headers = {"Content-Type": "application/json"}  # Correct content type: JSON

    try:
        response = requests.post(api_url, json=data, headers=headers)  # Send JSON data
        response.raise_for_status()  # Check for HTTP errors
        result = response.json()  # Parse the JSON response
        print(f"Carbon Emission Prediction: {result.get('prediction', 'N/A')}")
        return result  # Return the result (including success/error)

    except requests.exceptions.RequestException as e:
        print(f"Error sending data to backend: {e}")
        return {"error": str(e), "success": False}  # Return error as a dictionary
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return {"error": str(e), "success": False} # Return error as dictionary

if __name__ == "__main__":
    amazon_url = "https://www.amazon.com/dp/B08N5WRWNW"  # Or any other URL

    scraped_data = scrape_amazon_product(amazon_url)
    if scraped_data:
        result = send_to_backend(scraped_data) # Capture the return value
        print("Full Result from Backend:", result) # Print the full result
        if result and result.get("success"): # Check if request was successful
            print("Prediction:", result.get("prediction"))
        else:
            print("Error:", result.get("error"))