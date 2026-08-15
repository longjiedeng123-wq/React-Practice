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

export default GroceryItem;