/**
 * script.js - Frontend JavaScript for the Calculator
 * 
 * This script runs entirely in the user's browser (client-side).
 * It manages the calculator's state, responds to button clicks and keyboard presses,
 * and sends mathematical expressions to the Flask backend via the Fetch API.
 */

// --- STATE MANAGEMENT ---
// These variables track what is currently happening on the calculator screen.
let currentExpression = "";      // The expression string being built (e.g., "12+5*3")
let lastActionWasEvaluation = false; // Flag to check if the last button pressed was '='

// --- DOM ELEMENT REFERENCES ---
// Grabbing handles for the interactive display areas on our calculator.
const expressionViewer = document.getElementById("expression-viewer");
const resultViewer = document.getElementById("result-viewer");

// --- KEY EVENT MAPPING ---
// Maps standard physical keyboard keys to the IDs of our calculator buttons.
const KEYBOARD_MAP = {
    "0": "btn-0", "1": "btn-1", "2": "btn-2", "3": "btn-3", "4": "btn-4",
    "5": "btn-5", "6": "btn-6", "7": "btn-7", "8": "btn-8", "9": "btn-9",
    ".": "btn-decimal",
    "+": "btn-add", "-": "btn-subtract", "*": "btn-multiply", "/": "btn-divide",
    "(": "btn-paren-open", ")": "btn-paren-close",
    "Enter": "btn-equals", "=": "btn-equals",
    "Backspace": "btn-backspace",
    "Escape": "btn-clear", "c": "btn-clear", "C": "btn-clear"
};


// --- INITIALIZATION ---
// Wait until the complete webpage is loaded, then register all events.
document.addEventListener("DOMContentLoaded", () => {
    setupButtonListeners();
    setupKeyboardListener();
});


/**
 * Hooks up click events for all interactive buttons on the keypad.
 */
function setupButtonListeners() {
    // 1. Hook up all numeric digits (0-9) and decimal points
    const digitButtons = document.querySelectorAll(".btn-digit");
    digitButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            handleDigitInput(btn.innerText);
        });
    });

    // 2. Hook up all arithmetic operators (+, -, *, /)
    const operatorButtons = document.querySelectorAll(".btn-operator");
    operatorButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            handleOperatorInput(btn.innerText);
        });
    });

    // 3. Clear button (C)
    document.getElementById("btn-clear").addEventListener("click", () => {
        clearCalculator();
    });

    // 4. Backspace button (Delete last character)
    document.getElementById("btn-backspace").addEventListener("click", () => {
        handleBackspace();
    });

    // 5. Parenthesis buttons (Open / Close)
    document.getElementById("btn-paren-open").addEventListener("click", () => {
        handleParenInput("(");
    });
    document.getElementById("btn-paren-close").addEventListener("click", () => {
        handleParenInput(")");
    });

    // 6. Equals button (=) - This is where the magic happens!
    document.getElementById("btn-equals").addEventListener("click", () => {
        calculateResult();
    });
}


/**
 * Registers keyboard event listener, mapping physical keystrokes to calculator buttons.
 */
function setupKeyboardListener() {
    document.addEventListener("keydown", (event) => {
        const buttonId = KEYBOARD_MAP[event.key];
        if (buttonId) {
            // Prevent default action (e.g. Backspace going back a page, or "/" searching text)
            event.preventDefault();
            
            // Get the element and trigger visual hover feedback & click
            const buttonElement = document.getElementById(buttonId);
            if (buttonElement) {
                // Add a small active class for keyboard visual feedback
                buttonElement.classList.add("active-keyboard");
                buttonElement.click();
                
                // Remove the feedback class shortly after
                setTimeout(() => {
                    buttonElement.classList.remove("active-keyboard");
                }, 100);
            }
        }
    });
}


// --- CORE CALCULATOR LOGIC ---

/**
 * Handles numeric digit inputs (0-9) and the decimal point (.)
 */
function handleDigitInput(digit) {
    // If the last thing we did was evaluate an expression, and the user types a new digit,
    // we want to clear the slate and start a fresh number.
    if (lastActionWasEvaluation) {
        currentExpression = "";
        lastActionWasEvaluation = false;
    }

    // Edge-case: If entering a decimal point, make sure the current number block
    // doesn't already contain a decimal. (e.g., prevent "12.34.5")
    if (digit === ".") {
        // Find the last number token in the active expression
        const tokens = currentExpression.split(/[\+\-\*\/()]/);
        const activeToken = tokens[tokens.length - 1];
        if (activeToken.includes(".")) {
            return; // Ignore the click since it already has a decimal
        }
        
        // If they start with a dot, prefix it with a zero: ".5" becomes "0.5"
        if (currentExpression === "" || /[\+\-\*\/()]$/.test(currentExpression)) {
            currentExpression += "0";
        }
    }

    // Add the digit to our formula
    currentExpression += digit;
    updateDisplay();
}


