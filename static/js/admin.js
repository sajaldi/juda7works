document.addEventListener("DOMContentLoaded", function() {
    let categoriaField = document.querySelector("#id_categoria");

    if (categoriaField) {
        categoriaField.addEventListener("change", function() {
            let categoriaId = this.value;  // Obtener el ID de la categoría seleccionada
            
            fetch(`/admin/get_activos_por_categoria/?categoria_id=${categoriaId}`)
                .then(response => response.json())
                .then(data => {
                    console.log("Activos obtenidos:", data); // Verificar la respuesta aquí
                    let activosField = document.querySelector("#id_activos");
                    if (activosField) {
                        activosField.innerHTML = "";  // Limpiar opciones anteriores
                        data.activos.forEach(activo => {
                            let option = document.createElement("option");
                            option.value = activo.id;
                            option.textContent = activo.nombre;
                            activosField.appendChild(option);
                        });
                    }
                })
                .catch(error => console.error("Error al obtener activos:", error));
        });
    }
});
