import { useState, useEffect} from 'react';
import AddForm from './AddForm.jsx'; 
import GroceryItem from './GroceryItem.jsx';

function App() { 
	const [groceries, setGroceries] = useState(
		JSON.parse(localStorage.getItem("groceries-list")) || ["apple", "banana", "orange"]);
	
	
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
		fetch("https://www.themealdb.com/api/json/v1/1/random.php")
		.then(response => response.json())
		.then(data => {
			const recipeName = data.meals[0].strMeal;
			console.log(recipeName);
			setGroceries([...groceries, recipeName]);
		})
	}
	
	return ( 
		<div> 
			<AddForm triggerAdd = {handleAdd}/>
			<button onClick = {handleFetchRandom}>
				Suprise Me!
			</button>
			<ul>
				{groceries.map(item => <GroceryItem key = {item} name = {item} triggerDelete = {handleDelete}/>)}
			</ul>
		</div> 
	); 
}

export default App;