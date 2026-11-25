/**
 * @file Lógica de la interfaz de AI Code Generator & Debugger.
 *
 * Toda la comunicación con el backend se realiza con `fetch`. Las respuestas
 * del modelo se insertan en el DOM mediante `textContent` o creando nodos,
 * nunca con `innerHTML`, para evitar inyección de HTML.
 */

"use strict";

/**
 * Muestra un mensaje de error dentro de un contenedor.
 *
 * @param {HTMLElement} container - Elemento donde se mostrará el mensaje.
 * @param {string} message - Texto del error.
 * @returns {void}
 */
function showError(container, message) {
    container.replaceChildren();
    const paragraph = document.createElement("p");
    paragraph.className = "error-message";
    paragraph.textContent = message;
    container.appendChild(paragraph);
}

/**
 * Sustituye el contenido de un contenedor por un párrafo de texto plano.
 *
 * @param {HTMLElement} container - Elemento que se actualizará.
 * @param {string} text - Texto a mostrar.
 * @returns {void}
 */
function setParagraph(container, text) {
    container.replaceChildren();
    const paragraph = document.createElement("p");
    paragraph.textContent = text;
    container.appendChild(paragraph);
}

/** Campo de texto donde se escribe la descripción o el código. */
const codeInput = document.getElementById("code-input");
/** Selector del modo de operación (generate/debug). */
const modeSelect = document.getElementById("mode");
/** Botón que envía el formulario. */
const submitButton = document.getElementById("submit-button");
/** Salida donde se muestra el código. */
const outputArea = document.getElementById("output");

/**
 * Envía el prompt y el modo al backend y pinta el código resultante.
 *
 * @async
 * @function generateCode
 * @param {Event} event - Evento de clic del botón.
 * @returns {Promise<void>} No devuelve valor; actualiza el DOM.
 */
async function generateCode(event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append("prompt", codeInput.value);
    formData.append("mode", modeSelect.value);

    try {
        const response = await fetch("/generate_code", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            outputArea.textContent = "Error: Failed to process the request.";
            return;
        }

        const data = await response.json();
        outputArea.textContent = data.code;
    } catch (error) {
        outputArea.textContent = "Error: Failed to process the request.";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    submitButton.addEventListener("click", generateCode);
});
