import { useState } from "react";
import './App.css';
function AddForm(props) {
    const [inputValue, setInputValue] = useState("");
    const [errorMessage, setErrorMessage] = useState("");
    function handleSubmit() {
        if (inputValue.trim() === "") return;
        setErrorMessage(props.triggerAdd(inputValue, errorMessage));
        setInputValue("");
    }
    return (
        <div className = "add-form">
            <div className = "input-container">
            <input 
                className = "add-input"
                type = "text"
                value = {inputValue}
                onChange = {(e) => setInputValue(e.target.value)}
                placeholder = "Enter an item..."
            />
            {errorMessage && <p className = "error-message">{errorMessage}</p>}
            </div>
            <button 
                className = "add-btn"
                onClick = {handleSubmit}>
                Add item
            </button>
            
        </div>
    );
}

export default AddForm;