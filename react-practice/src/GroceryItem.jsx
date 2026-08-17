import { useState } from 'react';
import './App.css';
function GroceryItem (props) {
    const [quantity, setQuantity] = useState(1); 
    const hasData = props.data !== null && props.data !== undefined;
    
    return (
        <li className="grocery-item">
            
            <div className="item-main">
                <span className="item-name">
                    {props.name} 
                    {hasData && props.data.chinese_name ? ` (${props.data.chinese_name})` : ""} 
                    <span className="item-quantity">
                        - Qty: {quantity}
                    </span>
                </span>
                
                {/* Render Rich Pricing Data conditionally */}
                {hasData && (
                    <div className="item-details">
                        
                        {/* Display Sale Price or Original Price */}
                        {props.data.discount_price ? (
                            <span>
                                <span className="price-sale">Sale: ${props.data.discount_price}</span> 
                                {props.data.original_price && (
                                    <span className="price-original">${props.data.original_price}</span>
                                )}
                            </span>
                        ) : (
                            props.data.original_price && <span><strong>Price:</strong> ${props.data.original_price}</span>
                        )}
                        
                        {/* Display Unit and Quantity */}
                        {props.data.unit && <span> / {props.data.unit}</span>}
                        {props.data.quantity && <span> (Size: {props.data.quantity})</span>}
                        
                        {/* Display Tax and CRV badges */}
                        {props.data.has_crv && <span className="badge badge-crv">CRV</span>}
                        {props.data.taxable && <span className="badge badge-tax">TAX</span>}
                    </div>
                )}
            </div>
            
            <div className="item-actions">
                <button 
                    className="plus-btn"
                    onClick={() => setQuantity(quantity + 1)}>
                    Plus
                </button>
                <button
                    className="delete-btn"
                    onClick={() => props.triggerDelete(props.rawItem)}>
                    Delete
                </button>
            </div>
        </li>
    );
}

export default GroceryItem;