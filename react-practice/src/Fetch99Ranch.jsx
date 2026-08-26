import { useState } from 'react';

function Fetch99Ranch({updateGroceries}) {
    const [isLoading, setIsLoading] = useState(false);
    const [ statusMessage, setStatusMessage ] = useState("");
    function triggerScraper() {
        setIsLoading(true);
        setStatusMessage("Starting AI background scraper...");

        fetch(import.meta.env.SCRAPING || "http://127.0.0.1:8000/api/prices")
        .then(response => response.json())
        .then(data => {
            setStatusMessage(data.message); 
        })
        .catch(error => {
            console.error("fetch error: ", error);
            setStatusMessage("Error starting scraper.");
        })
        .finally(() => {
            setIsLoading(false);
        });
    }

    function loadSavedProducts() {
        setIsLoading(true);
        setStatusMessage("Fetching database...");

        fetch(import.meta.env.DATABASE || "http://127.0.0.1:8000/api/products")
        .then(response => response.json())
        .then(responseData => {
            if (responseData.status === "success") {
                const validItems = responseData.data.filter(item => item.english_name != null);
                updateGroceries(validItems)
                setStatusMessage(`Loaded ${validItems.length} items from database!`)
            }
        }).catch(error => {
            console.error("fetch error: ", error);
            setStatusMessage("Error loading products.");
        }).finally(() => {
            setIsLoading(false);
        });
    }

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            <button 
                className="fetch-btn"
                disabled={isLoading}
                onClick={triggerScraper}>
                Trigger 99 Ranch AI Scrape
            </button>
            <button 
                className="fetch-btn"
                style={{ backgroundColor: "#3b82f6" }}
                disabled={isLoading}
                onClick={loadSavedProducts}>
                Load Saved Groceries
            </button>
            {statusMessage && <p style={{ fontSize: "14px", color: "#4b5563", margin: "0", textAlign: "center" }}>{statusMessage}</p>}
        </div>
    );
}

export default Fetch99Ranch;