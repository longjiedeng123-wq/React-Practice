import './App.css';
import { useState, useEffect} from 'react';
import AddForm from './AddForm.jsx'; 
import GroceryItem from './GroceryItem.jsx';

function App() { 
	const [groceries, setGroceries] = useState(
		JSON.parse(localStorage.getItem("groceries-list")) || ["apple", "banana", "orange"]);
	const [isLoading, setIsLoading] = useState(false);
	
	useEffect(() => {
		localStorage.setItem("groceries-list", JSON.stringify(groceries));
	}, [groceries]);
	function handleAdd(inputValue) {
		if (groceries.includes(inputValue)) {
			alert("Item already exists in the list!");
			return;
		}
		setGroceries([...groceries, inputValue]);
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
		window.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "-blank");
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