document.addEventListener('DOMContentLoaded', function() {
    // Sélectionne le conteneur du tableau
    const container = document.querySelector('.container');
    if (!container) return;

    let isDragging = false;
    let startX = 0, startY = 0;
    let startScrollLeft = 0, startScrollTop = 0;

    // Enregistre la position de départ du doigt et la position de scroll actuelle
    container.addEventListener('touchstart', function(event) {
        if (event.touches.length === 1) {
            isDragging = true;
            const touch = event.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
            startScrollLeft = container.scrollLeft;
            startScrollTop = container.scrollTop;
        }
    }, { passive: true });

    // Fait défiler le conteneur en fonction du déplacement du doigt
    container.addEventListener('touchmove', function(event) {
        if (!isDragging || event.touches.length !== 1) return;
        event.preventDefault(); // Empêche le scroll natif du navigateur pour contrôler le défilement
        const touch = event.touches[0];
        container.scrollLeft = startScrollLeft - (touch.clientX - startX);
        container.scrollTop = startScrollTop - (touch.clientY - startY);
    }, { passive: false });

    // Réinitialise l'état du glissement à la fin du toucher
    container.addEventListener('touchend', function() {
        isDragging = false;
    }, { passive: true });
});
