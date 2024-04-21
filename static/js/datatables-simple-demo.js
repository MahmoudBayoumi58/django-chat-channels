window.addEventListener('DOMContentLoaded', event => {
    const tables = document.querySelectorAll('.simple-datatable');
    tables.forEach(table => {
        new simpleDatatables.DataTable(table);
    });
});
