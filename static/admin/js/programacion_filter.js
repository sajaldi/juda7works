document.addEventListener("DOMContentLoaded", function () {
    var categoriaField = document.querySelector("#id_categoria");
    var activosField = document.querySelector("#id_activos");

    if (categoriaField && activosField) {
        categoriaField.addEventListener("change", function () {
            var categoriaId = categoriaField.value;

            fetch(`/admin/get_activos_por_categoria/?categoria=${categoriaId}`)
                .then(response => response.json())
                .then(data => {
                    activosField.innerHTML = "";
                    data.activos.forEach(function (activo) {
                        var option = document.createElement("option");
                        option.value = activo.id;
                        option.textContent = activo.nombre;
                        activosField.appendChild(option);
                    });
                })
                .catch(error => console.error("Error al cargar activos:", error));
        });
    }
});
