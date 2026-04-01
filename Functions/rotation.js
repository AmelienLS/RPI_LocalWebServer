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

    // Appliqué immédiatement pour éviter un flash avant DOMContentLoaded
    applyAngle(getAngle());

    document.addEventListener('DOMContentLoaded', function () {
        var btn = document.createElement('button');
        btn.id = 'btn-rotate-screen';
        btn.title = 'Rotation 90\u00b0 horaire';
        btn.innerHTML = '&#8635;';
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            var next = (getAngle() + 90) % 360;
            localStorage.setItem(KEY, next);
            applyAngle(next);
        });
        document.body.appendChild(btn);
    });
})();
