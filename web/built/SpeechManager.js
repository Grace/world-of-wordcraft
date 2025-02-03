import { TextQueue } from "./TextQueue.js";
import { ViewportManager } from "./ViewportManager.js";
export class SpeechManager {
    constructor(container) {
        this.container = container;
        this.queue = new TextQueue();
        this.viewport = new ViewportManager(container);
        this.speechEnabled = localStorage.getItem('speechEnabled') === 'true';
        this.speechRate = parseFloat(localStorage.getItem('speechRate') ?? '1.0');
    }
    speak(text) {
        const id = this.queue.add(text);
        const element = this.createTextElement(text, id);
        this.container.appendChild(element);
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = this.speechRate;
            utterance.onend = () => this.queue.markRead(id);
            window.speechSynthesis.speak(utterance);
        }
    }
    createTextElement(text, id) {
        const p = document.createElement('p');
        p.textContent = text;
        this.viewport.observe(p, id);
        return p;
    }
    stop() {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
    }
    repeatVisible() {
        if ('speechSynthesis' in window) {
            const unreadText = this.queue.getUnread()
                .filter(entry => entry.isVisible)
                .map(entry => entry.content)
                .join(' ');
            if (unreadText) {
                const utterance = new SpeechSynthesisUtterance(unreadText);
                utterance.rate = this.speechRate;
                window.speechSynthesis.speak(utterance);
            }
        }
    }
    getSpeechEnabled() {
        return this.speechEnabled;
    }
    setSpeechEnabled(enabled) {
        this.speechEnabled = enabled;
        localStorage.setItem('speechEnabled', enabled.toString());
    }
    getSpeechRate() {
        return this.speechRate;
    }
    setSpeechRate(rate) {
        this.speechRate = rate;
        localStorage.setItem('speechRate', rate.toString());
    }
}
//# sourceMappingURL=SpeechManager.js.map