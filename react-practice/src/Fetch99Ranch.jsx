import { useState } from 'react';

function Fetch99Ranch({updateGroceries}) {
    const [isLoading, setIsLoading] = useState(false);
    const [ statusMessage, setStatusMessage ] = useState("");
    const [userPrompt, setUserPrompt] = useState("");
    function triggerScraper() {
        setIsLoading(true);
        setStatusMessage("Starting AI background scraper...");

        fetch(import.meta.env.VITE_SCRAPING || "http://127.0.0.1:8000/api/prices")
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

        fetch(import.meta.env.VITE_DATABASE || "http://127.0.0.1:8000/api/products")
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

    async function askAgent(userQuestion){
        setIsLoading(true);
        setStatusMessage("Asking AI agent...");

        try {
            const response = await fetch(import.meta.env.VITE_AGENT || "http://127.0.0.1:8000/api/agent", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ user_prompt: userQuestion })
            });
            const data = await response.json();
            setStatusMessage(data.conversational_message);

            updateGroceries(data.ui_items);
        } catch (error) {
            console.error("fetch error: ", error);
            setStatusMessage("Error asking AI agent.");
        } finally {
            setIsLoading(false);
        }
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
            
            {/* 2. Add the Agent Input and Button */}
            <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
                <input 
                    type="text"
                    placeholder="Ask about healthy proteins or sales..."
                    value={userPrompt}
                    onChange={(e) => setUserPrompt(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && userPrompt && !isLoading) {
                            askAgent(userPrompt);
                        }
                    }}
                    style={{ flex: 1, padding: "8px", borderRadius: "4px", border: "1px solid #ccc" }}
                />
                <button 
                    className="fetch-btn"
                    style={{ backgroundColor: "#10b981" }}
                    disabled={isLoading || !userPrompt}
                    onClick={() => askAgent(userPrompt)}>
                    Ask AI Agent
                </button>
            </div>

            {statusMessage && <p style={{ fontSize: "14px", color: "#4b5563", margin: "0", textAlign: "center" }}>{statusMessage}</p>}
        </div>
    );
}

export default Fetch99Ranch;