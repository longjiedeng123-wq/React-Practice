import { useState, useEffect } from 'react';

function ScraperDashboard({updateGroceries, loadSavedProducts}) {
    const [isLoading, setIsLoading] = useState(false);
    const [ statusMessage, setStatusMessage ] = useState("");
    const [liveUrl, setLiveUrl] = useState(null);
    const [isScrapingJobActive, setIsScrapingJobActive] = useState(false);
    useEffect(() => {
        let intervalId;
        
        // We now poll based on the job being active, not the iframe existing
        if (isScrapingJobActive) {
            intervalId = setInterval(() => {
                const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
                fetch(`${baseUrl}/api/status`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === "processing") {
                        // Phase 2: Browser is done, AI is working
                        setLiveUrl(null); // Drop the glass wall / iframe
                        setStatusMessage("Browser closed. Gemini AI is extracting prices...");
                    } else if (data.status === "idle") {
                        // Phase 3: Everything is finished
                        setLiveUrl(null);
                        setIsScrapingJobActive(false); // Stop the polling loop
                        setStatusMessage("Scrape complete! Loading new items...");
                        loadSavedProducts();
                    }
                })
                .catch(err => console.error("Polling error:", err));
            }, 3000); 
        }

        return () => {
            if (intervalId) clearInterval(intervalId);
        };
    }, [isScrapingJobActive]); // Depend on the job state, not liveUrl
    function triggerScraper() {
        setIsLoading(true);
        setIsScrapingJobActive(true);
        setStatusMessage("Starting AI background scraper...");
        setLiveUrl(null);
        const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
        fetch(`${baseUrl}/api/prices`)
        .then(response => response.json())
        .then(data => {
            setStatusMessage(data.message); 
            if (data.iframe_url) {
                setLiveUrl(data.iframe_url); // <-- Save the cloud URL
            }
        })
        .catch(error => {
            console.error("fetch error: ", error);
            setStatusMessage("Error starting scraper.");
        })
        .finally(() => {
            setIsLoading(false);
        });
    }

    function triggerAlbertsonsScraper() {
        setIsLoading(true);
        setStatusMessage("Starting Albertsons background scraper...");
        setIsScrapingJobActive(true);
        setLiveUrl(null);
        const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
        fetch(`${baseUrl}/api/scrape-albertsons`)
        .then(response => response.json())
        .then(data => {
            setStatusMessage(data.message); 
            if (data.iframe_url) {
                setLiveUrl(data.iframe_url); // <-- Capture the Browserbase cloud session URL
            }
        })
        .catch(error => {
            console.error("fetch error: ", error);
            setStatusMessage("Error starting Albertsons scraper.");
        })
        .finally(() => {
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
                style={{ backgroundColor: "#ef4444" }}
                disabled={isLoading}
                onClick={triggerAlbertsonsScraper}>
                Trigger Albertsons Scrape
            </button>
            
            
            

            {statusMessage && <p style={{ fontSize: "14px", color: "#4b5563", margin: "0", textAlign: "center" }}>{statusMessage}</p>}
            {liveUrl && (
                <iframe 
                    src={liveUrl} 
                    style={{ 
                        width: "100%", 
                        height: "650px", // <-- Increased height
                        border: "1px solid #ccc", 
                        borderRadius: "8px", 
                        marginTop: "15px",
                        pointerEvents: "none" // <-- THE GLASS WALL
                    }}
                    title="Live Browser Session"
                />
            )}
        </div>
    );
}

export default ScraperDashboard;