document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("import-form");
    const loader = document.getElementById("loader");

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Evita que el formulario se envíe instantáneamente

        // Oculta el formulario y muestra la barra de carga
        form.style.display = "none";
        loader.style.display = "block";

        // Simula el tiempo de importación con un retraso antes de enviar el formulario
        setTimeout(() => {
            form.submit(); // Envía el formulario después de 3 segundos
        }, 3000);
    });
});
