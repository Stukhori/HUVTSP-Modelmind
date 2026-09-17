document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.querySelector("[data-file-input]");
    const dropZone = document.querySelector("[data-drop-zone]");
    const fileName = document.querySelector("[data-file-name]");
    const filePrompt = document.querySelector("[data-file-prompt]");

    const updateFileState = () => {
        if (!fileInput || !fileName) return;
        const file = fileInput.files && fileInput.files[0];
        fileName.textContent = file ? file.name : "No file selected";
        if (filePrompt) filePrompt.textContent = file ? "Workbook ready" : "Drop a workbook here";
        if (dropZone) dropZone.classList.toggle("has-file", Boolean(file));
    };

    if (fileInput) fileInput.addEventListener("change", updateFileState);

    if (dropZone && fileInput) {
        ["dragenter", "dragover"].forEach((eventName) => {
            dropZone.addEventListener(eventName, (event) => {
                event.preventDefault();
                dropZone.classList.add("is-dragging");
            });
        });
        ["dragleave", "drop"].forEach((eventName) => {
            dropZone.addEventListener(eventName, (event) => {
                event.preventDefault();
                dropZone.classList.remove("is-dragging");
            });
        });
        dropZone.addEventListener("drop", (event) => {
            if (event.dataTransfer.files.length) {
                fileInput.files = event.dataTransfer.files;
                updateFileState();
            }
        });
    }

    const question = document.querySelector("#user_question");
    document.querySelectorAll("[data-prompt]").forEach((button) => {
        button.addEventListener("click", () => {
            if (!question) return;
            question.value = button.dataset.prompt;
            question.focus();
        });
    });

    const form = document.querySelector("[data-analysis-form]");
    const submitButton = document.querySelector("[data-submit-button]");
    if (form && submitButton) {
        form.addEventListener("submit", () => {
            submitButton.disabled = true;
            submitButton.querySelector("span").textContent = "Analyzing workbook…";
            submitButton.classList.add("is-loading");
        });
    }
});
