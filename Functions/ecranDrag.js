document.addEventListener('DOMContentLoaded', function() {
    // Sélectionne le conteneur et initialise les variables pour le suivi du glissement
    const container = document.querySelector('.container');
    let startX = 0, startY = 0;
    let initialTranslateX = 0, initialTranslateY = 0;

    // Définit une valeur de transformation initiale pour éviter une translation indéfinie
    container.style.transform = "translate(0px, 0px)";

    // Ajoute un écouteur d'événements pour détecter le début du toucher avec deux doigts
    container.addEventListener('touchstart', function(event) {
        if (event.touches.length === 2) {
            event.preventDefault(); // Empêche le comportement par défaut pour pouvoir gérer le geste personnalisé
            // Calcule la position centrale initiale en prenant la moyenne des coordonnées des deux doigts
            const touch1 = event.touches[0];
            const touch2 = event.touches[1];
            startX = (touch1.pageX + touch2.pageX) / 2;
            startY = (touch1.pageY + touch2.pageY) / 2;
            // Récupère la transformation actuelle pour déterminer la translation de départ
            const style = window.getComputedStyle(container);
            const matrix = new DOMMatrixReadOnly(style.transform);
            initialTranslateX = matrix.m41;
            initialTranslateY = matrix.m42;
        }
    }, {passive: false});

    // Ajoute un écouteur d'événements pour le mouvement de toucher avec deux doigts
    container.addEventListener('touchmove', function(event) {
        if (event.touches.length === 2) {
            event.preventDefault(); // Empêche le défilement par défaut
            // Récupère la position actuelle moyenne des deux doigts
            const touch1 = event.touches[0];
            const touch2 = event.touches[1];
            const currentX = (touch1.pageX + touch2.pageX) / 2;
            const currentY = (touch1.pageY + touch2.pageY) / 2;
            // Calcule la différence par rapport à la position de départ pour animer le déplacement
            const deltaX = currentX - startX;
            const deltaY = currentY - startY;
            // Met à jour la transformation CSS pour déplacer le conteneur en fonction du glissement
            container.style.transform = `translate(${initialTranslateX + deltaX}px, ${initialTranslateY + deltaY}px)`;
        }
    }, {passive: false});
});
