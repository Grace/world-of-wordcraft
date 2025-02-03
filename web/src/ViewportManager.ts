export class ViewportManager {
    private observer: IntersectionObserver;
    private visibleElements = new Set<string>();

    constructor(private container: HTMLElement) {
        this.observer = new IntersectionObserver(
            this.handleIntersection.bind(this),
            { root: container }
        );
    }

    private handleIntersection(entries: IntersectionObserverEntry[]): void {
        entries.forEach(entry => {
            const id = entry.target.getAttribute('data-id');
            if (id) {
                if (entry.isIntersecting) {
                    this.visibleElements.add(id);
                } else {
                    this.visibleElements.delete(id);
                }
            }
        });
    }

    public observe(element: HTMLElement, id: string): void {
        element.setAttribute('data-id', id);
        this.observer.observe(element);
    }
}