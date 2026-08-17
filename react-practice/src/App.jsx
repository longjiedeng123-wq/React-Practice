import './App.css';
import { useState, useEffect} from 'react';
import AddForm from './AddForm.jsx'; 
import GroceryItem from './GroceryItem.jsx';
import Fetch99Ranch from './Fetch99Ranch.jsx';

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
	function handleAdd(inputValue, errorMessage) {
		const WHITELIST_REGEX = /[^a-zA-Z0-9 ]/g;
		if (WHITELIST_REGEX.test(inputValue)) {
      		inputValue = inputValue.replace(WHITELIST_REGEX, "");
    	}
		const cleanedInput = inputValue.trim().toLowerCase().replace(WHITELIST_REGEX, '').replace(/\s+/g, ' ');
		// Update duplicate check to safely handle both strings and objects
        const isDuplicate = groceries.some(item => {
            // If it's an object, grab the english_name. Otherwise, just use the string.
            const itemName = typeof item === 'object' && item !== null ? item.english_name : item;
            
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
		setGroceries([...groceries, ...items]);
	}
	function removeAllItem() {
		setGroceries([]);
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
                
                <Fetch99Ranch updateGroceries={handleFetchedItems} />
				<button 
					className="remove-all-btn"
					onClick={removeAllItem}
				>
					remove all
				</button>
            </div>
			
			<ul className="grocery-list">
                {groceries.map((item, index) => {
                    const isObject = typeof item === 'object' && item !== null;
                    const itemName = isObject ? item.english_name : item;
                    
                    return (
                        <GroceryItem 
                            key={`${index}-${itemName}`} 
                            name={itemName} 
                            data={isObject ? item : null} 
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
		</div> 
	); 
}

export default App;