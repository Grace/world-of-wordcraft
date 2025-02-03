interface TextEntry {
    id: string;
    content: string;
    timestamp: number;
    isRead: boolean;
    isVisible: boolean;
}

export class TextQueue {
    private entries: TextEntry[] = [];
    private maxEntries = 1000;
    private readIndex = 0;

    static generateUUID(): string {
        let d = new Date().getTime();
        if (typeof performance !== 'undefined' && typeof performance.now === 'function') {
          d += performance.now(); //use high-precision timer if available
        }
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
          let r = (d + Math.random() * 16) % 16 | 0;
          d = Math.floor(d / 16);
          return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
      }

    public add(content: string): string {
        const entry: TextEntry = {
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

    public markRead(id: string): void {
        const index = this.entries.findIndex(e => e.id === id);
        if (index !== -1) {
            this.entries[index].isRead = true;
            this.readIndex = Math.max(this.readIndex, index + 1);
        }
    }

    public getUnread(): TextEntry[] {
        return this.entries.slice(this.readIndex);
    }

    private cleanup(): void {
        if (this.entries.length > this.maxEntries) {
            this.entries = this.entries.slice(-this.maxEntries);
            this.readIndex = Math.max(0, this.readIndex - this.maxEntries);
        }
    }
}