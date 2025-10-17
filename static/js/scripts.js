document.addEventListener("DOMContentLoaded", function() {
    // Mostrar el modal de éxito o errores al cargar la página
    var modalElement = document.getElementById('modalAlerta');
    if (modalElement) {
        var modal = new bootstrap.Modal(modalElement);
        modal.show();
    }
});

function toggleComentarios() {
    var comentariosOcultos = document.querySelector('.comentarios_ocultos');
    var boton = document.getElementById('ver_comentarios');

    if (comentariosOcultos) {
        if (comentariosOcultos.style.display === 'none') {
            comentariosOcultos.style.display = 'block';
            boton.textContent = 'Ocultar comentarios';
        } else {
            comentariosOcultos.style.display = 'none';
            boton.textContent = 'Ver todos los comentarios';
        }
    }
}

