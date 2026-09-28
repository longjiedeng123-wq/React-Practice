import { useState } from 'react';

function AiAgent({ updateGroceries }) {
    const [userPrompt, setUserPrompt] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [statusMessage, setStatusMessage] = useState("");

    
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
        <div style={{ display: "flex", gap: "10px", marginTop: "20px", flexDirection: "column" }}>
            <div style={{ display: "flex", gap: "10px" }}>
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
                    style={{ backgroundColor: "#10b981", color: "white" }}
                    disabled={isLoading || !userPrompt}
                    onClick={() => askAgent(userPrompt)}>
                    Ask AI Agent
                </button>
            </div>
            {statusMessage && <p style={{ fontSize: "14px", color: "#4b5563", margin: "0", textAlign: "center" }}>{statusMessage}</p>}
        </div>
    );
}

export default AiAgent;