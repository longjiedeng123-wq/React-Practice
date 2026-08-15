import { useState } from "react";
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

export default AddForm;