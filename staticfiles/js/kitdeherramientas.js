function toggleCategoria(header) {
    var contenido = header.nextElementSibling;
    if (contenido.style.display === "none" || contenido.style.display === "") {
        contenido.style.display = "block";
    } else {
        contenido.style.display = "none";
    }
}

