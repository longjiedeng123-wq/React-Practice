import { useState } from 'react';

function Fetch99Ranch({updateGroceries}) {
    const [isLoading, setIsLoading] = useState(false);

    function fetchGroceryData () {
        setIsLoading(true);

        fetch("http://127.0.0.1:8000/api/prices")
        .then(response => {
            if(!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        }).then(responseData => {
            if (responseData.status === "success") {
            
                const validItems = responseData.data.filter(item => item.english_name != null);

                updateGroceries(validItems)
            }
        }).catch(error => {
            console.error("fetch error: ", error);
        }).finally(() => {
            setIsLoading(false);
        });
    }
    return (
        <div>
            <button 
                className="fetch-btn"
                disabled={isLoading}
                onClick={fetchGroceryData}>
                Get Current 99 ranch grocery data!
            </button>
        </div>
    )
}

export default Fetch99Ranch;