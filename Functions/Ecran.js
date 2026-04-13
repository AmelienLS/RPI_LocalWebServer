document.addEventListener('DOMContentLoaded', function () {
    const table  = document.getElementById('serigraphie-table');
    const tbody  = table.querySelector('tbody');
    const filters = document.querySelectorAll('.filter-input');

    // Ordre original des lignes pour le retour à défaut
    const originalOrder = Array.from(tbody.querySelectorAll('tr'));

    /* ── Filtres ── */
    function applyFilters() {
        tbody.querySelectorAll('tr').forEach(row => {
            let show = true;
            filters.forEach(filter => {
                const col = filter.getAttribute('data-column');
                const val = filter.value.toLowerCase().trim();
                if (val !== '') {
                    const cell = row.cells[col];
                    if (cell && !cell.textContent.toLowerCase().includes(val)) show = false;
                }
            });
            row.style.display = show ? '' : 'none';
        });
    }

    filters.forEach(f => f.addEventListener('input', applyFilters));

    /* ── Tri ── */
    var sortCol = -1;
    var sortDir = 0; // 0 = défaut, 1 = asc, -1 = desc

    table.querySelectorAll('thead th').forEach(function (th, colIndex) {
        if (!th.querySelector('.filter-input')) return; // colonnes sans filtre non triables

        th.classList.add('sortable');

        th.addEventListener('click', function (e) {
            if (e.target.tagName === 'INPUT') return; // clic sur le champ filtre → ignorer

            if (sortCol === colIndex) {
                sortDir = sortDir === 1 ? -1 : sortDir === -1 ? 0 : 1;
            } else {
                sortCol = colIndex;
                sortDir = 1;
            }

            // Mettre à jour les indicateurs sur tous les th
            table.querySelectorAll('thead th').forEach(h => h.removeAttribute('data-sort'));
            if (sortDir !== 0) th.setAttribute('data-sort', sortDir === 1 ? 'asc' : 'desc');

            if (sortDir === 0) {
                // Restaurer l'ordre original
                originalOrder.forEach(row => tbody.appendChild(row));
            } else {
                Array.from(tbody.querySelectorAll('tr'))
                    .sort(function (a, b) {
                        var aVal = a.cells[colIndex] ? a.cells[colIndex].textContent.trim() : '';
                        var bVal = b.cells[colIndex] ? b.cells[colIndex].textContent.trim() : '';
                        var aNum = parseFloat(aVal.replace(/\s/g, ''));
                        var bNum = parseFloat(bVal.replace(/\s/g, ''));
                        var cmp = (!isNaN(aNum) && !isNaN(bNum))
                            ? aNum - bNum
                            : aVal.localeCompare(bVal, 'fr', { sensitivity: 'base' });
                        return sortDir === 1 ? cmp : -cmp;
                    })
                    .forEach(row => tbody.appendChild(row));
            }

            applyFilters();
        });
    });
});
