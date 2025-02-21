document.addEventListener('DOMContentLoaded', function () {
    const table = document.getElementById('serigraphie-table');
    const filters = document.querySelectorAll('.filter-input');

    function applyFilters() {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            let show = true;
            filters.forEach(filter => {
                const columnIndex = filter.getAttribute('data-column');
                const filterValue = filter.value.toLowerCase().trim();
                if(filterValue !== '') {
                    const cell = row.cells[columnIndex];
                    if(cell && !cell.textContent.toLowerCase().includes(filterValue)) {
                        show = false;
                    }
                }
            });
            row.style.display = show ? '' : 'none';
        });
    }

    filters.forEach(filter => {
        filter.addEventListener('input', applyFilters);
    });
});