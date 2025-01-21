const output = document.getElementById('output');
const input = document.getElementById('input');
const sendButton = document.getElementById('send');

// Dynamically determine WebSocket URL
const wsUrl = 
    window.location.protocol === "https:"
    ? `wss://${window.location.host}/ws`
    : `ws://${window.location.host}/ws`;

console.log(`Connecting to WebSocket server at: ${wsUrl}`);
const ws = new WebSocket(wsUrl);

// Append a message to the output log
function appendToOutput(message) {
    const paragraph = document.createElement('p');
    paragraph.textContent = message;
    output.appendChild(paragraph);
    output.scrollTop = output.scrollHeight; // Scroll to the bottom
}

// Handle WebSocket events
ws.onopen = () => {
    console.log("WebSocket connection established.");
    appendToOutput("Connected to the server.");
};

ws.onerror = (error) => {
    console.error("WebSocket error:", error);
    appendToOutput("Connection error. Please try again.");
};

ws.onmessage = (event) => {
    try {
        const data = JSON.parse(event.data);
        
        if (data.type === "auth_request") {
            appendToOutput(data.message);
        } else if (data.type === "auth_success") {
            appendToOutput(data.message);
        } else if (data.type === "theme") {
            document.documentElement.setAttribute('data-theme', data.theme);
            localStorage.setItem('theme', data.theme);
            appendToOutput(data.message);
        } else if (data.type === "game_message") {
            appendToOutput(data.message);
        } else if (data.type === "error") {
            appendToOutput(`Error: ${data.message}`);
        }
    } catch (error) {
        console.error("Failed to parse message:", error);
        appendToOutput("Error: Failed to parse server message");
    }
};

ws.onclose = () => {
    console.log("WebSocket connection closed.");
    appendToOutput("Disconnected from the server.");
};

// Initialize theme from localStorage
const savedTheme = localStorage.getItem('theme') || 'default';
document.documentElement.setAttribute('data-theme', savedTheme);

// Send message to the server
function sendMessage() {
    const command = input.value.trim();
    if (command && ws.readyState === WebSocket.OPEN) {
        console.log(`Sending command: ${command}`);
        appendToOutput(`> ${command}`); // Display the command in the output
        ws.send(command); // Send the command to the server
        input.value = ''; // Clear the input box
    } else if (!command) {
        console.warn("Command is empty.");
    } else {
        console.warn("WebSocket is not open.");
        appendToOutput("Cannot send command: Not connected to the server.");
    }
}

// Event listeners
sendButton.addEventListener('click', sendMessage);
input.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent the default form submission
        sendMessage(); // Trigger the same logic as the Send button
    }
});
