(function () {
    var KEY = 'screen_rotation';

    function getAngle() {
        return parseInt(localStorage.getItem(KEY) || '0', 10);
    }

    function applyAngle(angle) {
        var html = document.documentElement;
        html.classList.remove('rot-90', 'rot-180', 'rot-270');
        if (angle === 90)  html.classList.add('rot-90');
        if (angle === 180) html.classList.add('rot-180');
        if (angle === 270) html.classList.add('rot-270');
    }

    function rotate(delta) {
        var next = (getAngle() + delta + 360) % 360;
        localStorage.setItem(KEY, next);
        applyAngle(next);
    }

    // Appliqué immédiatement pour éviter un flash avant DOMContentLoaded
    applyAngle(getAngle());

    document.addEventListener('DOMContentLoaded', function () {
        var btnCW = document.createElement('button');
        btnCW.id = 'btn-rotate-cw';
        btnCW.title = 'Rotation horaire';
        btnCW.innerHTML = '&#8635;';
        btnCW.addEventListener('click', function (e) {
            e.stopPropagation();
            rotate(90);
        });

        var btnCCW = document.createElement('button');
        btnCCW.id = 'btn-rotate-ccw';
        btnCCW.title = 'Rotation anti-horaire';
        btnCCW.innerHTML = '&#8634;';
        btnCCW.addEventListener('click', function (e) {
            e.stopPropagation();
            rotate(-90);
        });

        document.body.appendChild(btnCCW);
        document.body.appendChild(btnCW);
    });
})();
