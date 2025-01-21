const output = document.getElementById('output');
const input = document.getElementById('input');
const sendButton = document.getElementById('send');
const autoScroll = true; // Can be toggled by user preference
let speechEnabled = localStorage.getItem('speechEnabled') === 'true';
let speechRate = parseFloat(localStorage.getItem('speechRate')) || 1.0;

// Dynamically determine WebSocket URL
const wsUrl = 
    window.location.protocol === "https:"
    ? `wss://${window.location.host}/ws`
    : `ws://${window.location.host}/ws`;

console.log(`Connecting to WebSocket server at: ${wsUrl}`);
const ws = new WebSocket(wsUrl);

function scrollToBottom() {
    const lastMessage = output.lastElementChild;
    if (lastMessage && autoScroll) {
        lastMessage.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
}

// Append a message to the output log
function appendToOutput(message) {
    const paragraph = document.createElement('p');
    paragraph.textContent = message;
    output.appendChild(paragraph);
    scrollToBottom();
    
    // Speak message if enabled
    if (speechEnabled && 'speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(message);
        utterance.rate = speechRate;
        window.speechSynthesis.speak(utterance);
    }
}

// Enhanced MutationObserver
const observer = new MutationObserver((mutations) => {
    if (mutations.some(m => m.addedNodes.length > 0)) {
        scrollToBottom();
    }
});

observer.observe(output, {
    childList: true,
    subtree: true
});

// Add scroll visibility check
const scrollObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (!entry.isIntersecting && entry.target === output.lastElementChild) {
            scrollToBottom();
        }
    });
}, {
    root: output,
    threshold: 1.0
});

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
        
        switch(data.type) {
            case "auth_request":
            case "auth_success":
            case "game_message":
                appendToOutput(data.message);
                break;
            case "theme":
                document.documentElement.setAttribute('data-theme', data.theme);
                localStorage.setItem('theme', data.theme);
                appendToOutput(data.message);
                break;
            case "error":
                appendToOutput(`Error: ${data.message}`);
                break;
            case "fontsize":
                output.style.fontSize = `${data.size}px`;
                localStorage.setItem('fontSize', data.size);
                appendToOutput(data.message);
                break;
        }
        
        // Observe the last message for visibility
        const lastMessage = output.lastElementChild;
        if (lastMessage) {
            scrollObserver.observe(lastMessage);
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

// Initialize theme from localStorage - default to high-contrast
const savedTheme = localStorage.getItem('theme') || 'high-contrast';
document.documentElement.setAttribute('data-theme', savedTheme);

// Initialize font size from localStorage
const savedFontSize = localStorage.getItem('fontSize');
if (savedFontSize) {
    output.style.fontSize = `${savedFontSize}px`;
}

// Sanitize command input
function sanitizeCommand(command) {
    // Remove any potentially harmful characters
    return command.replace(/[<>]/g, '');
}

// Add speech command handler
function handleSpeechCommand(command) {
    const parts = command.split(' ');
    
    if (parts[0] === 'speech') {
        if (parts[1] === 'on') {
            speechEnabled = true;
            localStorage.setItem('speechEnabled', 'true');
            appendToOutput("Text-to-speech enabled");
            return true;
        } else if (parts[1] === 'off') {
            speechEnabled = false;
            localStorage.setItem('speechEnabled', 'false');
            appendToOutput("Text-to-speech disabled");
            return true;
        } else if (parts[1] === 'rate' && parts[2]) {
            const rate = parseFloat(parts[2]);
            if (rate >= 0.1 && rate <= 10) {
                speechRate = rate;
                localStorage.setItem('speechRate', rate.toString());
                appendToOutput(`Speech rate set to ${rate}`);
                return true;
            }
        } else if (parts[1] === 'repeat') {
            if ('speechSynthesis' in window) {
                const visibleText = output.textContent;
                const utterance = new SpeechSynthesisUtterance(visibleText);
                utterance.rate = speechRate;
                window.speechSynthesis.speak(utterance);
            } else {
                appendToOutput("Text-to-speech is not supported in your browser.");
            }
            return true;
        }
        appendToOutput("Usage: speech on|off|rate <0.1-10>|repeat");
        return true;
    }
    return false;
}

// Send message to the server
function sendMessage() {
    const command = sanitizeCommand(input.value.trim());
    if (!command) return;
    
    if (command.length > 1000) {
        appendToOutput("Error: Command too long");
        return;
    }
    
    // Handle speech commands locally
    if (handleSpeechCommand(command)) {
        input.value = '';
        return;
    }
    
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
