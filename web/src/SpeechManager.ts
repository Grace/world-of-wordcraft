import { TextQueue } from "./TextQueue";
import { ViewportManager } from "./ViewportManager";

export class SpeechManager {
    private queue: TextQueue;
    private viewport: ViewportManager;
    private speechEnabled: boolean;
    private speechRate: number;

    constructor(private container: HTMLElement) {
        this.queue = new TextQueue();
        this.viewport = new ViewportManager(container);
        this.speechEnabled = localStorage.getItem('speechEnabled') === 'true';
        this.speechRate = parseFloat(localStorage.getItem('speechRate') ?? '1.0');
    }

    public speak(text: string): void {
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

    private createTextElement(text: string, id: string): HTMLElement {
        const p = document.createElement('p');
        p.textContent = text;
        this.viewport.observe(p, id);
        return p;
    }

    public stop(): void {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
    }
    
    public repeatVisible(): void {
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

    public getSpeechEnabled(): boolean {
        return this.speechEnabled;
    }

    public setSpeechEnabled(enabled: boolean): void {
        this.speechEnabled = enabled;
        localStorage.setItem('speechEnabled', enabled.toString());
    }

    public getSpeechRate(): number {
        return this.speechRate;
    }

    public setSpeechRate(rate: number): void {
        this.speechRate = rate;
        localStorage.setItem('speechRate', rate.toString());
    }
}