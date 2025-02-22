document.getElementById("scrapeButton").addEventListener("click", function () {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      const url = tabs[0].url;
  
      // Send message to background script
      chrome.runtime.sendMessage({ action: "scrape", url: url }, function (response) {
        if (response.success) {
          document.getElementById("status").innerText = "Scraping and prediction successful!";
        } else {
          document.getElementById("status").innerText = "Error: " + response.error;
        }
      });
    });
  });
  