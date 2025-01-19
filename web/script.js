const output = document.getElementById('output');
const input = document.getElementById('input');
const sendButton = document.getElementById('send');

console.log("Connecting to WebSocket server...");
const ws = new WebSocket('ws://localhost:8765'); // Update to match your server URL

// Log WebSocket connection status
ws.onopen = () => {
    console.log("WebSocket connection established.");
    appendToOutput("Connected to the server.");
};

ws.onerror = (error) => {
    console.error("WebSocket error:", error);
    appendToOutput("Connection error. Please try again.");
};

ws.onmessage = (event) => {
    console.log("Message received from server:", event.data);
    const data = JSON.parse(event.data);
    appendToOutput(data.message);
};

ws.onclose = () => {
    console.log("WebSocket connection closed.");
    appendToOutput("Disconnected from the server.");
};

// Add event listeners for the Send button and Enter key
sendButton.addEventListener('click', sendMessage);
input.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const command = input.value.trim();
    if (command && ws.readyState === WebSocket.OPEN) {
        console.log("Sending command:", command);
        appendToOutput(`> ${command}`); // Show command in the output history
        ws.send(command); // Send command to the server
        input.value = ''; // Clear the input box
    } else if (!command) {
        console.warn("Command is empty.");
    } else {
        console.warn("WebSocket is not open.");
        appendToOutput("Cannot send command: Not connected to the server.");
    }
}

function appendToOutput(message) {
    const paragraph = document.createElement('p');
    paragraph.textContent = message;
    output.appendChild(paragraph);
    output.scrollTop = output.scrollHeight;
}
