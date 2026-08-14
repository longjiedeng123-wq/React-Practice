import { useState } from 'react'; 
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

function App() { 
	const [groceries, setGroceries] = useState(["apple", "banana", "orange"]);
	const [inputValue, setInputValue] = useState("");

	function handleAdd() {
		setGroceries([...groceries, inputValue]);
		setInputValue("");
	}
	function handleDelete(itemToDelete) {
		setGroceries(groceries.filter(item => item != itemToDelete));
	}
	return ( 
		<div> 
			<input
				type = "text"
				value = {inputValue}
				onChange = {(e) => setInputValue(e.target.value)}
			/>
			<button onClick={handleAdd}>
				Add Item
			</button>
			<ul>
				{groceries.map(item => <GroceryItem key = {item} name = {item} triggerDelete = {handleDelete}/>)}
			</ul>
		</div> 
	); 
}

export default App;