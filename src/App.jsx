import { useState, useEffect} from 'react'; 
function GroceryItem (props) {
	const [quantity, setQuantity] = useState(1); 
	
	return (
		<li className = "fruit-item">
			{props.name} - Quantity : {quantity}
			<button onClick = { () => setQuantity(quantity+1)}>
				Add
			</button>
			<button onClick = {() => props.triggerDelete(props.name)}>
				Delete
			</button>
		</li>
		
	);
}
function AddForm(props) {
	const [inputValue, setInputValue] = useState("");
	function handleSubmit() {
		if (inputValue.trim() === "") return;
		props.triggerAdd(inputValue);
		setInputValue("");
	}
	return (
		<div>
			<input
				type = "text"
				value = {inputValue}
				onChange = {(e) => setInputValue(e.target.value)}
			/>
			<button onClick = {handleSubmit}>
				Add item
			</button>
		</div>
	);
}
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

	return ( 
		<div> 
			<AddForm triggerAdd = {handleAdd}/>
			<ul>
				{groceries.map(item => <GroceryItem key = {item} name = {item} triggerDelete = {handleDelete}/>)}
			</ul>
		</div> 
	); 
}

export default App;