const output = document.getElementById('output');
const input = document.getElementById('input');
const sendButton = document.getElementById('send');
const autoScroll = true; // Can be toggled by user preference
// Add imports at top
import { SpeechManager } from './SpeechManager.js';
// Initialize SpeechManager after DOM elements
const speechManager = new SpeechManager(output);
// Dynamically determine WebSocket URL
const wsUrl = window.location.protocol === "https:"
    ? `wss://${window.location.host}/ws`
    : `ws://${window.location.host}/ws`;
console.log(`Connecting to WebSocket server at: ${wsUrl}`);
// Initialize WebSocket connection
let ws;
function connectWebSocket() {
    ws = new WebSocket(wsUrl);
    ws.onopen = () => {
        console.log('Connected to server');
        appendToOutput('Connected to server...');
    };
    ws.onmessage = (event) => {
        console.log('Raw message received:', event.data);
        try {
            const data = JSON.parse(event.data);
            console.log('Parsed message:', data);
            // Handle theme changes
            if (data.type === 'theme' && data.data?.theme) {
                document.documentElement.setAttribute('data-theme', data.data.theme);
                localStorage.setItem('theme', data.data.theme);
            }
            // Handle font size changes
            if (data.type === 'fontsize' && data.data?.fontSize) {
                if (output) {
                    output.style.fontSize = `${data.data.fontSize}px`;
                }
                localStorage.setItem('fontSize', data.data.fontSize);
            }
            // Handle speech rate changes
            if (data.type === 'speech-rate' && data.data?.speechRate) {
                speechManager.setSpeechRate(data.data.speechRate);
                // speechRate = data.data.speechRate;
                // localStorage.setItem('speechRate', speechRate.toString());
            }
            // Handle speech repeat
            if (data.type === 'speech-repeat' && data.data?.repeat) {
                if ('speechSynthesis' in window && speechManager.getSpeechEnabled()) {
                    if (output) {
                        const visibleText = output ? output.textContent : '';
                        if (visibleText) {
                            // const utterance = new SpeechSynthesisUtterance(visibleText || '');
                            // utterance.rate = speechRate;
                            // window.speechSynthesis.speak(utterance);
                            speechManager.repeatVisible();
                        }
                    }
                }
            }
            // Handle speech stop
            if (data.type === 'speech-stop' && data.data?.stop) {
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                }
            }
            if (data.type === 'room_description') {
                console.log('Room description:', data.message);
                appendToOutput(data.message);
                return;
            }
            appendToOutput(data.message);
            return;
        }
        catch (e) {
            console.error('Failed to parse message:', e);
            if (e instanceof Error) {
                appendToOutput('Error: ' + e.message);
            }
            else {
                appendToOutput('An unknown error occurred');
            }
        }
    };
    ws.onclose = () => {
        console.log('Disconnected from server');
        appendToOutput('Disconnected from server. Reconnecting...');
        setTimeout(connectWebSocket, 1000);
    };
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        appendToOutput('Connection error occurred');
    };
}
connectWebSocket();
function scrollToBottom() {
    if (output) {
        const lastMessage = output.lastElementChild;
        if (lastMessage && autoScroll) {
            lastMessage.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }
}
// Append a message to the output log
function appendToOutput(message) {
    const paragraph = document.createElement('p');
    paragraph.textContent = message;
    if (output) {
        output.appendChild(paragraph);
    }
    scrollToBottom();
    // Speak message if text-to-speech enabled
    if (speechManager.getSpeechEnabled() && 'speechSynthesis' in window) {
        // const utterance = new SpeechSynthesisUtterance(message);
        // utterance.rate = speechRate;
        // window.speechSynthesis.speak(utterance);
        speechManager.speak(message);
    }
}
// Enhanced MutationObserver
const observer = new MutationObserver((mutations) => {
    if (mutations.some(m => m.addedNodes.length > 0)) {
        scrollToBottom();
    }
});
if (output) {
    observer.observe(output, {
        childList: true,
        subtree: true
    });
}
// Add scroll visibility check
if (output) {
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
}
// Initialize theme from localStorage - default to high-contrast
const savedTheme = localStorage.getItem('theme') || 'high-contrast';
document.documentElement.setAttribute('data-theme', savedTheme);
// Initialize font size from localStorage
const savedFontSize = localStorage.getItem('fontSize');
if (savedFontSize) {
    if (output) {
        output.style.fontSize = `${savedFontSize}px`;
    }
}
function sanitizeCommand(command) {
    // Remove any potentially harmful characters
    return command.replace(/[<>]/g, '');
}
// Add speech command handler
function handleSpeechCommand(command) {
    const parts = command.split(' ');
    if (parts[0] === 'speech') {
        switch (parts[1]) {
            case 'on':
                speechManager.setSpeechEnabled(true);
                // localStorage.setItem('speechEnabled', 'true');
                //appendToOutput("Text-to-speech enabled");
                return true;
            case 'off':
                //speechEnabled = false;
                speechManager.setSpeechEnabled(false);
                // localStorage.setItem('speechEnabled', 'false');
                //appendToOutput("Text-to-speech disabled");
                return true;
            case 'rate':
                const rate = parseFloat(parts[2]);
                if (rate >= 0.1 && rate <= 10) {
                    speechManager.setSpeechRate(rate);
                    //speechRate = rate;
                    //localStorage.setItem('speechRate', rate.toString());
                    //appendToOutput(`Speech rate set to ${rate}`);
                }
                return true;
            case 'repeat':
                speechManager.repeatVisible();
                return true;
            case 'stop':
                speechManager.stop();
                //appendToOutput("Text-to-speech stopped");
                return true;
            default:
                appendToOutput("Usage: speech on|off|rate <0.1-10>|repeat|stop");
                return true;
        }
    }
    return false;
}
// Send message to the server
function sendMessage() {
    if (!input) {
        appendToOutput("Error: Input element not found");
        return;
    }
    const command = sanitizeCommand(input.value.trim());
    if (!command)
        return;
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
    }
    else if (!command) {
        console.warn("Command is empty.");
    }
    else {
        console.warn("WebSocket is not open.");
        appendToOutput("Cannot send command: Not connected to the server.");
    }
}
// Event listeners
if (sendButton) {
    sendButton.addEventListener('click', sendMessage);
}
input.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent the default form submission
        sendMessage(); // Trigger the same logic as the Send button
    }
});
//# sourceMappingURL=script.js.map