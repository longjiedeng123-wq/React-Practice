import './App.css';
import AiAgent from './AiAgent.jsx';
import AddForm from './AddForm.jsx'; 
import GroceryItem from './GroceryItem.jsx';
import ScraperDashboard from './ScraperDashboard.jsx';

import { useState, useEffect} from 'react';

function App() { 
	const [groceries, setGroceries] = useState(
		JSON.parse(localStorage.getItem("groceries-list")) || ["apple", "banana", "orange"]);

	const [isLoading, setIsLoading] = useState(false);

	const errorMessageBank = [
		"Space doesn't work anymore, no~", 
		"Nice try, but you can't add duplicates!",
		"Unfortunately, you have to find a better way to add duplicates",
		"How dare you try to add duplicates, you should be ashamed of yourself",
		"Don't do that, the system will be unhappy",
		"HaHaHa, this system is duplicate-proof, I know~I know~",
		"Error 404: Originality not found. That item is already here!",
		"Bro, you already typed this. Are we stuck in a time loop?",
		"The grocery list gods reject your duplicate offering.",
		"Deja vu! I just saw this item a second ago.",
		"Task failed successfully: you found an item that already exists!"
	];

	useEffect(() => {
		localStorage.setItem("groceries-list", JSON.stringify(groceries));
	}, [groceries]);
	function isValidObject(item) {
		return typeof item === 'object' && item !== null;
	}
	function extractItemName(item) {
		return isValidObject(item) ? (item.english_name || item.name) : item;
	}
	function handleAdd(inputValue, errorMessage) {
		const WHITELIST_REGEX = /[^a-zA-Z0-9 ]/g;
		if (WHITELIST_REGEX.test(inputValue)) {
      		inputValue = inputValue.replace(WHITELIST_REGEX, "");
    	}
		const cleanedInput = inputValue.trim().toLowerCase().replace(WHITELIST_REGEX, '').replace(/\s+/g, ' ');
		
        const isDuplicate = groceries.some(item => {
            
            const itemName = extractItemName(item);
            
            return itemName.trim().toLowerCase() === cleanedInput;
        });
		if (isDuplicate) {
			let randomErrorMessage;
			do {
				randomErrorMessage = errorMessageBank[Math.floor(Math.random() * errorMessageBank.length)];
			} while (randomErrorMessage === errorMessage)
			return randomErrorMessage;
		}
		setGroceries([...groceries, cleanedInput]);
		return "";
	}

	function handleDelete(itemToDelete) {
		setGroceries(groceries.filter(item => item !== itemToDelete));
	}

	function handleFetchRandom() {
		setIsLoading(true);
		fetch("https://www.themealdb.com/api/json/v1/1/random.php")
		.then(response => response.json())
		.then(data => {
			const recipeName = data.meals[0].strMeal;
			console.log(recipeName);
			setGroceries([...groceries, recipeName]);
		})
		.catch(error => {
			alert("Failed to fetch random recipe. Please try again later.");
			console.error("Fetch error:",error);
		})
		.finally(() => setIsLoading(false));
	}
	function triggerSecret() {
		window.open("https://www.youtube.com/watch?v=G8iEMVr7GFg", "-blank");
	}
	function handleFetchedItems(items) {
		setGroceries(prevGroceries => {
        const deduplicatedItems = items.filter(newItem => {
            const newItemName = extractItemName(newItem).trim().toLowerCase();
            
            const isDuplicate = prevGroceries.some(existingItem => {
                return extractItemName(existingItem).trim().toLowerCase() === newItemName;
            });
            
            return !isDuplicate;
        });

        return [...prevGroceries, ...deduplicatedItems];
    	});
	}
	
	function removeAllItem() {
		setGroceries([]);
	}
	function zipCodeSearch() {
		fetch("http://127.0.0.1:8000/api/test");
	}
	function loadSavedProducts() {
        setIsLoading(true);
        // Removed setStatusMessage because App.jsx doesn't have that state

        fetch(import.meta.env.VITE_DATABASE || "http://127.0.0.1:8000/api/products")
        .then(response => response.json())
        .then(responseData => {
            if (responseData.status === "success") {
                const validItems = responseData.data.filter(item => item.english_name != null);
                console.log("Database Payload:", validItems);
                
                // Changed from updateGroceries to the actual local function name:
                handleFetchedItems(validItems); 
            }
        }).catch(error => {
            console.error("fetch error: ", error);
        }).finally(() => {
            setIsLoading(false);
        });
    }


	return ( 
		<div className = "app-container"> 
			<h1 className = "app-title">
				Grocery List
			</h1>
			<AddForm triggerAdd = {handleAdd}/>
			<div className="button-group">
                <button 
                    className="surprise-btn"
                    onClick={handleFetchRandom} 
                    disabled={isLoading}>
                        {isLoading ? "Fetching ..." : "Surprise Me!"}
                </button>
                
                
				<button 
					className="remove-all-btn"
					onClick={removeAllItem}
				>
					remove all
				</button>
            </div>
			<div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
                <button 
                    className="load-btn"
                    style={{ backgroundColor: "#3b82f6", color: "white", padding: "8px", borderRadius: "4px" }}
                    onClick={loadSavedProducts}
                >
                    Load Saved Groceries
                </button>
            </div>

            {/* Pass loadSavedProducts so the dashboard can trigger it when the cloud job finishes */}
            <ScraperDashboard 
                updateGroceries={handleFetchedItems} 
                loadSavedProducts={loadSavedProducts} 
            />
			<AiAgent updateGroceries={handleFetchedItems} />
			<ul className="grocery-list">
                {groceries.map((item, index) => {
                    const itemName = extractItemName(item);
                    
                    return (
                        <GroceryItem 
                            key={`${index}-${itemName}`} 
                            name={itemName} 
                            data={isValidObject(item) ? item : null} 
                            rawItem={item} 
                            triggerDelete={handleDelete}
                        />
                    );
                })}
            </ul>
			<button 
				className = 'secret-btn'
				onClick ={triggerSecret}
			>
				Don't click me!
			</button>
			<button
				onClick={zipCodeSearch}
			>test zip code search</button>
		</div> 
	); 
}

export default App;