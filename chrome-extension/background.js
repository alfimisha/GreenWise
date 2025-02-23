chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.action === "scrape") {
        const url = request.url; // Get the URL from the message

        // Perform scraping here (Beautiful Soup equivalent in JavaScript)
        if (sender.tab && sender.tab.id) {
            chrome.scripting.executeScript({
                target: { tabId: sender.tab.id }, // Target the tab that sent the message
                func: scrapeProductData // Define the function to be injected
            }, (injectionResults) => {
                if (chrome.runtime.lastError) {
                    console.error("Content script injection error:", chrome.runtime.lastError);
                    sendResponse({ success: false, error: chrome.runtime.lastError.message });
                    return;
                }

                const scrapedData = injectionResults[0].result; // Get the result from the injection
                console.log("Scraped Data:", scrapedData);

                if (scrapedData) {
                    // Send the scraped data to the backend for prediction
                    sendToBackend(scrapedData, function (result) {
                        if (result.error) {
                            sendResponse({ success: false, error: result.error });
                        } else {
                            sendResponse({ success: true, prediction: result.prediction });
                            // Update the frontend with the prediction
                            updateFrontendWithPrediction(result.prediction);
                        }
                    });
                } else {
                    sendResponse({ success: false, error: "Failed to scrape product details." });
                }
            });
        } else {
            // Fallback if sender.tab.id is not available
            chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
                if (tabs[0] && tabs[0].id) {
                    chrome.scripting.executeScript({
                        target: { tabId: tabs[0].id }, // Fallback to active tab
                        func: scrapeProductData
                    }, (injectionResults) => {
                        if (chrome.runtime.lastError) {
                            console.error("Content script injection error:", chrome.runtime.lastError);
                            sendResponse({ success: false, error: chrome.runtime.lastError.message });
                            return;
                        }

                        const scrapedData = injectionResults[0].result; // Get the result from the injection
                        console.log("Scraped Data:", scrapedData);

                        if (scrapedData) {
                            sendToBackend(scrapedData, function (result) {
                                if (result.error) {
                                    sendResponse({ success: false, error: result.error });
                                } else {
                                    sendResponse({ success: true, prediction: result.prediction });
                                    // Update the frontend with the prediction
                                    updateFrontendWithPrediction(result.prediction);
                                }
                            });
                        } else {
                            sendResponse({ success: false, error: "Failed to scrape product details." });
                        }
                    });
                } else {
                    sendResponse({ success: false, error: "No active tab found." });
                }
            });
        }

        return true; // Keep the message channel open for async response
    }
});

// Function to scrape data from the page
function scrapeProductData() {
    const productName = document.querySelector("#productTitle")?.innerText?.trim() || "Unknown Product";
    // Improved country extraction:
    let country = "USA"; // Default value

    const shipsFromElement = document.querySelector("#merchant-info");

    if (shipsFromElement) {
        const shipsFromText = shipsFromElement.innerText.trim();

        // 1. Improved Regex (Handles many variations)
        const countryMatch = shipsFromText.match(/(?:ships from and sold by|Dispatched from and sold by|Sold by)\s+(.+?)(?:\s+from|\s+in|\s+at|\s+on|\s+for|\s+by|\s+and|\s*$)/i);

        if (countryMatch && countryMatch[1]) {
            country = countryMatch[1].trim();

            // 2. Robust Cleaning (Handles even more variations)
            country = country.replace(/\s+and others/i, "");
            country = country.replace(/\s+from.*$/i, "");
            country = country.replace(/\s+in.*$/i, "");
            country = country.replace(/\s+at.*$/i, "");
            country = country.replace(/\s+on.*$/i, "");
            country = country.replace(/\s+for.*$/i, "");
            country = country.replace(/\s+by.*$/i, "");
            country = country.replace(/\s+\(.*?\)|\s+\[.*?\]/g, ""); // Remove parentheses and brackets
            country = country.replace(/\s+Ltd.*$/i, ""); // Remove "Ltd" and similar
            country = country.replace(/\s+Inc.*$/i, ""); // Remove "Inc" and similar
            country = country.replace(/\s+Corp.*$/i, ""); // Remove "Corp" and similar
            country = country.replace(/\s+LLC.*$/i, ""); // Remove "LLC" and similar

            country = country.trim();

        } else {
            // 3. Fallback Strategies (If still needed) - Adapt as necessary
            // ... (You can add more fallbacks here if you find other variations)
        }
    }

    return {
        year_of_reporting: "2024",
        product_name: productName,
        country: country
    };
}

// Function to send data to Flask backend
function sendToBackend(data, callback) {
    fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) { // Check for HTTP errors
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json(); // Parse JSON response
    })
    .then(result => {
        callback(result); // Call the callback with the backend response
    })
    .catch(error => {
        callback({ error: error.message }); // Return error if the fetch fails
    });
}

// Function to update the frontend with prediction
function updateFrontendWithPrediction(prediction) {
    // Update the content script or popup with the prediction
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        chrome.scripting.executeScript({
            target: { tabId: tabs[0].id },
            func: displayPrediction,
            args: [prediction]
        });
    });
}

// Function to display prediction on the page
function displayPrediction(prediction) {
    // Find a location to display the prediction on the page
    const predictionElement = document.createElement("div");
    predictionElement.textContent = `Predicted Carbon Emission: ${prediction} kg CO2e`;
    predictionElement.style.position = "fixed"; // Fix the position at the top of the page
    predictionElement.style.top = "20px";
    predictionElement.style.left = "20px";
    predictionElement.style.backgroundColor = "rgba(0, 0, 0, 0.7)";
    predictionElement.style.color = "white";
    predictionElement.style.padding = "10px";
    predictionElement.style.borderRadius = "5px";
    document.body.appendChild(predictionElement); // Append it to the body (or wherever you want)
}
