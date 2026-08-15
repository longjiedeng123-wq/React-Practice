import './App.css';
import { useState, useEffect} from 'react';
import AddForm from './AddForm.jsx'; 
import GroceryItem from './GroceryItem.jsx';

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
		"Task failed successfully: you found an item that already exists!"];
	useEffect(() => {
		localStorage.setItem("groceries-list", JSON.stringify(groceries));
	}, [groceries]);
	function handleAdd(inputValue, errorMessage) {
		const WHITELIST_REGEX = /[^a-zA-Z0-9 ]/g;
		if (WHITELIST_REGEX.test(inputValue)) {
      		inputValue = inputValue.replace(WHITELIST_REGEX, "");
    	}
		const cleanedInput = inputValue.trim().toLowerCase().replace(WHITELIST_REGEX, '').replace(/\s+/g, ' ');
		const isDuplicate = groceries.some(item => item.trim().toLowerCase() === cleanedInput);
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
	return ( 
		<div className = "app-container"> 
			<h1 className = "app-title">
				Grocery List
			</h1>
			<AddForm triggerAdd = {handleAdd}/>
			<button 
				className = "surprise-btn"
				onClick = {handleFetchRandom} 
				disabled={isLoading}>
					{isLoading ? "Fetching ..." : "Suprise Me!"}
			</button>
			<ul className = "grocery-list">
				{groceries.map(item => <GroceryItem key = {item} name = {item} triggerDelete = {handleDelete}/>)}
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