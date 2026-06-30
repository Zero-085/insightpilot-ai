/**
 * InsightPilot AI - Upload Handler
 * Controls file selection, dropzone listeners, and file format validation.
 */
const Upload = {
    init: (dropzoneEl, fileInputEl, callbacks) => {
        if (!dropzoneEl || !fileInputEl) return;

        // Click on dropzone triggers file picker
        dropzoneEl.addEventListener("click", () => {
            if (dropzoneEl.classList.contains("disabled")) return;
            fileInputEl.click();
        });

        // File selection via input trigger
        fileInputEl.addEventListener("change", (e) => {
            const files = e.target.files;
            if (files && files.length > 0) {
                Upload.processSelection(files[0], callbacks);
            }
            // Reset value so same file can be selected again
            fileInputEl.value = "";
        });

        // Drag & Drop event bindings
        dropzoneEl.addEventListener("dragover", (e) => {
            e.preventDefault();
            if (dropzoneEl.classList.contains("disabled")) return;
            dropzoneEl.style.borderColor = "var(--primary)";
            dropzoneEl.style.backgroundColor = "var(--primary-light)";
        });

        const resetDropzoneStyle = () => {
            dropzoneEl.style.borderColor = "#cbd5e1";
            dropzoneEl.style.backgroundColor = "#faf5ff";
        };

        dropzoneEl.addEventListener("dragleave", (e) => {
            e.preventDefault();
            resetDropzoneStyle();
        });

        dropzoneEl.addEventListener("drop", (e) => {
            e.preventDefault();
            resetDropzoneStyle();
            if (dropzoneEl.classList.contains("disabled")) return;

            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                Upload.processSelection(files[0], callbacks);
            }
        });
    },

    /**
     * Validates file locally and triggers the upload callback flow.
     */
    processSelection: (file, callbacks) => {
        // Client-side CSV validation
        if (!file.name.toLowerCase().endsWith(".csv")) {
            if (callbacks.onError) {
                callbacks.onError("Client Validation Error: Only CSV files (.csv) are accepted.");
            }
            return;
        }

        if (file.size > 25 * 1024 * 1024) { // 25MB limit
            if (callbacks.onError) {
                callbacks.onError("Client Validation Error: File size exceeds the 25MB limit.");
            }
            return;
        }

        // Trigger upload pipeline start callback
        if (callbacks.onSelect) {
            callbacks.onSelect(file);
        }
    },

    setDisabled: (dropzoneEl, fileInputEl, isDisabled) => {
        if (!dropzoneEl || !fileInputEl) return;
        if (isDisabled) {
            dropzoneEl.classList.add("disabled");
            fileInputEl.disabled = true;
        } else {
            dropzoneEl.classList.remove("disabled");
            fileInputEl.disabled = false;
        }
    }
};
