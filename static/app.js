document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.querySelector("[data-file-input]");
    const dropZone = document.querySelector("[data-drop-zone]");
    const fileName = document.querySelector("[data-file-name]");
    const filePrompt = document.querySelector("[data-file-prompt]");
    const uploadError = document.querySelector("[data-upload-error]");
    const maxWorkbookBytes = 15 * 1024 * 1024;

    const updateFileState = () => {
        if (!fileInput || !fileName) return;
        const file = fileInput.files && fileInput.files[0];
        let error = "";
        if (file && !file.name.toLowerCase().endsWith(".xlsx")) error = "Choose an .xlsx workbook.";
        else if (file && file.size > maxWorkbookBytes) error = "Choose an .xlsx workbook under 15 MB.";
        fileInput.setCustomValidity(error);
        if (uploadError) {
            uploadError.textContent = error;
            uploadError.hidden = !error;
        }
        fileName.textContent = file ? file.name : "No file selected";
        if (filePrompt) filePrompt.textContent = file && !error ? "Workbook ready" : "Drop a workbook here";
        if (dropZone) dropZone.classList.toggle("has-file", Boolean(file && !error));
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
            if (event.dataTransfer.files.length === 1) {
                fileInput.files = event.dataTransfer.files;
                updateFileState();
            } else if (uploadError) {
                uploadError.textContent = "Drop one workbook at a time.";
                uploadError.hidden = false;
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

    document.querySelectorAll("[data-analysis-form]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const submitButton = event.submitter || form.querySelector("[data-submit-button]");
            if (!submitButton) return;
            if (submitButton.name) {
                const scope = document.createElement("input");
                scope.type = "hidden";
                scope.name = submitButton.name;
                scope.value = submitButton.value;
                form.append(scope);
            }
            submitButton.disabled = true;
            submitButton.querySelector("span").textContent = "Analyzing workbook…";
            submitButton.classList.add("is-loading");
        });
    });

    document.querySelectorAll("[data-tabs]").forEach((tabGroup) => {
        const tabs = Array.from(tabGroup.querySelectorAll("[role='tab']"));
        const activateTab = (nextTab) => {
            tabs.forEach((tab) => {
                const isActive = tab === nextTab;
                const panel = document.getElementById(tab.dataset.tabTarget);
                tab.classList.toggle("is-active", isActive);
                tab.setAttribute("aria-selected", String(isActive));
                tab.tabIndex = isActive ? 0 : -1;
                if (panel) {
                    panel.hidden = !isActive;
                    panel.classList.toggle("is-active", isActive);
                }
            });
        };

        tabs.forEach((tab, index) => {
            tab.addEventListener("click", () => activateTab(tab));
            tab.addEventListener("keydown", (event) => {
                if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
                event.preventDefault();
                let nextIndex = index;
                if (event.key === "ArrowRight") nextIndex = (index + 1) % tabs.length;
                if (event.key === "ArrowLeft") nextIndex = (index - 1 + tabs.length) % tabs.length;
                if (event.key === "Home") nextIndex = 0;
                if (event.key === "End") nextIndex = tabs.length - 1;
                activateTab(tabs[nextIndex]);
                tabs[nextIndex].focus();
            });
        });
    });
});
