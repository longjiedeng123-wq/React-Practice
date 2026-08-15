import { useState } from "react";
import './App.css';
function AddForm(props) {
    const [inputValue, setInputValue] = useState("");
    function handleSubmit() {
        if (inputValue.trim() === "") return;
        props.triggerAdd(inputValue);
        setInputValue("");
    }
    return (
        <div className = "add-form">
            <input 
                className = "add-input"
                type = "text"
                value = {inputValue}
                onChange = {(e) => setInputValue(e.target.value)}
                placeholder = "Enter an item..."
            />
            <button 
                className = "add-btn"
                onClick = {handleSubmit}>
                Add item
            </button>
        </div>
    );
}

export default AddForm;