export class ViewportManager {
    constructor(container) {
        this.container = container;
        this.visibleElements = new Set();
        this.observer = new IntersectionObserver(this.handleIntersection.bind(this), { root: container });
    }
    handleIntersection(entries) {
        entries.forEach(entry => {
            const id = entry.target.getAttribute('data-id');
            if (id) {
                if (entry.isIntersecting) {
                    this.visibleElements.add(id);
                }
                else {
                    this.visibleElements.delete(id);
                }
            }
        });
    }
    observe(element, id) {
        element.setAttribute('data-id', id);
        this.observer.observe(element);
    }
}
//# sourceMappingURL=ViewportManager.js.map