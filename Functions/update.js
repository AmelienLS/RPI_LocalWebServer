(function () {
    var btnUpdate = document.getElementById('btn-update');
    if (!btnUpdate) return;

    btnUpdate.addEventListener('click', function () {
        btnUpdate.disabled = true;
        btnUpdate.textContent = 'Mise à jour…';

        fetch('/update', { method: 'POST' })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var result = document.getElementById('update-result');
                document.getElementById('update-branch').textContent = 'Branche : ' + data.branch;
                document.getElementById('update-output').textContent = data.output || '(aucun changement)';
                result.style.display = 'block';

                if (data.will_restart) {
                    var sec = 8;
                    var cd = document.getElementById('update-countdown');
                    cd.textContent = 'Redémarrage du service dans ' + sec + 's…';
                    var iv = setInterval(function () {
                        sec--;
                        if (sec <= 0) {
                            clearInterval(iv);
                            cd.textContent = 'Rechargement…';
                            location.reload();
                        } else {
                            cd.textContent = 'Redémarrage du service dans ' + sec + 's…';
                        }
                    }, 1000);
                } else {
                    btnUpdate.disabled = false;
                    btnUpdate.textContent = 'Mettre à jour';
                }
            })
            .catch(function () {
                btnUpdate.disabled = false;
                btnUpdate.textContent = 'Mettre à jour';
            });
    });
})();
