(function () {
    var KEY = 'screen_rotation';

    function getAngle() {
        return parseInt(localStorage.getItem(KEY) || '0', 10);
    }

    function applyAngle(angle) {
        var html = document.documentElement;
        html.classList.remove('rot-90');
        if (angle === 90) html.classList.add('rot-90');
    }

    // Appliqué immédiatement pour éviter un flash avant DOMContentLoaded
    applyAngle(getAngle());

    document.addEventListener('DOMContentLoaded', function () {
        var btn = document.createElement('button');
        btn.id = 'btn-rotate-screen';
        btn.innerHTML = '&#8635;';

        function updateBtn(angle) {
            btn.title = angle === 0 ? 'Passer en portrait' : 'Passer en paysage';
        }

        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            // 0° → 90° CW, 90° → 0° CCW
            var next = getAngle() === 0 ? 90 : 0;
            localStorage.setItem(KEY, next);
            applyAngle(next);
            updateBtn(next);
        });

        updateBtn(getAngle());
        document.body.appendChild(btn);
    });
})();