/**
 * Handles operator inputs (+, -, *, /)
 */
function handleOperatorInput(operator) {
    // If we just evaluated an expression, we can "chain" the operator directly
    // onto the previous answer (e.g., if result is 15, clicking "+" makes it "15+")
    if (lastActionWasEvaluation) {
        lastActionWasEvaluation = false;
    }

    // Edge case: If the expression is empty, we only allow minus (-) for negative numbers
    if (currentExpression === "") {
        if (operator === "-") {
            currentExpression += operator;
            updateDisplay();
        }
        return; // Other operators are ignored if there's no preceding number
    }

    // Edge case: If the last character in the expression is already an operator,
    // we swap it for the new operator. E.g. changing "5 + " to "5 * "
    const lastChar = currentExpression.trim().slice(-1);
    if (["+", "-", "*", "/"].includes(lastChar)) {
        currentExpression = currentExpression.slice(0, -1) + operator;
    } else {
        currentExpression += operator;
    }

    updateDisplay();
}


/**
 * Handles parenthesis keys ( '(' and ')' )
 */
function handleParenInput(paren) {
    if (lastActionWasEvaluation) {
        currentExpression = "";
        lastActionWasEvaluation = false;
    }
    
    currentExpression += paren;
    updateDisplay();
}


/**
 * Handles deleting the last typed character (Backspace).
 */
function handleBackspace() {
    if (lastActionWasEvaluation) {
        // If we just ran a calculation, Backspace clears the display screen
        clearCalculator();
        return;
    }

    if (currentExpression.length > 0) {
        currentExpression = currentExpression.slice(0, -1);
        updateDisplay();
    }
}


/**
 * Resets the calculator's state back to zero.
 */
function clearCalculator() {
    currentExpression = "";
    lastActionWasEvaluation = false;
    expressionViewer.innerText = "";
    resultViewer.innerText = "0";
    // Reset visual error state in case it was active
    resultViewer.classList.remove("error-text");
}


/**
 * Updates the screen displays to represent the current expression.
 */
function updateDisplay() {
    // Show the built formula/expression in the top viewer
    expressionViewer.innerText = currentExpression;

    // Show the active typing in the bottom viewer.
    // If expression is empty, default display back to "0".
    if (currentExpression === "") {
        resultViewer.innerText = "0";
        return;
    }

    // Split expression into operator tokens to find the current active number block
    const tokens = currentExpression.split(/[\+\-\*\/()]/);
    const lastNumToken = tokens[tokens.length - 1];

    if (lastNumToken !== undefined && lastNumToken !== "") {
        resultViewer.innerText = lastNumToken;
    } else {
        // If the expression ends with an operator (like "12 + "), show the overall expression
        resultViewer.innerText = currentExpression;
    }
}


// --- BACKEND API COMMUNICATION ---

/**
 * Sends the mathematical expression to the Flask API backend for calculation.
 */
async function calculateResult() {
    // If there is no expression to calculate, do nothing!
    if (!currentExpression.trim()) {
        return;
    }

    // Visual loading state
    resultViewer.innerText = "Calculating...";
    resultViewer.classList.remove("error-text");

    try {
        // Make the asynchronous POST request to our Flask backend API
        const response = await fetch("/calculate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ expression: currentExpression })
        });

        // Parse the JSON output sent by Flask
        const data = await response.json();

        if (data.status === "success") {
            // Update the display screen to show the result
            expressionViewer.innerText = currentExpression + " =";
            resultViewer.innerText = data.result;
            
            // Set up state for subsequent inputs:
            // Chaining operators will extend this result; typing numbers will wipe it.
            currentExpression = data.result.toString();
            lastActionWasEvaluation = true;
        } else {
            // Display errors (like "Division by Zero" or syntax errors) returned by the backend
            handleDisplayError(data.message);
        }
    } catch (error) {
        // Handle physical network errors or lost server connection
        console.error("API Fetch Error:", error);
        handleDisplayError("Server Error");
    }
}


/**
 * Shows an error state on the calculator display.
 */
function handleDisplayError(errorMessage) {
    resultViewer.innerText = errorMessage;
    resultViewer.classList.add("error-text");
    // We keep the last entered expression in the top history viewer so the user can see what they did wrong
    expressionViewer.innerText = currentExpression;
    
    // Set state so typing new keys clears the error
    lastActionWasEvaluation = true;
}
