document.addEventListener("DOMContentLoaded", () => {

    const formularios = document.querySelectorAll("form");

    formularios.forEach(formulario => {

        formulario.addEventListener("submit", () => {

            const boton = formulario.querySelector(
                'button[type="submit"]'
            );

            if (boton && formulario.checkValidity()) {

                boton.disabled = true;

                boton.style.opacity = "0.7";

                boton.textContent = "PROCESANDO...";

            }

        });

    });

});