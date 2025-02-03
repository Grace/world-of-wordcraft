export class TextQueue {
    constructor() {
        this.entries = [];
        this.maxEntries = 1000;
        this.readIndex = 0;
    }
    static generateUUID() {
        let d = new Date().getTime();
        if (typeof performance !== 'undefined' && typeof performance.now === 'function') {
            d += performance.now(); //use high-precision timer if available
        }
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            let r = (d + Math.random() * 16) % 16 | 0;
            d = Math.floor(d / 16);
            return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
    }
    add(content) {
        const entry = {
            id: TextQueue.generateUUID(),
            content,
            timestamp: Date.now(),
            isRead: false,
            isVisible: true
        };
        this.entries.push(entry);
        this.cleanup();
        return entry.id;
    }
    markRead(id) {
        const index = this.entries.findIndex(e => e.id === id);
        if (index !== -1) {
            this.entries[index].isRead = true;
            this.readIndex = Math.max(this.readIndex, index + 1);
        }
    }
    getUnread() {
        return this.entries.slice(this.readIndex);
    }
    cleanup() {
        if (this.entries.length > this.maxEntries) {
            this.entries = this.entries.slice(-this.maxEntries);
            this.readIndex = Math.max(0, this.readIndex - this.maxEntries);
        }
    }
}
//# sourceMappingURL=TextQueue.js.map