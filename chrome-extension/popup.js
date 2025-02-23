document.getElementById("scrapeButton").addEventListener("click", function () {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      const url = tabs[0].url;

      // Send message to background script
      chrome.runtime.sendMessage({ action: "scrape", url: url }, function (response) {
          console.log("Popup Response:", response); // Debugging log

          if (response.success) {
              document.getElementById("status").innerText =
                  `Loaded data successfully! Product: ${response.product_name}

                  
                  
                  Carbon emissions: ${response.prediction}`;
          } else {
              document.getElementById("status").innerText = "Error: " + response.error;
          }
      });
  });
});
