$(function () {

    $(".datatable").DataTable({

        responsive: true,
        autoWidth: false,
        pageLength: 10,
        lengthMenu: [

            [10, 25, 50, 100, -1],

            [10, 25, 50, 100, "Todos"]

        ],

        order: [[0, "desc"]],
        stateSave: true,
        searching: true,
        paging: true,
        info: true,
        lengthChange: true,

        language: {

            decimal: "",
            emptyTable: "No existen registros.",
            info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
            infoEmpty: "0 registros",
            infoFiltered: "(Filtrado de _MAX_ registros)",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ registros",
            loadingRecords: "Cargando...",
            processing: "Procesando...",

            search: "Buscar:",
            zeroRecords: "No se encontraron resultados",

            paginate: {

                first: "Primero",
                last: "Último",
                next: "Siguiente",
                previous: "Anterior"

            }

        },

        dom: 'Bfrtip',

        buttons: [

            {

                extend: 'excel',
                text: 'Excel',
                className: 'btn btn-success btn-sm'

            },

            {

                extend: 'pdf',
                text: 'PDF',
                className: 'btn btn-danger btn-sm'

            },

            {

                extend: 'print',
                text: 'Imprimir',
                className: 'btn btn-secondary btn-sm'

            }

        ]

    });

});