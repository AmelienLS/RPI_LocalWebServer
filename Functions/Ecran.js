document.addEventListener('DOMContentLoaded', function () {
    const table = document.getElementById('serigraphie-table');
    const filters = document.querySelectorAll('.filter-input');

    filters.forEach(filter => {
        filter.addEventListener('input', function () {
            const columnIndex = this.getAttribute('data-column');
            const filterValue = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const cell = row.cells[columnIndex];
                if (cell) {
                    const cellText = cell.textContent.toLowerCase();
                    if (cellText.includes(filterValue)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                }
            });
        });
    });
});
