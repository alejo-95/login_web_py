// const btnDelete = document.querySelectorAll('.btn-delete');
// if (btnDelete) {
//     const btnArray = Array.from(btnDelete);
//     btnArray.forEach((btn) => {
//         btn.addEventListener('click', (e) => {
//             if (!confirm('Esta seguro que desea eliminar el registro?')) {
//                 e.preventDefault();
//             }
//         });
//     })
// }

$(document).ready(function () {
    $('#example').DataTable({
        columnDefs: [
            { targets: '_all', className: 'text-center' } // Centra las columnas asignadas
        ],
        "aLengthMenu": [[3, 5, 10, 25, -1], [3, 5, 10, 25, "Todo"]],
        "iDisplayLength": 3,
        "language": {
            "lengthMenu": "Mostrar _MENU_ datos por página",
            "zeroRecords": "No se encuentran datos - lo sentimos",
            "info": "Mostrando página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay datos disponibles",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "search": "Busqueda:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        }
    }
    );
});