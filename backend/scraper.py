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

        country_item = None
        country_items = soup.find_all("li", class_="a-list-item")  # Find all items with the a-list-item class
        
        for item in country_items:
            if "country" in item.get_text(strip=True).lower():  # Adjust logic to match the country info
                country_item = item
                break
        
        # Ensure that country_item was found
        if country_item:
            country = country_item.get_text(strip=True)
        else:
            country = "Unknown Country"  # Default if no country info found

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
    headers = {"Content-Type": "application/json"}  # Ensure JSON format

    try:
        response = requests.post(api_url, json=data, headers=headers)  # Use `json=` instead of `data=`
        response.raise_for_status()  # Raise an error for HTTP issues
        result = response.json()  # Parse the JSON response
        print(f"Carbon Emission Prediction: {result.get('prediction', 'N/A')}")
        return result  

    except requests.exceptions.RequestException as e:
        print(f"Error sending data to backend: {e}")
        return {"error": str(e), "success": False}

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