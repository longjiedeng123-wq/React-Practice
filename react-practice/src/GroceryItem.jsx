import { useState } from 'react';
import './App.css';
function GroceryItem (props) {
    const [quantity, setQuantity] = useState(1); 
    
    return (
        <li className = "grocery-item">
            <span className = "item-name">
                {props.name} - Quantity : {quantity}
            </span>
            <button 
                className = "plus-btn"
                onClick = { () => setQuantity(quantity+1)}>
                    Plus
            </button>
            <button
                className = "delete-btn"
                onClick = {() => props.triggerDelete(props.name)}>
                    Delete
            </button>
        </li>
        
    );
}

export default GroceryItem;