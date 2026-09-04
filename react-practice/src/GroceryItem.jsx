import { useState } from 'react';
import './App.css';

function GroceryItem (props) {
    const [quantity, setQuantity] = useState(1); 
    
    
    const itemData = props.data || props; 
    const displayName = itemData.english_name || itemData.name || props.name;
    const displayPrice = itemData.discount_price || itemData.price;
    
    const hasData = itemData !== null && itemData !== undefined;
    
    return (
        <li className="grocery-item">
            <div className="item-main">
                <span className="item-name">
                    {displayName} 
                    {hasData && itemData.chinese_name ? ` (${itemData.chinese_name})` : ""} 
                    <span className="item-quantity">
                        - Qty: {quantity}
                    </span>
                </span>
                
                {hasData && (
                    <div className="item-details">
                        {displayPrice ? (
                            <span>
                                <span className="price-sale">Sale: ${Number(displayPrice).toFixed(2)}</span> 
                                {itemData.original_price && (
                                    <span className="price-original">${itemData.original_price}</span>
                                )}
                            </span>
                        ) : (
                            itemData.original_price && <span><strong>Price:</strong> ${itemData.original_price}</span>
                        )}
                        
                        {itemData.unit && <span> / {itemData.unit}</span>}
                        {itemData.quantity && <span> (Size: {itemData.quantity})</span>}
                        {itemData.has_crv && <span className="badge badge-crv">CRV</span>}
                        {itemData.taxable && <span className="badge badge-tax">TAX</span>}
                    </div>
                )}
            </div>
            
            <div className="item-actions">
                <button className="plus-btn" onClick={() => setQuantity(quantity + 1)}>Plus</button>
                <button className="delete-btn" onClick={() => props.triggerDelete(props.rawItem)}>Delete</button>
            </div>
        </li>
    );
}

export default GroceryItem;