const output = document.getElementById('output');
const input = document.getElementById('input');
const sendButton = document.getElementById('send');

// Dynamically determine the WebSocket URL based on the environment
const wsUrl =
    window.location.hostname === "world-of-wordcraft-production.up.railway.app"
        ? "wss://world-of-wordcraft:8765" // Production URL with WebSocket Secure (wss)
        : "ws://localhost:8765"; // Development URL

console.log(`Connecting to WebSocket server at: ${wsUrl}`);
const ws = new WebSocket(wsUrl);

// Handle WebSocket connection events
ws.onopen = () => {
    console.log("WebSocket connection established.");
    appendToOutput("Connected to the server.");
};

ws.onerror = (error) => {
    console.error("WebSocket error:", error);
    appendToOutput("Connection error. Please try again.");
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data); // Parse server response
    appendToOutput(data.message);
};

ws.onclose = () => {
    console.log("WebSocket connection closed.");
    appendToOutput("Disconnected from the server.");
};

// Send a message to the server when the button is clicked or Enter is pressed
sendButton.addEventListener('click', sendMessage);
input.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

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

function appendToOutput(message) {
    const paragraph = document.createElement('p');
    paragraph.textContent = message;
    output.appendChild(paragraph);
    output.scrollTop = output.scrollHeight; // Scroll to the bottom of the output
}
